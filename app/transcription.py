from __future__ import annotations

from pathlib import Path
from typing import Any


def transcribe_audio(
    audio_path: Path, model_name: str, language: str | None
) -> tuple[list[dict[str, Any]], str]:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    raw_segments, info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
    )
    segments = [
        {"start": segment.start, "end": segment.end, "text": segment.text}
        for segment in raw_segments
    ]
    return segments, info.language
