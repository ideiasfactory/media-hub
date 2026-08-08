# Segmentação multi-repo — Media Hub

**Status:** Active (momento de segmentação open / ops / cloud)  
**Data:** 2026-08-07  
**Relacionado:** [OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md) ·
[ADR-033](DECISIONS.md#adr-033--artefato-público-promote-privado-media-hub-ops) ·
[CICD.md](CICD.md)

Documento **público fino**: topologia dos repositórios e DAG deste momento.
Detalhe IHL → `media-hub-ops`. Bootstrap SaaS → `media-hub-cloud`.

---

## Topologia atual (3 repos)

| Repo | Visibilidade | Papel | Depende de |
|------|--------------|-------|------------|
| [`ideiasfactory/media-hub`](https://github.com/ideiasfactory/media-hub) | Público | **Core** open (Apache-2.0): app, CI, Dockerfile, Compose DEV, publish GHCR | — |
| `ideiasfactory/media-hub-ops` | Privado | **Ops IHL**: promote homolog, desired state, runbook | Imagem `ghcr.io/ideiasfactory/media-hub` |
| `ideiasfactory/media-hub-cloud` | Privado | **SaaS** comercial (skeleton): auth cloud, billing, multi-tenant futuros | Core (imagem/API); **não** ops IHL |

**Não renomear** `media-hub` para `-oss` / `-core`.

**Dependência unidirecional:** `ops` → core · `cloud` → core. Core nunca
depende de ops ou cloud. Ops ≠ cloud.

Índice de produto (épicos/roadmap) permanece neste repo open, com marcação
`repo=core|ops|cloud` onde relevante.

---

## DAG — segmentação (este momento)

```text
[Inventory IHL leaks]
        │
        ├──────────────────────┐
        ▼                      ▼
[Copy IHL detail → ops]   [Sanitize open ADRs/docs]
        │                      │
        └──────────┬───────────┘
                   │
                   ▼
         [Cross-links READMEs]
                   │
                   ▼
              [PRs open + ops]

[Create media-hub-cloud skeleton]  ── paralelo após inventory ──► [Cross-links]
[Update OPEN_CORE / ROADMAP]      ── com sanitize ─────────────►
```

| Aresta | Serial / paralelo | Notas |
|--------|-------------------|--------|
| Inventory → copy + sanitize | Serial (copy antes de apagar do open) | Conteúdo IHL já no ops runbook; open só sanitiza |
| Cloud create ∥ ops enrich ∥ open branch | Paralelo | Após inventory |
| Cross-links → PRs | Serial | Docs consistentes antes do PR |

---

## Feito neste momento (docs)

- Sanitizar ADRs públicos (031 sem topologia; 029/032/024/033 alinhados)
- `OPEN_CORE_AND_OPS.md` + este ponteiro
- Skeleton `media-hub-cloud`
- Ops README / DAG de follow-ups IHL

## Follow-ups (humano / paralelo)

| # | Task | Repo | Bloqueio |
|---|------|------|----------|
| 1 | Re-registar runner / Environment `homolog` no ops | ops | Org/host |
| 2 | Permissões GHCR package read para ops (e depois cloud) | org | Admin |
| 3 | Validar promote E2E homolog | ops | 1+2 |
| 4 | Checklist residual EPIC-041 (ops) | ops | 3 |
| 5 | Primeiro épico cloud (app skeleton) | cloud | PO |
| 6 | Clones locais / workspaces Cursor | local | Dev |

Detalhe operacional: runbook no `media-hub-ops`. Roadmap cloud: docs do
`media-hub-cloud`.
