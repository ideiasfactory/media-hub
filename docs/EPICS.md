# Épicos — Media Hub

Catálogo detalhado dos épicos do produto. Visão estratégica e releases:
[ROADMAP.md](ROADMAP.md). Arquitetura: [ARCHITECTURE.md](ARCHITECTURE.md).
ADRs: [DECISIONS.md](DECISIONS.md).

Legenda de status: **Em andamento** · **Planejado** · **Concluído** · **Bloqueado**

### Classificação multi-repo (quando aplicável)

Usar nos épicos que tocam mais de um repositório do produto (core OSS / ops /
cloud). O monorepo `media-hub` continua a ser o núcleo; repos adicionais
**consomem** o core (dependência unidirecional). Ver
[OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md) · [ADR-033](DECISIONS.md#adr-033--artefato-público-promote-privado-media-hub-ops).

| Campo | Valores |
|-------|---------|
| **Repos** | `core` · `ops` · `cloud` · `core+ops` · `core+cloud` |
| **Tipo** | **A** só core · **B** só ops/cloud · **C** cross-repo |
| **Repo primário** | ex. `ideiasfactory/media-hub` |
| **Repo secundário** | ex. `ideiasfactory/media-hub-ops` (se houver) |
| **Contrato** | API / imagem / env / digest — o que o secundário consome |
| **Ordem de entrega** | 1) … 2) … (sempre core → consumidor no tipo C) |

**Tipo A** — 1 PR no core; ops só bump de pin se quiser homologar.  
**Tipo B** — 1 PR no ops/cloud; pin de artefato core já existente.  
**Tipo C** — contrato no core (compatível) → release/tag/digest → PR no consumidor.

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

**Status:** Em andamento (incremento cancelamento entregue na v0.2.0; resto aberto)  
**Release:** v0.2 (incremento) · follow-ups pós-0.2  
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

### Entregue na v0.2.0 (incremento)

- Cancelamento de jobs em andamento (`POST /api/v1/jobs/{id}/cancel` + botão na UI)
- Checkbox de **forçar reprocessamento** na UI (integra com EPIC-003)

### Pendente (fora do fechamento 0.2.0)

- Download de vídeo, playlists, legendas existentes, seleção de qualidade

### Critérios de aceite (sprint v0.2)

- Pelo menos um incremento entregue e testável (prioridade a definir no kickoff:
  vídeo **ou** playlists **ou** cancelamento/UX — sem obrigar o épico inteiro
  numa única PR) — **atendido** (cancelamento)
- Sem bypass de DRM/login/geo (ADR-013)
- Documentação e release notes atualizadas ao fechar a versão (ADR-021)

---

## EPIC-003 — Content Registry

**Status:** Concluído (implementação inicial `registry.jsonl` na v0.2.0)  
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

### Critérios de aceite (sprint v0.2)

- Registry em disco (`registry.jsonl`) consultado antes do pipeline
- Job repetido sem `force` reutiliza artefatos / evita re-download e re-transcrição
- `force=true` força reprocessamento e atualiza o registro
- Testes cobrindo hit/miss do registry
- ADR-010 marcado como Accepted ao concluir

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

**Status:** Fase 1 concluída (v0.2.0); restante planejado para v0.7  
**Release:** v0.2 (fase 1 — logging) · v0.7 (métricas, tracing, dashboards)  
**Depende de:** EPIC-001  
**ADRs:** 022

### Escopo completo

Métricas, tracing, logs estruturados e dashboards.

### Fase 1 — Logging local (entregue na v0.2.0)

Entregar logging operacional sem stack de observabilidade externa:

| Destino | Comportamento |
|---------|----------------|
| Console | Mesmo formato “estilo Java” (ver abaixo) |
| Disco | Arquivos sob `logs/` (gitignored) |

**Formato (estilo Java / Log4j-like), exemplo:**

```text
2026-08-06 13:35:01,123 INFO  [MainThread] media_hub.jobs - Job abc123 started
```

Campos mínimos: `timestamp` (`yyyy-MM-dd HH:mm:ss,SSS`), `LEVEL`, `[thread]`,
`logger`, mensagem. Exceções com stack trace no mesmo handler.

**Retenção e arquivo:**

- Logs ativos/diários em disco com **retenção de 30 dias** (arquivos mais
  antigos que 30 dias são elegíveis a remoção ou arquivamento).
