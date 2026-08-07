from __future__ import annotations

from pathlib import Path

import backend.jobs as jobs
from backend.jobs import JobStore
from backend.models import JobRequest, JobStatus
from backend.registry import build_entry, content_identity, find_by_identity, upsert
from backend.utils import extract_youtube_video_id


def test_extract_youtube_video_id() -> None:
    assert extract_youtube_video_id("https://www.youtube.com/watch?v=abc123XYZ") == "abc123XYZ"
    assert extract_youtube_video_id("https://youtu.be/abc123XYZ") == "abc123XYZ"
    assert extract_youtube_video_id("https://www.youtube.com/shorts/abc123XYZ") == "abc123XYZ"


def test_registry_upsert_and_lookup(tmp_path: Path) -> None:
    path = tmp_path / "registry.jsonl"
    identity = content_identity(
        platform="youtube",
        video_id="video123",
        canonical_url="https://www.youtube.com/watch?v=video123",
        duration=3,
        title="Vídeo",
    )
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    (artifact_dir / "audio.mp3").write_bytes(b"x")
    (artifact_dir / "transcript.txt").write_text("oi\n", encoding="utf-8")
    upsert(
        build_entry(
            content_hash=identity,
            platform="youtube",
            url="https://www.youtube.com/watch?v=video123",
            canonical_url="https://www.youtube.com/watch?v=video123",
            video_id="video123",
            title="Vídeo",
            channel="Canal",
            duration=3,
            artifacts=["audio.mp3", "transcript.txt"],
            artifact_dir=str(artifact_dir),
            transcript_hash="t",
            audio_hash="a",
        ),
        path=path,
    )
    found = find_by_identity(identity, path=path)
    assert found is not None
    assert found["video_id"] == "video123"


def _stub_pipeline(monkeypatch, store: JobStore, tmp_path: Path) -> None:
    monkeypatch.setattr(jobs, "job_store", store)
    monkeypatch.setattr(jobs, "OUTPUT_ROOT", tmp_path)
    monkeypatch.setattr(
        jobs,
        "fetch_metadata",
        lambda url: {
            "id": "video123",
            "title": "Vídeo de teste",
            "channel": "Canal de teste",
            "duration": 3,
        },
    )

    def fake_download(url: str, job_dir: Path) -> Path:
        audio = job_dir / "audio.mp3"
        audio.write_bytes(b"fake mp3")
        return audio

    monkeypatch.setattr(jobs, "download_audio", fake_download)
    monkeypatch.setattr(
        jobs,
        "transcribe_audio",
        lambda audio, model, language: (
            [{"start": 0.0, "end": 2.5, "text": "Transcrição de teste."}],
            "pt",
        ),
    )


def test_process_job_uses_registry_cache(monkeypatch, tmp_path: Path) -> None:
    store = JobStore()
    registry_path = tmp_path / "registry.jsonl"
    monkeypatch.setattr(
        jobs,
        "find_by_identity",
        lambda identity: find_by_identity(identity, registry_path),
    )
    monkeypatch.setattr(
        jobs,
        "upsert",
        lambda entry: upsert(entry, path=registry_path),
    )
    _stub_pipeline(monkeypatch, store, tmp_path / "out")

    first = store.create(
        JobRequest(url="https://www.youtube.com/watch?v=video123", model="tiny", force=False)
    )
    jobs.process_job(first.job_id)
    assert store.get(first.job_id).status == JobStatus.COMPLETED

    download_calls = {"n": 0}

    def counting_download(url: str, job_dir: Path) -> Path:
        download_calls["n"] += 1
        audio = job_dir / "audio.mp3"
        audio.write_bytes(b"fake")
        return audio

    monkeypatch.setattr(jobs, "download_audio", counting_download)
    second = store.create(
        JobRequest(url="https://www.youtube.com/watch?v=video123", model="tiny", force=False)
    )
    jobs.process_job(second.job_id)
    completed = store.get(second.job_id)
    assert completed is not None
    assert completed.status == JobStatus.COMPLETED
    assert completed.from_cache is True
    assert download_calls["n"] == 0
    assert "from_cache" in (completed.metadata or {})


def test_process_job_force_bypasses_registry(monkeypatch, tmp_path: Path) -> None:
    store = JobStore()
    registry_path = tmp_path / "registry.jsonl"
    monkeypatch.setattr(
        jobs,
        "find_by_identity",
        lambda identity: find_by_identity(identity, registry_path),
    )
    monkeypatch.setattr(
        jobs,
        "upsert",
        lambda entry: upsert(entry, path=registry_path),
    )
    _stub_pipeline(monkeypatch, store, tmp_path / "out")

    first = store.create(
        JobRequest(url="https://www.youtube.com/watch?v=video123", model="tiny", force=False)
    )
    jobs.process_job(first.job_id)

    download_calls = {"n": 0}

    def counting_download(url: str, job_dir: Path) -> Path:
        download_calls["n"] += 1
        audio = job_dir / "audio.mp3"
        audio.write_bytes(b"fake")
        return audio

    monkeypatch.setattr(jobs, "download_audio", counting_download)
    forced = store.create(
        JobRequest(url="https://www.youtube.com/watch?v=video123", model="tiny", force=True)
    )
    jobs.process_job(forced.job_id)
    assert store.get(forced.job_id).status == JobStatus.COMPLETED
    assert download_calls["n"] == 1


def test_request_cancel_stops_job(monkeypatch, tmp_path: Path) -> None:
    store = JobStore()
    monkeypatch.setattr(jobs, "job_store", store)
    monkeypatch.setattr(jobs, "OUTPUT_ROOT", tmp_path)
    job = store.create(JobRequest(url="https://www.youtube.com/watch?v=video123", model="tiny"))

    def slow_metadata(url: str):
        store.request_cancel(job.job_id)
        return {"id": "x", "title": "t", "channel": "c", "duration": 1}

    monkeypatch.setattr(jobs, "fetch_metadata", slow_metadata)
    monkeypatch.setattr(
        jobs,
        "download_audio",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("no download")),
    )

    jobs.process_job(job.job_id)
    finished = store.get(job.job_id)
    assert finished is not None
    assert finished.status == JobStatus.CANCELLED
