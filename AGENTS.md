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
11. Manter `docs/ROADMAP.md`, `docs/EPICS.md` e `docs/ARCHITECTURE.md` alinhados ao escopo autorizado; não implementar épicos futuros sem aprovação explícita.
12. Após o fechamento da v0.2 / v0.2.1, a próxima faixa autorizada é **v0.2.x**:
    EPIC-035 (segurança) → EPIC-036 (Docker com volumes) → EPIC-037 (docs) →
    EPIC-038 restante. Não antecipar adapters sociais (v0.3) sem concluir ou
    reautorizar essa ordem. (A fatia 038 + EPIC-039 na 0.2.1 foi reautorizada.)

## Arquitetura inicial

Monorepo modular em um único processo Uvicorn:

- `frontend/` — HTML/CSS/JS (Jinja2 + static);
- `bff/` — páginas, API `/api/v1`, auth, OpenAPI;
- `backend/` — jobs, yt-dlp/FFmpeg, faster-whisper, models/utils;
- `app/` — composition root (`uvicorn app.main:app`);
- armazenamento local em `output/{job_id}`;
- sem banco de dados, Redis, Celery, Docker ou frontend SPA no EPIC-001 / 0.1.x.
  Docker com volumes no host entra na faixa **v0.2.x** (EPIC-036), após hardening
  de segurança (EPIC-035).

## Comandos obrigatórios antes da entrega

```bash
pytest
python -m compileall app backend bff frontend
```

Quando o ambiente possuir FFmpeg e acesso à internet, realizar também um smoke test manual com vídeo público curto e autorizado.
