"""User-facing and technical release notes helpers."""

from __future__ import annotations

from typing import Any

from app import __version__

# Friendly highlights shown in the UI. Keep language simple and user-oriented.
USER_RELEASES: list[dict[str, Any]] = [
    {
        "version": "0.1.1",
        "date": "2026-08-06",
        "title": "API pronta para integração",
        "summary": "O Media Hub ganhou proteção por API Key, documentação Swagger, versionamento e novidades na interface.",
        "highlights": [
            "Documentação interativa da API em /docs",
            "Endpoints versionados em /api/v1",
            "Proteção opcional por API Key via arquivo .env",
            "Página de novidades para acompanhar as versões",
            "Licença clara para uso não comercial",
        ],
    },
    {
        "version": "0.1.0",
        "date": "2026-08-06",
        "title": "Primeiro MVP do YouTube",
        "summary": "Baixe o áudio de um vídeo público, transcreva localmente e baixe MP3, TXT, SRT e JSON.",
        "highlights": [
            "Interface simples na porta 8010",
            "Transcrição com Whisper local",
            "Acompanhamento do progresso do job",
            "Download dos artefatos gerados",
        ],
    },
]


def current_version() -> str:
    return __version__


def list_user_releases() -> list[dict[str, Any]]:
    return list(USER_RELEASES)


def latest_user_release() -> dict[str, Any]:
    return USER_RELEASES[0]
