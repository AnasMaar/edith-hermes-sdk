"""OIDC bearer authentication and tenant identity extraction."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import HTTPException, Request
from jwt import PyJWKClient

from .config import Settings


@dataclass(frozen=True, slots=True)
class Identity:
    tenant_id: str
    subject_id: str

    @property
    def owner(self) -> tuple[str, str]:
        return self.tenant_id, self.subject_id

    def document(self) -> dict[str, str]:
        return {"tenantId": self.tenant_id, "subjectId": self.subject_id}


class Authenticator:
    def __init__(self, settings: Settings):
        self.settings = settings
        jwks_url = (
            settings.oidc_jwks_url or settings.oidc_issuer.rstrip("/") + "/.well-known/jwks.json"
        )
        self._jwks = PyJWKClient(jwks_url) if settings.auth_mode == "oidc" else None

    async def __call__(self, request: Request) -> Identity:
        return await self.from_headers(request.headers)

    async def from_headers(self, headers: Mapping[str, str]) -> Identity:
        if self.settings.auth_mode == "none":
            return Identity(
                headers.get("x-edith-tenant", self.settings.anonymous_tenant_id),
                headers.get("x-edith-subject", self.settings.anonymous_subject_id),
            )
        authorization = headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            raise HTTPException(401, "Bearer authentication is required")
        token = authorization[7:].strip()
        if self.settings.auth_mode == "static":
            configured = self.settings.dev_tokens.get(token)
            if not configured:
                raise HTTPException(401, "Invalid development token")
            return Identity(configured["tenantId"], configured["subjectId"])
        try:
            assert self._jwks is not None
            signing_key = await asyncio.to_thread(self._jwks.get_signing_key_from_jwt, token)
            claims: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256", "EdDSA"],
                audience=self.settings.oidc_audience,
                issuer=self.settings.oidc_issuer,
                options={"require": ["exp", "iat", self.settings.subject_claim]},
            )
            tenant = str(claims[self.settings.tenant_claim])
            subject = str(claims[self.settings.subject_claim])
        except (KeyError, ValueError, jwt.PyJWTError) as exc:
            raise HTTPException(401, "Invalid bearer token") from exc
        if not tenant or not subject:
            raise HTTPException(401, "Token is missing tenant or subject identity")
        return Identity(tenant, subject)
