# CI/CD — Media Hub (repositório público)

Baseline para **contribuidores e self-host**: CI, build da imagem e publicação
no GHCR. **Promote para homolog IHL** não vive neste repositório — ver
`ideiasfactory/media-hub-ops` (privado) e
[OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md) ·
[ADR-033](DECISIONS.md#adr-033--artefato-público-promote-privado-media-hub-ops).

Relacionado: [EPIC-040](EPICS.md#epic-040--cicd-ihl-homolog-mac-srv-01) ·
[EPIC-041](EPICS.md#epic-041--separação-ops-ihl-do-repositório-open-media-hub-ops) ·
[ADR-027+](DECISIONS.md) · [EPIC-036](EPICS.md#epic-036--deploy-docker-com-volumes-no-host) ·
[VERSIONING.md](VERSIONING.md)

---

## Princípios

1. **Build once, promote same artifact** — a imagem promovida a um ambiente é a
   mesma binária (digest) produzida no build; não se reconstrói por ambiente
   (ADR-027). O *promote* IHL ocorre no repo ops privado.
2. **SemVer + prereleases** — releases: `x.y.z`; candidatos: `x.y.z-rc.N`;
   builds de integração em `main`: tags `sha-<short>` / `dev-<fullsha>`.
3. **Artefatos imutáveis** — tags apontam para digests; **não** usar `latest`
   como identidade única em homolog/prod.
4. **Digest = identidade definitiva** — promoção referencia
   `ghcr.io/ideiasfactory/media-hub@sha256:…`.
5. **Registry** — GitHub Container Registry (GHCR).
6. **Segredos fora do Git** — só placeholders no repo; secrets no host / Environments.
7. **Aprovação humana para produção** (quando existir) — fora deste repo open.

---

## O que este repo faz

| Peça | Caminho | Papel |
|------|---------|--------|
| CI | `.github/workflows/ci.yml` | Ruff, Bandit, pip-audit, pytest |
| Build/publish | `.github/workflows/build-publish.yml` | Imagem → GHCR |
| DEV Compose | `docker-compose.yml` (raiz) | Self-host local |
| Dockerfile | `Dockerfile` | Imagem da aplicação |

| Peça | Onde |
|------|------|
| Deploy homolog (`deploy-homolog.yml`) | `ideiasfactory/media-hub-ops` (privado) |
| Desired state `deploy/homolog/` | idem |
| Runbook runner / Environment `homolog` | idem |

Regra: **artefato público, promote privado**.

---

## Ambientes (visão de produto)

| Ambiente | Onde | Como | Status |
|----------|------|------|--------|
| **DEV** | máquina do desenvolvedor | `docker compose up --build` (raiz) | Ativo (este repo) |
| **HOMOLOG** | infra IHL | promote no repo **ops** privado | Ativo (ops) |
| **PROD** | a definir | GitHub Environment `production` stub | **Não ativo** |

Detalhe de host, labels de runner e secrets de homolog **não** são
documentados aqui (ops interno).

---

## Imagem GHCR

```
ghcr.io/ideiasfactory/media-hub
```

Exemplos:

```
ghcr.io/ideiasfactory/media-hub:0.2.2-rc.1
ghcr.io/ideiasfactory/media-hub:sha-abc1234
ghcr.io/ideiasfactory/media-hub@sha256:…
```

---

## Fluxo (open)

```text
PR ──► CI (lint/test/security) ──► build image (sem push)
         │
main / tag v* / workflow_dispatch
         │
         ▼
   Build + push GHCR (digest)
         │
         ▼
   [ops privado] promote digest → homolog IHL
```

1. **CI** — `.github/workflows/ci.yml`.
2. **Build/publish** — `.github/workflows/build-publish.yml` → GHCR.
3. **Homolog** — workflow no `media-hub-ops` (não neste repositório).

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

## Promover um digest (operadores IHL)

1. Obter o digest no summary do job **Build** (ou `gh api` / GHCR UI).
2. No repo privado `media-hub-ops`, disparar deploy homolog com
   `ghcr.io/ideiasfactory/media-hub@sha256:…`.
3. Seguir o runbook desse repo (Environment, runner, smoke `/health`).

---

## Secrets e permissões (open)

| Nome | Onde | Uso |
|------|------|-----|
| `GITHUB_TOKEN` | Actions (automático) | push GHCR com `packages: write` |

Pacotes GHCR: garantir `permissions.packages: write` no build e política do
pacote adequada para leitores autorizados (incl. runner do ops).

---

## GitOps-ready (sem antecipar K3s)

Hoje: Compose DEV neste repo; desired state de homolog no ops.

Futuro (fora desta faixa): K3s/manifests, promoção PROD com aprovação humana,
mesma imagem (digest) DEV→HOMOLOG→PROD. Não implementar até autorização explícita.

---

## Fora de escopo (agora)

- Pipeline de produção ativo neste ou no ops
- Branches permanentes por ambiente
- Rebuild por ambiente
- Tag `latest` como única referência de promote
- Contornar DRM/auth/geo (ADR-013)
- Documentar topologia interna IHL no repositório público
