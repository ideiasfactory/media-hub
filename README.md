# Media Hub

[![Version](https://img.shields.io/badge/version-0.1.2-blue.svg)](CHANGELOG.md)
[![CI](https://github.com/ideiasfactory/media-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/ideiasfactory/media-hub/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: PolyForm Noncommercial](https://img.shields.io/badge/license-PolyForm%20Noncommercial-lightgrey.svg)](LICENSE)
[![API](https://img.shields.io/badge/API-/api/v1-orange.svg)](http://localhost:8010/docs)
[![Docs](https://img.shields.io/badge/docs-roadmap%20%7C%20ADRs-informational.svg)](docs/README.md)

MVP web local para baixar o áudio de um vídeo público do YouTube, transcrevê-lo com
Whisper e disponibilizar MP3, TXT, SRT e metadados JSON.

Monorepo modular (um processo): `frontend/` · `bff/` · `backend/` · `app/`.

| | |
|---|---|
| Interface | [http://localhost:8010](http://localhost:8010) |
| Novidades (usuário) | [http://localhost:8010/changelog](http://localhost:8010/changelog) |
| Swagger | [http://localhost:8010/docs](http://localhost:8010/docs) |
| Changelog técnico | [CHANGELOG.md](CHANGELOG.md) |
| Produto / ADRs | [docs/](docs/README.md) |

## Requisitos

- Python 3.11 ou superior;
- FFmpeg disponível no `PATH`;
- acesso à internet para o processamento de vídeos e para baixar o modelo Whisper
  na primeira utilização;
- CPU com espaço em disco e memória compatíveis com o modelo escolhido.

### Instalar o FFmpeg

macOS com Homebrew:

```bash
brew install ffmpeg
```

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```

Confirme com:

```bash
ffmpeg -version
```

## Instalação

```bash
git clone https://github.com/ideiasfactory/media-hub.git
cd media-hub
git switch main
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Opcional — proteja a API definindo no `.env`:

```bash
MEDIA_HUB_API_KEY=troque-esta-chave
```

## Execução

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

Acesse [http://localhost:8010](http://localhost:8010), cole a URL de um vídeo
público individual, escolha modelo e idioma e clique em **Baixar e Transcrever**.

## API

Contrato atual: **`/api/v1`** (SemVer do app em `/health` → campo `version`).

- `GET /`: interface web;
- `GET /changelog`: novidades amigáveis;
- `GET /health`: health check + versão;
- `GET /docs`: Swagger UI;
- `GET /redoc`: ReDoc;
- `POST /api/v1/jobs`: cria um job;
- `GET /api/v1/jobs/{job_id}`: consulta status e resultado;
- `GET /api/v1/jobs/{job_id}/files/{filename}`: baixa um artefato permitido.

Quando `MEDIA_HUB_API_KEY` estiver definido, envie o header `X-API-Key` (ou
`Authorization: Bearer <key>`). A UI same-origin usa cookie HttpOnly automaticamente.

Exemplo:

```bash
curl -X POST http://localhost:8010/api/v1/jobs \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: troque-esta-chave' \
  -d '{"url":"https://www.youtube.com/watch?v=VIDEO_ID","model":"base","language":"autodetect"}'
```

Breaking changes de contrato usam novo path (`/api/v2`) — ver [ADR-017](docs/DECISIONS.md).

## Testes

Os testes unitários não acessam a internet nem carregam modelos Whisper.

```bash
pytest
python -m compileall app backend bff frontend
```

Para lint e segurança (mesmo conjunto do CI):

```bash
python -m pip install -r requirements-dev.txt
ruff check app backend bff frontend tests
ruff format --check app backend bff frontend tests
bandit -r app backend bff -ll -c pyproject.toml
pip-audit
```

O pipeline GitHub Actions (`.github/workflows/ci.yml`) executa lint, Bandit,
`pip-audit`, Dependency Review (em PRs) e testes em Python 3.11/3.12.
## Arquivos gerados

Cada job usa `output/{job_id}/` e pode produzir:

- `audio.mp3`;
- `transcript.txt`;
- `transcript.srt`;
- `metadata.json`.

## Limitações conhecidas

- jobs existem somente em memória e são perdidos ao reiniciar a aplicação;
- execute exatamente um processo Uvicorn; múltiplos workers não compartilham jobs;
- arquivos antigos não são limpos automaticamente;
- o processamento concorre pelos recursos locais e não possui fila ou limite;
- modelos são baixados pelo `faster-whisper` na primeira utilização;
- vídeos indisponíveis, privados, com restrições ou alterações do YouTube podem falhar;
- somente vídeos individuais do YouTube são aceitos; playlists estão fora do escopo;
- a qualidade e a velocidade variam conforme áudio, idioma, CPU e modelo;
- com API Key ativa, o cookie HttpOnly da UI é adequado ao uso local single-tenant.

## Troubleshooting

- **FFmpeg não encontrado:** instale-o e confirme `ffmpeg -version`.
- **Modelo demora na primeira execução:** aguarde o download inicial e verifique
  conexão e espaço em disco.
- **Vídeo não processa:** confirme que a URL é pública, individual e acessível sem
  login. Atualizações do `yt-dlp` podem ser necessárias quando o YouTube muda.
- **Job desapareceu:** reiniciar o Uvicorn limpa o estado em memória; crie novo job.
- **Processamento muito lento:** use o modelo `tiny`; `small` exige mais CPU e memória.
- **401 na API:** defina/envie `MEDIA_HUB_API_KEY` ou deixe a variável vazia no `.env`
  para modo aberto local.

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) e o [Código de Conduta](CODE_OF_CONDUCT.md).

## Licença

Distribuído sob a [PolyForm Noncommercial License 1.0.0](LICENSE).

- Uso, estudo e contribuição **não comerciais** são permitidos.
- **Uso comercial** exige licença/acordo separado com a Ideias Factory.
- Isto é software **source-available**, não OSI “Open Source” (a restrição
  comercial é intencional).

## Uso responsável

Utilize somente conteúdo próprio, autorizado ou cujo processamento seja permitido
pela legislação e pelos termos aplicáveis. É proibido qualquer uso ilegal —
incluindo exploração ou abuso sexual de crianças e adolescentes e demais crimes
listados no disclaimer. O projeto não contorna DRM, autenticação, restrições
territoriais ou outros controles de acesso e não usa cookies ou credenciais de
plataformas de mídia.

Leia a [Isenção de Responsabilidade](DISCLAIMER.md) (direitos autorais, usos
ilegais proibidos e limitação de responsabilidade) e a
[Política de Privacidade](PRIVACY.md) (como tratamos dados na instância local).