- Histórico compactado em **`tar.gz`** com nome no formato **`yyyy-mm`**
  (ex.: `logs/archive/2026-08.tar.gz`), agrupando o mês civil.
- Rotação/arquivo pode rodar no startup do processo e/ou sob demanda (job
  leve); sem cron externo obrigatório no MVP desta fase.
- Não enviar logs a SaaS (Datadog, CloudWatch, etc.) nesta fase.

**Critérios de aceite (fase 1):**

- Console e arquivo usam o mesmo formatter estilo Java
- Diretório `logs/` (e `logs/archive/`) documentados; ausentes do Git
- Política de 30 dias verificável (teste ou rotina documentada)
- Arquivo mensal `yyyy-mm.tar.gz` gerado para meses elegíveis
- Sem métricas/tracing/dashboards nesta fase (ficam para o restante do épico)

### Fora da fase 1

Prometheus/OpenTelemetry, dashboards, alertas, correlação distribuída — v0.7.

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

---

## EPIC-034 — Monorepo modular (frontend / BFF / backend)

**Status:** Concluído  
**Release:** v0.1.x (0.1.1)  
**Depende de:** EPIC-001  
**ADRs:** 020

### Objetivo

Reorganizar o monólito monolítico de pastas em um **monorepo modular**, separando
as camadas frontend, BFF e backend sem introduzir múltiplos processos, Docker ou
deploy distribuído.

### Inclui

```
frontend/   # templates + static
bff/        # páginas HTML, /api/v1, auth, factory FastAPI
backend/    # jobs, media, transcription, models, utils
app/        # composition root (uvicorn app.main:app)
```

### Critérios de aceite

- `uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload` continua válido
- UI, API, health e Swagger funcionam como antes
- `pytest` e `python -m compileall app backend bff frontend` passam
- documentação de arquitetura atualizada
- frontend não importa backend; BFF é a única ponte HTTP → domínio

---

## EPIC-035 — Validação de vulnerabilidades de segurança

**Status:** Planejado (próxima prioridade após fechar v0.2)  
**Release:** v0.2.x  
**Depende de:** EPIC-001; base de CI já existente (Bandit / `pip-audit` / Dependabot em 0.1.2)  
**ADRs:** 023

### Objetivo

Estabelecer validação contínua e critérios de aceite de segurança da aplicação,
além do lint/SAST já presente no CI, antes de expandir superfície (adapters
sociais e deploy em container).

### Já entregue (baseline 0.1.2 — não reimplementar)

- Ruff + Bandit no CI
- `pip-audit` + Dependency Review em PRs
- Dependabot semanal

### Inclui (este épico)

- política de severidade: falhar CI em vulnerabilidades **High/Critical** de
  dependências (e documentar exceções temporárias com prazo)
- checklist de segurança da aplicação (OWASP ASVS / cheat sheet leve):
  auth API Key, path traversal, upload/download whitelist, headers HTTP
  sensíveis, exposição de `.env` / segredos, logging sem vazamento de keys
- varredura de segredos no repositório (ex.: GitHub secret scanning e/ou
  ferramenta no CI)
- revisão pontual dos endpoints e da UI quanto a XSS refletido / CSRF onde
  aplicável ao modelo cookie + API Key
- relatório ou seção em docs com baseline e gaps aceitos para o MVP local
- quando EPIC-036 existir: scan de imagem de container (ex.: Trivy) no CI ou
  no fluxo de build documentado

### Critérios de aceite

- CI bloqueia High/Critical em dependências (ou exceção ADR/documentada)
- checklist de app security executado e gaps registrados
- nenhum segredo de exemplo real no repo; `.env.example` sem valores sensíveis
- README / docs descrevem como rodar as verificações localmente
- sem introduzir bypass de DRM/auth/geo (ADR-013)

### Fora de escopo

- pentest comercial completo
- WAF / rate limiting distribuído / multi-tenant IAM (EPIC-023)
- correção de CVEs em dependências transitivas sem caminho de upgrade
  (registrar como limitação)

---

## EPIC-036 — Deploy Docker com volumes no host

**Status:** Planejado (após ou em paralelo controlado com EPIC-035)  
**Release:** v0.2.x  
**Depende de:** EPIC-001; preferencialmente após baseline de segurança (EPIC-035)  
**ADRs:** 024

