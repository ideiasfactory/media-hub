from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_ARTIFACTS = frozenset({"audio.mp3", "transcript.txt", "transcript.srt", "metadata.json"})
YOUTUBE_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }
)


def is_valid_youtube_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        host = (parsed.hostname or "").lower().rstrip(".")
        if (
            parsed.scheme not in {"http", "https"}
            or host not in YOUTUBE_HOSTS
            or parsed.username
            or parsed.password
            or parsed.port not in {None, 80, 443}
        ):
            return False
        if host.endswith("youtu.be"):
            return bool(parsed.path.strip("/"))
        return bool(parsed.path.strip("/") or parsed.query)
    except ValueError:
        return False


def is_allowed_artifact(filename: str) -> bool:
    return (
        filename in ALLOWED_ARTIFACTS
        and Path(filename).name == filename
        and "/" not in filename
        and "\\" not in filename
    )


def resolve_artifact(job_dir: Path, filename: str) -> Path:
    if not is_allowed_artifact(filename):
        raise ValueError("Arquivo não permitido.")
    root = job_dir.resolve()
    candidate = (root / filename).resolve()
    if candidate.parent != root:
        raise ValueError("Caminho de arquivo inválido.")
    return candidate


def format_srt_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(float(seconds) * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(segments: Iterable[dict[str, object]]) -> str:
    blocks: list[str] = []
    for index, segment in enumerate(segments, start=1):
        start = format_srt_timestamp(float(segment["start"]))
        end = format_srt_timestamp(float(segment["end"]))
        text = str(segment["text"]).strip()
        blocks.append(f"{index}\n{start} --> {end}\n{text}")
    return "\n\n".join(blocks) + ("\n" if blocks else "")
