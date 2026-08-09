from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

ENV_WHISPER_DEVICE = "MEDIA_HUB_WHISPER_DEVICE"
ENV_WHISPER_COMPUTE_TYPE = "MEDIA_HUB_WHISPER_COMPUTE_TYPE"

ALLOWED_DEVICES = frozenset({"cpu", "cuda"})
DEFAULT_COMPUTE_BY_DEVICE = {
    "cpu": "int8",
    "cuda": "float16",
}

logger = logging.getLogger(__name__)


class WhisperDeviceError(RuntimeError):
    """Raised when the requested Whisper device cannot be initialized."""


def resolve_whisper_device(raw: str | None = None) -> str:
    """Return Whisper device from env/config. Default remains CPU (ADR-006)."""
    value = (raw if raw is not None else os.getenv(ENV_WHISPER_DEVICE, "")).strip().lower()
    if not value:
        return "cpu"
    if value not in ALLOWED_DEVICES:
        allowed = ", ".join(sorted(ALLOWED_DEVICES))
        raise ValueError(f"Invalid {ENV_WHISPER_DEVICE}={value!r}. Allowed: {allowed}.")
    return value


def resolve_whisper_compute_type(device: str, raw: str | None = None) -> str:
    """Return compute_type; default int8 on CPU, float16 on CUDA."""
    value = (raw if raw is not None else os.getenv(ENV_WHISPER_COMPUTE_TYPE, "")).strip()
    if value:
        return value
    return DEFAULT_COMPUTE_BY_DEVICE.get(device, "int8")


def build_whisper_model(model_name: str, device: str, compute_type: str) -> Any:
    """Construct WhisperModel; CUDA failures do **not** fall back to CPU."""
    from faster_whisper import WhisperModel

    logger.info(
        "Loading Whisper model=%s device=%s compute_type=%s",
        model_name,
        device,
        compute_type,
    )
    try:
        return WhisperModel(model_name, device=device, compute_type=compute_type)
    except Exception as exc:
        if device == "cuda":
            raise WhisperDeviceError(
                f"{ENV_WHISPER_DEVICE}=cuda but CUDA is unavailable or WhisperModel "
                f"failed to initialize ({exc}). Fix the NVIDIA/CUDA stack "
                f"(nvidia-smi, Docker --gpus), or set {ENV_WHISPER_DEVICE}=cpu. "
                "Media Hub does not silently fall back to CPU when cuda is requested."
            ) from exc
        raise


def transcribe_audio(
    audio_path: Path, model_name: str, language: str | None
) -> tuple[list[dict[str, Any]], str]:
    device = resolve_whisper_device()
    compute_type = resolve_whisper_compute_type(device)
    model = build_whisper_model(model_name, device, compute_type)
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
