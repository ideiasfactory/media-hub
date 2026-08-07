# Deploy manifests

Desired-state layouts per environment (ADR-029 / EPIC-040).

| Path | Environment | Notes |
|------|-------------|-------|
| `../docker-compose.yml` (repo root) | DEV | Local build + volumes |
| `homolog/` | HOMOLOG | Promote from GHCR on `mac-srv-01` |
| _(none yet)_ | PROD | Deferred — see [docs/CICD.md](../docs/CICD.md) |

Do not store real secrets here. Use `.env.example` and GitHub Environment secrets.
