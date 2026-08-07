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
from backend.registry import (
    STEP_DONE,
    STEP_DOWNLOAD,
    STEP_FILES,
    STEP_METADATA,
    STEP_TRANSCRIBE,
    build_entry,
    canonical_youtube_url,
    content_dir,
    content_identity,
    find_by_identity,
    find_latest,
    step_rank,
    upsert,
)
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
    resumed: bool = False

    def public(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("source_url")
        data.pop("model")
        data.pop("requested_language")
        data.pop("force")
        data.pop("from_cache")
        data.pop("resumed")
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


def _list_artifacts(directory: Path) -> list[str]:
    return sorted(name for name in ALLOWED_ARTIFACTS if (directory / name).is_file())


def _mirror_to_job_dir(content_path: Path, job_dir: Path) -> list[str]:
    job_dir.mkdir(parents=True, exist_ok=True)
    present: list[str] = []
    for name in ALLOWED_ARTIFACTS:
        src = content_path / name
        if src.is_file():
            shutil.copy2(src, job_dir / name)
            present.append(name)
    return sorted(present)


def _clear_content_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _checkpoint(
    *,
    content_hash: str,
    job: Job,
    canonical_url: str,
    video_id: str | None,
    title: str,
    channel: str,
    duration: Any,
    content_path: Path,
    status: str,
    last_step: str,
) -> None:
    artifacts = _list_artifacts(content_path)
    upsert(
        build_entry(
            content_hash=content_hash,
            platform="youtube",
            url=job.source_url,
            canonical_url=canonical_url,
            video_id=video_id,
            title=title,
            channel=channel,
            duration=duration,
            artifacts=artifacts,
            artifact_dir=str(content_path.resolve()),
            transcript_hash=_file_sha256(content_path / "transcript.txt"),
            audio_hash=_file_sha256(content_path / "audio.mp3"),
            status=status,
            last_step=last_step,
        )
    )


def _load_source_metadata(content_path: Path) -> dict[str, Any] | None:
    meta_path = content_path / "metadata.json"
    if not meta_path.is_file():
        return None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _complete_from_registry(job_id: str, job: Job, entry: dict[str, Any]) -> None:
    source_dir = Path(entry["artifact_dir"])
    job_dir = OUTPUT_ROOT / job_id
    present = _mirror_to_job_dir(source_dir, job_dir)
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
        "resumed": False,
    }
    meta_path = job_dir / "metadata.json"
    if meta_path.is_file():
        try:
            stored = json.loads(meta_path.read_text(encoding="utf-8"))
            if isinstance(stored, dict):
                metadata["detected_language"] = stored.get("detected_language")
        except json.JSONDecodeError:
            pass
    job_store.update(
        job_id,
        status=JobStatus.COMPLETED,
        progress=100,
        message="Concluído (reutilizado do registry)",
        metadata=metadata,
        transcript=transcript,
        artifacts=present,
        from_cache=True,
        resumed=False,
    )
    logger.info("Job %s atendido via registry (%s)", job_id, entry.get("content_hash"))


def _infer_completed_step(content_path: Path, entry: dict[str, Any] | None) -> str | None:
    """Determine how far artifacts allow us to skip, respecting last_step."""
    recorded = (entry or {}).get("last_step")
    if (content_path / "transcript.txt").is_file() and (content_path / "transcript.srt").is_file():
        inferred = STEP_TRANSCRIBE
    elif (content_path / "audio.mp3").is_file():
        inferred = STEP_DOWNLOAD
    elif _load_source_metadata(content_path) is not None:
        inferred = STEP_METADATA
    else:
        inferred = None

    if inferred is None:
        return None
    if recorded and step_rank(recorded) < step_rank(inferred):
        # Prefer files on disk if they are further along than registry claim.
        return inferred
    if recorded and step_rank(recorded) >= step_rank(STEP_DONE):
        return STEP_DONE
    if recorded and step_rank(recorded) >= step_rank(inferred):
        return recorded
    return inferred