### Objetivo

Oferecer uma forma oficial de executar o Media Hub em Docker, mantendo o
modelo de **um único processo Uvicorn**, com dados persistentes no host via
volumes mapeados.

### Inclui

- `Dockerfile` (Python 3.11+, FFmpeg instalado, entrypoint `uvicorn app.main:app`)
- `docker-compose.yml` (ou equivalente) para subir a app na porta **8010**
- volumes externos no host (obrigatórios):

| Caminho no container | Volume no host (exemplo) | Conteúdo |
|----------------------|--------------------------|----------|
| `/app/.env` ou dir de config | `./.env` / `./config` | configurações / API Key |
| `/app/logs` | `./logs` | logs diários + `archive/` |
| `/app/output` | `./output` | artefatos por `job_id` |
| `/app/registry.jsonl` (ou dir) | `./registry.jsonl` | Content Registry (EPIC-003) |

- documentação de build/run, permissões de UID/GID se necessário, e limites
  conhecidos (jobs em memória continuam voláteis no restart do container)
- `.dockerignore` para não copiar `output/`, `logs/`, `.env`, `.venv` para a imagem
- imagem **não** embute segredos; config só via env/arquivo montado

### Critérios de aceite

- `docker compose up` (ou `docker run` documentado) sobe a UI em
  `http://localhost:8010`
- logs escritos no volume do host; artefatos em `output/` no host
- reiniciar o container preserva `output/`, `logs/` e registry no host
- jobs em memória continuam perdidos no restart (comportamento atual documentado)
- `pytest` / CI de app não exigem Docker para passar; smoke Docker documentado
- sem Kubernetes, Swarm ou multi-réplica nesta etapa

### Fora de escopo

- orquestração K8s / Helm
- workers/Redis (EPIC-015)
- build multi-arch obrigatório (pode ser follow-up)
- storage remoto (MinIO/S3 — EPIC-004)
- promote/CD homolog (EPIC-040 / EPIC-041); este épico só entrega packaging
  local/imagem

### Encaixe com EPIC-040 / EPIC-041

A fatia mínima de Dockerfile + Compose é pré-requisito do publish GHCR
(EPIC-040) e do promote no ops privado (EPIC-041).

---

## EPIC-037 — Documentação operacional (segurança + Docker)

**Status:** Planejado (acompanha EPIC-035 e EPIC-036)  
**Release:** v0.2.x  
**Depende de:** EPIC-035 e/ou EPIC-036 (pode avançar em PR conjunta)  
**ADRs:** 021, 023, 024

### Objetivo

Atualizar a documentação do produto para refletir hardening de segurança,
deploy Docker com volumes e a nova ordem de prioridade do roadmap — sem
duplicar o conteúdo dos épicos.

### Inclui

- README: seção “Docker”, volumes, quick start containerizado, comandos de
  segurança locais alinhados ao CI
- `docs/ARCHITECTURE.md`: diagrama/nota de deploy em container + mapeamento
  de volumes; seção Segurança atualizada com baseline EPIC-035
- `docs/ROADMAP.md` / `docs/EPICS.md`: status e prioridade de execução
- `docs/DECISIONS.md`: ADRs 023/024 Accepted ao concluir implementação
- `AGENTS.md` / `CONTRIBUTING.md`: quando Docker passa a ser caminho suportado
- limitações conhecidas: jobs em memória vs persistência de disco via volumes
- release notes (ADR-021) ao fechar a faixa v0.2.x

### Critérios de aceite

- um contribuidores consegue clonar → `docker compose up` → processar job de
  teste seguindo só o README
- “fora do escopo” deixa de listar Docker como bloqueado quando o épico fechar
- links cruzados ROADMAP ↔ EPICS ↔ ADR ↔ ARCHITECTURE coerentes
- sem documentação órfã de flags/arquivos que não existam no repo

### Fora de escopo (este épico)

- vitrine de descoberta (GIF, matriz de adapters, README EN, topics GitHub,
  issues `good first issue`, campanhas) — **EPIC-038**
- mudança de licença / dual-license — TASK-038-01 / ADR-025

---

## EPIC-038 — Comunidade, visibilidade e engajamento open source

