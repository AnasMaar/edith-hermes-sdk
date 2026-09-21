"""Fail-closed production configuration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def _list(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(slots=True)
class Settings:
    database_url: str = "postgresql+asyncpg://edith:edith@postgres:5432/edith_hermes"
    oidc_issuer: str = ""
    oidc_audience: str = "edith-hermes-control-plane"
    oidc_jwks_url: str = ""
    tenant_claim: str = "tenant_id"
    subject_claim: str = "sub"
    allow_insecure_dev_auth: bool = False
    dev_tokens: dict[str, dict[str, str]] = field(default_factory=dict)
    build_command: str = "buildctl"
    buildkit_address: str = "tcp://buildkit.hermes-system.svc:1234"
    require_digest_pinned_base: bool = True
    allowed_base_repositories: list[str] = field(
        default_factory=lambda: ["nousresearch/hermes-agent"]
    )
    artifact_base_url: str = ""
    artifact_bearer_token: str = ""
    artifact_max_bytes: int = 268_435_456
    require_image_scan: bool = True
    require_image_signature: bool = True
    trivy_command: str = "trivy"
    cosign_command: str = "cosign"
    cosign_key: str = ""
    kubernetes_context: str = ""
    runtime_namespace: str = "hermes-runtimes"
    runtime_service_account: str = "hermes-runtime"
    runtime_bridge_image: str = "ghcr.io/anasmaar/edith-hermes-runtime-bridge:v0.2.0"
    image_pull_secrets: list[str] = field(default_factory=list)
    default_storage_size: str = "5Gi"
    default_storage_class: str = ""
    gateway_port: int = 9119
    bridge_port: int = 8081
    worker_poll_seconds: float = 1.0
    worker_concurrency: int = 4
    public_base_url: str = ""
    inference_base_url: str = "https://inference-api.nousresearch.com/v1"
    inference_api_key: str = ""
    cloud_invoke_url: str = ""
    cloud_bearer_token: str = ""

    @classmethod
    def from_env(cls) -> Settings:
        defaults = cls()
        raw_tokens = os.getenv("EDITH_DEV_TOKENS", "{}")
        return cls(
            database_url=os.getenv("EDITH_DATABASE_URL", defaults.database_url),
            oidc_issuer=os.getenv("EDITH_OIDC_ISSUER", ""),
            oidc_audience=os.getenv("EDITH_OIDC_AUDIENCE", defaults.oidc_audience),
            oidc_jwks_url=os.getenv("EDITH_OIDC_JWKS_URL", ""),
            tenant_claim=os.getenv("EDITH_TENANT_CLAIM", defaults.tenant_claim),
            subject_claim=os.getenv("EDITH_SUBJECT_CLAIM", defaults.subject_claim),
            allow_insecure_dev_auth=_bool("EDITH_ALLOW_INSECURE_DEV_AUTH"),
            dev_tokens=json.loads(raw_tokens),
            build_command=os.getenv("EDITH_BUILDKIT_COMMAND", defaults.build_command),
            buildkit_address=os.getenv("EDITH_BUILDKIT_ADDRESS", defaults.buildkit_address),
            require_digest_pinned_base=_bool("EDITH_REQUIRE_DIGEST_PINNED_BASE", True),
            allowed_base_repositories=_list("EDITH_ALLOWED_BASE_REPOSITORIES")
            or ["nousresearch/hermes-agent"],
            artifact_base_url=os.getenv("EDITH_ARTIFACT_BASE_URL", ""),
            artifact_bearer_token=os.getenv("EDITH_ARTIFACT_BEARER_TOKEN", ""),
            artifact_max_bytes=int(os.getenv("EDITH_ARTIFACT_MAX_BYTES", "268435456")),
            require_image_scan=_bool("EDITH_REQUIRE_IMAGE_SCAN", True),
            require_image_signature=_bool("EDITH_REQUIRE_IMAGE_SIGNATURE", True),
            trivy_command=os.getenv("EDITH_TRIVY_COMMAND", defaults.trivy_command),
            cosign_command=os.getenv("EDITH_COSIGN_COMMAND", defaults.cosign_command),
            cosign_key=os.getenv("EDITH_COSIGN_KEY", ""),
            kubernetes_context=os.getenv("EDITH_KUBERNETES_CONTEXT", ""),
            runtime_namespace=os.getenv("EDITH_RUNTIME_NAMESPACE", defaults.runtime_namespace),
            runtime_service_account=os.getenv(
                "EDITH_RUNTIME_SERVICE_ACCOUNT", defaults.runtime_service_account
            ),
            runtime_bridge_image=os.getenv(
                "EDITH_RUNTIME_BRIDGE_IMAGE", defaults.runtime_bridge_image
            ),
            image_pull_secrets=_list("EDITH_IMAGE_PULL_SECRETS"),
            default_storage_size=os.getenv(
                "EDITH_DEFAULT_STORAGE_SIZE", defaults.default_storage_size
            ),
            default_storage_class=os.getenv("EDITH_DEFAULT_STORAGE_CLASS", ""),
            gateway_port=int(os.getenv("EDITH_GATEWAY_PORT", str(defaults.gateway_port))),
            bridge_port=int(os.getenv("EDITH_BRIDGE_PORT", str(defaults.bridge_port))),
            worker_poll_seconds=float(os.getenv("EDITH_WORKER_POLL_SECONDS", "1")),
            worker_concurrency=int(os.getenv("EDITH_WORKER_CONCURRENCY", "4")),
            public_base_url=os.getenv("EDITH_PUBLIC_BASE_URL", ""),
            inference_base_url=os.getenv("EDITH_INFERENCE_BASE_URL", defaults.inference_base_url),
            inference_api_key=os.getenv("EDITH_INFERENCE_API_KEY", ""),
            cloud_invoke_url=os.getenv("EDITH_CLOUD_INVOKE_URL", ""),
            cloud_bearer_token=os.getenv("EDITH_CLOUD_BEARER_TOKEN", ""),
        )

    def validate(self) -> None:
        if not self.allow_insecure_dev_auth and not (self.oidc_issuer and self.oidc_audience):
            raise RuntimeError(
                "EDITH_OIDC_ISSUER and EDITH_OIDC_AUDIENCE are required in production"
            )
        if self.allow_insecure_dev_auth and not self.dev_tokens:
            raise RuntimeError("EDITH_DEV_TOKENS must be configured when dev auth is enabled")
        if self.require_image_signature and not self.cosign_key:
            raise RuntimeError("EDITH_COSIGN_KEY is required when image signatures are enforced")
