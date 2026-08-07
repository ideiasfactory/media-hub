# Roadmap Estratégico — Media Hub

## Visão do produto

O **Media Hub** será a plataforma responsável pela aquisição, normalização,
transcrição, enriquecimento e disponibilização de conteúdo multimídia para o
ecossistema da Ideias Factory.

Seu papel é desacoplar a obtenção dos conteúdos da inteligência de negócio,
tornando-se uma camada reutilizável por:

- Video Lab
- AI Labs
- Bases RAG
- Agentes de IA
- Futuras APIs públicas

A evolução é orientada por **Adapters** (fontes) e **Transcribers** (engines),
para adicionar plataformas e motores sem alterar o restante do sistema.

Documentação relacionada: [ARCHITECTURE.md](ARCHITECTURE.md) ·
[EPICS.md](EPICS.md) · [DECISIONS.md](DECISIONS.md)

---

## Princípios

1. Entregar software funcionando antes de abstrações prematuras.
2. Toda estrutura criada deve ter uso imediato.
3. Isolar fontes (Adapters) e engines de STT (Transcribers).
4. Separar aquisição de Content Intelligence.
5. Evitar reprocessamento redundante (Content Registry / cache).
6. Não contornar DRM, autenticação, restrições territoriais ou controles de acesso.
7. Hardening de segurança e caminho de deploy reproduzível **antes** de expandir
   superfície com novos adapters sociais.
8. Tratar descoberta e contribuição externa como produto: narrativa, demo,
   issues contribuíveis e postura de licença explícitas **antes** de pedir
   colaboração em adapters (EPIC-038).

---

## Prioridade de execução (reavaliada)

Ordem autorizada pelo Product Owner (visibilidade/engajamento após base
operacional sólida):

| Ordem | Faixa | Foco | Épicos |
|------:|-------|------|--------|
| 1 | **v0.2** ✅ | YouTube + Registry + logging local | EPIC-002 (incremento), EPIC-003, EPIC-022 fase 1 |
| 2 | **v0.2.1** ✅ | Comunidade (fatia) + resume por URL | EPIC-038 (01/02/03/05), EPIC-039 |
| 3 | **v0.2.x** | Hardening + deploy + CI/CD homolog + docs ops | **EPIC-035 → (036 + 040) → 037** |
| 4 | **v0.2.x** | EPIC-038 restante | tasks 04, 06, 07, 08 |
| 5 | **v0.3** | Storage + adapters sociais + CLI | EPIC-004–006, EPIC-028 |
| 6 | **v0.4+** | Demais adapters, STT, persistência, inteligência | conforme mapa abaixo |

A **v0.2.1** foi reautorizada pelo PO **antes** de 035–037 para desbloquear
licença OSI, vitrine e retomada de jobs. Em seguida a ordem volta a:

1. **EPIC-035** — validação de vulnerabilidades
2. **EPIC-036** — Docker com volumes no host (+ fatia mínima para imagem)
3. **EPIC-040** — CI/CD IHL + homolog em `mac-srv-01` (GHCR, promote por digest)
4. **EPIC-037** — documentação operacional
5. **EPIC-038** restante — issues, distribuição, métricas

Motivo original (ainda válido para adapters): ampliar Instagram/TikTok sem
baseline de segurança/deploy aumenta risco; a fatia 038/039 antecipada não
implementa adapters sociais.

---

## Mapa de releases

| Release | Foco | Épicos principais |
|---------|------|-------------------|
| **v0.1** | Foundation + YouTube Web MVP | EPIC-001 |
| **v0.1.x** | Governança, DX, contrato e monorepo modular | EPIC-026–EPIC-034 |
| **v0.2** | YouTube Evolution + Registry + logging local | EPIC-002, EPIC-003, EPIC-022 (fase 1) |
| **v0.2.1** | Comunidade (fatia) + URL hash / resume | EPIC-038 (01/02/03/05), EPIC-039 |
| **v0.2.x** | Segurança, Docker, CI/CD homolog, docs ops, EPIC-038 restante | EPIC-035 → (036 + 040) → 037 → 038 |
| **v0.3** | Storage + adapters sociais + CLI | EPIC-004–EPIC-006, EPIC-028 |
| **v0.4** | Mais adapters + multi-transcriber | EPIC-007–EPIC-014 |
| **v0.5** | Persistência e escala | EPIC-015, EPIC-016 |
| **v0.6** | Inteligência e integração | EPIC-017–EPIC-020 |
| **v0.7** | Operação e plataforma | EPIC-021, EPIC-022 (resto), EPIC-023–024 |
| **v1.0** | Media Hub Platform estável | EPIC-025 |

