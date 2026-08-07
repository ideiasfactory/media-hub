# Arquitetura — Media Hub

Documentação relacionada: [ROADMAP.md](ROADMAP.md) · [EPICS.md](EPICS.md) ·
[DECISIONS.md](DECISIONS.md)

---

## Estado atual (v0.1.1 — monorepo modular)

O Media Hub continua um **único processo** Uvicorn, agora organizado em camadas
no monorepo (EPIC-034 / ADR-020):

```
frontend/   → templates Jinja2 + static (CSS/JS)
bff/        → HTTP edge: páginas, /api/v1, auth, OpenAPI
backend/    → domínio: jobs, media, transcription, models, utils
app/        → composition root (`uvicorn app.main:app`)
```

O navegador cria um job e consulta o estado por polling. O BFF autentica a UI
via cookie HttpOnly quando há API Key e delega o processamento ao backend.

### Fluxo operacional

1. `POST /api/v1/jobs` valida URL, modelo e idioma e retorna um UUID.
2. Uma tarefa de background do FastAPI atualiza o job mantido em memória.
3. `yt-dlp` obtém metadados e baixa somente o melhor áudio disponível.
4. O pós-processador do `yt-dlp` usa FFmpeg para gerar `audio.mp3`.
5. `faster-whisper`, em CPU com `compute_type="int8"`, gera segmentos e idioma.
6. A aplicação grava TXT, SRT e JSON em `output/{job_id}`.
7. A UI exibe o resultado e oferece downloads por whitelist fixa.

### Componentes por camada

| Camada | Pacote | Responsabilidade |
|--------|--------|------------------|
| Frontend | `frontend/` | `templates/`, `static/` |
| BFF | `bff/web.py` | Páginas `/`, `/changelog` |
| BFF | `bff/api/v1.py` | Contrato REST `/api/v1` |
| BFF | `bff/auth.py` | API Key + cookie UI |
| BFF | `bff/app.py` | Factory FastAPI, OpenAPI, static mount |
| Backend | `backend/jobs.py` | Estado em memória e orquestração |
| Backend | `backend/media.py` | yt-dlp / FFmpeg |
| Backend | `backend/transcription.py` | faster-whisper |
| Backend | `backend/models.py` | Schemas de job |
| Backend | `backend/utils.py` | URL, whitelist, SRT |
| App | `app/main.py` | Entrypoint `create_app()` |

### Restrições operacionais

- Um único processo Uvicorn na porta **8010** (não são microserviços separados).
- Jobs existem somente em memória; reinício perde o estado (arquivos no disco
  permanecem).
- Sem fila persistente, banco ou isolamento multiusuário.
- Somente vídeos individuais públicos do YouTube (`noplaylist`).

### Layout de artefatos

```
output/{job_id}/
  audio.mp3
  transcript.txt
  transcript.srt
  metadata.json
```

---

## Arquitetura alvo (plataforma)

### Visão de alto nível

```
                  URL
                   │
                   ▼
           Source Adapter
     (YouTube, Instagram...)
                   │
                   ▼
        Metadata Extraction
                   │
                   ▼
      Duplicate Detection Layer
      (Hash + Content Registry)
                   │
          Já existe?
          ┌───────────────┐
          │               │
         Sim             Não
          │               │
          ▼               ▼
 Retorna artefatos     Download
                          │
                          ▼
                 Audio Extraction
                          │
                          ▼
                 Speech To Text
                          │
                          ▼
             Transcript Normalization
                          │
                          ▼
             Content Intelligence
                          │
                          ▼
                Storage / API / UI
```

### Camadas modulares

```
UI
 ↓
API
 ↓
Application Services
 ↓
Source Adapters
 ↓
Media Pipeline
 ↓
Storage
 ↓
Content Intelligence
```

A Foundation nasce junto com a v0.1 (EPIC-001): estruturas futuras só entram
quando o épico correspondente estiver autorizado e o código tiver uso imediato.

---

## Componentes-alvo

### Frontend

