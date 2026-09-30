FROM python:3.13-slim

WORKDIR /app
RUN pip install --no-cache-dir "fastapi>=0.115,<1" "uvicorn[standard]>=0.32,<1" "websockets>=14,<16"
COPY services/runtime_bridge /app/services/runtime_bridge
COPY src/edith_hermes_rpc /app/services/runtime_bridge/edith_hermes_rpc
ENV PYTHONPATH=/app/services/runtime_bridge
USER 10001:10001
EXPOSE 8081
CMD ["uvicorn", "edith_hermes_runtime_bridge.app:app", "--host", "0.0.0.0", "--port", "8081"]
