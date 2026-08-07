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
    assert 'rel="apple-touch-icon"' in response.text
    assert 'rel="manifest"' in response.text


def test_app_icons() -> None:
    favicon = client.get("/favicon.ico")
    assert favicon.status_code == 200
    assert favicon.headers["content-type"].startswith("image/")
    assert favicon.content

    apple = client.get("/apple-touch-icon.png")
    assert apple.status_code == 200
    assert apple.headers["content-type"].startswith("image/")
    assert apple.content[:8] == b"\x89PNG\r\n\x1a\n"

    precomposed = client.get("/apple-touch-icon-precomposed.png")
    assert precomposed.status_code == 200
    assert precomposed.content == apple.content

    manifest = client.get("/static/site.webmanifest")
    assert manifest.status_code == 200
    assert "Media Hub" in manifest.text


def test_changelog_page() -> None:
    response = client.get("/changelog")
    assert response.status_code == 200
    assert "Novidades" in response.text
    assert "0.2.1" in response.text
    assert "0.2.0" in response.text
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
