# AGENTS.md

## Papéis do projeto

- **Chief Architect / Product Owner:** ChatGPT. Define arquitetura, escopo, prioridades, critérios de aceite e revisa as entregas.
- **Implementation Engineer:** Codex. Implementa, executa testes, documenta e abre pull requests.
- **Aprovação e merge:** humano.

## Regras de execução

1. Trabalhar sempre em branch dedicada e abrir PR para `main`.
2. Não fazer push direto em `main`.
3. Não expandir escopo sem autorização explícita.
4. Priorizar entrega funcional e simples sobre abstrações prematuras.
5. Executar testes antes de concluir.
6. Não expor segredos, cookies, credenciais ou dados pessoais.
7. Não implementar mecanismos para contornar DRM, autenticação, restrições territoriais ou controles de acesso.
8. Manter compatibilidade com Python 3.11+.
9. Para o MVP, executar com um único processo Uvicorn e manter jobs em memória.
10. Registrar limitações conhecidas no README e decisões relevantes em `docs/DECISIONS.md`.

## Arquitetura inicial

- FastAPI e Uvicorn.
- UI server-side com HTML, CSS e JavaScript puro.
- yt-dlp e FFmpeg para aquisição e conversão de áudio.
- faster-whisper para transcrição local.
- armazenamento local em `output/{job_id}`.
- sem banco de dados, Redis, Celery, Docker, autenticação ou frontend separado no EPIC-001.

## Comandos obrigatórios antes da entrega

```bash
pytest
python -m compileall app
```

Quando o ambiente possuir FFmpeg e acesso à internet, realizar também um smoke test manual com vídeo público curto e autorizado.
