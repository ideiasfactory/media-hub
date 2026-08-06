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

---

## Mapa de releases

| Release | Foco | Épicos principais |
|---------|------|-------------------|
| **v0.1** | Foundation + YouTube Web MVP | EPIC-001 |
| **v0.1.x** | Governança, DX e contrato | EPIC-026–EPIC-033 |
| **v0.2** | YouTube Evolution + Registry | EPIC-002, EPIC-003 |
| **v0.3** | Storage + adapters sociais + CLI | EPIC-004–EPIC-006, EPIC-028 |
| **v0.4** | Mais adapters + multi-transcriber | EPIC-007–EPIC-014 |
| **v0.5** | Persistência e escala | EPIC-015, EPIC-016 |
| **v0.6** | Inteligência e integração | EPIC-017–EPIC-020 |
| **v0.7** | Operação e plataforma | EPIC-021–EPIC-024 |
| **v1.0** | Media Hub Platform estável | EPIC-025 |

As releases são orientação de produto; a prioridade de cada épico pode ser
ajustada pelo Product Owner sem alterar a visão arquitetural.

A faixa **v0.1.x** pode avançar em paralelo ao fechamento do MVP e à v0.2:
licença, contribuição, README, SemVer, release notes, API Key e Swagger são
prioridade alta de higiene de produto.

---

## Status dos épicos

| Épico | Título | Status |
|-------|--------|--------|
| EPIC-001 | Foundation + YouTube Web MVP | Concluído |
| EPIC-002 | YouTube Adapter Evolution | Planejado |
| EPIC-003 | Content Registry | Planejado |
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
| EPIC-022 | Observabilidade | Planejado |
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

Detalhamento de cada épico: [EPICS.md](EPICS.md).

---

## Fases resumidas

### v0.1 — Foundation + YouTube Web MVP (EPIC-001) ✅

Aplicação funcional local: URL pública do YouTube → áudio → Whisper local →
TXT / SRT / JSON + UI e API na porta 8010. **Concluído.**

### v0.1.x — Governança e DX (EPIC-026–033) ✅

Higiene de produto (release **0.1.1**):

- licença source-available sem uso comercial (PolyForm Noncommercial);
- CONTRIBUTING / CODE_OF_CONDUCT / PR template;
- README com badges/widgets GitHub;
- SemVer do app + versionamento do contrato da API (`/api/v1`);
- release notes amigáveis na UI (`/changelog`) e notas técnicas no repositório;
- proteção da API por API Key em `.env`;
- exposição do Swagger/OpenAPI (`/docs`).

CLI (EPIC-028) permanece planejado para sprint seguinte.

### v0.2 — YouTube Evolution + Registry (EPIC-002, EPIC-003)

Melhorias no adaptador YouTube (vídeo, playlists, legendas, cancelamento) e
camada de deduplicação via Content Registry (`registry.jsonl`).

### v0.3 — Storage + Instagram / TikTok + CLI (EPIC-004–006, EPIC-028)

Abstração de storage (Filesystem → MinIO → S3), primeiros adapters além do
YouTube e CLI estável para automação, sem alterar regras de negócio.

### v0.4 — Ecossistema de fontes e transcribers (EPIC-007–014)

Facebook, LinkedIn, Vimeo, Twitch, Podcasts, documentos, imagens e múltiplos
motores de STT selecionáveis por configuração.

### v0.5 — Persistência e workers (EPIC-015, EPIC-016)

Jobs em Redis + workers com retry/cancelamento; migração do registry para
PostgreSQL.

### v0.6 — Inteligência e integração (EPIC-017–020)

Content Intelligence, integração com Video Lab, Search API e embeddings para RAG.

### v0.7 — Operação (EPIC-021–024)

Admin, observabilidade, autenticação completa (usuários/OAuth — evolução da
API Key do EPIC-026) e billing.

### v1.0 — Platform (EPIC-025)

Primeira versão considerada estável da plataforma de ingestão multimídia.

---

## Fora do escopo imediato

Itens abaixo permanecem fora até o épico correspondente ser autorizado:

- Instagram, TikTok e demais adapters (antes de EPIC-005+)
- banco de dados, Redis, Celery, Docker, Kubernetes
- autenticação completa com usuários/OAuth e billing (EPIC-023 / EPIC-024);
  API Key simples é EPIC-026
- frontend separado (React / Vue / Next.js)
- bypass de DRM, login, cookies ou restrições geográficas
- Content Intelligence e integração Video Lab (antes de EPIC-017 / EPIC-018)
- uso comercial do código sem licença comercial adicional (ADR-018)
