from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from backend.utils import is_valid_youtube_url


class JobStatus(str, Enum):
    QUEUED = "queued"
    FETCHING_METADATA = "fetching_metadata"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    GENERATING_FILES = "generating_files"
    COMPLETED = "completed"
    FAILED = "failed"


class JobRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    model: str = "base"
    language: str = "autodetect"

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()
        if not is_valid_youtube_url(value):
            raise ValueError("Informe uma URL pública válida do YouTube.")
        return value

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        if value not in {"tiny", "base", "small"}:
            raise ValueError("Modelo inválido.")
        return value

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        if value not in {"autodetect", "pt", "en", "es"}:
            raise ValueError("Idioma inválido.")
        return value


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    message: str
    metadata: dict[str, Any] | None = None
    transcript: str | None = None
    artifacts: list[str] = Field(default_factory=list)
