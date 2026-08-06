import bff.auth as auth
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_open_when_key_unset(monkeypatch) -> None:
    monkeypatch.delenv(auth.ENV_API_KEY, raising=False)
    app.openapi_schema = None
    response = client.get("/api/v1/jobs/does-not-exist")
    assert response.status_code == 404


def test_api_requires_key_when_configured(monkeypatch) -> None:
    monkeypatch.setenv(auth.ENV_API_KEY, "secret-test-key")
    app.openapi_schema = None

    denied = client.get("/api/v1/jobs/does-not-exist")
    assert denied.status_code == 401

    allowed = client.get(
        "/api/v1/jobs/does-not-exist",
        headers={"X-API-Key": "secret-test-key"},
    )
    assert allowed.status_code == 404

    bearer = client.get(
        "/api/v1/jobs/does-not-exist",
        headers={"Authorization": "Bearer secret-test-key"},
    )
    assert bearer.status_code == 404


def test_index_sets_api_key_cookie(monkeypatch) -> None:
    monkeypatch.setenv(auth.ENV_API_KEY, "secret-test-key")
    response = client.get("/")
    assert response.status_code == 200
    assert response.cookies.get(auth.API_KEY_COOKIE) == "secret-test-key"


def test_health_remains_public_with_api_key(monkeypatch) -> None:
    monkeypatch.setenv(auth.ENV_API_KEY, "secret-test-key")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_openapi_includes_security_when_key_set(monkeypatch) -> None:
    monkeypatch.setenv(auth.ENV_API_KEY, "secret-test-key")
    app.openapi_schema = None
    payload = client.get("/openapi.json").json()
    assert "ApiKeyAuth" in payload["components"]["securitySchemes"]
    assert payload["security"] == [{"ApiKeyAuth": []}]
