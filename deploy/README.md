# Deploy (community / self-host)

This public repository ships **DEV** Compose at the repo root
(`docker-compose.yml` + `Dockerfile`).

IHL homolog desired state and CD live in the private repo
`ideiasfactory/media-hub-ops` (EPIC-041 / ADR-033). See
[docs/CICD.md](../docs/CICD.md) and
[docs/OPEN_CORE_AND_OPS.md](../docs/OPEN_CORE_AND_OPS.md).

| Path | Environment | Notes |
|------|-------------|-------|
| `../docker-compose.yml` (repo root) | DEV | Local build + volumes |
| _(ops private)_ | HOMOLOG | Promote from GHCR |
| _(none yet)_ | PROD | Deferred |

Do not store real secrets in git. Use `.env.example` locally.
