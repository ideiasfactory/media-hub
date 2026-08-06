# Arquitetura — Media Hub

Documentação relacionada: [ROADMAP.md](ROADMAP.md) · [EPICS.md](EPICS.md) ·
[DECISIONS.md](DECISIONS.md)

---

## Estado atual (EPIC-001 / v0.1)

O Media Hub v0.1 é um monólito local. O FastAPI serve a página Jinja2, a API JSON
e os artefatos. O navegador cria um job e consulta o estado por polling.

### Fluxo operacional

1. `POST /api/jobs` valida URL, modelo e idioma e retorna um UUID.
2. Uma tarefa de background do FastAPI atualiza o job mantido em memória.
3. `yt-dlp` obtém metadados e baixa somente o melhor áudio disponível.
4. O pós-processador do `yt-dlp` usa FFmpeg para gerar `audio.mp3`.
5. `faster-whisper`, em CPU com `compute_type="int8"`, gera segmentos e idioma.
6. A aplicação grava TXT, SRT e JSON em `output/{job_id}`.
7. A UI exibe o resultado e oferece downloads por whitelist fixa.

### Componentes atuais

| Módulo | Responsabilidade |
|--------|------------------|
| `main.py` | App FastAPI, templates, estáticos, health check |
| `api.py` | Criação, consulta e download de jobs |
| `jobs.py` | Estado em memória e orquestração do processamento |
| `media.py` | Integração mínima com yt-dlp / FFmpeg |
| `transcription.py` | Integração mínima com faster-whisper |
| `models.py` | Modelos de request/response |
| `utils.py` | Validação de URL, segurança de arquivos e SRT |

### Restrições operacionais (v0.1)

- Um único processo Uvicorn na porta **8010**.
- Jobs existem somente em memória; reinício perde o estado (arquivos no disco
  permanecem).
- Sem fila persistente, banco, autenticação ou isolamento multiusuário.
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

A Foundation nasce junto com o MVP: estruturas futuras só entram quando o épico
correspondente estiver autorizado e o código tiver uso imediato.

---

## Componentes-alvo

### Frontend

Interação do usuário: envio de URLs, consulta de jobs, download de artefatos e
visualização de transcrições. No v0.1: HTML / CSS / JS puro servidos pelo FastAPI.

### API

Contratos REST: criação de jobs, status, download, pesquisa e futura API pública.

Endpoints atuais (contrato a versionar em EPIC-029, tipicamente `/api/v1/...`):

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/` | Interface web |
| `GET` | `/health` | Health check (público) |
| `POST` | `/api/jobs` | Cria job |
| `GET` | `/api/jobs/{job_id}` | Status e resultado |
| `GET` | `/api/jobs/{job_id}/files/{filename}` | Download whitelist |

Evoluções planejadas de plataforma (v0.1.x):

- **API Key** via `.env` nos endpoints `/api/*` (EPIC-026 / ADR-015)
- **OpenAPI / Swagger** em `/docs` (EPIC-027 / ADR-016)
- **CLI** como cliente da API (EPIC-028)
- **SemVer** do produto + path versionado do contrato (EPIC-029 / ADR-017)
- **Release notes** amigáveis na UI + changelog técnico no repo (EPIC-030)

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

## Estratégia de deduplicação (EPIC-003)

Identificador único preferencial:

```
platform + video_id
```

Fallback quando não houver `video_id`:

```
SHA256(canonical_url + duration + title)
```

Hashes auxiliares: `transcript_hash`, `audio_hash` — para detectar alterações.

Registro inicial (`registry.jsonl`) por conteúdo:

```
content_hash, platform, url, canonical_url, video_id, title, channel,
duration, published_at, downloaded_at, artifacts, transcript_hash,
audio_hash, status
```

Fluxo:

```
URL → Normalização → Hash → Registry → Existe?
  → Sim: retorna artefatos
  → Não: executa pipeline
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
- logging;
- mensagens amigáveis ao usuário.

Explicitamente fora de escopo em qualquer versão:

- cookies de sessão de plataformas;
- bypass de DRM, login ou restrição geográfica;
- uso de credenciais de terceiros sem autorização explícita de produto.

---

## Evolução sem overengineering

| Quando | O que introduzir |
|--------|------------------|
| EPIC-001 | Monólito funcional, sem interfaces “para o futuro” |
| EPIC-026–033 | API Key, Swagger, SemVer, release notes, licença, CONTRIBUTING, README |
| EPIC-002 / 005 | Extrair `SourceAdapter` quando o segundo adapter exigir |
| EPIC-003 | Registry JSONL quando deduplicação for prioridade |
| EPIC-004 | Abstração de storage quando MinIO/S3 for necessário |
| EPIC-014 | Interface `Transcriber` quando houver segundo engine |
| EPIC-015 | Redis / workers quando memória deixar de bastar |
| EPIC-016 | PostgreSQL quando JSONL deixar de escalar |
| EPIC-028 | CLI como cliente da API (sem duplicar pipeline) |

Decisões formais: [DECISIONS.md](DECISIONS.md).