**Status:** Em andamento (v0.2.1 — tasks 01, 02, 03, 05; restante follow-up)  
**Release:** v0.2.1 (fatia) → follow-up v0.2.x  
**Depende de:** EPIC-032, EPIC-033; PO reautorizou fatia antes de EPIC-035–037  
**ADRs:** 018 (revisão → Apache-2.0), 025

### Objetivo

Tornar o Media Hub um repositório **source-available com alta descoberta e
colaboração**, medindo sucesso por stars, forks, visitors, Discussions e —
principalmente — **PRs externos em adapters e features**, sem expandir escopo
de produto além do funil de comunidade.

### Contexto

O projeto já tem higiene de governança (licença, CONTRIBUTING, badges, SemVer,
CI). O gargalo para visibilidade é narrativa + demo + issues contribuíveis +
distribuição. A licença PolyForm Noncommercial (ADR-018) limita adoção
comercial e parte do efeito rede de OSS permissivo; a postura deve ser
decidida explicitamente neste épico (TASK-038-01).

### Inclui (visão)

- decisão documentada de licença / dual-license vs. manter Noncommercial
- README “vitrine”: frase memorável, demo visual, matriz de adapters, EN
- metadados GitHub (description, topics, social preview)
- funil de contribuição: labels, `good first issue`, template New Adapter
- documentação do contrato de Adapter para contribuidores
- ritmo de Releases e comunicação
- plano de distribuição inicial (comunidades técnicas)
- métricas de engajamento (Insights) e ritual de revisão

### Tarefas

| ID | Tarefa | Entrega |
|----|--------|---------|
| **TASK-038-01** | Postura de licença e colaboração | ADR-025 + revisão ADR-018: manter Noncommercial, dual-license, ou migração OSI; impacto em forks/awesome lists documentado; README “Licença” atualizado |
| **TASK-038-02** | Narrativa e README discovery | Frase-gancho no topo; tabela **Adapters** (YouTube ✅ / demais 🔲 → épicos); GIF/demo 20–30s (URL → MP3/TXT/SRT); seção “quando usar vs yt-dlp+Whisper CLI”; README em **inglês** (ou bilingue PT/EN) |
| **TASK-038-03** | Metadados GitHub | Description curta em EN; topics (`whisper`, `yt-dlp`, `transcription`, `fastapi`, `self-hosted`, `python`, …); Open Graph / social preview se aplicável; Discussions habilitadas (opcional) |
| **TASK-038-04** | Funil de issues contribuíveis | Labels `good first issue`, `help wanted`, `adapter`; 5–8 issues públicas; ≥2 starters pequenas; template GitHub **New Adapter** com checklist (contrato, testes, ADR-013, sem DRM) |
| **TASK-038-05** | Contrato Adapter para contribuidores | Doc curta (`docs/` ou seção CONTRIBUTING): onde plugar, critérios de aceite mínimos, referência ADR-007/014; alinhada aos épicos 005+ sem implementar adapters |
| **TASK-038-06** | Ritmo de Releases | Política: release notes a cada incremento SemVer (ADR-021); GitHub Releases com notas humanas; mencionar contribuidores no CHANGELOG |
| **TASK-038-07** | Distribuição inicial | Checklist executável (não spam): 1 post técnico (Dev.to/Hashnode); 1 comunidade self-hosted ou AI; Show HN **opcional** após demo estável; PRs em awesome lists **somente se** a licença for aceita; LinkedIn/X com o GIF |
| **TASK-038-08** | Métricas e ritual | Baseline de Insights (visitors, clones, stars, forks); meta qualitativa: ≥1 PR externo ou Discussion útil; revisão mensal leve no ROADMAP |

### Ordem sugerida das tarefas

1. **TASK-038-01** (bloqueia narrativa de licença e elegibilidade a listas)  
2. **TASK-038-02** + **TASK-038-03** (vitrine e descoberta no GitHub)  
3. **TASK-038-04** + **TASK-038-05** (funil antes de pedir colaboração em adapters)  
4. **TASK-038-06** (ritmo contínuo)  
5. **TASK-038-07** (só com demo estável — idealmente pós-Docker EPIC-036)  
6. **TASK-038-08** (acompanhamento)

### Critérios de aceite