Interação do usuário: envio de URLs, consulta de jobs, download de artefatos e
visualização de transcrições. No v0.1: HTML / CSS / JS puro servidos pelo FastAPI.

### API

Contratos REST: criação de jobs, status, download, pesquisa e futura API pública.

Endpoints atuais (contrato `/api/v1`):

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/` | Interface web |
| `GET` | `/changelog` | Novidades amigáveis |
| `GET` | `/health` | Health check + versão |
| `GET` | `/docs` | Swagger UI |
| `POST` | `/api/v1/jobs` | Cria job |
| `GET` | `/api/v1/jobs/{job_id}` | Status e resultado |
| `GET` | `/api/v1/jobs/{job_id}/files/{filename}` | Download whitelist |

Segurança da API (v0.1.1):

- `MEDIA_HUB_API_KEY` no `.env` protege `/api/v1/*` (header `X-API-Key` ou Bearer).
- Sem key configurada, a API permanece aberta para uso local.
- UI same-origin recebe cookie HttpOnly `media_hub_api_key`.
- `GET /health`, `/`, `/changelog` e estáticos permanecem públicos.

### Job Manager

Criação, execução, monitoramento, cancelamento e retry.

- **Hoje:** memória + background tasks do FastAPI.
- **Depois (EPIC-015):** Redis + workers.

### Source Adapters

Cada plataforma isolada atrás da mesma interface:

```python
class SourceAdapter:
    def supports(self, url: str) -> bool: ...
    def get_metadata(self, url: str) -> dict: ...
    def download(self, url: str, dest: Path) -> Path: ...
    def download_audio(self, url: str, dest: Path) -> Path: ...
    def get_transcript(self, url: str) -> str | None: ...
```

No v0.1 a lógica YouTube vive em `media.py` sem interface formal. A extração do
contrato ocorre em EPIC-002 / EPIC-005 conforme novos adapters forem necessários.

### Media Pipeline

Download, extração, conversão e normalização de áudio/mídia.

### Transcriber

```python
class Transcriber:
    def transcribe(self, audio: Path, *, language: str | None, model: str) -> TranscriptResult: ...
```

Implementação atual: Faster Whisper (CPU, `int8`). Futuras: Whisper API, OpenAI,
Deepgram, Azure Speech, Google Speech, AssemblyAI (EPIC-014).

### Content Intelligence (EPIC-017+)

Camada desacoplada da aquisição: resumo, capítulos, hooks, palavras-chave,
classificação, embeddings, cenas, cortes para Shorts.

### Storage

| Fase | Implementação |
|------|---------------|
| Atual | Filesystem (`output/`) |
| EPIC-004 | Abstração Filesystem → MinIO → S3 |
| Futuro | Azure Blob, Google Storage |

### Metadata Store / Registry

| Fase | Implementação |
|------|---------------|
| Atual | `metadata.json` por job |
| EPIC-003 | `registry.jsonl` (deduplicação) |
| EPIC-016 | PostgreSQL |

---

## Estratégia de deduplicação (EPIC-003 / EPIC-039)

Identificador único (v0.2.1):

```
SHA256(https://www.youtube.com/watch?v={video_id})
```

URLs equivalentes (`youtu.be`, `shorts`, `watch?v=`) normalizam para a mesma
forma canônica antes do hash. Entradas legadas `youtube:{video_id}` ainda são
reconhecidas na leitura.

Hashes auxiliares: `transcript_hash`, `audio_hash` — para detectar alterações.

Registro inicial (`registry.jsonl`) por conteúdo:

```
content_hash, platform, url, canonical_url, video_id, title, channel,
duration, published_at, downloaded_at, artifacts, transcript_hash,
audio_hash, status, last_step, artifact_dir
```

**Identidade (v0.2.1 / EPIC-039):** `content_hash = SHA256(canonical_url)` com
`canonical_url = https://www.youtube.com/watch?v={id}`.

Artefatos estáveis em `output/by-content/{content_hash}/`; cada job espelha
cópias em `output/{job_id}/` para download.

Fluxo:

```
URL → Canonicalização → Hash → Registry
  → ready: reutiliza artefatos
  → in_progress/failed/cancelled + last_step: retoma
  → miss ou force: pipeline (checkpoint por etapa)
```

Reprocessamento explícito apenas com `force=true`.

---

## Estratégia de cache

Sempre consultar o Registry antes de baixar ou transcrever. Nunca baixar de novo
um conteúdo já existente, salvo `force=true`.

---

## Modelo de job (v0.1)

Campos em memória:

```
job_id, status, progress, message, metadata, transcript, artifacts
```

Estados:

```
queued → fetching_metadata → downloading → transcribing
  → generating_files → completed | failed
```

---

## Segurança

Implementado / obrigatório:

- validação de URL;
- whitelist de arquivos de download;
- proteção contra path traversal;
- logging (fase 1 do EPIC-022 / ADR-022: console + disco, formato estilo Java);
- mensagens amigáveis ao usuário;
- baseline de CI (Bandit, `pip-audit`, Dependency Review, Dependabot) desde 0.1.2.

Planejado (v0.2.x — EPIC-035 / ADR-023):

- política de falha em vulnerabilidades High/Critical;
- checklist de segurança da aplicação;
- varredura de segredos; scan de imagem quando houver Docker (EPIC-036).

Explicitamente fora de escopo em qualquer versão:

- cookies de sessão de plataformas;
- bypass de DRM, login ou restrição geográfica;
- uso de credenciais de terceiros sem autorização explícita de produto.

---

## Deploy (planejado / em andamento — EPIC-036 + EPIC-040 + EPIC-041)

Caminho alvo para execução em container (faixa v0.2.x), mantendo um único
processo Uvicorn:

```
Host                         Container
─────                        ─────────
./.env          ──────────►  config / env
./logs          ──────────►  /app/logs
./output        ──────────►  /app/output
./registry.jsonl ─────────►  registry
```

Jobs em memória continuam voláteis no restart; apenas disco mapeado persiste.

### Ambientes e promote (EPIC-040 / EPIC-041 / ADR-027–033)

| Ambiente | Onde | Mecanismo |
|----------|------|-----------|
| DEV | máquina local | `docker compose` (raiz deste repo) |
| HOMOLOG | infra IHL | promote no repo privado `media-hub-ops` |
| PROD | futuro | documentado; sem pipeline ativo |

Imagem: `ghcr.io/ideiasfactory/media-hub` (identidade por **digest**).  
Estratégia pública: [CICD.md](CICD.md) · fronteira OSS/ops:
[OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md).

---

## Evolução sem overengineering

| Quando | O que introduzir |
|--------|------------------|
| EPIC-001 | Monólito funcional, sem interfaces “para o futuro” |
| EPIC-026–034 (0.1.1) | API Key, Swagger, SemVer `/api/v1`, release notes, licença, CONTRIBUTING, README, monorepo modular |
| EPIC-028 | CLI como cliente da API (sem duplicar pipeline) |
| EPIC-002 / 005 | Extrair `SourceAdapter` quando o segundo adapter exigir |
| EPIC-003 | Registry JSONL quando deduplicação for prioridade |
| EPIC-022 (fase 1) | Logging local console+disco, retenção 30d, archive `yyyy-mm.tar.gz` |
| EPIC-035–037 + 040 (0.2.x) | Segurança, Docker+volumes, CI/CD IHL homolog, docs ops |
| EPIC-038 (0.2.x) | Comunidade / visibilidade: licença, README discovery, issues, distribuição |
| EPIC-004 | Abstração de storage quando MinIO/S3 for necessário |
| EPIC-014 | Interface `Transcriber` quando houver segundo engine |
| EPIC-015 | Redis / workers quando memória deixar de bastar |
| EPIC-016 | PostgreSQL quando JSONL deixar de escalar |

Decisões formais: [DECISIONS.md](DECISIONS.md).
