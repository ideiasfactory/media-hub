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

# Last successful WhisperModel load (cheap status for /health).
_whisper_runtime: dict[str, Any] = {
    "device_requested": None,
    "device_effective": None,
    "compute_type": None,
    "cuda_fallback": False,
}


class WhisperDeviceError(RuntimeError):
    """Raised when Whisper cannot initialize on any usable device."""


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


def get_whisper_device_status() -> dict[str, Any]:
    """Return configured + last-effective Whisper device (for health/ops)."""
    return {
        "device_requested": resolve_whisper_device(),
        "device_effective": _whisper_runtime["device_effective"],
        "compute_type": _whisper_runtime["compute_type"],
        "cuda_fallback": bool(_whisper_runtime["cuda_fallback"]),
    }


def _record_whisper_runtime(
    *,
    requested: str,
    effective: str,
    compute_type: str,
    cuda_fallback: bool,
) -> None:
    _whisper_runtime["device_requested"] = requested
    _whisper_runtime["device_effective"] = effective
    _whisper_runtime["compute_type"] = compute_type
    _whisper_runtime["cuda_fallback"] = cuda_fallback


def build_whisper_model(model_name: str, device: str, compute_type: str) -> Any:
    """Construct WhisperModel; CUDA unavailable → CPU + warning (not silent)."""
    from faster_whisper import WhisperModel

    requested = device
    logger.info(
        "Loading Whisper model=%s device=%s compute_type=%s",
        model_name,
        device,
        compute_type,
    )
    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
    except Exception as exc:
        if device != "cuda":
            raise
        cpu_compute = resolve_whisper_compute_type("cpu")
        logger.warning(
            "%s=cuda requested but CUDA is unavailable or WhisperModel failed "
            "to initialize (%s); falling back to CPU (compute_type=%s). "
            "Fix the NVIDIA/CUDA stack (nvidia-smi, Docker --gpus) to use GPU.",
            ENV_WHISPER_DEVICE,
            exc,
            cpu_compute,
        )
        logger.info(
            "Loading Whisper model=%s device=cpu compute_type=%s (after CUDA fallback)",
            model_name,
            cpu_compute,
        )
        try:
            model = WhisperModel(model_name, device="cpu", compute_type=cpu_compute)
        except Exception as cpu_exc:
            raise WhisperDeviceError(
                f"{ENV_WHISPER_DEVICE}=cuda failed ({exc}) and CPU fallback also "
                f"failed ({cpu_exc})."
            ) from cpu_exc
        _record_whisper_runtime(
            requested=requested,
            effective="cpu",
            compute_type=cpu_compute,
            cuda_fallback=True,
        )
        logger.warning(
            "Whisper using device=cpu compute_type=%s (requested=%s; CUDA fallback)",
            cpu_compute,
            requested,
        )
        return model

    _record_whisper_runtime(
        requested=requested,
        effective=device,
        compute_type=compute_type,
        cuda_fallback=False,
    )
    logger.info(
        "Whisper using device=%s compute_type=%s (requested=%s)",
        device,
        compute_type,
        requested,
    )
    return model


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
