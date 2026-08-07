"""Content Registry (registry.jsonl) for deduplicating YouTube processing."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "registry.jsonl"
_lock = threading.Lock()


def content_identity(
    *,
    platform: str,
    video_id: str | None,
    canonical_url: str,
    duration: Any,
    title: str,
) -> str:
    if video_id:
        return f"{platform}:{video_id}"
    raw = f"{canonical_url}|{duration}|{title}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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


def find_by_identity(content_hash: str, path: Path | None = None) -> dict[str, Any] | None:
    registry = path or REGISTRY_PATH
    with _lock:
        for entry in reversed(_read_all(registry)):
            if entry.get("content_hash") == content_hash and entry.get("status") == "ready":
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
        "Registry atualizado: %s (%s)",
        payload.get("content_hash"),
        payload.get("video_id") or payload.get("title"),
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
    }
