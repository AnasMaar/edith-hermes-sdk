"""Convenient, typed provider login handles over the generated auth contract."""

from __future__ import annotations

import asyncio
import webbrowser
from typing import Any, cast
from urllib.parse import urlsplit

from .errors import EdithHermesError
from .generated.types_providers import ProviderLogin
from .resources import UNSET, Resource, Unset, payload


class ProviderLoginError(EdithHermesError):
    """A login ended without approval; ``login`` contains its safe public state."""

    def __init__(self, login: ProviderLogin):
        self.login = login
        super().__init__(f"Provider login {login['status']}: {login['errorCode']}")


class ProviderResourceBase(Resource):
    async def _login(
        self, *, open_browser: bool = False, idempotency_key: str | Unset = UNSET
    ) -> ProviderLoginBase:
        """Start login; explicit user approval is still required at the provider.

        Opening the browser is opt-in. Nothing selects a model or starts inference.
        The returned handle can be polled, awaited, cancelled or reattached by ID.
        """
        from .generated.resources import ProviderLoginResource

        info = cast(
            "ProviderLogin",
            await self._invoke("startProviderLogin", payload({"idempotency_key": idempotency_key})),
        )
        login = ProviderLoginResource(self._sdk, **{**self._scope, "login_id": info["id"]})
        login._remember(info)
        if open_browser:
            await login.open_browser()
        return login


class ProviderLoginBase(Resource):
    _info: ProviderLogin | None = None

    def _remember(self, info: Any) -> ProviderLogin:
        self._info = cast("ProviderLogin", info)
        return self._info

    @property
    def id(self) -> str:
        return self._scope["login_id"]

    @property
    def info(self) -> ProviderLogin:
        if self._info is None:
            raise RuntimeError(
                "Fetch the login with await login.get() before reading its instructions"
            )
        return self._info.copy()

    @property
    def verification_url(self) -> str | None:
        return self.info["verificationUrl"]

    @property
    def user_code(self) -> str | None:
        return self.info["userCode"]

    @property
    def status(self) -> str:
        return self.info["status"]

    async def open_browser(self) -> bool:
        """Open only the provider verification page. Never automate consent."""
        url = self.verification_url
        if not url:
            raise RuntimeError("This login has no verification URL")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError(
                "Provider verification URLs must use HTTPS without embedded credentials"
            )
        return await asyncio.to_thread(webbrowser.open, url)

    async def wait(
        self,
        *,
        timeout: float = 900,
        poll_interval: float | None = None,
        raise_on_failure: bool = True,
    ) -> ProviderLogin:
        """Wait for consent. Timeout/cancelling this coroutine does not cancel native login.

        Polling uses Hermes' advertised interval unless overridden. An explicit
        ``cancel()`` is needed to cancel the native flow. Approval does not change
        the profile's model/provider: choose that separately with ``update()``.
        """
        interval = (
            poll_interval
            if poll_interval is not None
            else (self._info["pollInterval"] if self._info else 5)
        )
        info = self._remember(
            await self._wait(
                "getProviderLogin",
                "status",
                {"approved", "denied", "expired", "cancelled", "failed"},
                timeout=timeout,
                poll_interval=interval,
            )
        )
        if raise_on_failure and info["status"] != "approved":
            raise ProviderLoginError(info)
        return info
