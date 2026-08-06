# Arquitetura

## Visão geral

O Media Hub v0.1 é uma aplicação monolítica local. O FastAPI serve a página Jinja2,
a API JSON e os artefatos. O navegador cria um job e consulta seu estado por polling.

## Fluxo

1. `POST /api/jobs` valida a URL, o modelo e o idioma e retorna um UUID.
2. Uma tarefa de background do FastAPI atualiza o job mantido em memória.
3. `yt-dlp` obtém metadados e baixa somente o melhor áudio disponível.
4. O pós-processador do `yt-dlp` usa FFmpeg para gerar `audio.mp3`.
5. `faster-whisper`, em CPU com `compute_type="int8"`, gera segmentos e idioma.
6. A aplicação grava TXT, SRT e JSON em `output/{job_id}`.
7. A UI exibe o resultado e oferece downloads por uma whitelist fixa.

## Componentes

- `main.py`: aplicação, templates, arquivos estáticos e health check.
- `api.py`: criação, consulta e downloads de jobs.
- `jobs.py`: estado em memória e orquestração do processamento.
- `media.py`: integração mínima com yt-dlp/FFmpeg.
- `transcription.py`: integração mínima com faster-whisper.
- `utils.py`: validação de URL, segurança de arquivos e SRT.

## Restrições operacionais

A aplicação deve usar um único processo Uvicorn. Reiniciar o processo perde o estado
dos jobs, embora arquivos já gerados permaneçam no disco. Não há fila persistente,
controle de concorrência ou isolamento multiusuário nesta versão.
