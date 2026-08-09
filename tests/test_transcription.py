from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from backend.transcription import (
    WhisperDeviceError,
    build_whisper_model,
    resolve_whisper_compute_type,
    resolve_whisper_device,
    transcribe_audio,
)


def test_resolve_whisper_device_defaults_to_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MEDIA_HUB_WHISPER_DEVICE", raising=False)
    assert resolve_whisper_device() == "cpu"


@pytest.mark.parametrize("value", ["cuda", "CUDA", " Cuda "])
def test_resolve_whisper_device_accepts_cuda(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("MEDIA_HUB_WHISPER_DEVICE", value)
    assert resolve_whisper_device() == "cuda"


def test_resolve_whisper_device_rejects_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MEDIA_HUB_WHISPER_DEVICE", "mps")
    with pytest.raises(ValueError, match="MEDIA_HUB_WHISPER_DEVICE"):
        resolve_whisper_device()


def test_resolve_compute_type_defaults_by_device(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MEDIA_HUB_WHISPER_COMPUTE_TYPE", raising=False)
    assert resolve_whisper_compute_type("cpu") == "int8"
    assert resolve_whisper_compute_type("cuda") == "float16"


def test_resolve_compute_type_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEDIA_HUB_WHISPER_COMPUTE_TYPE", "int8_float16")
    assert resolve_whisper_compute_type("cuda") == "int8_float16"


def _install_fake_faster_whisper(monkeypatch: pytest.MonkeyPatch, fake_model: Any) -> None:
    import sys

    fake_fw = ModuleType("faster_whisper")
    fake_fw.WhisperModel = fake_model
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_fw)


def test_transcribe_audio_uses_resolved_device(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("MEDIA_HUB_WHISPER_DEVICE", "cuda")
    monkeypatch.delenv("MEDIA_HUB_WHISPER_COMPUTE_TYPE", raising=False)

    captured: dict[str, str] = {}

    class FakeModel:
        def __init__(self, model_name: str, device: str, compute_type: str) -> None:
            captured["model_name"] = model_name
            captured["device"] = device
            captured["compute_type"] = compute_type

        def transcribe(self, _path: str, language: str | None, vad_filter: bool):
            assert vad_filter is True
            assert language is None
            segments = [
                SimpleNamespace(start=0.0, end=1.0, text=" hello"),
            ]
            info = SimpleNamespace(language="en")
            return segments, info

    _install_fake_faster_whisper(monkeypatch, FakeModel)

    audio = tmp_path / "a.wav"
    audio.write_bytes(b"x")
    segments, lang = transcribe_audio(audio, "tiny", None)

    assert captured == {
        "model_name": "tiny",
        "device": "cuda",
        "compute_type": "float16",
    }
    assert lang == "en"
    assert segments == [{"start": 0.0, "end": 1.0, "text": " hello"}]


def test_transcribe_audio_cpu_default_int8(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("MEDIA_HUB_WHISPER_DEVICE", raising=False)
    monkeypatch.delenv("MEDIA_HUB_WHISPER_COMPUTE_TYPE", raising=False)

    captured: dict[str, str] = {}

    class FakeModel:
        def __init__(self, model_name: str, device: str, compute_type: str) -> None:
            captured["device"] = device
            captured["compute_type"] = compute_type

        def transcribe(self, _path: str, language: str | None, vad_filter: bool):
            return [], SimpleNamespace(language="pt")

    _install_fake_faster_whisper(monkeypatch, FakeModel)

    audio = tmp_path / "a.wav"
    audio.write_bytes(b"x")
    _, lang = transcribe_audio(audio, "base", "pt")
    assert lang == "pt"
    assert captured == {"device": "cpu", "compute_type": "int8"}


def test_cuda_init_failure_does_not_fallback_to_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    class BoomModel:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError("CUDA driver not found")

    _install_fake_faster_whisper(monkeypatch, BoomModel)

    with pytest.raises(WhisperDeviceError, match="does not silently fall back"):
        build_whisper_model("tiny", "cuda", "float16")


def test_cpu_init_failure_is_not_wrapped_as_device_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BoomModel:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError("weights missing")

    _install_fake_faster_whisper(monkeypatch, BoomModel)

    with pytest.raises(RuntimeError, match="weights missing"):
        build_whisper_model("tiny", "cpu", "int8")
