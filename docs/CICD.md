# Estratégia CI/CD IHL — Media Hub

Documento de baseline operacional para **DEV → HOMOLOG** (promote imutável).
PROD é futuro e **não** possui pipeline ativo neste repositório.

Relacionado: [EPIC-040](EPICS.md#epic-040--cicd-ihl-homolog-mac-srv-01) ·
[ADR-027+](DECISIONS.md) · [EPIC-036](EPICS.md#epic-036--deploy-docker-com-volumes-no-host) ·
[VERSIONING.md](VERSIONING.md)

---

## Princípios

1. **Build once, promote same artifact** — a imagem promovida a homolog é a
   mesma binária (digest) produzida no build; não se reconstrói por ambiente.
2. **SemVer + prereleases** — releases: `x.y.z`; candidatos: `x.y.z-rc.N`;
   builds de integração em `main`: tags `sha-<short>` / `dev-<fullsha>`.
3. **Artefatos imutáveis** — tags apontam para digests; **não** usar `latest`
   como identidade única em homolog/prod.
4. **Digest = identidade definitiva** — promoção referencia
   `ghcr.io/ideiasfactory/media-hub@sha256:…`.
5. **Ambiente = desired state** — manifests em `deploy/<env>/` (Compose +
   `versions.yaml`); **sem** branches permanentes `homolog`/`prod`.
6. **Registry** — GitHub Container Registry (GHCR).
7. **Segredos fora do Git** — GitHub Environments / secrets do host; só
   placeholders no repo.
8. **Aprovação humana para produção** (quando existir) — Environment
   `production` com required reviewers; hoje apenas documentado.

---

## Ambientes (realidade atual)

| Ambiente | Onde | Como | Status |
|----------|------|------|--------|
| **DEV** | máquina do desenvolvedor | `docker compose up --build` (raiz) | Ativo |
| **HOMOLOG** | host `mac-srv-01` | Actions self-hosted + `deploy/homolog/` | Ativo (CD) |
| **PROD** | a definir (híbrido futuro) | GitHub Environment `production` stub | **Não ativo** |

### Runner homolog

| Campo | Valor |
|-------|-------|
| Hostname / runner name | `mac-srv-01` |
| Labels | `self-hosted`, `mac`, `homolog` |
| Runner group | `self-hosted-runner-ideias` |
| Workflow | `.github/workflows/deploy-homolog.yml` |
| GitHub Environment | `homolog` |
| Porta HTTP | `8010` (`MEDIA_HUB_PORT`) |
| URL LAN (preferencial) | `http://mac-srv-01:8010/` → USB LAN **`192.168.15.23`** |
| Health | `http://mac-srv-01:8010/health` |

`runs-on: [self-hosted, mac, homolog]` seleciona o nó pelas labels (o nome do
runner e o grupo são configurados na org/GitHub; o workflow não referencia o
grupo diretamente).

**Rede no host:** `mac-srv-01` tem Wi‑Fi (`en0`, tipicamente `192.168.15.21`) e
USB LAN (`en6`, **`192.168.15.23`**). O acesso LAN estável para SSH/HTTP é o
USB LAN. Em clientes IHL, `/etc/hosts` (e SSH `HostName`) devem apontar
`mac-srv-01` para **`192.168.15.23`** — `192.168.15.21` costuma ser
inalcançável a partir de outras máquinas da faixa. mDNS (`mac-srv-01.local`)
pode anunciar o IP Wi‑Fi; prefira o nome curto via hosts ou o IP `.23`.

---

## Imagem GHCR

```
ghcr.io/ideiasfactory/media-hub
```

Escolha alinhada ao remote `ideiasfactory/media-hub` (ADR-030). Exemplos:

```
ghcr.io/ideiasfactory/media-hub:0.2.2-rc.1
ghcr.io/ideiasfactory/media-hub:sha-abc1234
ghcr.io/ideiasfactory/media-hub@sha256:…
```

---

## Fluxo

```text
PR ──► CI (lint/test/security) ──► build image (sem push)
         │
main / tag v* / workflow_dispatch
         │
         ▼
   Build + push GHCR (digest)
         │
         ▼
   workflow_dispatch Deploy homolog
         │
         ▼
   mac-srv-01: compose pull/up + /health
```

1. **CI** — `.github/workflows/ci.yml` (Ruff, Bandit, pip-audit, pytest).
2. **Build/publish** — `.github/workflows/build-publish.yml` → GHCR.
3. **Homolog** — `.github/workflows/deploy-homolog.yml` promove a ref/digest
   escolhida; atualiza desired state em `~/media-hub-homolog` no host.

---

## Desired state (homolog)

```
deploy/homolog/
  docker-compose.yml   # serviço único, volumes no host
  versions.yaml        # pin de tag/digest (metadado)
  .env.example         # sem segredos reais
```

No runner, o workflow materializa em
`${MEDIA_HUB_HOMOLOG_DATA_DIR:-$HOME/media-hub-homolog}`:

- `.env`, `logs/`, `output/`, `registry.jsonl`
- `docker-compose.yml` + `versions.yaml` atualizados no deploy

Alinhado a EPIC-036 / ADR-024 (volumes de config, logs, output, registry).

---

## DEV local

```bash
cp .env.example .env
mkdir -p logs output
touch registry.jsonl
docker compose up --build
curl -fsS http://127.0.0.1:8010/health
```

Sem Docker: continue com venv + `uvicorn app.main:app --port 8010` (README).

---

## GitHub Environments

### `homolog` (obrigatório agora)

1. Repo → **Settings → Environments → New environment** → nome `homolog`
   (já pode existir via API/`gh`).
2. Opcional: secret `MEDIA_HUB_API_KEY`; variable `MEDIA_HUB_PORT` (default `8010`).
3. Sem required reviewers no MVP de homolog (pode endurecer depois).
4. Deployment branches: qualquer branch ou só `main`/tags — preferir `main` +
   `workflow_dispatch` controlado.

### `production` (futuro — não ativar deploy)

Criar o Environment `production` só quando houver host/prod e ADR de promoção.
Configurar **required reviewers**. Não há workflow de deploy prod neste repo.

---

## Secrets e permissões

| Nome | Onde | Uso |
|------|------|-----|
| `GITHUB_TOKEN` | Actions (automático) | push/pull GHCR com `packages: write` / `read` |
| `MEDIA_HUB_API_KEY` | Environment `homolog` (opcional) | API Key da instância homolog |
| `MEDIA_HUB_HOMOLOG_DATA_DIR` | runner env (opcional) | override do diretório de dados |

Pacotes GHCR: garantir que o workflow de build tenha `permissions.packages: write`
e que a política do pacote permita leitura pelo runner homolog (público interno
ou grant ao `GITHUB_TOKEN` do repo).

---

## Runbook — falhas comuns

### Build GHCR falha em permissão

- Conferir `permissions: packages: write` no workflow.
- Em orgs: pacotes podem exigir `GITHUB_TOKEN` com acesso a packages habilitado
  nas settings do repo/org.

### Deploy homolog não aparece em Actions / `gh workflow run` 404

Workflows **somente** `workflow_dispatch` só ficam listados depois de existirem
na branch default (`main`). Até o merge, o job **Validate homolog manifests**
roda em PRs que tocam `deploy/homolog/**`. Após merge em `main`, use:

```bash
gh workflow run deploy-homolog.yml \
  -f image_ref='ghcr.io/ideiasfactory/media-hub@sha256:…'
```

- Runner `mac-srv-01` offline ou sem labels `mac` e `homolog`.
- Confirmar runner group `self-hosted-runner-ideias` e que o repo tem acesso.
- `gh run list --workflow=deploy-homolog.yml` e inspecionar “Waiting for a runner”.

### `docker compose` no Mac

- Docker Desktop (ou engine equivalente) deve estar rodando na sessão do runner.
- Labels do runner não instalam Docker; isso é pré-requisito do host.

### Health check falha

- Porta `MEDIA_HUB_PORT` / variable do Environment.
- Logs: `docker compose logs` no `DATA_DIR` do host.
- Primeira subida pode demorar (deps já na imagem; Whisper baixa modelo no
  primeiro job, não no `/health`).
- Se `curl http://mac-srv-01:8010/health` timeout mas
  `curl http://192.168.15.23:8010/health` OK → corrigir `/etc/hosts` (e cache
  DNS) para `192.168.15.23 mac-srv-01`, não `.21`.
- Se ambos timeout: host pode ter entrado em idle sleep (`pmset sleep` curto).
  Wake-on-LAN (`womp`) no USB LAN (`dc:32:62:56:38:91`); no host, manter
  `caffeinate -dims` (LaunchAgent) ou `sudo pmset -a sleep 0` para papel de
  servidor. Confirmar container: `docker ps --filter name=media-hub`.

### Promover RC

1. Tag `vX.Y.Z-rc.N` (ou `workflow_dispatch` no build).
2. Anotar digest no summary do job Build.
3. `workflow_dispatch` Deploy homolog com
   `ghcr.io/ideiasfactory/media-hub@sha256:…`.

---

## GitOps-ready (sem antecipar K3s)

Hoje: Compose + `versions.yaml` como desired state versionado.

Futuro (fora desta faixa): K3s/manifests, promoção PROD com aprovação humana,
mesma imagem (digest) DEV→HOMOLOG→PROD. Não implementar até autorização explícita.

---

## Fora de escopo (agora)

- Pipeline de produção ativo
- Branches permanentes por ambiente
- Rebuild por ambiente
- Tag `latest` como única referência de promote
- Contornar DRM/auth/geo (ADR-013)
