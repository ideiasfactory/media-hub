from fastapi.testclient import TestClient

from app import __version__
from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}


def test_index() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Media Hub" in response.text
    assert "Baixar e Transcrever" in response.text
    assert 'id="job-form"' in response.text
    assert 'id="copy-transcript"' in response.text
    assert "/changelog" in response.text
    assert f"v{__version__}" in response.text


def test_changelog_page() -> None:
    response = client.get("/changelog")
    assert response.status_code == 200
    assert "Novidades" in response.text
    assert "0.1.2" in response.text
    assert "0.1.1" in response.text


def test_openapi_and_docs() -> None:
    docs = client.get("/docs")
    assert docs.status_code == 200
    schema = client.get("/openapi.json")
    assert schema.status_code == 200
    payload = schema.json()
    assert payload["info"]["version"] == __version__
    paths = payload["paths"]
    assert "/api/v1/jobs" in paths
    assert "/api/jobs" not in paths


def test_create_job_validation_on_v1() -> None:
    response = client.post(
        "/api/v1/jobs",
        json={"url": "https://example.com/not-youtube", "model": "base", "language": "pt"},
    )
    assert response.status_code == 422
