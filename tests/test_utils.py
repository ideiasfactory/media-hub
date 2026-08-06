from app.utils import (
    generate_srt,
    is_allowed_artifact,
    is_valid_youtube_url,
    format_srt_timestamp,
)


def test_format_srt_timestamp() -> None:
    assert format_srt_timestamp(0) == "00:00:00,000"
    assert format_srt_timestamp(3661.234) == "01:01:01,234"


def test_generate_srt() -> None:
    segments = [
        {"start": 0.0, "end": 1.25, "text": " Olá mundo "},
        {"start": 61.5, "end": 63.0, "text": "Segundo trecho."},
    ]
    assert generate_srt(segments) == (
        "1\n00:00:00,000 --> 00:00:01,250\nOlá mundo\n\n"
        "2\n00:01:01,500 --> 00:01:03,000\nSegundo trecho.\n"
    )


def test_youtube_url_validation() -> None:
    assert is_valid_youtube_url("https://www.youtube.com/watch?v=abc123")
    assert is_valid_youtube_url("https://youtu.be/abc123")
    assert is_valid_youtube_url("https://music.youtube.com/watch?v=abc123")
    assert not is_valid_youtube_url("https://youtube.com.evil.example/watch?v=abc")
    assert not is_valid_youtube_url("file:///tmp/video")
    assert not is_valid_youtube_url("https://user:pass@youtube.com/watch?v=abc")
    assert not is_valid_youtube_url("https://youtube.com:8443/watch?v=abc")


def test_artifact_whitelist() -> None:
    for filename in ("audio.mp3", "transcript.txt", "transcript.srt", "metadata.json"):
        assert is_allowed_artifact(filename)
    assert not is_allowed_artifact("../metadata.json")
    assert not is_allowed_artifact("video.mp4")
    assert not is_allowed_artifact("/etc/passwd")
