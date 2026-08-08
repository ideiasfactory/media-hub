"""User-facing and technical release notes helpers."""

from __future__ import annotations

from typing import Any

from app import __version__

# Friendly highlights shown in the UI. Keep language simple and user-oriented.
USER_RELEASES: list[dict[str, Any]] = [
    {
        "version": "0.2.1",
        "date": "2026-08-06",
        "title": "Retomada, licença aberta e vitrine",
        "summary": (
            "Jobs interrompidos podem continuar de onde pararam, o projeto "
            "passa a Apache-2.0 e o README ganha demo visual para quem descobre "
            "o repositório."
        ),
        "highlights": [
            "Mesma URL YouTube retoma o processamento após falha ou cancelamento",
            "Identidade estável pela URL canônica (youtu.be e watch?v= são iguais)",
            "Licença Apache-2.0 para facilitar forks e uso comercial do código",
            "README bilingue com GIF de demonstração e matriz de adapters",
            "Guia para propor novos adapters sem bypass de DRM",
        ],
    },
    {
        "version": "0.2.0",
        "date": "2026-08-06",
        "title": "Registry, logs e cancelamento",
        "summary": (
            "O Media Hub evita reprocessar o mesmo vídeo, grava logs locais "
            "legíveis e permite cancelar um job em andamento pela interface."
        ),
        "highlights": [
            "Reuso automático de áudio e transcrição já gerados (registry)",
            "Opção de forçar novo processamento quando você quiser",
            "Botão para cancelar jobs em andamento",
            "Logs no console e em arquivo, com retenção de 30 dias",
            "Ícones e atalho para instalar como app no celular/desktop",
        ],
    },
    {
        "version": "0.1.2",
        "date": "2026-08-06",
        "title": "Mais segurança e transparência",
        "summary": (
            "O Media Hub ganhou pipeline de qualidade no GitHub, auditoria de "
            "dependências e documentos claros de privacidade e uso responsável."
        ),
        "highlights": [
            "Testes, lint e checagens de segurança automáticos no CI",
            "Dependências revisadas contra vulnerabilidades conhecidas",
            "Política de privacidade explicando o que fica na sua máquina",
            "Isenção de responsabilidade com regras explícitas de uso ilegal",
            "Tolerância zero a exploração ou abuso de crianças e adolescentes",
        ],
    },
    {
        "version": "0.1.1",
        "date": "2026-08-06",
        "title": "API pronta para integração",
        "summary": (
            "O Media Hub ganhou proteção por API Key, documentação Swagger, "
            "versionamento, novidades na interface e organização em camadas "
            "no monorepo."
        ),
        "highlights": [
            "Documentação interativa da API em /docs",
            "Endpoints versionados em /api/v1",
            "Proteção opcional por API Key via arquivo .env",
            "Página de novidades para acompanhar as versões",
            "Licença clara para uso não comercial",
            "Código organizado em frontend, BFF e backend (ainda um único processo)",
        ],
    },
    {
        "version": "0.1.0",
        "date": "2026-08-06",
        "title": "Foundation YouTube (v0.1)",
        "summary": (
            "Baixe o áudio de um vídeo público, transcreva localmente e baixe MP3, TXT, SRT e JSON."
        ),
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
