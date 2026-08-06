# Épicos — Media Hub

Catálogo detalhado dos épicos do produto. Visão estratégica e releases:
[ROADMAP.md](ROADMAP.md). Arquitetura: [ARCHITECTURE.md](ARCHITECTURE.md).
ADRs: [DECISIONS.md](DECISIONS.md).

Legenda de status: **Em andamento** · **Planejado** · **Concluído** · **Bloqueado**

---

## EPIC-001 — Foundation + YouTube Web MVP

**Status:** Concluído  
**Release:** v0.1  
**ADRs:** 001–006, 013, 014

### Objetivo

Disponibilizar aplicação funcional local para validar arquitetura, fluxo e UX.

### Inclui

- FastAPI + Uvicorn (porta 8010)
- UI server-side (HTML / CSS / JS)
- API REST de jobs
- yt-dlp + FFmpeg (áudio)
- faster-whisper (CPU, int8)
- Artefatos: MP3, TXT, SRT, metadata.json
- Testes offline + README

### Critérios de aceite

- App inicia; UI em `http://localhost:8010`
- Job criado com progresso; áudio e transcrição gerados
- Downloads funcionam; testes e `compileall` passam
- Smoke test com vídeo público curto autorizado (quando houver rede/FFmpeg)

### Fora de escopo

Instagram, TikTok, playlists, download de vídeo, DB, Redis, Docker, auth, CI cloud,
Content Intelligence, Video Lab.

---

## EPIC-002 — YouTube Adapter Evolution

**Status:** Planejado  
**Release:** v0.2  
**Depende de:** EPIC-001  
**ADRs:** 004 (revisão), 007

### Objetivo

Evoluir o suporte YouTube além do MVP de áudio individual.

### Melhorias previstas

- Download do vídeo (além do áudio)
- Playlists
- Seleção de qualidade
- Uso de legendas existentes quando disponíveis
- Retomada / cancelamento de jobs
- Melhorias de UX de progresso e erros

---

## EPIC-003 — Content Registry

**Status:** Planejado  
**Release:** v0.2  
**Depende de:** EPIC-001  
**ADRs:** 010, 012

### Objetivo

Eliminar downloads e transcrições redundantes via identificação única de conteúdos.

### Implementação inicial

Arquivo `registry.jsonl` com campos:

```
content_hash, platform, url, canonical_url, video_id, title, channel,
duration, published_at, downloaded_at, artifacts, transcript_hash,
audio_hash, status
```

### Fluxo

```
URL → Normalização → Hash → Registry → Existe?
  → Sim: retorna artefatos existentes
  → Não: executa processamento
```

### Regras

- Identidade preferencial: `platform + video_id`
- Fallback: `SHA256(canonical_url + duration + title)`
- Reprocessar somente com `force=true`
- Migração futura para PostgreSQL (EPIC-016)

---

## EPIC-004 — Storage Abstraction

**Status:** Planejado  
**Release:** v0.3  
**Depende de:** EPIC-001  
**ADRs:** 011

### Objetivo

Separar artefatos, metadados e cache atrás de uma interface de storage.

### Evolução

```
Filesystem → MinIO → S3
```

Sem alterar regras de negócio do pipeline. Backends adicionais (Azure Blob, GCS)
podem seguir o mesmo contrato.

---

## EPIC-005 — Instagram Adapter

**Status:** Planejado  
**Release:** v0.3  
**Depende de:** EPIC-001 (idealmente após extrair SourceAdapter)  
**ADRs:** 007, 013

### Escopo

Reels e vídeos públicos: metadados, áudio e transcrição. Sem bypass de login/DRM.

---

## EPIC-006 — TikTok Adapter

**Status:** Planejado  
**Release:** v0.3  
**Depende de:** EPIC-001  
**ADRs:** 007, 013

### Escopo

Vídeos públicos: metadados, download, áudio e transcrição.

---

## EPIC-007 — Facebook Adapter

**Status:** Planejado  
**Release:** v0.4  
**ADRs:** 007, 013

### Escopo

