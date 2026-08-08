# Contribuindo com o Media Hub

Obrigado por contribuir. Este guia resume o fluxo esperado para humanos e agentes.

## Antes de começar

1. Leia [README.md](README.md) e [AGENTS.md](AGENTS.md).
2. Alinhe-se à **arquitetura** e ao **roadmap** do produto (obrigatório antes de
   propor features ou adapters):
   - [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — monorepo `frontend` / `bff` /
     `backend`, jobs, registry, limites do produto local;
   - [docs/ROADMAP.md](docs/ROADMAP.md) — releases e prioridade de execução
     autorizada pelo Product Owner;
   - [docs/EPICS.md](docs/EPICS.md) — catálogo de épicos (o que está aberto,
     concluído ou fora de escopo);
   - [docs/DECISIONS.md](docs/DECISIONS.md) — ADRs (decisões que não devem ser
     reabertas sem revisão explícita).
3. Confirme que o trabalho está autorizado por um épico aberto — não expanda
   escopo além do roadmap vigente.
4. Use apenas conteúdo público/autorizado; não implemente bypass de DRM, login,
   cookies de plataforma ou restrições geográficas ([ADR-013](docs/DECISIONS.md)).

Índice completo da documentação: [docs/README.md](docs/README.md).
Propor novo adapter: [docs/ADAPTERS.md](docs/ADAPTERS.md).

## Setup local

```bash
git clone https://github.com/ideiasfactory/media-hub.git
cd media-hub
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Opcional: defina `MEDIA_HUB_API_KEY` no `.env` para testar a proteção da API.

## Branch e PR

1. Crie uma branch dedicada a partir de `main` (`feature/...` ou `release/...`).
2. Faça commits pequenos e descritivos.
3. Abra PR para `main` — nunca faça push direto em `main`.
4. Descreva o épico relacionado (ver [EPICS.md](docs/EPICS.md)), o impacto e o
   plano de teste; cite ADRs afetados quando houver mudança de decisão.

## Checklist obrigatório

```bash
pytest
python -m compileall app backend bff frontend
```

Recomendado antes do PR (alinhado ao CI):

```bash
python -m pip install -r requirements-dev.txt
ruff check app backend bff frontend tests
ruff format --check app backend bff frontend tests
bandit -r app backend bff -ll -c pyproject.toml
pip-audit
```

Quando houver FFmpeg e rede, faça smoke test com vídeo público curto autorizado.

## Padrões

- Python 3.11+.
- Simplicidade primeiro; abstrações só com uso imediato ([ADR-014](docs/DECISIONS.md)).
- Respeite a arquitetura descrita em [ARCHITECTURE.md](docs/ARCHITECTURE.md)
  (um processo Uvicorn; jobs em memória na arquitetura atual; sem antecipar
  DB/Redis/Docker sem épico autorizado).
- Trabalhe na ordem do [ROADMAP.md](docs/ROADMAP.md); não puxe épicos futuros
  sem reautorização.
- Atualize README/limitações e ADRs quando a decisão mudar.
- Marque status do épico em `docs/ROADMAP.md` e `docs/EPICS.md`.
- Não commit `.env`, segredos, cookies ou dados pessoais.
- Licença do projeto: Apache License 2.0 — contribuições sob os mesmos termos.

## API e versionamento

- Contrato atual: `/api/v1`.
- Breaking change de contrato exige nova versão de path (`/api/v2`) e bump MAJOR
  (ou política pré-1.0 documentada no CHANGELOG).
- Documentação interativa: `/docs`.
- Política de release: [docs/VERSIONING.md](docs/VERSIONING.md) e ADR-021.

## Dúvidas

Abra uma issue com o template adequado ou discuta no PR antes de grandes mudanças.
