from pathlib import Path

import backend.jobs as jobs
from backend.jobs import JobStore
from backend.models import JobRequest, JobStatus


def test_process_job_generates_all_artifacts(monkeypatch, tmp_path: Path) -> None:
    store = JobStore()
    monkeypatch.setattr(jobs, "job_store", store)
    monkeypatch.setattr(jobs, "OUTPUT_ROOT", tmp_path / "out")
    monkeypatch.setattr(jobs, "find_by_identity", lambda identity: None)
    monkeypatch.setattr(jobs, "upsert", lambda entry: None)
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

    job = store.create(
        JobRequest(
            url="https://www.youtube.com/watch?v=video123",
            model="tiny",
            language="autodetect",
        )
    )
    jobs.process_job(job.job_id)

    completed = store.get(job.job_id)
    assert completed is not None
    assert completed.status == JobStatus.COMPLETED
    assert completed.progress == 100
    assert completed.transcript == "Transcrição de teste."
    assert completed.metadata is not None
    assert completed.metadata["detected_language"] == "pt"
    assert completed.artifacts == [
        "audio.mp3",
        "metadata.json",
        "transcript.srt",
        "transcript.txt",
    ]
    for filename in completed.artifacts:
        assert (tmp_path / "out" / job.job_id / filename).is_file()
