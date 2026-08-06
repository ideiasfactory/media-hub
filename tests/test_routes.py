from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Media Hub" in response.text
    assert "Baixar e Transcrever" in response.text
    assert 'id="job-form"' in response.text
    assert 'id="copy-transcript"' in response.text
