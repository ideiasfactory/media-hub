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

## Releases

1. Atualizar `app/__init__.py` (`__version__`).
2. Atualizar `CHANGELOG.md` (técnico) e `app/releases.py` (usuário).
3. Atualizar badge de versão no README.
4. Tag Git `vX.Y.Z` após merge em `main`.
