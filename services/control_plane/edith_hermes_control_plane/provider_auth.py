"""Profile-scoped native dashboard auth, with a secret-free login registry."""

from __future__ import annotations

import math
import re
import time
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, NoReturn
from urllib.parse import quote

import httpx

if TYPE_CHECKING:
    from .auth import Identity
    from .engine import ProductionEngine

OPERATIONS = {
    "listAuthProviders",
    "getAuthProvider",
    "disconnectAuthProvider",
    "startProviderLogin",
    "getProviderLogin",
    "cancelProviderLogin",
    "listProviderAccounts",
    "removeProviderAccount",
}
TERMINAL = {"approved", "denied", "expired", "cancelled", "failed"}
ERROR_CODES = {
    "denied": "authorization_denied",
    "expired": "authorization_expired",
    "failed": "authorization_failed",
    "cancelled": "cancelled",
}


def _fail(status: int, title: str, detail: str, *, retryable: bool = False) -> NoReturn:
    # Late import keeps this adapter independent of the engine dispatch cycle.
    from .engine import Problem

    raise Problem(status, title, detail, retryable=retryable)


def _timestamp(value: Any) -> float | None:
    try:
        result = (
            datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
            if isinstance(value, str) and "T" in value
            else float(value)
        )
        return result if math.isfinite(result) else None
    except (ValueError, TypeError, OverflowError):
        return None


def _iso(value: Any) -> str | None:
    stamp = _timestamp(value)
    try:
        return (
            datetime.fromtimestamp(stamp, timezone.utc).isoformat() if stamp is not None else None
        )
    except (ValueError, OverflowError, OSError):
        return None


def _credential_status(raw: dict[str, Any]) -> dict[str, Any]:
    expires = _timestamp(raw.get("expires_at"))
    revoked = raw.get("revoked") is True or raw.get("status") == "revoked"
    expired = expires is not None and expires <= time.time()
    validity = "revoked" if revoked else "expired" if expired else "unknown"
    state = (
        validity
        if validity != "unknown"
        else "unknown"
        if raw.get("error")
        else "authenticated"
        if raw.get("logged_in")
        else "unauthenticated"
    )
    return {
        "state": state,
        "loggedIn": bool(raw.get("logged_in")),
        "validity": validity,
        "expiresAt": _iso(raw.get("expires_at")),
        "hasRefreshToken": bool(raw.get("has_refresh_token")),
        "source": raw.get("source"),
    }


def _provider(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw["id"],
        "name": raw.get("name") or raw["id"],
        "flow": raw.get("flow") or "external",
        "loginSupported": raw.get("flow") == "device_code",
        "disconnectSupported": bool(raw.get("disconnectable")),
        "cliCommand": raw.get("cli_command"),
        "docsUrl": raw.get("docs_url"),
        "status": _credential_status(raw.get("status") or {}),
    }


