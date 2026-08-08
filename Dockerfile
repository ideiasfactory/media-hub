# Media Hub — single Uvicorn process (EPIC-036 / ADR-024)
# Image: ghcr.io/ideiasfactory/media-hub
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MEDIA_HUB_HOME=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg curl ca-certificates unzip \
    && curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh \
    && deno --version \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && python -m pip install "yt-dlp[default]==2026.7.4"

COPY app ./app
COPY backend ./backend
COPY bff ./bff
COPY frontend ./frontend

RUN mkdir -p /app/output /app/logs \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin mediahub \
    && chown -R mediahub:mediahub /app

USER mediahub

EXPOSE 8010

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8010/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
