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
| [ADR-010](#adr-010--content-registry-e-deduplicação) | Content Registry e deduplicação | Accepted |
| [ADR-011](#adr-011--storage-filesystem-first) | Storage filesystem-first | Accepted (diretriz) |
| [ADR-012](#adr-012--metadata-store-jsonl--postgresql) | Metadata Store JSONL → PostgreSQL | Proposed |
| [ADR-013](#adr-013--sem-contorno-de-drm-auth-ou-geo) | Sem contorno de DRM, auth ou geo | Accepted |
| [ADR-014](#adr-014--extrair-abstrações-somente-com-uso-imediato) | Extrair abstrações somente com uso imediato | Accepted |
| [ADR-015](#adr-015--api-key-via-variável-de-ambiente) | API Key via variável de ambiente | Accepted |
| [ADR-016](#adr-016--openapi--swagger-nativos-do-fastapi) | OpenAPI / Swagger nativos do FastAPI | Accepted |
| [ADR-017](#adr-017--semver-e-versionamento-do-contrato-da-api) | SemVer e versionamento do contrato da API | Accepted |
| [ADR-018](#adr-018--licença-polyform-noncommercial-100) | Licença PolyForm Noncommercial 1.0.0 | Superseded by ADR-018b / Apache-2.0 |
| [ADR-019](#adr-019--release-notes-em-dois-níveis) | Release notes em dois níveis | Accepted |
| [ADR-020](#adr-020--monorepo-modular-frontend--bff--backend) | Monorepo modular frontend / BFF / backend | Accepted |
| [ADR-021](#adr-021--checklist-obrigatório-ao-fechar-uma-versão) | Checklist obrigatório ao fechar uma versão | Accepted |
| [ADR-022](#adr-022--logging-local-estilo-java-com-retenção-e-arquivo-mensal) | Logging local estilo Java com retenção e arquivo mensal | Accepted |
| [ADR-023](#adr-023--validação-contínua-de-vulnerabilidades) | Validação contínua de vulnerabilidades | Proposed |
| [ADR-024](#adr-024--deploy-docker-com-volumes-no-host) | Deploy Docker com volumes no host | Proposed |
| [ADR-025](#adr-025--comunidade-visibilidade-e-engajamento) | Comunidade, visibilidade e engajamento | Accepted |
| [ADR-026](#adr-026--identidade-por-url-canônica-e-checkpoint-de-jobs) | Identidade por URL canônica e checkpoint de jobs | Accepted |
| [ADR-027](#adr-027--cicd-ihl-build-once-promote) | CI/CD IHL: build once, promote | Proposed |
| [ADR-028](#adr-028--semver-rc-e-prereleases-de-artefato) | SemVer + RC/dev prereleases de artefato | Proposed |
| [ADR-029](#adr-029--ambiente-como-desired-state) | Ambiente como desired state (sem env branches) | Proposed |
| [ADR-030](#adr-030--ghcr-e-identidade-por-digest) | GHCR e identidade por digest | Proposed |
| [ADR-031](#adr-031--homologação-em-mac-srv-01) | Homologação em mac-srv-01 (runner self-hosted) | Proposed |
| [ADR-032](#adr-032--dev-compose-prod-adiado-gitops-ready) | DEV Compose; PROD adiado; GitOps-ready | Proposed |
| [ADR-033](#adr-033--artefato-público-promote-privado-media-hub-ops) | Artefato público / promote privado (`media-hub-ops`) | Accepted |

Documentação operacional (comunidade): [CICD.md](CICD.md).  
Open core / multi-repo: [OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md).

---

## ADR-001 — Monólito local com jobs em memória

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-001

### Contexto

A primeira entrega (v0.1) precisava validar fluxo de aquisição e UX rapidamente,
sem infraestrutura distribuída.

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
download de vídeo completo, autenticação e cookies ficam fora do escopo da v0.1.

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

A v0.1 exige STT local, sem depender de APIs pagas na primeira entrega.

### Decisão

Usar `faster-whisper` em CPU com `compute_type=int8`. Modelos permitidos: `tiny`,
`base`, `small`. Idiomas: autodetect, `pt`, `en`, `es`.

### Consequências

- Zero custo de API no caminho feliz da v0.1.
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

Content Intelligence é camada posterior e opcional no pipeline. A v0.1 entrega
apenas artefatos de aquisição/transcrição. Integrações (ex.: Video Lab) consomem
saídas normalizadas, não o downloader.

### Consequências

- Media Hub permanece reutilizável por vários produtos.
- EPIC-001 não inclui resumo, classificação ou embeddings.
- Video Lab Integration (EPIC-018) depende de artefatos estáveis + Intelligence.

---

## ADR-010 — Content Registry e deduplicação

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-003; revisado por EPIC-039

### Contexto

Reprocessar o mesmo vídeo gera custo de rede, CPU e disco desnecessários.

### Decisão

Introduzir Content Registry (inicialmente `registry.jsonl`) consultado antes de
qualquer download. Hashes auxiliares: `audio_hash`, `transcript_hash`.
Reprocessar só com `force=true`.

**Identidade (desde EPIC-039 / ADR-026):** `SHA256(canonical_youtube_url)` —
URLs equivalentes (`youtu.be` / `watch?v=` / `shorts`) colapsam na mesma chave.
A forma antiga `platform:video_id` permanece legível para migração.

### Consequências

- Cache semântico de conteúdos entre jobs.
- Substituição futura por PostgreSQL (ADR-012 / EPIC-016).
- Implementado na v0.2: `registry.jsonl`; v0.2.1: checkpoint/retomada (ADR-026).

---

## ADR-011 — Storage filesystem-first

**Status:** Accepted (diretriz de produto)  
**Data:** 2026-08-06  
**Épico:** EPIC-001 (fato); EPIC-004 (abstração)

### Contexto

Object storage adiciona complexidade operacional cedo demais para a v0.1.

### Decisão

Armazenar artefatos no filesystem (`output/{job_id}/`). Quando necessário,
introduzir abstração que permita Filesystem → MinIO → S3 sem mudar regras de
negócio.

### Consequências

- Operação local simples na v0.1.
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

A Foundation nasce com a v0.1, mas interfaces formais (`SourceAdapter`,
`Transcriber`, Storage) só são extraídas quando houver uso imediato (segundo
adapter, segundo engine, segundo backend de storage) ou quando o épico autorizado
exigir a abstração como entrega.

### Consequências

- Código do EPIC-001 permanece direto e testável.
- Diretrizes ADR-007/008/011 orientam o desenho sem forçar classes vazias.
- Refactors de extração são esperados e aceitos nos épicos correspondentes.

---

## ADR-015 — API Key via variável de ambiente

**Status:** Accepted  
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

**Status:** Accepted  
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

**Status:** Accepted  
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

**Status:** Superseded (substituída por Apache-2.0 na v0.2.1 — ver ADR-025)  
**Data:** 2026-08-06  
**Épico:** EPIC-031

### Contexto

O código deveria permanecer público para estudo e contribuição, **sem** autorizar
uso comercial gratuito. Licenças OSI (MIT, Apache, GPL) permitem uso comercial e
não atendiam ao requisito original da v0.1.x.

### Decisão (histórica)

Adotar a **PolyForm Noncommercial License 1.0.0** como licença do repositório
até a v0.2.0.

### Superação

Na v0.2.1 (TASK-038-01 / ADR-025) o projeto migrou para **Apache License 2.0**
para ampliar engajamento open source (forks, awesome lists, uso comercial
compatível com a licença). O DISCLAIMER e a ADR-013 continuam a reger uso de
conteúdos de terceiros.

---

## ADR-019 — Release notes em dois níveis

**Status:** Accepted  
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

---

## ADR-020 — Monorepo modular frontend / BFF / backend

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-034

### Contexto

A v0.1 nasceu com todos os módulos em `app/`. Isso acelerou a entrega, mas misturou
apresentação, borda HTTP e domínio no mesmo pacote, dificultando evolução (CLI,
adapters, workers) sem reorganização posterior.

### Decisão

Manter **um único processo** e um monorepo, separando pastas por camada:

| Camada | Pacote | Papel |
|--------|--------|-------|
| Frontend | `frontend/` | Templates e estáticos |
| BFF | `bff/` | Páginas, `/api/v1`, auth, OpenAPI, factory |
| Backend | `backend/` | Jobs, media, transcription, models, utils |
| App | `app/` | Composition root (`uvicorn app.main:app`) |

Regras de dependência:

- `frontend` não importa `backend` nem `bff`;
- `backend` não importa `bff` nem `frontend`;
- `bff` orquestra HTTP e chama `backend`;
- `app` apenas instancia o BFF.

### Consequências

- Clareza de fronteiras sem custo operacional de microserviços.
- Entrypoint e porta 8010 inalterados (compatível com ADR-001 / ADR-005).
- Extrair processo/serviço real no futuro fica mais barato.
- Não introduz Docker, filas ou frontend SPA nesta etapa.

---

## ADR-021 — Checklist obrigatório ao fechar uma versão

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-030 (processo)  
**Relacionado:** [ADR-017](#adr-017--semver-e-versionamento-do-contrato-da-api),
[ADR-019](#adr-019--release-notes-em-dois-níveis)

### Contexto

ADR-019 define *o quê* publicar (notas de usuário + changelog técnico). Na
prática, releases podem fechar com `__version__` atualizado e um dos artefatos
esquecido (UI desatualizada, links do Keep a Changelog quebrados, badge do
README defasado). Isso gera inconsistência entre `/health`, `/changelog` e o
repositório.

### Decisão

**Toda** versão fechada (tag SemVer / PR de release) deve completar este
checklist antes do merge em `main`:

1. **Versão canônica:** `app/__init__.py` → `__version__ = "X.Y.Z"`.
2. **Changelog técnico:** em `CHANGELOG.md`, mover o conteúdo de `[Unreleased]`
   para uma seção `## [X.Y.Z] - YYYY-MM-DD` (Added / Changed / Fixed /
   Security conforme Keep a Changelog) e atualizar os links de comparação no
   rodapé (`[Unreleased]`, `[X.Y.Z]`, …).
3. **Release notes de usuário:** em `bff/releases.py`, inserir um novo item no
   topo de `USER_RELEASES` com `version`, `date`, `title`, `summary` e
   `highlights` em linguagem simples (sem jargão de ADR/épico).
4. **Superfície pública:** badge de versão no `README.md`; testes que assertam
   a versão na página `/changelog` (se existirem).
5. **Documentação de processo:** se o fluxo de release mudar, atualizar
   `docs/VERSIONING.md` na mesma PR.
6. **Verificação:** `pytest` e `python -m compileall app backend bff frontend`
   (e o CI, quando aplicável).
7. **Após merge:** tag Git `vX.Y.Z` alinhada ao `__version__`.

Não se considera “versão fechada” apenas com bump de número sem os dois níveis
de release notes (ADR-019).

### Consequências

- PRs de release ficam previsíveis e revisáveis.
- `/changelog`, `CHANGELOG.md` e `__version__` permanecem sincronizados.
- Agentes e contribuidores têm um procedimento explícito (também espelhado em
  `docs/VERSIONING.md`).
- Custo pequeno e constante por release; evita retrabalho pós-tag.

---

## ADR-022 — Logging local estilo Java com retenção e arquivo mensal

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-022 (fase 1)  
**Release:** v0.2

### Contexto

A operação local do Media Hub precisa de logs legíveis no console e persistidos
em disco para diagnóstico, sem introduzir stack de observabilidade (métricas,
tracing, dashboards) nesta sprint. O time pediu formato familiar a logs Java
(padrão próximo a Log4j/Logback) e política clara de retenção/arquivo.

### Decisão

1. **Destinos:** handlers de **console** e **arquivo** com o **mesmo** formatter.
2. **Formato estilo Java**, por exemplo:
   `yyyy-MM-dd HH:mm:ss,SSS LEVEL [thread] logger - message`
3. **Diretório:** `logs/` para arquivos ativos; `logs/archive/` para históricos
   compactados (ambos fora do Git).
4. **Retenção:** arquivos de log ativos com idade **> 30 dias** são removidos
   ou incorporados ao arquivo mensal e em seguida removidos.
5. **Arquivo mensal:** compactar histórico elegível em
   `logs/archive/yyyy-mm.tar.gz` (mês civil, ex.: `2026-08.tar.gz`).
6. **Quando arquivar/limpar:** no startup da aplicação e/ou rotina leve
   documentada; sem depender de cron externo na fase 1.
7. **Fora desta ADR:** envio a SaaS, OpenTelemetry, Prometheus, dashboards
   (restante do EPIC-022 / v0.7).

Implementação preferencial: `logging` da stdlib (Formatter customizado +
FileHandler/Rotating ou arquivos diários), sem obrigar Loguru/structlog nesta
fase.

### Consequências

- Diagnóstico local consistente entre terminal e disco.
- Disco controlado pela retenção de 30 dias + `tar.gz` mensal.
- EPIC-022 avança em fatia útil sem antecipar a plataforma de observabilidade.
- Operadores devem garantir espaço em disco em `logs/` e `logs/archive/`.

---

## ADR-023 — Validação contínua de vulnerabilidades

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-035  
**Release:** v0.2.x

### Contexto

O CI da 0.1.2 já executa Bandit, `pip-audit`, Dependency Review e Dependabot.
Antes de Docker e de novos adapters, o produto precisa de uma política explícita
de severidade, checklist de segurança da aplicação e varredura de segredos —
sem transformar o produto local self-hosted em programa de pentest.

### Decisão

1. Manter e endurecer o baseline de CI: falhar o pipeline em vulnerabilidades
   de dependência **High/Critical**, com exceções temporárias documentadas
   (motivo + prazo) quando não houver upgrade viável.
2. Adotar checklist leve de segurança da aplicação (auth API Key, path
   traversal, whitelist de downloads, exposição de `.env`, ausência de
   segredos em logs/UI).
3. Incluir varredura de segredos no fluxo de contribuição/CI.
4. Quando existir imagem Docker (EPIC-036), acrescentar scan de imagem
   (ex.: Trivy) ao build documentado ou ao CI.
5. Continuar proibindo bypass de DRM/auth/geo (ADR-013).

### Consequências

- Segurança deixa de ser só “ferramentas no CI” e passa a ter critérios de aceite.
- Adapters sociais (v0.3) entram sobre uma baseline mais clara.
- Pode atrasar merges se houver CVE High/Critical sem mitigação — risco aceito.

---

## ADR-024 — Deploy Docker com volumes no host

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-036  
**Release:** v0.2.x

### Contexto

Operadores precisam de um caminho de deploy reproduzível sem abandonar o
modelo de monólito local (um processo Uvicorn, jobs em memória). Logs
(ADR-022), artefatos (`output/`) e configuração (`.env`) devem sobreviver ao
ciclo de vida do container.

### Decisão

1. Entregar `Dockerfile` + `docker-compose` (ou equivalente) com um único
   serviço Uvicorn na porta **8010**.
2. Mapear para volumes/arquivos no **host**:
   - configuração / `.env`
   - `logs/` (e `logs/archive/`)
   - `output/`
   - `registry.jsonl` (Content Registry)
3. A imagem não embute segredos; `.dockerignore` exclui dados locais.
4. Jobs em memória permanecem voláteis no restart do container; só disco
   persistido via volumes.
5. Sem Kubernetes, multi-réplica ou workers nesta ADR (EPIC-015+).

### Consequências

- Deploy local/homologação fica previsível e documentável (EPIC-037).
- Dados operacionais ficam no host, facilitando backup e inspeção.
- ADR-001 (jobs em memória) continua válida dentro do container.
- Implementação autorizada na v0.2.x; remove Docker da lista de “fora do
  escopo imediato” ao fechar o épico.
- Demo “one command” alimenta o funil de descoberta do EPIC-038.

---

## ADR-025 — Comunidade, visibilidade e engajamento

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-038  
**Release:** v0.2.1 (fatia 01/02/03/05; PO reautorizou antes de 035–037)

### Contexto

O Media Hub já possui higiene de governança (licença, CONTRIBUTING, badges,
SemVer, CI). O objetivo de produto inclui ganhar **visibilidade e colaboração**
externa nos adapters e demais features. Stars e forks sozinhos não geram PRs;
é necessário narrativa, demo, issues contribuíveis e postura de licença
explícita. A PolyForm Noncommercial (ADR-018) reduzia elegibilidade a algumas
listas “awesome” e adoção comercial.

### Decisão

1. Na **v0.2.1**, executar fatia do **EPIC-038** (tasks 01, 02, 03, 05) em
   paralelo ao **EPIC-039**, **antes** de 035–037 (reautorização explícita do PO).
2. **TASK-038-01:** migrar para **Apache License 2.0** (OSI permissiva) —
   revisa ADR-018.
3. Tratar README + metadados GitHub + demo visual (GIF) como **vitrine**.
4. Publicar contrato de Adapter (`docs/ADAPTERS.md`) antes da v0.3.
5. Tasks 04/06/07/08 e funil completo de issues ficam para follow-up.
6. Sucesso primário: PRs externos / Discussions úteis; stars/forks secundários.

### Consequências

- Maior elegibilidade a awesome lists e forks comerciais.
- DISCLAIMER e ADR-013 continuam obrigatórios em posts públicos.
- EPIC-038 não implementa adapters; apenas prepara o funil.

---

## ADR-026 — Identidade por URL canônica e checkpoint de jobs

**Status:** Accepted  
**Data:** 2026-08-06  
**Épico:** EPIC-039  
**Release:** v0.2.1

### Contexto

O registry da v0.2 só gravava `status=ready` ao final. Jobs interrompidos
(falha, cancelamento, restart do processo) perdiam progresso. A chave
`platform:video_id` não era explicitamente “hash da URL”, requisito de produto
para deduplicar pelo endereço canônico do vídeo.

### Decisão

1. **Identidade:** `content_hash = SHA256(canonical_url)` com
   `canonical_url = https://www.youtube.com/watch?v={id}`.
2. **Artefatos estáveis:** `output/by-content/{content_hash}/`; espelho em
   `output/{job_id}/` para a API de download.
3. **Checkpoint** no `registry.jsonl` após cada etapa:
   `status` ∈ {`in_progress`, `ready`, `failed`, `cancelled`};
   `last_step` ∈ {`metadata`, `download`, `transcribe`, `files`, `done`}.
4. **Retomada:** nova submissão da mesma URL (novo `job_id`) sem `force`
   continua a partir dos artefatos/`last_step` válidos; `force=true` limpa e
   reprocessa.
5. Leituras aceitam entradas legadas `youtube:{id}` quando o `video_id` casa.

### Consequências

- Segunda execução após falha parcial não re-baixa áudio já presente.
- Disco sob `by-content/` cresce com conteúdos distintos (limpeza ainda manual).
- Jobs em memória (ADR-001) permanecem; só o checkpoint é persistente.

---

## ADR-027 — CI/CD IHL: build once, promote

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-040 (com EPIC-036)  
**Release:** v0.2.x  
**Mapa estratégia IHL:** ADR-01 / ADR-02 (build once + artefato imutável)

### Contexto

O Media Hub precisa de maturidade CI/CD para homologar a mesma imagem que o
CI produziu, sem rebuild por ambiente e sem misturar “branches de ambiente”
com o ciclo de produto.

### Decisão

1. **Build once, promote same artifact:** o pipeline de build publica uma
   imagem no GHCR; homolog (e futuro prod) **puxa** essa imagem — não reconstrói
   a partir do Git no ambiente alvo.
2. Artefatos de deploy são **imutáveis**; correções exigem novo build/versão.
3. Workflows: CI de código (`.github/workflows/ci.yml`) separado de
   build/publish (`.github/workflows/build-publish.yml`) neste repo; CD homolog
   vive em `ideiasfactory/media-hub-ops` (ADR-033 / EPIC-041).
4. Estratégia pública em [CICD.md](CICD.md); runbook IHL no ops.

### Consequências

- Homolog depende de Docker packaging (EPIC-036 / ADR-024) e de GHCR.
- Falhas de promote são de pull/config, não de “compila diferente no servidor”.
- Exige disciplina de tags/digests (ADR-028 / ADR-030).

---

## ADR-028 — SemVer + RC/dev prereleases de artefato

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-040  
**Release:** v0.2.x  
**Relacionado:** [ADR-017](#adr-017--semver-e-versionamento-do-contrato-da-api),
[ADR-021](#adr-021--checklist-obrigatório-ao-fechar-uma-versão)  
**Mapa estratégia IHL:** ADR-03 (SemVer + RC)

### Contexto

ADR-017/021 cobrem SemVer do **produto** e checklist de release. Falta política
explícita para **imagens/artefatos** promovíveis (RC vs estável vs dev).

### Decisão

1. Releases estáveis: tags Git `vX.Y.Z` → imagem `ghcr.io/ideiasfactory/media-hub:X.Y.Z`.
2. Release candidates: `vX.Y.Z-rc.N` → imagem `:X.Y.Z-rc.N` (prerelease SemVer).
3. Builds de `main` (não release): tags `sha-<short>` e `dev-<fullsha>` — **não**
   promovem a “versão de produto” sem RC/tag explícita.
4. Homolog promove preferencialmente **RC** (ou digest de um RC); produção futura
   só promove artefato já validado (sem `-rc` / sem `dev-`).
5. Continuar checklist ADR-021 ao fechar `X.Y.Z` estável.

### Consequências

- Operadores distinguem candidato vs estável pela tag.
- `latest` não é identidade de promote (ADR-030).

---

## ADR-029 — Ambiente como desired state

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-040  
**Release:** v0.2.x  
**Mapa estratégia IHL:** ADR-04 / ADR-05 (desired state; sem env branches)

### Contexto

Branches permanentes `homolog`/`production` divergem do `main`, duplicam
hotfixes e quebram a premissa de promote do mesmo artefato.

### Decisão

1. **Não** criar branches de longa duração por ambiente.
2. Desired state versionado sob `deploy/<ambiente>/` (Compose + `versions.yaml`).
3. GitHub Environments (`homolog` agora; `production` futuro) controlam secrets,
   proteção e auditoria de deploy — não o conteúdo do código da app.
4. Mudança de versão em homolog = atualizar pin (tag/digest) + redeploy, via
   workflow ou PR no manifest.

### Consequências

- CD lê manifests do branch/ref do workflow (tipicamente `main` do ops).
- Rollback = redeploy de digest anterior conhecido.
- Desired state de homolog: repo `media-hub-ops` (ADR-033); DEV Compose
  permanece na raiz do open.

---

## ADR-030 — GHCR e identidade por digest

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-040  
**Release:** v0.2.x  
**Mapa estratégia IHL:** ADR-06 / ADR-07 (registry + digest)

### Contexto

Precisamos de um registry alinhado ao GitHub org/repo, com identidade estável
para promote.

### Decisão

1. Registry: **GHCR**.
2. Nome da imagem: **`ghcr.io/ideiasfactory/media-hub`** (owner = org do remote
   `ideiasfactory/media-hub`).
3. **Digest (`@sha256:…`) é a identidade definitiva** em promote homolog/prod.
4. Tags SemVer/RC/sha são conveniência humana e de listagem; o workflow de
   build **não** publica `latest` como tag única de identidade (`latest=false`
   no metadata).
5. Build em runners GitHub-hosted; pull no self-hosted homolog.

### Consequências

- Packages: write no job de publish; read no deploy.
- Operadores devem copiar o digest do summary do build ao promover.

---

## ADR-031 — Homologação em mac-srv-01

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-040  
**Release:** v0.2.x  
**Mapa estratégia IHL:** runner / environment homolog

### Contexto

A homologação da Ideias Factory para este produto roda no host **mac-srv-01**,
com GitHub Actions self-hosted.

### Decisão

1. Deploy homolog **somente** via workflow com
   `runs-on: [self-hosted, mac, homolog]` e `environment: homolog`.
2. Fatos do runner (configurados na org/host, não no YAML além das labels):
   - nome: `mac-srv-01`
   - labels: `mac`, `homolog` (+ `self-hosted`)
   - runner group: `self-hosted-runner-ideias`
   - acesso LAN preferencial: USB Ethernet **`192.168.15.23`** (não o IP Wi‑Fi
     `.21` para clientes da rede)
   - HTTP homolog: porta **8010** → `http://mac-srv-01:8010/health`
3. Pré-requisitos no host: Docker/Compose operacional; diretório de dados com
   volumes (ADR-024); acesso de pull ao GHCR; host acordado (evitar idle sleep
   agressivo — `caffeinate` / `pmset`).
4. Smoke mínimo: `GET /health` após `compose up`.
5. **Localização (ADR-033):** o workflow e manifests de homolog residem no
   repo privado `ideiasfactory/media-hub-ops`, não no open source. Topologia
   detalhada do host fica no runbook do ops.
5. Segredos (ex.: `MEDIA_HUB_API_KEY`) no GitHub Environment `homolog` ou no
   `.env` do host — nunca no Git.

### Consequências

- Se o runner estiver offline, o CD fica queued (runbook em CICD.md).
- Homolog e DEV compartilham o modelo de volumes do EPIC-036.
- Resolução DNS/`/etc/hosts` errada (`.21`) parece “serviço fora” mesmo com
  container healthy no USB LAN.

---

## ADR-032 — DEV Compose; PROD adiado; GitOps-ready

**Status:** Proposed  
**Data:** 2026-08-06  
**Épico:** EPIC-040 (com EPIC-036)  
**Release:** v0.2.x  
**Mapa estratégia IHL:** ADR-08 / ADR-09 / ADR-10 (DEV; PROD híbrido; GitOps)

### Contexto

Precisamos de DEV local previsível e um caminho claro para PROD sem ativá-lo
agora, mantendo a arquitetura preparada para GitOps futuro (K3s).

### Decisão

1. **DEV** = máquina do desenvolvedor com **Docker Compose** na raiz
   (`docker-compose.yml` + `Dockerfile`); venv+uvicorn permanece suportado.
2. **PROD** = **não implementado**; documentar Environment `production` e
   aprovação humana futura; **nenhum** workflow de deploy prod ativo.
3. Arquitetura **GitOps-ready**: desired state em git (Compose hoje);
   evolução futura para K3s/manifests **sem** mudar o princípio build-once /
   digest — só quando autorizado.
4. Promoção futura a prod exige aprovação humana (required reviewers no
   Environment `production`).

### Consequências

- EPIC-036 entrega a base de imagem/volumes; EPIC-040 entrega promote/CD
  (baseline); a **localização** do promote IHL passa a ADR-033 / EPIC-041.
- Evita overengineering (sem K8s na v0.2.x).

---

## ADR-033 — Artefato público / promote privado (`media-hub-ops`)

**Status:** Accepted  
**Data:** 2026-08-07  
**Épico:** EPIC-041 (revisa localização do promote de ADR-027 / 029 / 031)  
**Release:** v0.2.x  
**Doc:** [OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md)

### Contexto

O repositório público misturava **publicação de artefato OSS** (CI, imagem
GHCR) com **CD e topologia IHL** (runner `mac-srv-01`, Environment `homolog`,
desired state de homolog). Isso acopla ops interna a contribuidores externos e
dificulta um futuro produto comercial (SaaS) sem fork divergente do core
Apache-2.0.

### Decisão

1. **Artefato público, promote privado** — `ideiasfactory/media-hub` publica
   a imagem imutável em GHCR; o promote para homolog (e futuros ambientes IHL)
   vive no repo privado `ideiasfactory/media-hub-ops`.
2. **Dependência unidirecional** — ops (e futuro cloud) → core. O core **não**
   depende de ops/SaaS.
3. **Criar `media-hub-ops`** com `deploy-homolog.yml`, `deploy/homolog/`,
   runbook de runner/Environment/secrets. A imagem continua
   `ghcr.io/ideiasfactory/media-hub` (mesmo digest, ADR-027).
4. **Sanitizar docs públicos** — `CICD.md` descreve self-host + publish GHCR;
   detalhe de host IHL fica no ops. Ver [OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md).
5. **Não criar** `media-hub-cloud` nesta decisão; reavaliar quando houver
   multi-tenant/billing.

### Consequências

- Runner self-hosted e GitHub Environment `homolog` devem estar associados ao
  repo (ou org grant) **privado** — passo operacional manual após a migração.
- EPIC-040 permanece a baseline de princípios (build once / digest / desired
  state); EPIC-041 só muda *onde* o CD IHL vive.
- Contribuições OSS não precisam de labels/runner IHL no actionlint do open.
- Produto multi-repo: classificar épicos A/B/C em [EPICS.md](EPICS.md).

---