- ADR-025 Accepted com postura de licença explícita e consequências
- README (EN ou bilingue) com demo visual + matriz de adapters
- topics + description EN configurados no GitHub
- ≥5 issues abertas; ≥2 com `good first issue`; template New Adapter publicado
- CONTRIBUTING (ou docs) descreve como propor um adapter
- checklist de distribuição preenchido ao menos uma vez (ou adiado com motivo)
- Insights baseline registrado em nota curta (ROADMAP / Discussion / ADR)
- sem implementação de adapters sociais neste épico (permanecem EPIC-005+)
- sem bypass de DRM/login/geo (ADR-013); DISCLAIMER permanece obrigatório em posts

### Fora de escopo

- implementar Instagram/TikTok/etc. (v0.3+)
- mudar arquitetura ou extrair `SourceAdapter` só “para a comunidade” sem segundo uso (ADR-014)
- programa pago de bounties / sponsorships (pode ser follow-up)
- marketing pago ou growth hacking agressivo
- alterar escopo de EPIC-035–037 (este épico consome o resultado deles)

### Dependências e encaixe na v0.2.x

```
EPIC-035 → (EPIC-036 + EPIC-040) → EPIC-041 → EPIC-037 → EPIC-038 → (v0.3 adapters)
```

Docker + docs (036/037) alimentam a demo “one command” usada em TASK-038-02/07.
EPIC-040 publica a imagem no GHCR; EPIC-041 promove o mesmo digest em homolog
via `media-hub-ops`.
Issues de adapters (038-04) preparam contribuição na v0.3 sem antecipar código.

---

## EPIC-039 — Identidade por URL + checkpoint/retomada de jobs

**Status:** Concluído (v0.2.1)  
**Release:** v0.2.1  
**Depende de:** EPIC-003  
**ADRs:** 010 (revisão), 026

### Objetivo

Identificar conteúdos pelo hash da URL canônica e retomar pipelines interrompidos
na segunda execução da mesma URL, sem recomeçar do zero.

### Inclui

- `content_hash = SHA256(canonical_youtube_url)`
- Checkpoint em `registry.jsonl` (`status`, `last_step`) após cada etapa
- Artefatos estáveis em `output/by-content/{content_hash}/`
- Retomada automática sem `force`; `force=true` reinicia

### Critérios de aceite

- URLs equivalentes (`youtu.be` / `watch?v=`) compartilham o mesmo hash
- Job parcial (ex.: áudio baixado) → nova execução pula o download
- `force=true` limpa o diretório de conteúdo e reprocessa
- Testes cobrindo hash estável, cache ready e resume
- ADR-026 Accepted

### Fora de escopo

- Persistência de jobs em Redis/DB (EPIC-015)
- Kill cooperativo de FFmpeg/Whisper no meio da syscall
- Limpeza automática de `by-content/`

---

## EPIC-040 — CI/CD IHL + homolog mac-srv-01