Vídeos públicos e Watch, dentro dos limites legais e técnicos suportados.

---

## EPIC-008 — LinkedIn Adapter

**Status:** Planejado  
**Release:** v0.4  
**ADRs:** 007, 013

### Escopo

Vídeos públicos.

---

## EPIC-009 — Vimeo Adapter

**Status:** Planejado  
**Release:** v0.4  
**ADRs:** 007, 013

### Escopo

Vídeos públicos / acessíveis sem contornar controles de acesso.

---

## EPIC-010 — Twitch Adapter

**Status:** Planejado  
**Release:** v0.4  
**ADRs:** 007, 013

### Escopo

Conteúdos públicos suportados (VODs/clips conforme viabilidade).

---

## EPIC-011 — Podcast Adapter

**Status:** Planejado  
**Release:** v0.4  
**ADRs:** 007, 013

### Escopo

- Feeds RSS públicos
- Spotify / Apple Podcasts somente quando houver mecanismos oficialmente suportados

---

## EPIC-012 — Document Adapter

**Status:** Planejado  
**Release:** v0.4  
**ADRs:** 007

### Escopo

PDF, DOCX, PPTX → texto, OCR quando necessário, preparação para embeddings.

---

## EPIC-013 — Image Adapter

**Status:** Planejado  
**Release:** v0.4  
**ADRs:** 007

### Escopo

OCR, EXIF e caption por IA.

---

## EPIC-014 — Multi Transcriber

**Status:** Planejado  
**Release:** v0.4  
**Depende de:** EPIC-001  
**ADRs:** 006 (revisão), 008

### Objetivo

Permitir engines de STT selecionáveis por configuração:

- Faster Whisper (já existente)
- OpenAI / Whisper API
- Deepgram
- Azure Speech
- Google Speech
- AssemblyAI

---

## EPIC-015 — Jobs Persistentes

**Status:** Planejado  
**Release:** v0.5  
**Depende de:** EPIC-001  
**ADRs:** 001 (supersede parcial)

### Objetivo

Substituir jobs em memória por Redis + workers com fila, retry e cancelamento.

---

## EPIC-016 — PostgreSQL

**Status:** Planejado  
**Release:** v0.5  
**Depende de:** EPIC-003  
**ADRs:** 012

### Objetivo

Migrar Content Registry de `registry.jsonl` para PostgreSQL, preservando o modelo
de conteúdo e hashes.

---

## EPIC-017 — Content Intelligence

**Status:** Planejado  
**Release:** v0.6  
**Depende de:** EPIC-001  
**ADRs:** 009

### Objetivo

Gerar automaticamente a partir da transcrição normalizada:

- resumo
- capítulos
- assuntos
- palavras-chave
- categorias
- entidades
- timestamps

Hooks, cenas e cortes para Shorts podem entrar neste épico ou em fatias
subsequentes conforme prioridade do Video Lab.

---

## EPIC-018 — Video Lab Integration

**Status:** Planejado  
**Release:** v0.6  
**Depende de:** EPIC-001, preferencialmente EPIC-017  
**ADRs:** 009

### Fluxo-alvo

```
URL → Media Hub → Transcript → Hooks → Cortes → Assets → Render
```

Disponibilizar API/contratos estáveis para o Video Lab consumir artefatos e
inteligência sem acoplar ao downloader.

---

## EPIC-019 — Search API

**Status:** Planejado  
**Release:** v0.6  
**Depende de:** EPIC-003 ou EPIC-016

### Escopo

Pesquisar títulos, canais, assuntos, palavras e conteúdos indexados.

---

## EPIC-020 — Embeddings

**Status:** Planejado  
**Release:** v0.6  
**Depende de:** EPIC-001  
**ADRs:** 009

### Objetivo

Gerar embeddings dos conteúdos e preparar o Media Hub como fonte para RAG
(AI Labs / bases vetoriais).

---

## EPIC-021 — Administração

**Status:** Planejado  
**Release:** v0.7

### Escopo

Tela administrativa: jobs, histórico, registry, limpeza, reprocessamento e
métricas operacionais básicas.

