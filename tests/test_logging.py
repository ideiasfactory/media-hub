from __future__ import annotations

import logging
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.logging_setup import JavaStyleFormatter, maintain_log_retention, setup_logging


def test_java_style_formatter_shape() -> None:
    formatter = JavaStyleFormatter()
    record = logging.LogRecord(
        name="media_hub.jobs",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Job abc started",
        args=(),
        exc_info=None,
    )
    record.created = datetime(2026, 8, 6, 13, 35, 1, 123000).timestamp()
    record.msecs = 123
    record.threadName = "MainThread"
    line = formatter.format(record)
    assert "2026-08-06 13:35:01,123" in line
    assert "INFO" in line
    assert "[MainThread]" in line
    assert "media_hub.jobs" in line
    assert "Job abc started" in line


def test_setup_logging_writes_console_and_file(tmp_path: Path) -> None:
    log_path = setup_logging(logs_dir=tmp_path)
    assert log_path.is_file()
    logging.getLogger("test.setup").info("hello disk")
    for handler in logging.getLogger().handlers:
        handler.flush()
    content = log_path.read_text(encoding="utf-8")
    assert "hello disk" in content
    assert "test.setup" in content


def test_maintain_log_retention_archives_old_files(tmp_path: Path) -> None:
    old = tmp_path / "media-hub-2026-01-01.log"
    old.write_text("old line\n", encoding="utf-8")
    old_mtime_dt = datetime.now(timezone.utc) - timedelta(days=45)
    old_mtime = old_mtime_dt.timestamp()
    import os

    os.utime(old, (old_mtime, old_mtime))

    recent = tmp_path / "media-hub-2026-08-01.log"
    recent.write_text("recent\n", encoding="utf-8")

    result = maintain_log_retention(tmp_path, retention_days=30)
    assert not old.exists()
    assert recent.exists()
    month_key = old_mtime_dt.strftime("%Y-%m")
    archive = tmp_path / "archive" / f"{month_key}.tar.gz"
    assert archive.is_file()
    assert str(archive) in result["archives"]
    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    assert "media-hub-2026-01-01.log" in names
