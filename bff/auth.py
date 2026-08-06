"""API key protection for /api/v1 routes."""

from __future__ import annotations

import os

from fastapi import Header, HTTPException, Request, status

API_KEY_HEADER = "X-API-Key"
API_KEY_COOKIE = "media_hub_api_key"
ENV_API_KEY = "MEDIA_HUB_API_KEY"


def get_configured_api_key() -> str:
    return os.getenv(ENV_API_KEY, "").strip()


def api_key_required() -> bool:
    return bool(get_configured_api_key())


def extract_provided_api_key(
    request: Request,
    x_api_key: str | None = None,
    authorization: str | None = None,
) -> str | None:
    if x_api_key and x_api_key.strip():
        return x_api_key.strip()
    if authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer" and value.strip():
            return value.strip()
    cookie = request.cookies.get(API_KEY_COOKIE)
    if cookie and cookie.strip():
        return cookie.strip()
    return None


async def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias=API_KEY_HEADER),
    authorization: str | None = Header(default=None),
) -> None:
    expected = get_configured_api_key()
    if not expected:
        return
    provided = extract_provided_api_key(request, x_api_key, authorization)
    if provided != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida ou ausente. Informe o header X-API-Key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