---

## EPIC-022 — Observabilidade

**Status:** Planejado  
**Release:** v0.7

### Escopo

Métricas, tracing, logs estruturados e dashboards.

---

## EPIC-023 — Autenticação completa (usuários / OAuth)

**Status:** Planejado  
**Release:** v0.7  
**Depende de:** EPIC-026  
**ADRs:** 015 (evolução)

### Escopo

Evoluir a proteção da API Key simples (EPIC-026) para:

- usuários
- múltiplas API Keys gerenciáveis
- OAuth

Necessário antes de API pública / multi-tenant. A API Key via `.env` permanece
como modo local/single-tenant até este épico.

---

## EPIC-024 — Billing

**Status:** Planejado  
**Release:** v0.7  
**Depende de:** EPIC-023

### Escopo

Quotas, consumo e planos.

---

## EPIC-025 — Media Hub Platform 1.0

**Status:** Planejado  
**Release:** v1.0  
**Depende de:** conjunto mínimo dos épicos anteriores definido pelo PO

### Objetivo

Primeira versão considerada estável da plataforma de ingestão multimídia da
Ideias Factory: múltiplos adapters, transcribers, storage, persistência, workers,
observabilidade e integração consolidada com Video Lab.

---

## EPIC-026 — API Key via `.env`

**Status:** Concluído  
**Release:** v0.1.x  
**Depende de:** EPIC-001  
**ADRs:** 015

### Objetivo

Proteger os endpoints da API (`/api/*`) com uma API Key configurada por
variável de ambiente, sem usuários nem OAuth.

### Inclui

- variável `MEDIA_HUB_API_KEY` (ou equivalente) em `.env` / `.env.example`
- header padrão (ex.: `X-API-Key` ou `Authorization: Bearer`)
- UI local pode continuar autenticada pelo mesmo segredo ou por exceção
  documentada para `GET /` e estáticos
- `GET /health` permanece público
- testes cobrindo ausência/invalidade da key
- documentação no README

### Critérios de aceite

- request sem key válida em `/api/*` retorna 401
- key lida apenas de ambiente; nunca commitada
- Swagger (quando EPIC-027 estiver ativo) documenta o esquema de segurança

---

## EPIC-027 — OpenAPI / Swagger

**Status:** Concluído  
**Release:** v0.1.x  
**Depende de:** EPIC-001  
**ADRs:** 016

### Objetivo

Expor a documentação interativa da API gerada pelo FastAPI.

### Inclui

- Swagger UI em `/docs`
- ReDoc em `/redoc` (opcional)
- schema OpenAPI em `/openapi.json`
- metadados (título, versão SemVer, descrição) alinhados ao app
- proteção documentada quando API Key estiver ativa (EPIC-026)

### Critérios de aceite

- `/docs` acessível e coerente com os endpoints reais
- versão da API refletida no schema

---

## EPIC-028 — CLI Media Hub

**Status:** Planejado  
**Release:** v0.1.x / v0.3  
**Depende de:** EPIC-001; preferencialmente EPIC-026  
**ADRs:** —

### Objetivo

Oferecer um CLI para uso como tool (automação, scripts, agentes), consumindo a
mesma API/serviço.

### Inclui

- comando instalável (ex.: `media-hub` via `pyproject` / console script)
- subcomandos mínimos: `health`, `jobs create`, `jobs status`, `jobs download`
- autenticação por API Key (env ou flag)
- saída amigável + JSON (`--json`) para integração
- help e exemplos no README

### Critérios de aceite

- criar job, acompanhar status e baixar artefatos sem UI
- não duplicar lógica de pipeline; CLI é cliente da API

---

## EPIC-029 — Versionamento SemVer e contrato da API

**Status:** Concluído  
**Release:** v0.1.x  
**Depende de:** EPIC-001  
**ADRs:** 017

### Objetivo

Adotar SemVer para o produto e versionar o contrato da API quando houver
breaking change.

### Inclui

