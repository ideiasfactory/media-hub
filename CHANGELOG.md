# Changelog

Todas as mudanças notáveis deste projeto são documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adota [Semantic Versioning](https://semver.org/lang/pt-BR/).

Notas amigáveis para usuário final: interface em `/changelog`.
Política de contrato da API: [ADR-017](docs/DECISIONS.md#adr-017--semver-e-versionamento-do-contrato-da-api).

## [Unreleased]

## [0.1.1] - 2026-08-06

### Added

- Licença PolyForm Noncommercial 1.0.0 (`LICENSE`).
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` e templates GitHub de issue/PR.
- API Key opcional via `MEDIA_HUB_API_KEY` (`.env`) com header `X-API-Key`.
- OpenAPI/Swagger em `/docs` e ReDoc em `/redoc`, com esquema de segurança quando a key está ativa.
- Versionamento do contrato em `/api/v1`.
- Release notes amigáveis em `/changelog` e endpoint auxiliar `/api/releases`.
- `GET /health` passa a retornar `version`.
- README com badges e links de documentação.
- Monorepo modular: pacotes `frontend/`, `bff/` e `backend/` (EPIC-034 / ADR-020).

### Changed

- Rotas de jobs movidas de `/api/...` para `/api/v1/...` (breaking para clientes da 0.1.0).
- Código de domínio e UI separados do composition root (`app/main.py` só cria o app).
- ADRs 015–020 marcados como Accepted; épicos 026–027, 029–034 concluídos.

### Security

- Endpoints `/api/v1/*` exigem API Key quando `MEDIA_HUB_API_KEY` está definido.
- UI same-origin autentica via cookie HttpOnly `media_hub_api_key`.

## [0.1.0] - 2026-08-06

### Added

- Foundation + YouTube Web MVP (EPIC-001).
- FastAPI UI + API, jobs em memória, yt-dlp/FFmpeg, faster-whisper.
- Artefatos `audio.mp3`, `transcript.txt`, `transcript.srt`, `metadata.json`.
- Documentação inicial de roadmap, épicos, arquitetura e ADRs.

[Unreleased]: https://github.com/ideiasfactory/media-hub/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/ideiasfactory/media-hub/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ideiasfactory/media-hub/releases/tag/v0.1.0
