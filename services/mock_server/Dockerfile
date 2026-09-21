FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
COPY services/mock_server /app/services/mock_server
RUN pip install --no-cache-dir . fastapi uvicorn

ENV PYTHONPATH=/app/services/mock_server
ENV EDITH_MOCK_DATABASE=/data/mock-state.db
VOLUME ["/data"]
EXPOSE 8080
CMD ["uvicorn", "edith_hermes_mock.app:app", "--host", "0.0.0.0", "--port", "8080"]

