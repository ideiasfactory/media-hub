# Versionamento

O Media Hub usa [Semantic Versioning](https://semver.org/lang/pt-BR/):

```
MAJOR.MINOR.PATCH
```

## Produto

- **MAJOR:** mudança incompatível no produto ou no contrato público da API.
- **MINOR:** funcionalidade compatível.
- **PATCH:** correção compatível.

Antes de `1.0.0`, breaking changes ainda podem ocorrer em MINOR, mas devem ser
documentadas explicitamente no [CHANGELOG.md](../CHANGELOG.md).

## Contrato da API

- Path versionado: `/api/v1`, `/api/v2`, …
- Breaking change de contrato → nova versão de path **e** bump MAJOR do app
  (ADR-017).
- Versão atual do app: campo `version` em `GET /health` e em `/openapi.json`.

## Prereleases (artefatos / imagens)

Além das releases estáveis `X.Y.Z`:

- **RC:** tags Git `vX.Y.Z-rc.N` → imagem GHCR `:X.Y.Z-rc.N` (homolog).
- **Dev (`main`):** tags `sha-<short>` / `dev-<fullsha>` — não são versão de produto.

Identidade definitiva de promote: **digest** (`@sha256:…`).  
Detalhes: [CICD.md](CICD.md) · [ADR-028](DECISIONS.md#adr-028--semver-rc-e-prereleases-de-artefato).

## Releases

Checklist obrigatório ao fechar uma versão ([ADR-021](DECISIONS.md#adr-021--checklist-obrigatório-ao-fechar-uma-versão)):

1. Atualizar `app/__init__.py` (`__version__`).
2. Atualizar `CHANGELOG.md` (técnico) — mover itens de `[Unreleased]` para
   `[X.Y.Z]` e ajustar links de comparação.
3. Atualizar `bff/releases.py` (`USER_RELEASES`) com notas amigáveis na UI.
4. Atualizar badge de versão no README.
5. Atualizar testes que fixam a versão na página `/changelog`, se houver.
6. Rodar `pytest` e `python -m compileall app backend bff frontend`.
7. Abrir PR para `main`; após merge, criar tag Git `vX.Y.Z`.

Release notes em dois níveis: [ADR-019](DECISIONS.md#adr-019--release-notes-em-dois-níveis).