class ProviderAuthentication:
    def __init__(self, engine: ProductionEngine):
        self.engine = engine

    async def _request(
        self,
        instance: dict[str, Any],
        profile: str,
        method: str,
        path: str,
        *,
        missing_session: bool = False,
        missing_account: bool = False,
    ) -> dict[str, Any] | None:
        try:
            response = await self.engine.gateway.dashboard_request(
                instance["connection"], method, path, profile=profile
            )
        except httpx.HTTPError:
            return _fail(
                502,
                "Provider authentication unavailable",
                "Could not contact Hermes",
                retryable=True,
            )
        except (ValueError, StopIteration):
            return _fail(
                501,
                "Provider authentication unsupported",
                "This connection has no supported dashboard transport",
            )
        if response.status_code == 404:
            if missing_session:
                return None
            if missing_account:
                return _fail(
                    404, "Account not found", "No native credential-pool entry exists at that index"
                )
            return _fail(
                501,
                "Provider authentication unsupported",
                "This Hermes runtime lacks the required dashboard auth endpoint",
            )
        if response.status_code in {401, 403}:
            return _fail(
                502,
                "Runtime authentication failed",
                "The control plane could not authenticate to Hermes; this is not a provider credential error",
            )
        if response.is_error:
            status = 422 if response.status_code < 500 else 502
            return _fail(
                status,
                "Provider request failed",
                "Hermes rejected the provider-auth request; native response details are withheld",
                retryable=response.status_code >= 500,
            )
        try:
            value = response.json()
            if not isinstance(value, dict):
                raise ValueError("Not an object")
        except (ValueError, TypeError):
            return _fail(
                502, "Invalid runtime response", "Hermes returned an invalid provider-auth response"
            )
        return value

    async def _catalog(self, instance: dict[str, Any], profile: str) -> list[dict[str, Any]]:
        value = await self._request(instance, profile, "GET", "/api/providers/oauth")
        assert value is not None
        rows = value.get("providers")
        if not isinstance(rows, list) or any(
            not isinstance(row, dict) or not row.get("id") for row in rows
        ):
            return _fail(
                502, "Invalid runtime response", "Hermes returned an invalid provider catalog"
            )
        return [_provider(row) for row in rows]

    @staticmethod
    def _public(record: dict[str, Any]) -> dict[str, Any]:
        # Never return native session identifiers or arbitrary upstream fields.
        return {
            key: record[key]
            for key in (
                "id",
                "instanceId",
                "profileId",
                "providerId",
                "flow",
                "status",
                "verificationUrl",
                "userCode",
                "expiresAt",
                "pollInterval",
                "errorCode",
            )
        }

    async def _save(self, record: dict[str, Any], identity: Identity) -> dict[str, Any]:
        stored = await self.engine.database.save_provider_login(
            record["id"], identity.owner, record
        )
        return self._public(stored)

    async def _poll(
        self,
        record: dict[str, Any],
        instance: dict[str, Any],
        profile: str,
        identity: Identity,
    ) -> dict[str, Any]:
        if record["status"] in TERMINAL:
            return record
        path = f"/api/providers/oauth/{quote(record['providerId'], safe='')}/poll/{quote(record['nativeSessionId'], safe='')}"
        native = await self._request(instance, profile, "GET", path, missing_session=True)
        if native is None:
            record.update(status="expired", errorCode="runtime_session_lost")
        else:
            native_state = native.get("status")
            if native_state not in {
                "pending",
                "approved",
                "denied",
                "expired",
                "error",
                "cancelled",
            }:
                return _fail(
                    502, "Invalid runtime response", "Hermes returned an unknown login status"
                )
            state = "failed" if native_state == "error" else native_state
            expiry = _timestamp(record["expiresAt"])
            if state == "pending" and expiry is not None and expiry <= time.time():
                state = "expired"
                # Stop the worker, not just the SDK's polling loop, on expiry.
                await self._request(
                    instance,
                    profile,
                    "DELETE",
                    f"/api/providers/oauth/sessions/{quote(record['nativeSessionId'], safe='')}",
                    missing_session=True,
                )
            record.update(status=state, errorCode=ERROR_CODES.get(state))
        return await self.engine.database.save_provider_login(record["id"], identity.owner, record)

    async def handle(
        self, operation: str, args: dict[str, Any], identity: Identity
    ) -> tuple[int, Any]:
        if args.get("body"):
            return _fail(
                422,
                "Unsupported request body",
                "Provider-auth operations do not accept credentials or scope overrides in a request body",
            )
        instance = await self.engine._instance(args["instanceId"], identity)
        profile = await self.engine._profile_name(args["instanceId"], args["profileId"], identity)
        # Native RPC accepts display-case names, but dashboard HTTP validates the
        # canonical on-disk ID strictly (hermes_cli.profiles.normalize_profile_name).
        profile = profile.strip().lower()
        if instance.get("status") != "ready":
            return _fail(409, "Instance unavailable", "The Hermes instance is not ready")
        provider_id = args.get("providerId")
        if provider_id is not None and not re.fullmatch(
            r"[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}", provider_id
        ):
            return _fail(422, "Invalid provider", "Provider IDs must be catalog slugs")
        provider_path = "/api/providers/oauth/" + quote(provider_id or "", safe="")
        if operation == "listAuthProviders":
            return 200, {"items": await self._catalog(instance, profile)}
        if operation in {"getAuthProvider", "startProviderLogin", "disconnectAuthProvider"}:
            card = next(
                (
                    item
                    for item in await self._catalog(instance, profile)
                    if item["id"] == provider_id
                ),
                None,
            )
            if card is None:
                return _fail(
                    404, "Provider not found", "This OAuth provider is not available in Hermes"
                )
            if operation == "getAuthProvider":
                return 200, card
            if operation == "disconnectAuthProvider":
                if not card["disconnectSupported"]:
                    return _fail(
                        501,
                        "Disconnect unsupported",
                        "This provider requires external credential management; consult its catalog metadata",
                    )
                result = await self._request(instance, profile, "DELETE", provider_path)
                assert result is not None
                return 200, {"ok": bool(result.get("ok")), "providerId": provider_id}
            if not card["loginSupported"]:
                return _fail(
                    501,
                    "Login unsupported",
                    "This provider requires an external login; consult its catalog metadata",
                )
            native = await self._request(instance, profile, "POST", provider_path + "/start")
            assert native is not None
            if not isinstance(native.get("session_id"), str) or not native["session_id"]:
                return _fail(
                    502, "Invalid runtime response", "Hermes did not return a login session"
                )
            expiry = time.time() + max(1, min(float(native.get("expires_in") or 900), 86400))
            record = {
                "id": "login_" + uuid.uuid4().hex,
                "instanceId": args["instanceId"],
                "profileId": args["profileId"],
                "providerId": provider_id,
                "nativeSessionId": native["session_id"],
                "flow": native.get("flow") or card["flow"],
                "status": "pending",
                "verificationUrl": native.get("verification_url"),
                "userCode": native.get("user_code"),
                "expiresAt": _iso(expiry),
                "pollInterval": max(1, min(float(native.get("poll_interval") or 5), 60)),
                "errorCode": None,
            }
            return 201, await self._save(record, identity)
        if operation in {"getProviderLogin", "cancelProviderLogin"}:
            record = await self.engine.required("provider_login", args["loginId"], identity)
            if any(record[key] != args[key] for key in ("instanceId", "profileId", "providerId")):
                return _fail(
                    404,
                    "Login not found",
                    "This login does not belong to the selected provider/profile",
                )
            record = await self._poll(record, instance, profile, identity)
            if operation == "cancelProviderLogin" and record["status"] == "approved":
                return _fail(
                    409,
                    "Login already approved",
                    "Use provider.disconnect() to clear approved credentials",
                )
            if operation == "cancelProviderLogin" and record["status"] == "pending":
                result = await self._request(
                    instance,
                    profile,
                    "DELETE",
                    "/api/providers/oauth/sessions/" + quote(record["nativeSessionId"], safe=""),
                    missing_session=True,
                )
                record.update(
                    status="cancelled" if result and result.get("ok") else "expired",
                    errorCode="cancelled"
                    if result and result.get("ok")
                    else "runtime_session_lost",
                )
                return 200, await self._save(record, identity)
            return 200, self._public(record)
        if operation == "listProviderAccounts":
            result = await self._request(instance, profile, "GET", "/api/credentials/pool")
            assert result is not None
            entries: list[dict[str, Any]] = next(
                (
                    row.get("entries", [])
                    for row in result.get("providers", [])
                    if row.get("provider") == provider_id
                ),
                [],
            )
            return 200, {
                "items": [
                    {
                        "id": row["id"],
                        "index": row["index"],
                        "providerId": provider_id,
                        "label": row.get("label") or "",
                        "authType": row.get("auth_type") or "",
                        "source": row.get("source") or "",
                        "priority": row.get("priority") or 0,
                        "requestCount": row.get("request_count") or 0,
                        "hasRefreshToken": bool(row.get("has_refresh")),
                        "lastStatus": row.get("last_status"),
                        "validity": _credential_status(row)["validity"],
                    }
                    for row in entries
                ]
            }
        if operation == "removeProviderAccount":
            try:
                index = int(args["accountIndex"])
                if index < 1:
                    raise ValueError()
            except (ValueError, TypeError):
                return _fail(422, "Invalid account index", "Account indexes are one-based integers")
            result = await self._request(
                instance,
                profile,
                "DELETE",
                "/api/credentials/pool/" + quote(str(provider_id), safe="") + f"/{index}",
                missing_account=True,
            )
            assert result is not None
            return 200, {
                "ok": bool(result.get("ok")),
                "providerId": provider_id,
                "count": result.get("count", 0),
            }
        return _fail(501, "Unsupported auth operation", "No provider adapter is installed")
