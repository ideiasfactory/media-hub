"""Logging setup: Java-style formatter, disk + console, retention and monthly archives."""

from __future__ import annotations

import logging
import tarfile
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOGS_ROOT = Path(__file__).resolve().parent.parent / "logs"
ARCHIVE_DIRNAME = "archive"
RETENTION_DAYS = 30
LOG_FILE_PREFIX = "media-hub"


class JavaStyleFormatter(logging.Formatter):
    """Format close to Log4j/Logback: timestamp LEVEL [thread] logger - message."""

    def format(self, record: logging.LogRecord) -> str:
        created = datetime.fromtimestamp(record.created)
        timestamp = created.strftime("%Y-%m-%d %H:%M:%S") + f",{int(record.msecs):03d}"
        level = f"{record.levelname:<7}"
        line = f"{timestamp} {level} [{record.threadName}] {record.name} - {record.getMessage()}"
        if record.exc_info:
            line = f"{line}\n{self.formatException(record.exc_info)}"
        return line


def _daily_log_path(logs_dir: Path, when: datetime | None = None) -> Path:
    day = (when or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    return logs_dir / f"{LOG_FILE_PREFIX}-{day}.log"


def _rewrite_tar_gz(archive_path: Path, new_files: list[Path]) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=archive_path.parent, suffix=".tar.gz", delete=False
    ) as tmp:
        tmp_path = Path(tmp.name)
    try:
        with tarfile.open(tmp_path, "w:gz") as out_tar:
            if archive_path.is_file():
                with tarfile.open(archive_path, "r:gz") as old_tar:
                    for member in old_tar.getmembers():
                        extracted = old_tar.extractfile(member)
                        if extracted is not None:
                            out_tar.addfile(member, extracted)
            for path in new_files:
                out_tar.add(path, arcname=path.name)
        tmp_path.replace(archive_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def maintain_log_retention(
    logs_dir: Path | None = None,
    *,
    retention_days: int = RETENTION_DAYS,
) -> dict[str, list[str]]:
    """Archive log files older than retention_days into logs/archive/yyyy-mm.tar.gz."""
    root = logs_dir or LOGS_ROOT
    root.mkdir(parents=True, exist_ok=True)
    archive_dir = root / ARCHIVE_DIRNAME
    archive_dir.mkdir(parents=True, exist_ok=True)

    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    by_month: dict[str, list[Path]] = {}
    for path in sorted(root.glob(f"{LOG_FILE_PREFIX}-*.log")):
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if mtime >= cutoff:
            continue
        month_key = mtime.strftime("%Y-%m")
        by_month.setdefault(month_key, []).append(path)

    archived: list[str] = []
    removed: list[str] = []
    for month_key, files in by_month.items():
        archive_path = archive_dir / f"{month_key}.tar.gz"
        _rewrite_tar_gz(archive_path, files)
        archived.append(str(archive_path))
        for path in files:
            path.unlink(missing_ok=True)
            removed.append(path.name)
    return {"archives": archived, "removed": removed}


def setup_logging(
    *,
    level: int = logging.INFO,
    logs_dir: Path | None = None,
) -> Path:
    """Configure root logging to console + daily file with Java-style format."""
    root = logs_dir or LOGS_ROOT
    root.mkdir(parents=True, exist_ok=True)
    (root / ARCHIVE_DIRNAME).mkdir(parents=True, exist_ok=True)
    maintain_log_retention(root)

    formatter = JavaStyleFormatter()
    log_path = _daily_log_path(root)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # Replace prior Media Hub handlers to keep setup idempotent under --reload.
    for handler in list(root_logger.handlers):
        if getattr(handler, "_media_hub_handler", False):
            root_logger.removeHandler(handler)
            handler.close()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler._media_hub_handler = True  # type: ignore[attr-defined]

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler._media_hub_handler = True  # type: ignore[attr-defined]

    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)

    logging.getLogger(__name__).info("Logging ativo: console + %s", log_path)
    return log_path
