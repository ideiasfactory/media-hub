# Deploy (community / self-host)

This public repository ships **DEV** Compose at the repo root
(`docker-compose.yml` + `Dockerfile`).

IHL homolog desired state and CD live in the private repo
`ideiasfactory/media-hub-ops` (EPIC-041 / ADR-033). See
[docs/CICD.md](../docs/CICD.md),
[docs/OPEN_CORE_AND_OPS.md](../docs/OPEN_CORE_AND_OPS.md), and
[docs/REPO_SEGMENTATION.md](../docs/REPO_SEGMENTATION.md).

| Path | Environment | Notes |
|------|-------------|-------|
| `../docker-compose.yml` (repo root) | DEV | Local build + volumes |
| _(ops private)_ | HOMOLOG | Promote from GHCR |
| _(none yet)_ | PROD | Deferred |

Do not store real secrets in git. Use `.env.example` locally.

### Whisper: CPU vs CUDA

Dual mode — see `.env.example` and
[ADR-034](../docs/DECISIONS.md#adr-034--faster-whisper-device-opcional-via-env-cuda).

| Mode | Env | Notes |
|------|-----|-------|
| CPU (default) | unset / `MEDIA_HUB_WHISPER_DEVICE=cpu` | Safe; DEV Compose + `./Dockerfile` (GHCR) |
| CUDA (opt-in) | `MEDIA_HUB_WHISPER_DEVICE=cuda` | Needs `nvidia-smi` + Docker `--gpus`; STT conc=1; if CUDA unavailable → **CPU + warning** (not silent) |

**GPU image / Compose (opt-in, P1-03):**

```bash
docker compose -f docker-compose.yml -f docker-compose.cuda.yml up --build -d
```

- `Dockerfile.cuda` — NVIDIA CUDA 12 + cuDNN runtime base (not the GHCR default).
- Default `Dockerfile` / GHCR publish stays **CPU-only** so CI and Air hosts stay lean.
- Build the CUDA image on a GPU host (or CI with Buildx + NVIDIA); pin/tag yourself
  when promoting (ops/cloud).

GPU worker bind-mounts (ops/cloud) should use a native Linux filesystem path
(e.g. `$HOME/ihl/{project}/…` on WSL2), not `/mnt/c/...`.