As releases são orientação de produto; a prioridade de cada épico pode ser
ajustada pelo Product Owner sem alterar a visão arquitetural.

A faixa **v0.1.x** pode avançar em paralelo ao fechamento do MVP e à v0.2:
licença, contribuição, README, SemVer, release notes, API Key e Swagger são
prioridade alta de higiene de produto.

A faixa **v0.2.x** (após **0.2.1**) retoma hardening: segurança + Docker +
CI/CD IHL (homolog `mac-srv-01`) + docs ops + restante do EPIC-038, antes dos
adapters sociais (v0.3). Estratégia: [CICD.md](CICD.md).

---

## Status dos épicos

| Épico | Título | Status |
|-------|--------|--------|
| EPIC-001 | Foundation + YouTube Web MVP | Concluído |
| EPIC-002 | YouTube Adapter Evolution | Em andamento (cancelamento na 0.2.0; resto aberto) |
| EPIC-003 | Content Registry | Concluído (v0.2.0) |
| EPIC-004 | Storage Abstraction | Planejado |
| EPIC-005 | Instagram Adapter | Planejado |
| EPIC-006 | TikTok Adapter | Planejado |
| EPIC-007 | Facebook Adapter | Planejado |
| EPIC-008 | LinkedIn Adapter | Planejado |
| EPIC-009 | Vimeo Adapter | Planejado |
| EPIC-010 | Twitch Adapter | Planejado |
| EPIC-011 | Podcast Adapter | Planejado |
| EPIC-012 | Document Adapter | Planejado |
| EPIC-013 | Image Adapter | Planejado |
| EPIC-014 | Multi Transcriber | Planejado |
| EPIC-015 | Jobs Persistentes | Planejado |
| EPIC-016 | PostgreSQL | Planejado |
| EPIC-017 | Content Intelligence | Planejado |
| EPIC-018 | Video Lab Integration | Planejado |
| EPIC-019 | Search API | Planejado |
| EPIC-020 | Embeddings | Planejado |
| EPIC-021 | Administração | Planejado |
| EPIC-022 | Observabilidade | Fase 1 concluída (v0.2.0); resto planejado (v0.7) |
| EPIC-023 | Autenticação completa (usuários / OAuth) | Planejado |
| EPIC-024 | Billing | Planejado |
| EPIC-025 | Media Hub Platform 1.0 | Planejado |
| EPIC-026 | API Key via `.env` | Concluído |
| EPIC-027 | OpenAPI / Swagger | Concluído |
| EPIC-028 | CLI Media Hub | Planejado |
| EPIC-029 | Versionamento SemVer e contrato da API | Concluído |
| EPIC-030 | Release notes (usuário + técnico) | Concluído |
| EPIC-031 | Licenciamento (PolyForm Noncommercial) | Concluído |
| EPIC-032 | Documentos e regras de contribuição | Concluído |
| EPIC-033 | README aprimorado e widgets GitHub | Concluído |
| EPIC-034 | Monorepo modular (frontend / BFF / backend) | Concluído |
| EPIC-035 | Validação de vulnerabilidades de segurança | Planejado (v0.2.x — prioridade 1) |
| EPIC-036 | Deploy Docker com volumes no host | Planejado (v0.2.x — prioridade 2; fatia imagem com 040) |
| EPIC-037 | Documentação operacional (segurança + Docker) | Planejado (v0.2.x — prioridade 4) |
| EPIC-038 | Comunidade, visibilidade e engajamento open source | Em andamento (v0.2.1 — tasks 01/02/03/05) |
| EPIC-039 | Identidade por URL + checkpoint/retomada | Concluído (v0.2.1) |
| EPIC-040 | CI/CD IHL + homolog mac-srv-01 | Em andamento (v0.2.x — com EPIC-036) |

Detalhamento de cada épico: [EPICS.md](EPICS.md).

---

## Fases resumidas

### v0.1 — Foundation + YouTube Web MVP (EPIC-001) ✅

Aplicação funcional local: URL pública do YouTube → áudio → Whisper local →
TXT / SRT / JSON + UI e API na porta 8010. **Concluído.**

### v0.1.x — Governança e DX (EPIC-026–034) ✅

Higiene de produto (release **0.1.1** / **0.1.2**):