- versão canônica do app (ex.: `__version__` / `pyproject` / tag Git)
- política SemVer documentada (MAJOR.MINOR.PATCH)
- versionamento de contrato: prefixo de rota (`/api/v1/...`) e/ou header
  `Accept` / documentação OpenAPI
- em breaking change: bump MAJOR do app **e** nova versão de contrato
  (`/api/v2`), com período de convivência documentado quando aplicável
- changelog ligado às tags

### Critérios de aceite

- versão visível na API (`/health` ou OpenAPI) e no README
- guia claro do que constitui breaking change no contrato

---

## EPIC-030 — Release notes (usuário + técnico)

**Status:** Concluído  
**Release:** v0.1.x  
**Depende de:** EPIC-029  
**ADRs:** 019

### Objetivo

Publicar notas de versão em dois níveis: usuário final e time técnico.

### Inclui

**Usuário final (amigável)**

- página/seção na UI (ex.: `/changelog` ou modal “Novidades”)
- linguagem simples: o que mudou, o que ganhou, o que precisa saber
- sem jargão de implementação

**Técnico (time / repo)**

- `CHANGELOG.md` ou `docs/releases/` seguindo Keep a Changelog
- detalhes de breaking changes, migrações, ADRs relacionados, commits/PRs

### Critérios de aceite

- cada release SemVer gera entrada técnica no repo
- UI exibe as notas amigáveis da versão corrente (e histórico recente)
- breaking changes destacados nos dois formatos

---

## EPIC-031 — Licenciamento (PolyForm Noncommercial)

**Status:** Concluído  
**Release:** v0.1.x  
**ADRs:** 018

### Objetivo

Licenciar o repositório como código **source-available**, permitindo uso,
estudo e contribuição **não comercial**, sem permissão de uso comercial.

### Licença escolhida

**PolyForm Noncommercial License 1.0.0**

Motivo: é uma licença feita para software (não apenas conteúdo), permite
uso/modificação/distribuição para fins não comerciais e exige acordo separado
para uso comercial. Não é OSI “Open Source” (propositalmente: restrição
comercial).

### Inclui

- arquivo `LICENSE` com o texto integral
- menção clara no README (badge + seção “Licença”)
- nota de que uso comercial requer licença adicional junto à Ideias Factory
- revisão de dependências quanto a compatibilidade de redistribuição

### Critérios de aceite

- `LICENSE` presente e referenciado
- README explica o que é permitido / não permitido em linguagem simples

---

## EPIC-032 — Documentos e regras de contribuição

**Status:** Concluído  
**Release:** v0.1.x  
**Depende de:** EPIC-031 (recomendado)

### Objetivo

Definir como a comunidade e o time contribuem com qualidade e segurança.

### Inclui

- `CONTRIBUTING.md` — setup, branch, testes, PR, escopo vs épicos
- `CODE_OF_CONDUCT.md` — comportamento esperado
- templates GitHub: PR, bug report, feature request
- alinhamento com `AGENTS.md` (não expandir escopo, sem bypass DRM, etc.)
- checklist: `pytest` + `compileall` antes do PR

### Critérios de aceite

- novos contribuidores conseguem abrir PR seguindo o guia
- templates disponíveis no repositório

---

## EPIC-033 — README aprimorado e widgets GitHub

**Status:** Concluído  
**Release:** v0.1.x  
**Depende de:** EPIC-001; idealmente EPIC-029 e EPIC-031

### Objetivo

Tornar o README a vitrine do projeto: claro para humanos e rico em sinais
visuais do GitHub.

### Inclui

- estrutura: badges, overview, quick start, API, CLI (quando existir), docs,
  licença, contribuição
- widgets/badges sugeridos: versão/SemVer, licença, Python, testes/CI (quando
  houver), última release, issues
- link para `docs/`, Swagger, release notes
- screenshots ou GIF da UI (opcional, mas desejável)
- troubleshooting mantido e atualizado

### Critérios de aceite

- README autoexplicativo para clonar → rodar em poucos minutos
- badges renderizam no GitHub
- não duplica o roadmap; aponta para `docs/`
