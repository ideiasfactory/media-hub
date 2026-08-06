from __future__ import annotations

import json
import logging
import threading
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.media import download_audio, fetch_metadata
from app.models import JobRequest, JobStatus
from app.transcription import transcribe_audio
from app.utils import ALLOWED_ARTIFACTS, generate_srt

logger = logging.getLogger(__name__)
OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "output"


@dataclass
class Job:
    job_id: str
    source_url: str
    model: str
    requested_language: str
    status: JobStatus = JobStatus.QUEUED
    progress: int = 0
    message: str = "Aguardando processamento"
    metadata: dict[str, Any] | None = None
    transcript: str | None = None
    artifacts: list[str] = field(default_factory=list)

    def public(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("source_url")
        data.pop("model")
        data.pop("requested_language")
        return data


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, request: JobRequest) -> Job:
        job = Job(
            job_id=str(uuid4()),
            source_url=request.url,
            model=request.model,
            requested_language=request.language,
        )
        with self._lock:
            self._jobs[job.job_id] = job
        return deepcopy(job)

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return deepcopy(job) if job else None

    def update(self, job_id: str, **changes: Any) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in changes.items():
                setattr(job, key, value)


job_store = JobStore()


def process_job(job_id: str) -> None:
    job = job_store.get(job_id)
    if not job:
        return
    job_dir = OUTPUT_ROOT / job_id

    try:
        job_dir.mkdir(parents=True, exist_ok=False)
        job_store.update(
            job_id,
            status=JobStatus.FETCHING_METADATA,
            progress=10,
            message="Obtendo metadados",
        )
        source_metadata = fetch_metadata(job.source_url)

        job_store.update(
            job_id,
            status=JobStatus.DOWNLOADING,
            progress=25,
            message="Baixando áudio",
        )
        audio_path = download_audio(job.source_url, job_dir)

        job_store.update(
            job_id,
            status=JobStatus.TRANSCRIBING,
            progress=55,
            message="Transcrevendo áudio",
        )
        language = None if job.requested_language == "autodetect" else job.requested_language
        segments, detected_language = transcribe_audio(audio_path, job.model, language)
        transcript = " ".join(segment["text"].strip() for segment in segments).strip()

        job_store.update(
            job_id,
            status=JobStatus.GENERATING_FILES,
            progress=85,
            message="Gerando arquivos",
        )
        metadata = {
            "job_id": job_id,
            "source": "youtube",
            "source_url": job.source_url,
            "video_id": source_metadata.get("id"),
            "title": source_metadata.get("title") or "Sem título",
            "channel": source_metadata.get("channel")
            or source_metadata.get("uploader")
            or "Canal desconhecido",
            "duration_seconds": source_metadata.get("duration"),
            "requested_language": job.requested_language,
            "detected_language": detected_language,
            "model": job.model,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
        (job_dir / "transcript.txt").write_text(transcript + "\n", encoding="utf-8")
        (job_dir / "transcript.srt").write_text(generate_srt(segments), encoding="utf-8")
        (job_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        artifacts = sorted(
            filename for filename in ALLOWED_ARTIFACTS if (job_dir / filename).is_file()
        )
        job_store.update(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            message="Concluído",
            metadata=metadata,
            transcript=transcript,
            artifacts=artifacts,
        )
    except Exception:
        logger.exception("Falha ao processar job %s", job_id)
        job_store.update(
            job_id,
            status=JobStatus.FAILED,
            message=(
                "Não foi possível processar o vídeo. Verifique a URL, a disponibilidade "
                "pública do conteúdo e a instalação do FFmpeg."
            ),
        )
