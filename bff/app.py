"""FastAPI application factory for the Media Hub BFF."""

from __future__ import annotations

from backend.jobs import OUTPUT_ROOT
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from frontend import STATIC_DIR

from app import __version__
from bff.api.v1 import router as api_v1_router
from bff.auth import api_key_required
from bff.web import router as web_router

load_dotenv()


def create_app() -> FastAPI:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    application = FastAPI(
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
    application.include_router(web_router)
    application.include_router(api_v1_router)
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    def custom_openapi() -> dict:
        if application.openapi_schema:
            return application.openapi_schema
        schema = get_openapi(
            title=application.title,
            version=application.version,
            description=application.description,
            routes=application.routes,
        )
        if api_key_required():
            schema.setdefault("components", {}).setdefault("securitySchemes", {})["ApiKeyAuth"] = {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
            }
            schema["security"] = [{"ApiKeyAuth": []}]
        application.openapi_schema = schema
        return application.openapi_schema

    application.openapi = custom_openapi  # type: ignore[method-assign]
    return application
