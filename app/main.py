from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import __version__
from app.api import router
from app.auth import API_KEY_COOKIE, api_key_required, get_configured_api_key
from app.jobs import OUTPUT_ROOT
from app.releases import list_user_releases, latest_user_release

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Media Hub",
    version=__version__,
    description=(
        "Aquisição e transcrição de mídia para o ecossistema Ideias Factory. "
        "API versionada em `/api/v1`. Proteja os endpoints com `MEDIA_HUB_API_KEY` "
        "e o header `X-API-Key` quando em uso compartilhado."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.include_router(router)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    if api_key_required():
        schema.setdefault("components", {}).setdefault("securitySchemes", {})["ApiKeyAuth"] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
        }
        schema["security"] = [{"ApiKeyAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]


def _html_response(request: Request, name: str, context: dict | None = None) -> HTMLResponse:
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


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request) -> HTMLResponse:
    return _html_response(
        request,
        "index.html",
        {"latest_release": latest_user_release(), "api_key_enabled": api_key_required()},
    )


@app.get("/changelog", response_class=HTMLResponse, include_in_schema=False)
def changelog_page(request: Request) -> HTMLResponse:
    return _html_response(
        request,
        "changelog.html",
        {"releases": list_user_releases()},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/releases", include_in_schema=False)
def releases_json() -> JSONResponse:
    return JSONResponse({"version": __version__, "releases": list_user_releases()})
