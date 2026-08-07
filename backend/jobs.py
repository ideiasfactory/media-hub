from __future__ import annotations

import hashlib
import json
import logging
import shutil
import threading
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from backend.media import download_audio, fetch_metadata
from backend.models import JobRequest, JobStatus
from backend.registry import build_entry, content_identity, find_by_identity, upsert
from backend.transcription import transcribe_audio
from backend.utils import ALLOWED_ARTIFACTS, extract_youtube_video_id, generate_srt

logger = logging.getLogger(__name__)
OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "output"


class JobCancelled(Exception):
    """Raised when a running job honors a cancel request."""


@dataclass
class Job:
    job_id: str
    source_url: str
    model: str
    requested_language: str
    force: bool = False
    status: JobStatus = JobStatus.QUEUED
    progress: int = 0
    message: str = "Aguardando processamento"
    metadata: dict[str, Any] | None = None
    transcript: str | None = None
    artifacts: list[str] = field(default_factory=list)
    cancel_requested: bool = False
    from_cache: bool = False

    def public(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("source_url")
        data.pop("model")
        data.pop("requested_language")
        data.pop("force")
        data.pop("from_cache")
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
            force=request.force,
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

    def request_cancel(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            terminal = {
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            }
            if job.status in terminal:
                return deepcopy(job)
            job.cancel_requested = True
            job.message = "Cancelamento solicitado"
            return deepcopy(job)


job_store = JobStore()


def _file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ensure_not_cancelled(job_id: str) -> None:
    job = job_store.get(job_id)
    if job and job.cancel_requested:
        raise JobCancelled()


def _complete_from_registry(job_id: str, job: Job, entry: dict[str, Any]) -> None:
    source_dir = Path(entry["artifact_dir"])
    job_dir = OUTPUT_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    artifacts = [name for name in entry.get("artifacts", []) if name in ALLOWED_ARTIFACTS]
    for name in artifacts:
        src = source_dir / name
        if src.is_file():
            shutil.copy2(src, job_dir / name)
    transcript = None
    transcript_path = job_dir / "transcript.txt"
    if transcript_path.is_file():
        transcript = transcript_path.read_text(encoding="utf-8").strip()
    metadata = {
        "job_id": job_id,
        "source": entry.get("platform") or "youtube",
        "source_url": job.source_url,
        "video_id": entry.get("video_id"),
        "title": entry.get("title") or "Sem título",
        "channel": entry.get("channel") or "Canal desconhecido",
        "duration_seconds": entry.get("duration"),
        "requested_language": job.requested_language,
        "detected_language": None,
        "model": job.model,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "from_cache": True,
        "content_hash": entry.get("content_hash"),
    }
    meta_path = job_dir / "metadata.json"
    if meta_path.is_file():
        try:
            stored = json.loads(meta_path.read_text(encoding="utf-8"))
            if isinstance(stored, dict):
                metadata["detected_language"] = stored.get("detected_language")
        except json.JSONDecodeError:
            pass
    present = sorted(name for name in artifacts if (job_dir / name).is_file())
    job_store.update(
        job_id,
        status=JobStatus.COMPLETED,
        progress=100,
        message="Concluído (reutilizado do registry)",
        metadata=metadata,
        transcript=transcript,
        artifacts=present,
        from_cache=True,
    )
    logger.info("Job %s atendido via registry (%s)", job_id, entry.get("content_hash"))


def process_job(job_id: str) -> None:
    job = job_store.get(job_id)
    if not job:
        return
    job_dir = OUTPUT_ROOT / job_id
    logger.info("Job %s iniciado (force=%s)", job_id, job.force)

    try:
        job_dir.mkdir(parents=True, exist_ok=False)
        video_id_hint = extract_youtube_video_id(job.source_url)
        if video_id_hint and not job.force:
            early_hash = content_identity(
                platform="youtube",
                video_id=video_id_hint,
                canonical_url=job.source_url,
                duration="",
                title="",
            )
            cached = find_by_identity(early_hash)
            if cached and Path(cached.get("artifact_dir", "")).is_dir():
                _ensure_not_cancelled(job_id)
                _complete_from_registry(job_id, job, cached)
                return

        job_store.update(
            job_id,
            status=JobStatus.FETCHING_METADATA,
            progress=10,
            message="Obtendo metadados",
        )
        _ensure_not_cancelled(job_id)
        source_metadata = fetch_metadata(job.source_url)
        video_id = source_metadata.get("id") or video_id_hint
        title = source_metadata.get("title") or "Sem título"
        channel = (
            source_metadata.get("channel")
            or source_metadata.get("uploader")
            or "Canal desconhecido"
        )
        duration = source_metadata.get("duration")
        identity = content_identity(
            platform="youtube",
            video_id=video_id,
            canonical_url=job.source_url,
            duration=duration,
            title=title,
        )
        if not job.force:
            cached = find_by_identity(identity)
            if cached and Path(cached.get("artifact_dir", "")).is_dir():
                _ensure_not_cancelled(job_id)
                _complete_from_registry(job_id, job, cached)
                return

        job_store.update(
            job_id,
            status=JobStatus.DOWNLOADING,
            progress=25,
            message="Baixando áudio",
        )
        _ensure_not_cancelled(job_id)
        audio_path = download_audio(job.source_url, job_dir)

        job_store.update(
            job_id,
            status=JobStatus.TRANSCRIBING,
            progress=55,
            message="Transcrevendo áudio",
        )
        _ensure_not_cancelled(job_id)
        language = None if job.requested_language == "autodetect" else job.requested_language
        segments, detected_language = transcribe_audio(audio_path, job.model, language)
        transcript = " ".join(segment["text"].strip() for segment in segments).strip()

        job_store.update(
            job_id,
            status=JobStatus.GENERATING_FILES,
            progress=85,
            message="Gerando arquivos",
        )
        _ensure_not_cancelled(job_id)
        metadata = {
            "job_id": job_id,
            "source": "youtube",
            "source_url": job.source_url,
            "video_id": video_id,
            "title": title,
            "channel": channel,
            "duration_seconds": duration,
            "requested_language": job.requested_language,
            "detected_language": detected_language,
            "model": job.model,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "from_cache": False,
            "content_hash": identity,
        }
        (job_dir / "transcript.txt").write_text(transcript + "\n", encoding="utf-8")
        (job_dir / "transcript.srt").write_text(generate_srt(segments), encoding="utf-8")
        (job_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        artifacts = sorted(
            filename for filename in ALLOWED_ARTIFACTS if (job_dir / filename).is_file()
        )
        upsert(
            build_entry(
                content_hash=identity,
                platform="youtube",
                url=job.source_url,
                canonical_url=job.source_url,
                video_id=video_id,
                title=title,
                channel=channel,
                duration=duration,
                artifacts=artifacts,
                artifact_dir=str(job_dir.resolve()),
                transcript_hash=_file_sha256(job_dir / "transcript.txt"),
                audio_hash=_file_sha256(job_dir / "audio.mp3"),
            )
        )
        job_store.update(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            message="Concluído",
            metadata=metadata,
            transcript=transcript,
            artifacts=artifacts,
            from_cache=False,
        )
        logger.info("Job %s concluído", job_id)
    except JobCancelled:
        logger.info("Job %s cancelado", job_id)
        job_store.update(
            job_id,
            status=JobStatus.CANCELLED,
            message="Processamento cancelado pelo usuário",
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