**Status:** Concluído (baseline no open; promote IHL re-homed em EPIC-041)  
**Release:** v0.2.x  
**Depende de:** EPIC-036 (imagem Docker + volumes); preferencialmente após ou em
paralelo controlado com EPIC-035  
**ADRs:** 027, 028, 029, 030, 031, 032 (e 024 para packaging); localização do
promote → [ADR-033](DECISIONS.md#adr-033--artefato-público-promote-privado-media-hub-ops) /
[EPIC-041](EPICS.md#epic-041--separação-ops-ihl-do-repositório-open-media-hub-ops)  
**Doc:** [CICD.md](CICD.md) · [OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md)

### Objetivo

Implementar a baseline CI/CD IHL do Media Hub: build once → GHCR (digest) →
promote para **HOMOLOG**, com DEV local via Compose e **PROD apenas
documentado** (sem pipeline ativo).

### Nota de fronteira (pós-EPIC-041)

A baseline (princípios ADR-027–032, `build-publish.yml`, Compose DEV, doc
pública sanitizada) permanece neste repo. O **workflow e manifests de deploy
homolog** passaram para o repo privado `ideiasfactory/media-hub-ops`
(EPIC-041). Dogfooding da imagem OSS no IHL continua; só o *onde* do CD mudou.

### Ambientes

| Ambiente | Alvo | Status |
|----------|------|--------|
| DEV | máquina local + `docker compose` | Ativo (este repo) |
| HOMOLOG | `mac-srv-01` via `media-hub-ops` | CD no ops privado |
| PROD | futuro | Documentado / não ativo |

### Relação com EPIC-036

EPIC-036 entrega `Dockerfile`, Compose e volumes no host. **EPIC-040 consome
essa imagem**: publish no GHCR e (via 041) deploy homolog. Sequência autorizada
na v0.2.x:

```
EPIC-035 → (EPIC-036 + EPIC-040) → EPIC-041 → EPIC-037 → EPIC-038 restante → (v0.3)
```

Homolog **não** funciona sem packaging Docker (036).

### Inclui (entregue)

- ADRs 027–032 e estratégia [CICD.md](CICD.md) (sanitizada na 041)
- Workflow build/publish → `ghcr.io/ideiasfactory/media-hub` (SemVer/RC/sha;
  sem `latest` como identidade)
- DEV: `docker-compose.yml` na raiz
- Princípios: build once, digest, desired state, PROD stub documentado

### Critérios de aceite

- CI existente permanece verde (lint/test/security)
- Build de imagem válido no GitHub-hosted runner; push GHCR em `main`/tags/`workflow_dispatch`
- DEV: `docker compose config` (e up documentado) na raiz
- Nenhum workflow de produção ativo; PROD só em docs
- Segredos reais ausentes do Git; placeholders documentados
- ROADMAP / ARCHITECTURE / CHANGELOG alinhados
- Promote homolog: ver critérios de EPIC-041 (repo ops)

### Fora de escopo

- Deploy production automatizado
- K3s / Helm / Argo CD (só GitOps-ready)
- Rebuild da app no host de homolog
- Contorno de DRM/auth/geo (ADR-013)

---

## EPIC-041 — Separação ops IHL do repositório open (media-hub-ops)

**Status:** Em andamento  
**Release:** v0.2.x (ajuste de fronteira pós-EPIC-040)  
**Depende de:** EPIC-040 (baseline CD existente)  
**Repos:** core+ops  
**Tipo:** C (extrai ops do monorepo open → repo privado; core continua a
publicar a imagem)  
**Repo primário:** ideiasfactory/media-hub  
**Repo secundário:** ideiasfactory/media-hub-ops (privado)  
**Contrato:** imagem GHCR `ghcr.io/ideiasfactory/media-hub@sha256:…` (ou tag RC)  
**Ordem:** 1) criar ops + espelhar deploy 2) validar promote no mac-srv-01
3) remover CD/manifests IHL do open 4) docs/ADR  
**ADRs:** 033; revê 027, 029, 031 no que toca *localização* do promote  
**Doc:** [OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md) · [CICD.md](CICD.md)

### Objetivo

Separar **publicação de artefato OSS** de **deploy em infra IHL**, alinhando o
repo público ao modelo open core e preparando o produto multi-repo sem fork
divergente.

### Inclui

- Documento `docs/OPEN_CORE_AND_OPS.md` (discussão, conclusões, observações)
- ADR-033: artefato público / promote privado; dependência unidirecional
- Template de classificação multi-repo (A/B/C) em `EPICS.md`
- Criar repo privado `media-hub-ops` com:
  - workflow deploy homolog (equivalente ao anterior no open)
  - `deploy/homolog/` (compose + versions.yaml + .env.example)
  - README/runbook IHL (runner, Environment `homolog`, secrets)
- Reapontar runner self-hosted / Environment para o repo privado (passo manual)
- Remover do open: `.github/workflows/deploy-homolog.yml`, `deploy/homolog/`,
  labels actionlint só de homolog
- Atualizar `CICD.md`, `deploy/README.md`, README, ROADMAP, CHANGELOG, AGENTS
- Manter no open: `ci.yml`, `build-publish.yml`, Dockerfile, Compose DEV

### Critérios de aceite

- Repo `media-hub-ops` existe, **privado**, com CD homolog (workflow + manifests)
- Repo open **não** contém workflow nem manifests de deploy IHL
- Build/publish GHCR no open continua; promote usa o mesmo digest
- `CICD.md` público descreve self-host + publish; detalhe de host IHL só no ops
- EPIC-040: baseline entregue; promote re-homed em 041 (explícito no ROADMAP)
- `pytest` + `compileall` no open (sem regressão de app)
- Sem segredos no Git (open ou ops)

### Fora de escopo

- Criar `media-hub-cloud` / SaaS multi-tenant / billing
- Pipeline de produção
- Mudança de licença do core
- Alterar contrato `/api/v1` da aplicação
- Adapters sociais (v0.3)

---

