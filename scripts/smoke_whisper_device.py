#!/usr/bin/env python3
"""Smoke-check Whisper device selection (CPU default or CUDA opt-in).

Dual mode (ADR-034):

    # CPU (default) — config only
    python scripts/smoke_whisper_device.py

    # CUDA — loads WhisperModel; falls back to CPU with warning if CUDA unavailable
    MEDIA_HUB_WHISPER_DEVICE=cuda python scripts/smoke_whisper_device.py --load-model
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.transcription import (  # noqa: E402
    WhisperDeviceError,
    build_whisper_model,
    get_whisper_device_status,
    resolve_whisper_compute_type,
    resolve_whisper_device,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--load-model",
        action="store_true",
        help="Construct WhisperModel (downloads tiny weights on first use).",
    )
    parser.add_argument(
        "--model",
        default="tiny",
        help="Model name when --load-model is set (default: tiny).",
    )
    args = parser.parse_args()

    device = resolve_whisper_device()
    compute_type = resolve_whisper_compute_type(device)
    print(f"MEDIA_HUB_WHISPER_DEVICE={os.getenv('MEDIA_HUB_WHISPER_DEVICE', '')!r}")
    print(f"MEDIA_HUB_WHISPER_COMPUTE_TYPE={os.getenv('MEDIA_HUB_WHISPER_COMPUTE_TYPE', '')!r}")
    print(f"resolved device={device} compute_type={compute_type}")

    if not args.load_model:
        print("OK (config only; pass --load-model to construct WhisperModel)")
        return 0

    try:
        model = build_whisper_model(args.model, device, compute_type)
    except WhisperDeviceError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    status = get_whisper_device_status()
    print(
        f"WhisperModel loaded model={args.model!r} "
        f"device_effective={status['device_effective']!r} "
        f"compute_type={status['compute_type']!r} "
        f"cuda_fallback={status['cuda_fallback']}"
    )
    del model
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
