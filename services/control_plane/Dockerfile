FROM moby/buildkit:v0.24.0 AS buildkit
FROM aquasec/trivy:0.66.0 AS trivy
FROM gcr.io/projectsigstore/cosign:v2.5.3 AS cosign
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid 10000 edith && useradd --uid 10000 --gid 10000 --create-home edith
COPY --from=buildkit /usr/bin/buildctl /usr/local/bin/buildctl
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
COPY --from=cosign /ko-app/cosign /usr/local/bin/cosign

WORKDIR /app
COPY pyproject.toml uv.lock README.md /app/
COPY src /app/src
COPY services/control_plane /app/services/control_plane
RUN pip install --no-cache-dir ".[control-plane]"

ENV PYTHONPATH=/app/services/control_plane \
    HOME=/home/edith \
    DOCKER_CONFIG=/home/edith/.docker \
    EDITH_DATABASE_URL=sqlite+aiosqlite:////var/lib/edith/edith-hermes.db \
    EDITH_LOCAL_RUNTIME_ROOT=/var/lib/edith/runtimes \
    EDITH_SECRET_DIRECTORY=/var/lib/edith/secrets
RUN mkdir -p /home/edith/.docker /var/lib/edith /var/run/secrets/edith-build /var/run/secrets/edith-callback && \
    chown -R 10000:10000 /home/edith /var/lib/edith /var/run/secrets/edith-build /var/run/secrets/edith-callback
USER 10000:10000
EXPOSE 8080
CMD ["uvicorn", "edith_hermes_control_plane.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
