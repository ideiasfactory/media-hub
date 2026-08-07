# Open core, ops IHL e produto multi-repo

**Status:** Accepted (EPIC-041 + ADR-033)  
**Data:** 2026-08-07  
**Relacionado:** [CICD.md](CICD.md) · [REPO_SEGMENTATION.md](REPO_SEGMENTATION.md) ·
[EPIC-040](EPICS.md#epic-040--cicd-ihl-homolog-mac-srv-01) ·
[EPIC-041](EPICS.md#epic-041--separação-ops-ihl-do-repositório-open-media-hub-ops) ·
ADR-027–032 · [ADR-033](DECISIONS.md#adr-033--artefato-público-promote-privado-media-hub-ops)

## Contexto

Discussão de produto sobre:

1. Manter o Media Hub **open source** (Apache-2.0) e, no futuro, um **SaaS
   comercial** sem fork divergente permanente.
2. Preocupação: o repo público incluía **CD de Release Candidates para homolog
   IHL**, misturando artefato open com ops interna.
3. Como continuar o modelo de maturidade (épicos, ADRs, monorepo modular)
   quando o produto passar a ter **mais de um repositório**.

## Conclusões

### Modelo de negócio / código

- Padrão alinhado a Confluent/Elastic (camada comercial sobre núcleo):
  **open core + produto que consome o core**, não dois forks espelhados.
- Dependência **unidirecional**: ops/cloud → core. O core nunca depende do SaaS.
- Fluxo de features: genéricas sobem para o OSS; billing, multi-tenant, CD IHL
  e segredos de ambiente ficam no lado privado.
- Com Apache-2.0, publicar a imagem no GHCR é adequado ao OSS; **proteger o
  negócio** no curto prazo é via produto cloud/ops, não via mudar a licença
  do core (já migrámos PolyForm → Apache de propósito, ADR-025).

### Fronteira OSS vs ops (imediato)

| Fica no `media-hub` (público) | Sai para `media-hub-ops` (privado) |
|-------------------------------|-------------------------------------|
| CI (`ci.yml`) | `deploy-homolog.yml` |
| `Dockerfile` + Compose DEV (self-host) | `deploy/homolog/` |
| `build-publish.yml` → GHCR | Environment `homolog`, secrets, runner labels |
| Docs de self-host / SemVer | Runbook IHL (host, paths, rede) |

Regra: **artefato público, promote privado**. Mantém “build once, promote same
digest” (ADR-027); só muda *onde* vive o promote.

### Multi-repo sem abandonar monorepo

- O **produto open** continua monorepo (`frontend` / `bff` / `backend` / `app`).
- Segundo repo = **ops fino** (manifests + CD), não SaaS.
- Terceiro repo = **`media-hub-cloud`** (privado): skeleton da camada comercial;
  depende do core (imagem/API); **não** contém ops IHL. Ver
  [REPO_SEGMENTATION.md](REPO_SEGMENTATION.md).
- Um **backlog/épicos únicos** no open; código e CI por fronteira.
- Classificar mudanças: **A** só core · **B** só ops/cloud · **C** cross-repo
  (contrato → release core → consume). Ver template em [EPICS.md](EPICS.md).

### Observações

- Homologar a *imagem* OSS no IHL continua válido (dogfooding); o que não deve
  ser público é o pipeline e a topologia interna.
- Evitar: forks espelhados, submodule em `main` sem pin, duplicar lógica do
  core no cloud, épicos cloud que assumem API ainda não publicada.
- EPIC-040 entrega publish GHCR + princípios; EPIC-041 **re-localiza** o
  promote IHL para o repo privado sem descartar o princípio build-once.
- Detalhe IHL em workflows/`CICD.md` públicos era ruído para contribuidores
  e acoplamento ops↔produto.

## Decisão (ADR-033)

1. Criar repo privado `ideiasfactory/media-hub-ops`.
2. Mover para lá deploy homolog + desired state + runner/Environment docs.
3. No público: manter CI + build/publish GHCR + Compose DEV; sanitizar
   `CICD.md` (comunidade = self-host + publish; CD IHL = privado).
4. Template multi-repo (tipos A/B/C) em `EPICS.md`.
5. Repo SaaS `ideiasfactory/media-hub-cloud` **pode** existir como skeleton
   (docs; sem fork do open). Implementação multi-tenant/billing = épicos
   futuros (repo=`cloud`).

## Topologia e DAG

Visão dos 3 repos e tarefas de segmentação:
[REPO_SEGMENTATION.md](REPO_SEGMENTATION.md).