- licença Apache-2.0 (migração na v0.2.1; ver ADR-025);
- CONTRIBUTING / CODE_OF_CONDUCT / PR template;
- README com badges/widgets GitHub;
- SemVer do app + versionamento do contrato da API (`/api/v1`);
- release notes amigáveis na UI (`/changelog`) e notas técnicas no repositório;
- proteção da API por API Key em `.env`;
- exposição do Swagger/OpenAPI (`/docs`);
- monorepo modular com camadas `frontend/`, `bff/` e `backend/` (EPIC-034),
  mantendo um único processo Uvicorn;
- CI com lint, Bandit, `pip-audit` e Dependency Review (baseline de segurança).

CLI (EPIC-028) permanece planejado para **v0.3**.

### v0.2 — YouTube + Registry + logging (✅ 0.2.0)

| Épico | Entrega na sprint |
|-------|-------------------|
| **EPIC-002** | Incremento: cancelamento de jobs; resto (vídeo, playlists, legendas, qualidade) fica como follow-up |
| **EPIC-003** | Content Registry em `registry.jsonl` com deduplicação e `force=true` |
| **EPIC-022 (fase 1)** | Logs no console e em disco, formato estilo Java; retenção 30 dias; arquivo mensal `yyyy-mm.tar.gz` ([ADR-022](DECISIONS.md#adr-022--logging-local-estilo-java-com-retenção-e-arquivo-mensal)) |

### Próxima faixa / v0.2.x — Segurança + Docker + CI/CD + docs + EPIC-038 restante

Após a **v0.2.1** (fatia 038 + EPIC-039):

| Ordem | Épico | Entrega |
|------:|-------|---------|
| 1 | **EPIC-035** | Validação de vulnerabilidades além do baseline CI; política High/Critical; checklist de app security |
| 2 | **EPIC-036** | Docker / Compose com volumes de `.env`/config, `logs/` e `output/` no host ([ADR-024](DECISIONS.md#adr-024--deploy-docker-com-volumes-no-host)) |
| 3 | **EPIC-040** | CI/CD IHL: GHCR `ghcr.io/ideiasfactory/media-hub`, promote homolog em `mac-srv-01` ([CICD.md](CICD.md), ADR-027–032) |
| 4 | **EPIC-037** | Documentação operacional (README, ARCHITECTURE, CONTRIBUTING/AGENTS, release notes) |
| 5 | **EPIC-038** restante | Issues `good first issue`, distribuição, métricas (tasks 04/06/07/08) |

Metadados GitHub (description/topics) aplicados na 0.2.1 (TASK-038-03).

### v0.3 — Storage + Instagram / TikTok + CLI (EPIC-004–006, EPIC-028)

Abstração de storage (Filesystem → MinIO → S3), primeiros adapters além do
YouTube e CLI estável para automação, **depois** do hardening/deploy/comunidade
da v0.2.x — com issues `good first issue` / New Adapter já publicadas no
EPIC-038.

### v0.4 — Ecossistema de fontes e transcribers (EPIC-007–014)

Facebook, LinkedIn, Vimeo, Twitch, Podcasts, documentos, imagens e múltiplos
motores de STT selecionáveis por configuração.

### v0.5 — Persistência e workers (EPIC-015, EPIC-016)

Jobs em Redis + workers com retry/cancelamento; migração do registry para
PostgreSQL.

### v0.6 — Inteligência e integração (EPIC-017–020)

Content Intelligence, integração com Video Lab, Search API e embeddings para RAG.

### v0.7 — Operação (EPIC-021–024)

Admin, restante da observabilidade (métricas/tracing/dashboards — EPIC-022),
autenticação completa (usuários/OAuth — evolução da API Key do EPIC-026) e
billing.

### v1.0 — Platform (EPIC-025)

Primeira versão considerada estável da plataforma de ingestão multimídia.

---

## Fora do escopo imediato

Itens abaixo permanecem fora até o épico correspondente ser autorizado:

- Instagram, TikTok e demais adapters (antes de EPIC-005+; **depois** da v0.2.x,
  incluindo EPIC-038)
- banco de dados, Redis, Celery, Kubernetes (Docker/Compose da v0.2.x; K3s só
  como evolução GitOps-ready documentada em EPIC-040 / ADR-032)
- pipeline de **produção** ativo (PROD adiado; Environment `production` futuro)
- autenticação completa com usuários/OAuth e billing (EPIC-023 / EPIC-024);
  API Key simples é EPIC-026
- frontend separado (React / Vue / Next.js)
- bypass de DRM, login, cookies ou restrições geográficas
- Content Intelligence e integração Video Lab (antes de EPIC-017 / EPIC-018)
- métricas, tracing e dashboards (resto do EPIC-022 — fase 1 de logging é v0.2)
- código sob Apache-2.0 (ADR-025); DISCLAIMER continua a reger conteúdos de terceiros
