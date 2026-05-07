# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --registry=https://registry.npmmirror.com
COPY frontend/ .
RUN npm run build

# Stage 2: Python runtime
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV PYTHONPATH=/app

COPY pyproject.toml ./
RUN uv pip install --system --no-cache-dir \
    --index-url https://mirrors.aliyun.com/pypi/simple/ .

COPY app/ ./app/
COPY plugins/ ./plugins/
COPY --from=frontend-build /build/dist/ ./frontend/dist/

RUN mkdir -p app/config
VOLUME /app/app/config

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; r=urllib.request.urlopen('http://localhost:8000/version'); assert r.status==200" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
