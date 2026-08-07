# Source Adapters — contribution contract

How to propose a new media source (Instagram, TikTok, …) **without**
implementing it in this document. Aligns with [ADR-007](DECISIONS.md),
[ADR-013](DECISIONS.md), and [ADR-014](DECISIONS.md).

Portuguese summary: use this checklist when opening a **New Adapter** issue or
PR. Do not bypass DRM, login, cookies, or geo restrictions.

## Where it plugs in

Today the YouTube path lives in `backend/media.py` + `backend/jobs.py` (single
process). A future `SourceAdapter` interface (when a second platform lands) should
expose roughly:

| Concern | Responsibility |
|---------|----------------|
| URL validation | Accept only public, authorized URLs for that platform |
| Identity | Stable id / canonical URL for the Content Registry |
| Metadata | Title, channel/author, duration when available |
| Audio (or media) fetch | Produce a local file under the job/content directory |
| Errors | Map platform failures to clear user-facing messages |

Do **not** extract the interface “just for the community” without a second real
consumer ([ADR-014](DECISIONS.md)).

## Minimum acceptance criteria

1. **Public content only** — no login, cookies, DRM, or geo bypass ([ADR-013](DECISIONS.md)).
2. **Tests** — offline unit tests with fixtures/mocks; no live scraping in CI.
3. **Registry** — reuse `content_hash` / checkpoint rules ([ADR-026](DECISIONS.md)).
4. **Docs** — update README adapter matrix, `EPICS.md`, and limitations.
5. **Disclaimer** — keep UI/API warnings; never suggest illegal redistribution.
6. **Scope** — one platform per PR; match the authorized epic (EPIC-005+).

## Suggested issue / PR checklist

- [ ] Epic id (e.g. EPIC-005 Instagram)
- [ ] Sample **public** URLs for manual smoke tests
- [ ] URL patterns accepted / rejected
- [ ] Artifacts produced (audio, transcript, metadata)
- [ ] Failure modes documented
- [ ] No secrets committed

## References

- Roadmap / status: [ROADMAP.md](ROADMAP.md)
- Epic catalog: [EPICS.md](EPICS.md)
- Architecture target: [ARCHITECTURE.md](ARCHITECTURE.md)
- Contributing: [../CONTRIBUTING.md](../CONTRIBUTING.md)
