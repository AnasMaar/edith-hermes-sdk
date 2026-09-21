# syntax=docker/dockerfile:1.7
# Production builds should override this with a release tag or, preferably, a digest.
ARG HERMES_BASE_IMAGE=nousresearch/hermes-agent:latest
FROM ${HERMES_BASE_IMAGE}

LABEL org.opencontainers.image.title="Hermes SDK Kubernetes Runtime" \
      org.opencontainers.image.description="Kubernetes-oriented Hermes runtime derived from the official Nous Research image" \
      org.opencontainers.image.source="https://github.com/NousResearch/hermes-agent" \
      io.hermes.sdk.runtime="true"

# The upstream image intentionally starts as root to initialize s6 services and remap host UIDs.
# A Kubernetes pod supplies volume ownership through fsGroup, so this derivative bypasses s6 and
# executes one headless Hermes backend as the upstream non-root user.
USER 10000:10000

EXPOSE 9119
VOLUME ["/opt/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl --fail --silent --show-error http://127.0.0.1:9119/api/health || exit 1

ENTRYPOINT ["/opt/hermes/.venv/bin/hermes"]
CMD ["serve", "--host", "0.0.0.0", "--port", "9119"]

