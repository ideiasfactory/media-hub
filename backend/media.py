from __future__ import annotations

from pathlib import Path
from typing import Any


def _youtube_dl(options: dict[str, Any]):
    from yt_dlp import YoutubeDL

    return YoutubeDL(options)


def _base_options() -> dict[str, Any]:
    """Shared yt-dlp options for YouTube public URLs.

    Deno (or another JS runtime) must be on PATH so yt-dlp can solve YouTube
    n/sig challenges. Without it, format URLs often return HTTP 403.
    See https://github.com/yt-dlp/yt-dlp/wiki/EJS
    """
    return {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # Prefer default clients; drop android_sdkless which commonly 403s.
        "extractor_args": {
            "youtube": {
                "player_client": ["default", "-android_sdkless"],
            }
        },
    }


def fetch_metadata(url: str) -> dict[str, Any]:
    options = {
        **_base_options(),
        "skip_download": True,
    }
    with _youtube_dl(options) as downloader:
        info = downloader.extract_info(url, download=False)
    if not info or info.get("_type") == "playlist":
        raise RuntimeError("A URL não aponta para um vídeo público individual.")
    return info


def download_audio(url: str, job_dir: Path) -> Path:
    output_template = str(job_dir / "source.%(ext)s")
    options = {
        **_base_options(),
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with _youtube_dl(options) as downloader:
        downloader.download([url])

    generated = job_dir / "source.mp3"
    destination = job_dir / "audio.mp3"
    if not generated.is_file():
        candidates = list(job_dir.glob("source*.mp3"))
        if len(candidates) != 1:
            raise RuntimeError("O áudio MP3 não foi gerado.")
        generated = candidates[0]
    generated.replace(destination)
    return destination
