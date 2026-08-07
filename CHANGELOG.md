# Changelog

Todas as mudanças notáveis deste projeto são documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adota [Semantic Versioning](https://semver.org/lang/pt-BR/).

Notas amigáveis para usuário final: interface em `/changelog`.
Política de contrato da API: [ADR-017](docs/DECISIONS.md#adr-017--semver-e-versionamento-do-contrato-da-api).
Checklist de fechamento de versão: [ADR-021](docs/DECISIONS.md#adr-021--checklist-obrigatório-ao-fechar-uma-versão).

## [Unreleased]

### Added

- EPIC-040 / ADR-027–032: baseline CI/CD IHL — GHCR
  `ghcr.io/ideiasfactory/media-hub`, workflows build-publish + deploy homolog
  (`mac-srv-01`), desired state `deploy/homolog/`, doc [docs/CICD.md](docs/CICD.md).
- Fatia EPIC-036: `Dockerfile`, `docker-compose.yml` (DEV) e volumes alinhados
  a ADR-024 (base para promote homolog).

### Planned (v0.2 restante / follow-ups)

- Demais itens do EPIC-002 (vídeo, playlists, legendas, qualidade).
- EPIC-038 restante: tasks 04, 06, 07, 08 (issues funil, distribuição, métricas).

### Planned (v0.2.x)

- EPIC-035: validação de vulnerabilidades (política High/Critical, checklist
  de app security, secret scanning; ADR-023).
- EPIC-036 restante: endurecer packaging Docker / smoke documentado / UID-GID.
- EPIC-037: documentação operacional alinhada (README, ARCHITECTURE, AGENTS).
- EPIC-040 restante: validar CD end-to-end no runner `mac-srv-01` quando online.
## [0.2.1] - 2026-08-06

### Added

- EPIC-039 / ADR-026: identidade por `SHA256(URL canônica)`; checkpoint no
  registry (`status`, `last_step`); artefatos em `output/by-content/{hash}/`;
  retomada automática na segunda execução da mesma URL.
- EPIC-038 fatia: Apache-2.0 (TASK-038-01); README discovery bilingue + GIF
  (TASK-038-02); metadados GitHub (TASK-038-03); `docs/ADAPTERS.md` (TASK-038-05).
- Demo visual: `docs/assets/demo.gif`.

### Changed

- Licença: PolyForm Noncommercial → **Apache License 2.0** (ADR-018 superseded;
  ADR-025 Accepted).
- Registry: chave passa a ser hash da URL canônica YouTube (youtu.be / watch /
  shorts colapsam).

## [0.2.0] - 2026-08-06

### Added

- Logging local (EPIC-022 fase 1 / ADR-022): console + `logs/media-hub-YYYY-MM-DD.log`
  em formato estilo Java; retenção 30 dias; arquivo `logs/archive/yyyy-mm.tar.gz`.
- Content Registry `registry.jsonl` (EPIC-003 / ADR-010) com reuso de artefatos e
  `force` no `JobRequest` / UI.
- Cancelamento de jobs (EPIC-002 incremento): `POST /api/v1/jobs/{id}/cancel` e
  botão na interface.
- Ícones e PWA leve: favicon, apple-touch-icon, manifest e ícones 192/512.
- Badges no README (EPIC-033): status do CI em `main`, versão, Python 3.11/3.12,
  licença, último commit, issues, API e docs.

### Changed

- Documentação de produto alinhada à faixa v0.2.x (segurança → Docker → docs →
  comunidade / EPIC-038).

## [0.1.2] - 2026-08-06

### Added

- Pipeline CI no GitHub Actions (lint Ruff, Bandit, `pip-audit`, Dependency Review
  e testes em Python 3.11/3.12).
- `requirements-dev.txt`, `pyproject.toml` (Ruff/Bandit) e Dependabot semanal.
- `DISCLAIMER.md` (direitos autorais + tolerância zero a exploração infantil e
  outros usos ilegais) e `PRIVACY.md`.
- [ADR-021](docs/DECISIONS.md#adr-021--checklist-obrigatório-ao-fechar-uma-versão):
  checklist obrigatório de release notes ao fechar versão.

### Changed

- Avisos legais na UI e no Código de Conduta alinhados ao disclaimer.
- Compatibilidade de data/hora com `timezone.utc` (evita `ImportError` em
  runtimes sem `datetime.UTC`).

### Security

- Dependências atualizadas (`fastapi`, `requests`, `pytest`; piso
  `starlette>=1.3.1`) para eliminar CVEs reportados pelo `pip-audit`.

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

[Unreleased]: https://github.com/ideiasfactory/media-hub/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/ideiasfactory/media-hub/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/ideiasfactory/media-hub/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/ideiasfactory/media-hub/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/ideiasfactory/media-hub/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ideiasfactory/media-hub/releases/tag/v0.1.0