def process_job(job_id: str) -> None:
    job = job_store.get(job_id)
    if not job:
        return

    video_id_hint = extract_youtube_video_id(job.source_url)
    canonical_url = canonical_youtube_url(job.source_url) or job.source_url
    identity = content_identity(
        platform="youtube",
        video_id=video_id_hint,
        canonical_url=canonical_url,
    )
    content_path = content_dir(OUTPUT_ROOT, identity)
    job_dir = OUTPUT_ROOT / job_id
    logger.info("Job %s iniciado (force=%s hash=%s)", job_id, job.force, identity[:12])

    title = "Sem título"
    channel = "Canal desconhecido"
    duration: Any = None
    video_id = video_id_hint
    resumed = False

    try:
        job_dir.mkdir(parents=True, exist_ok=False)

        resume_from: str | None = None

        if job.force:
            _clear_content_dir(content_path)
        else:
            ready = find_by_identity(identity, video_id=video_id_hint, ready_only=True)
            if ready and Path(ready.get("artifact_dir", "")).is_dir():
                _ensure_not_cancelled(job_id)
                _complete_from_registry(job_id, job, ready)
                return

            latest = find_latest(identity, video_id=video_id_hint)
            if latest and latest.get("status") != "ready":
                prior = Path(latest.get("artifact_dir") or content_path)
                candidate = _infer_completed_step(prior if prior.is_dir() else content_path, latest)
                if candidate and step_rank(candidate) >= step_rank(STEP_METADATA):
                    if prior.is_dir():
                        content_path = prior
                    resume_from = candidate
                    resumed = True
                    title = latest.get("title") or title
                    channel = latest.get("channel") or channel
                    duration = latest.get("duration")
                    video_id = latest.get("video_id") or video_id
                    job_store.update(
                        job_id,
                        message=f"Retomando a partir de {resume_from}",
                        resumed=True,
                    )
                    logger.info(
                        "Job %s retomando last_step=%s dir=%s",
                        job_id,
                        resume_from,
                        content_path,
                    )

        content_path.mkdir(parents=True, exist_ok=True)

        # --- metadata ---
        if resume_from is None or step_rank(resume_from) < step_rank(STEP_METADATA):
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
            # Persist lightweight source snapshot for resume without full artifacts yet.
            snapshot = {
                "video_id": video_id,
                "title": title,
                "channel": channel,
                "duration_seconds": duration,
                "source_url": job.source_url,
                "canonical_url": canonical_url,
                "content_hash": identity,
            }
            (content_path / "metadata.json").write_text(
                json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            _checkpoint(
                content_hash=identity,
                job=job,
                canonical_url=canonical_url,
                video_id=video_id,
                title=title,
                channel=channel,
                duration=duration,
                content_path=content_path,
                status="in_progress",
                last_step=STEP_METADATA,
            )
        else:
            stored = _load_source_metadata(content_path) or {}
            video_id = stored.get("video_id") or video_id
            title = stored.get("title") or title
            channel = stored.get("channel") or channel
            duration = stored.get("duration_seconds", duration)

            # Still allow ready cache after metadata if a concurrent complete landed.
            if not job.force:
                ready = find_by_identity(identity, video_id=video_id, ready_only=True)
                if ready and Path(ready.get("artifact_dir", "")).is_dir():
                    _ensure_not_cancelled(job_id)
                    _complete_from_registry(job_id, job, ready)
                    return

        # --- download ---
        audio_path = content_path / "audio.mp3"
        if resume_from is None or step_rank(resume_from) < step_rank(STEP_DOWNLOAD):
            job_store.update(
                job_id,
                status=JobStatus.DOWNLOADING,
                progress=25,
                message="Baixando áudio",
            )
            _ensure_not_cancelled(job_id)
            audio_path = download_audio(job.source_url, content_path)
            _checkpoint(
                content_hash=identity,
                job=job,
                canonical_url=canonical_url,
                video_id=video_id,
                title=title,
                channel=channel,
                duration=duration,
                content_path=content_path,
                status="in_progress",
                last_step=STEP_DOWNLOAD,
            )
        else:
            if not audio_path.is_file():
                raise FileNotFoundError("Checkpoint indica download, mas audio.mp3 ausente")

        # --- transcribe ---
        segments: list[dict[str, Any]]
        detected_language: str | None
        transcript: str
        if resume_from is None or step_rank(resume_from) < step_rank(STEP_TRANSCRIBE):
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
            (content_path / "transcript.txt").write_text(transcript + "\n", encoding="utf-8")
            (content_path / "transcript.srt").write_text(generate_srt(segments), encoding="utf-8")
            _checkpoint(
                content_hash=identity,
                job=job,
                canonical_url=canonical_url,
                video_id=video_id,
                title=title,
                channel=channel,
                duration=duration,
                content_path=content_path,
                status="in_progress",
                last_step=STEP_TRANSCRIBE,
            )
        else:
            transcript = (content_path / "transcript.txt").read_text(encoding="utf-8").strip()
            detected_language = None
            stored = _load_source_metadata(content_path) or {}
            detected_language = stored.get("detected_language")
            segments = []

        # --- finalize files / metadata ---
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
            "canonical_url": canonical_url,
            "video_id": video_id,
            "title": title,
            "channel": channel,
            "duration_seconds": duration,
            "requested_language": job.requested_language,
            "detected_language": detected_language,
            "model": job.model,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "from_cache": False,
            "resumed": resumed,
            "content_hash": identity,
        }
        (content_path / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        _checkpoint(
            content_hash=identity,
            job=job,
            canonical_url=canonical_url,
            video_id=video_id,
            title=title,
            channel=channel,
            duration=duration,
            content_path=content_path,
            status="in_progress",
            last_step=STEP_FILES,
        )

        artifacts = _mirror_to_job_dir(content_path, job_dir)
        _checkpoint(
            content_hash=identity,
            job=job,
            canonical_url=canonical_url,
            video_id=video_id,
            title=title,
            channel=channel,
            duration=duration,
            content_path=content_path,
            status="ready",
            last_step=STEP_DONE,
        )
        job_store.update(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            message="Concluído (retomado)" if resumed else "Concluído",
            metadata=metadata,
            transcript=transcript,
            artifacts=artifacts,
            from_cache=False,
            resumed=resumed,
        )
        logger.info("Job %s concluído resumed=%s", job_id, resumed)
    except JobCancelled:
        logger.info("Job %s cancelado", job_id)
        try:
            _checkpoint(
                content_hash=identity,
                job=job,
                canonical_url=canonical_url,
                video_id=video_id,
                title=title,
                channel=channel,
                duration=duration,
                content_path=content_path,
                status="cancelled",
                last_step=_infer_completed_step(content_path, None) or STEP_METADATA,
            )
        except Exception:
            logger.exception("Falha ao gravar checkpoint de cancelamento")
        job_store.update(
            job_id,
            status=JobStatus.CANCELLED,
            message="Processamento cancelado pelo usuário",
        )
    except Exception:
        logger.exception("Falha ao processar job %s", job_id)
        try:
            _checkpoint(
                content_hash=identity,
                job=job,
                canonical_url=canonical_url,
                video_id=video_id,
                title=title,
                channel=channel,
                duration=duration,
                content_path=content_path,
                status="failed",
                last_step=_infer_completed_step(content_path, None) or STEP_METADATA,
            )
        except Exception:
            logger.exception("Falha ao gravar checkpoint de erro")
        job_store.update(
            job_id,
            status=JobStatus.FAILED,
            message=(
                "Não foi possível processar o vídeo. Verifique a URL, a disponibilidade "
                "pública do conteúdo e a instalação do FFmpeg."
            ),
        )
