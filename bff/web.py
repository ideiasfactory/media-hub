"""HTML routes served by the BFF from frontend templates."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from frontend import STATIC_DIR, TEMPLATES_DIR

from app import __version__
from bff.auth import API_KEY_COOKIE, api_key_required, get_configured_api_key
from bff.releases import latest_user_release, list_user_releases

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=TEMPLATES_DIR)

_FAVICON = STATIC_DIR / "favicon.ico"
_APPLE_TOUCH_ICON = STATIC_DIR / "apple-touch-icon.png"


def html_response(request: Request, name: str, context: dict | None = None) -> HTMLResponse:
    payload = {"app_version": __version__}
    if context:
        payload.update(context)
    response = templates.TemplateResponse(request=request, name=name, context=payload)
    api_key = get_configured_api_key()
    if api_key:
        response.set_cookie(
            key=API_KEY_COOKIE,
            value=api_key,
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
        )
    else:
        response.delete_cookie(API_KEY_COOKIE)
    return response


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(_FAVICON, media_type="image/x-icon")


@router.get("/apple-touch-icon.png", include_in_schema=False)
@router.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
def apple_touch_icon() -> FileResponse:
    return FileResponse(_APPLE_TOUCH_ICON, media_type="image/png")


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return html_response(
        request,
        "index.html",
        {"latest_release": latest_user_release(), "api_key_enabled": api_key_required()},
    )


@router.get("/changelog", response_class=HTMLResponse)
def changelog_page(request: Request) -> HTMLResponse:
    return html_response(
        request,
        "changelog.html",
        {"releases": list_user_releases()},
    )


@router.get("/api/releases")
def releases_json() -> JSONResponse:
    return JSONResponse({"version": __version__, "releases": list_user_releases()})
