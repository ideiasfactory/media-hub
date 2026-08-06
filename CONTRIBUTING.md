# Contribuindo com o Media Hub

Obrigado por contribuir. Este guia resume o fluxo esperado para humanos e agentes.

## Antes de começar

1. Leia [README.md](README.md), [AGENTS.md](AGENTS.md) e [docs/ROADMAP.md](docs/ROADMAP.md).
2. Confirme que o trabalho está autorizado por um épico aberto — não expanda escopo.
3. Use apenas conteúdo público/autorizado; não implemente bypass de DRM, login,
   cookies de plataforma ou restrições geográficas.

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
4. Descreva o épico relacionado, o impacto e o plano de teste.

## Checklist obrigatório

```bash
pytest
python -m compileall app
```

Quando houver FFmpeg e rede, faça smoke test com vídeo público curto autorizado.

## Padrões

- Python 3.11+.
- Simplicidade primeiro; abstrações só com uso imediato ([ADR-014](docs/DECISIONS.md)).
- Atualize README/limitações e ADRs quando a decisão mudar.
- Marque status do épico em `docs/ROADMAP.md` e `docs/EPICS.md`.
- Não commit `.env`, segredos, cookies ou dados pessoais.
- Licença do projeto: PolyForm Noncommercial 1.0.0 — contribuições sob os mesmos termos.

## API e versionamento

- Contrato atual: `/api/v1`.
- Breaking change de contrato exige nova versão de path (`/api/v2`) e bump MAJOR
  (ou política pré-1.0 documentada no CHANGELOG).
- Documentação interativa: `/docs`.

## Dúvidas

Abra uma issue com o template adequado ou discuta no PR antes de grandes mudanças.
