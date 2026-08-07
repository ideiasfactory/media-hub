"""Content Registry (registry.jsonl) for deduplicating and resuming jobs."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.utils import extract_youtube_video_id

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "registry.jsonl"
_lock = threading.Lock()

# Pipeline steps in order (EPIC-039).
STEP_METADATA = "metadata"
STEP_DOWNLOAD = "download"
STEP_TRANSCRIBE = "transcribe"
STEP_FILES = "files"
STEP_DONE = "done"

STEP_ORDER = (
    STEP_METADATA,
    STEP_DOWNLOAD,
    STEP_TRANSCRIBE,
    STEP_FILES,
    STEP_DONE,
)


def canonical_youtube_url(url: str) -> str | None:
    """Normalize common YouTube URL shapes to watch?v= form."""
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return None
    return f"https://www.youtube.com/watch?v={video_id}"


def content_hash_for_url(url: str) -> str | None:
    """SHA-256 of the canonical YouTube URL (identity key)."""
    canonical = canonical_youtube_url(url)
    if not canonical:
        return None
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def content_identity(
    *,
    platform: str = "youtube",
    video_id: str | None = None,
    canonical_url: str,
    duration: Any = None,
    title: str = "",
) -> str:
    """Return content_hash for a URL. Prefer URL-based hash (EPIC-039).

    Legacy kwargs kept for call-site compatibility; duration/title ignored.
    Falls back to platform:video_id only if the URL cannot be canonicalized.
    """
    hashed = content_hash_for_url(canonical_url)
    if hashed:
        return hashed
    if video_id:
        return f"{platform}:{video_id}"
    raw = f"{canonical_url}|{duration}|{title}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _legacy_youtube_identity(video_id: str) -> str:
    return f"youtube:{video_id}"


def _read_all(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            logger.warning("Linha inválida no registry ignorada")
    return entries


def _entry_matches(entry: dict[str, Any], content_hash: str, video_id: str | None) -> bool:
    if entry.get("content_hash") == content_hash:
        return True
    # Legacy EPIC-003 keys: youtube:{id}
    if video_id and entry.get("content_hash") == _legacy_youtube_identity(video_id):
        return True
    if video_id and entry.get("video_id") == video_id:
        entry_url = entry.get("canonical_url") or entry.get("url") or ""
        if content_hash_for_url(entry_url) == content_hash:
            return True
    return False


def find_latest(
    content_hash: str,
    *,
    video_id: str | None = None,
    path: Path | None = None,
) -> dict[str, Any] | None:
    """Return the most recent registry entry for this content (any status)."""
    registry = path or REGISTRY_PATH
    with _lock:
        for entry in reversed(_read_all(registry)):
            if _entry_matches(entry, content_hash, video_id):
                return entry
    return None


def find_by_identity(
    content_hash: str,
    path: Path | None = None,
    *,
    video_id: str | None = None,
    ready_only: bool = True,
) -> dict[str, Any] | None:
    """Lookup registry entry. By default only ``status == ready`` (cache hit)."""
    registry = path or REGISTRY_PATH
    with _lock:
        for entry in reversed(_read_all(registry)):
            if not _entry_matches(entry, content_hash, video_id):
                continue
            if ready_only and entry.get("status") != "ready":
                continue
            return entry
    return None


def upsert(entry: dict[str, Any], path: Path | None = None) -> None:
    """Append a new registry line (last write wins for a given content_hash on read)."""
    registry = path or REGISTRY_PATH
    registry.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(entry)
    payload.setdefault("downloaded_at", datetime.now(timezone.utc).isoformat())
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    with _lock:
        with registry.open("a", encoding="utf-8") as handle:
            handle.write(line)
    logger.info(
        "Registry atualizado: %s status=%s last_step=%s",
        payload.get("content_hash"),
        payload.get("status"),
        payload.get("last_step"),
    )


def build_entry(
    *,
    content_hash: str,
    platform: str,
    url: str,
    canonical_url: str,
    video_id: str | None,
    title: str,
    channel: str,
    duration: Any,
    artifacts: list[str],
    artifact_dir: str,
    transcript_hash: str | None,
    audio_hash: str | None,
    status: str = "ready",
    last_step: str = STEP_DONE,
) -> dict[str, Any]:
    return {
        "content_hash": content_hash,
        "platform": platform,
        "url": url,
        "canonical_url": canonical_url,
        "video_id": video_id,
        "title": title,
        "channel": channel,
        "duration": duration,
        "published_at": None,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": artifacts,
        "artifact_dir": artifact_dir,
        "transcript_hash": transcript_hash,
        "audio_hash": audio_hash,
        "status": status,
        "last_step": last_step,
    }


def step_rank(step: str | None) -> int:
    if not step:
        return -1
    try:
        return STEP_ORDER.index(step)
    except ValueError:
        return -1


def content_dir(output_root: Path, content_hash: str) -> Path:
    return output_root / "by-content" / content_hash
