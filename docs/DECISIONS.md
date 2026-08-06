# Decisões de Arquitetura (ADRs)

Registro de Architecture Decision Records do Media Hub.

Formato: contexto → decisão → consequências. Status: **Accepted**, **Proposed**,
**Deprecated** ou **Superseded**.

Documentação relacionada: [ARCHITECTURE.md](ARCHITECTURE.md) ·
[ROADMAP.md](ROADMAP.md) · [EPICS.md](EPICS.md)

---

## Índice

| ADR | Título | Status |
|-----|--------|--------|
| [ADR-001](#adr-001--monólito-local-com-jobs-em-memória) | Monólito local com jobs em memória | Accepted |
| [ADR-002](#adr-002--dependências-pesadas-importadas-sob-demanda) | Dependências pesadas importadas sob demanda | Accepted |
| [ADR-003](#adr-003--downloads-por-nomes-fixos) | Downloads por nomes fixos | Accepted |
| [ADR-004](#adr-004--um-vídeo-por-job) | Um vídeo por job | Accepted |
| [ADR-005](#adr-005--porta-fixa-8010-e-único-processo-uvicorn) | Porta fixa 8010 e único processo Uvicorn | Accepted |
| [ADR-006](#adr-006--faster-whisper-local-em-cpu) | Faster-Whisper local em CPU | Accepted |
| [ADR-007](#adr-007--arquitetura-baseada-em-adapters) | Arquitetura baseada em Adapters | Accepted (diretriz) |
| [ADR-008](#adr-008--interface-transcriber-desacoplada) | Interface Transcriber desacoplada | Accepted (diretriz) |
| [ADR-009](#adr-009--content-intelligence-desacoplada-da-aquisição) | Content Intelligence desacoplada da aquisição | Accepted (diretriz) |
| [ADR-010](#adr-010--content-registry-e-deduplicação) | Content Registry e deduplicação | Proposed |
| [ADR-011](#adr-011--storage-filesystem-first) | Storage filesystem-first | Accepted (diretriz) |
| [ADR-012](#adr-012--metadata-store-jsonl--postgresql) | Metadata Store JSONL → PostgreSQL | Proposed |
| [ADR-013](#adr-013--sem-contorno-de-drm-auth-ou-geo) | Sem contorno de DRM, auth ou geo | Accepted |
| [ADR-014](#adr-014--extrair-abstrações-somente-com-uso-imediato) | Extrair abstrações somente com uso imediato | Accepted |
| [ADR-015](#adr-015--api-key-via-variável-de-ambiente) | API Key via variável de ambiente | Proposed |
| [ADR-016](#adr-016--openapi--swagger-nativos-do-fastapi) | OpenAPI / Swagger nativos do FastAPI | Proposed |
| [ADR-017](#adr-017--semver-e-versionamento-do-contrato-da-api) | SemVer e versionamento do contrato da API | Proposed |
| [ADR-018](#adr-018--licença-polyform-noncommercial-100) | Licença PolyForm Noncommercial 1.0.0 | Proposed |
| [ADR-019](#adr-019--release-notes-em-dois-níveis) | Release notes em dois níveis | Proposed |

---

## ADR-001 — Monólito local com jobs em memória

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-001

### Contexto

O MVP precisa validar fluxo de aquisição e UX rapidamente, sem infraestrutura
distribuída.

### Decisão

Usar um único processo FastAPI com background tasks nativas e jobs apenas em
memória. Sem banco, broker ou workers no EPIC-001.

### Consequências

- Entrega rápida e operação simples (`uvicorn` na porta 8010).
- Estado de jobs é perdido ao reiniciar; arquivos em `output/` permanecem.
- Múltiplos workers Uvicorn não compartilham jobs — restrito a um processo.
- Persistência e filas ficam para EPIC-015 / EPIC-016.

---

## ADR-002 — Dependências pesadas importadas sob demanda

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-001

### Contexto

`yt-dlp` e `faster-whisper` são pesados e podem atrasar startup, health check e
testes unitários.

### Decisão

Importar `yt-dlp` e `faster-whisper` apenas no caminho de processamento do job.

### Consequências

- `GET /`, `GET /health` e testes sem rede/modelo permanecem leves.
- Falhas de importação de mídia/STT aparecem só ao processar um job.
- Testes unitários não dependem de internet nem de modelos baixados.

---

## ADR-003 — Downloads por nomes fixos

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-001

### Contexto

Expor arquivos gerados por job exige proteção contra path traversal e nomes
arbitrários.

### Decisão

Servir somente uma whitelist de nomes exatos (`audio.mp3`, `transcript.txt`,
`transcript.srt`, `metadata.json`). O caminho final deve resolver para dentro de
`output/{job_id}/`.

### Consequências

- Superfície de ataque reduzida.
- Contratos de download previsíveis para UI e clientes.
- Novos artefatos exigem atualização explícita da whitelist.

---

## ADR-004 — Um vídeo por job

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-001  
**Revisão prevista:** EPIC-002

### Contexto

Playlists e múltiplos itens aumentam complexidade de UX, progresso e storage.

### Decisão

Aceitar apenas vídeos individuais públicos do YouTube, com `noplaylist`. Playlists,
download de vídeo completo, autenticação e cookies ficam fora do MVP.

### Consequências

- Fluxo e critérios de aceite simples.
- Playlists e vídeo (não só áudio) entram em EPIC-002.
- Mensagens de erro claras para URLs não suportadas.

---

## ADR-005 — Porta fixa 8010 e único processo Uvicorn

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-001

### Contexto

O ecossistema Ideias Factory precisa de porta estável e previsível para o Media Hub.

### Decisão

Executar sempre em `0.0.0.0:8010` com um único processo:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

### Consequências

- Interface em `http://localhost:8010`.
- Compatível com jobs em memória (ADR-001).
- Mudança de porta ou multi-process exige revisão deste ADR e do Job Manager.

---

## ADR-006 — Faster-Whisper local em CPU

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-001  
**Revisão prevista:** EPIC-014

### Contexto

O MVP exige STT local, sem depender de APIs pagas na primeira entrega.

### Decisão

Usar `faster-whisper` em CPU com `compute_type=int8`. Modelos permitidos: `tiny`,
`base`, `small`. Idiomas: autodetect, `pt`, `en`, `es`.

### Consequências

- Zero custo de API no caminho feliz do MVP.
- Qualidade/velocidade limitadas pelo hardware local.
- Modelos são baixados na primeira utilização.
- Outros engines entram via interface Transcriber (ADR-008 / EPIC-014).

---

## ADR-007 — Arquitetura baseada em Adapters

**Status:** Accepted (diretriz de produto)  
**Data:** 2026-08-06  
**Épicos:** EPIC-002, EPIC-005+

### Contexto

O Media Hub deve suportar várias plataformas sem acoplar o pipeline a uma fonte.

### Decisão

Toda fonte externa será um **Source Adapter** com contrato comum
(`supports`, `get_metadata`, `download`, `download_audio`, `get_transcript`).
No EPIC-001 a lógica YouTube permanece em `media.py` sem interface formal.

### Consequências

- Novas plataformas não alteram API/UI/Job Manager de forma estrutural.
- A interface só é extraída quando o segundo adapter (ou evolução YouTube) exigir
  uso imediato (ADR-014).
- Adapters não devem implementar bypass de DRM/auth/geo (ADR-013).

---

## ADR-008 — Interface Transcriber desacoplada

**Status:** Accepted (diretriz de produto)  
**Data:** 2026-08-06  
**Épico:** EPIC-014

### Contexto

Diferentes produtos podem precisar de engines distintos (local vs cloud, custo vs
qualidade).

### Decisão

Transcrição passa por interface `Transcriber.transcribe(audio)`. Faster-Whisper é
a implementação inicial; OpenAI, Deepgram, Azure, Google e AssemblyAI são opções
futuras selecionáveis por configuração.

### Consequências

- Pipeline de mídia não conhece o vendor de STT.
- No EPIC-001 não há classe abstrata obrigatória — apenas o módulo
  `transcription.py`.
- Extração formal da interface ocorre com o segundo engine (ADR-014).

---

## ADR-009 — Content Intelligence desacoplada da aquisição

**Status:** Accepted (diretriz de produto)  
**Data:** 2026-08-06  
**Épico:** EPIC-017

### Contexto

Resumo, capítulos, hooks e embeddings são inteligência de negócio, não aquisição.

### Decisão

Content Intelligence é camada posterior e opcional no pipeline. O MVP entrega
apenas artefatos de aquisição/transcrição. Integrações (ex.: Video Lab) consomem
saídas normalizadas, não o downloader.

### Consequências

- Media Hub permanece reutilizável por vários produtos.
- EPIC-001 não inclui resumo, classificação ou embeddings.
- Video Lab Integration (EPIC-018) depende de artefatos estáveis + Intelligence.

---

## ADR-010 — Content Registry e deduplicação

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-003

### Contexto

Reprocessar o mesmo vídeo gera custo de rede, CPU e disco desnecessários.

### Decisão

Introduzir Content Registry (inicialmente `registry.jsonl`) consultado antes de
qualquer download. Identidade preferencial: `platform + video_id`; fallback
`SHA256(canonical_url + duration + title)`. Hashes auxiliares: `audio_hash`,
`transcript_hash`. Reprocessar só com `force=true`.

### Consequências

- Cache semântico de conteúdos entre jobs.
- Substituição futura por PostgreSQL (ADR-012 / EPIC-016).
- Ainda não implementado no EPIC-001.

---

## ADR-011 — Storage filesystem-first

**Status:** Accepted (diretriz de produto)  
**Data:** 2026-08-06  
**Épico:** EPIC-001 (fato); EPIC-004 (abstração)

### Contexto

Object storage adiciona complexidade operacional cedo demais para o MVP.

### Decisão

Armazenar artefatos no filesystem (`output/{job_id}/`). Quando necessário,
introduzir abstração que permita Filesystem → MinIO → S3 sem mudar regras de
negócio.

### Consequências

- Operação local simples no MVP.
- Limpeza automática e retenção ficam para épicos posteriores.
- EPIC-004 formaliza a interface de storage.

---

## ADR-012 — Metadata Store JSONL → PostgreSQL

**Status:** Proposed  
**Data:** 2026-08-06  
**Épicos:** EPIC-003, EPIC-016

### Contexto

O registry precisa começar simples e migrar quando consultas e concorrência
exigirem.

### Decisão

Usar `registry.jsonl` na primeira versão do Content Registry e migrar para
PostgreSQL em EPIC-016, preservando o modelo conceitual de conteúdo.

### Consequências

- Baixa barreira para EPIC-003.
- Limites claros de concorrência/consulta em JSONL.
- Migração planejada evita redesign do domínio.

---

## ADR-013 — Sem contorno de DRM, auth ou geo

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** transversal

### Contexto

Uso responsável e conformidade são requisitos do produto e das regras de agentes.

### Decisão

Não implementar cookies de plataforma, autenticação de terceiros, bypass de DRM,
login ou restrições territoriais. Processar apenas conteúdo público/autorizado
acessível sem contornar controles de acesso.

### Consequências

- Escopo de adapters limitado a conteúdo publicamente acessível pelos meios
  oficiais/suportados das ferramentas utilizadas.
- Falhas por conteúdo privado/restrito são erros esperados e documentados.
- Qualquer exceção exige ADR novo e aprovação humana explícita.

---

## ADR-014 — Extrair abstrações somente com uso imediato

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** transversal

### Contexto

Há risco de overengineering ao criar adapters, interfaces e storages “para o
futuro” sem segundo consumidor.

### Decisão

A Foundation nasce com o MVP, mas interfaces formais (`SourceAdapter`,
`Transcriber`, Storage) só são extraídas quando houver uso imediato (segundo
adapter, segundo engine, segundo backend de storage) ou quando o épico autorizado
exigir a abstração como entrega.

### Consequências

- Código do EPIC-001 permanece direto e testável.
- Diretrizes ADR-007/008/011 orientam o desenho sem forçar classes vazias.
- Refactors de extração são esperados e aceitos nos épicos correspondentes.

---

## ADR-015 — API Key via variável de ambiente

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-026  
**Evolução:** EPIC-023

### Contexto

A API REST será consumida por outros produtos (Video Lab, CLI, agentes). Mesmo
no modo single-tenant local, expor `/api/*` sem segredo é frágil.

### Decisão

Proteger endpoints `/api/*` com uma API Key única lida de `.env`
(ex.: `MEDIA_HUB_API_KEY`). `GET /health` permanece público. Autenticação com
usuários/OAuth e múltiplas keys fica para EPIC-023.

### Consequências

- Integrações usam header padrão documentado.
- Segredo nunca vai para o Git (`.env` no `.gitignore`; `.env.example` sem valor).
- UI e CLI precisam do mesmo segredo ou de política explícita de exceção.
- Não substitui autenticação multi-usuário.

---

## ADR-016 — OpenAPI / Swagger nativos do FastAPI

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-027

### Contexto

Clientes internos e o time precisam de contrato legível e experimentável sem
ferramenta externa.

### Decisão

Expor a documentação gerada pelo FastAPI: Swagger UI (`/docs`), schema
(`/openapi.json`) e opcionalmente ReDoc (`/redoc`). Manter metadados e versão
alinhados ao SemVer do produto.

### Consequências

- Baixo custo de manutenção (schema derivado do código).
- Com API Key ativa, o esquema de segurança deve aparecer no Swagger.
- Breaking changes no schema devem acompanhar ADR-017.

---

## ADR-017 — SemVer e versionamento do contrato da API

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-029

### Contexto

Consumidores (Video Lab, CLI, agentes) quebram se o contrato JSON/rotas mudar
sem sinal claro.

### Decisão

1. Versionar o **produto** com SemVer (`MAJOR.MINOR.PATCH`).
2. Versionar o **contrato da API** em path (`/api/v1/...`).
3. Breaking change de contrato → bump **MAJOR** do produto **e** nova versão de
   path (`/api/v2/...`), com convivência documentada quando necessário.
4. Mudanças compatíveis → MINOR ou PATCH, mantendo `/api/v1`.

### Consequências

- Tags Git e release notes alinhadas à versão.
- OpenAPI declara a versão do contrato.
- Exige disciplina para não alterar responses/campos obrigatórios em silêncio.

---

## ADR-018 — Licença PolyForm Noncommercial 1.0.0

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-031

### Contexto

O código deve permanecer público para estudo e contribuição, **sem** autorizar
uso comercial gratuito. Licenças OSI (MIT, Apache, GPL) permitem uso comercial e
não atendem ao requisito.

### Decisão

Adotar a **PolyForm Noncommercial License 1.0.0** como licença do repositório.

- Permite uso, modificação e redistribuição para fins **não comerciais**.
- Uso comercial exige licença/acordo separado com a Ideias Factory.
- Trata-se de licença **source-available**, não “Open Source” no sentido OSI —
  a restrição comercial é intencional.

Alternativas consideradas e rejeitadas para este objetivo:

| Licença | Motivo da rejeição |
|---------|-------------------|
| MIT / Apache-2.0 | Permitem uso comercial irrestrito |
| GPL / AGPL | Permitem uso comercial (com copyleft) |
| CC BY-NC 4.0 | Voltada a conteúdo; inadequada como licença principal de software |
| Commons Clause + Apache | Mais frágil/confusa que PolyForm para o mesmo fim |

### Consequências

- Arquivo `LICENSE` + seção clara no README.
- Contribuições sob a mesma licença (via CONTRIBUTING / DCO ou CLA simples).
- Uso comercial interno da Ideias Factory ou de clientes exige instrumento
  comercial à parte.
- Badges devem dizer a licença real (PolyForm Noncommercial), não “MIT”.

---

## ADR-019 — Release notes em dois níveis

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-030

### Contexto

Usuários finais e o time de engenharia precisam de informações diferentes na
mesma release.

### Decisão

Manter dois artefatos por versão:

1. **Usuário final:** texto amigável na UI (changelog / “Novidades”).
2. **Técnico:** `CHANGELOG.md` ou `docs/releases/` no repositório (Keep a
   Changelog), citando breaking changes, migrações e ADRs.

Ambos ligados à mesma tag SemVer.

### Consequências

- Processo de release inclui redigir os dois textos.
- UI não expõe detalhes internos desnecessários.
- Time preserva histórico técnico auditável no Git.
