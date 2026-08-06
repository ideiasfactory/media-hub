from __future__ import annotations

from pathlib import Path
from typing import Any


def _youtube_dl(options: dict[str, Any]):
    from yt_dlp import YoutubeDL

    return YoutubeDL(options)


def fetch_metadata(url: str) -> dict[str, Any]:
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
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
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
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
