# Decisões

## ADR-001 — Monólito local com jobs em memória

O MVP usa um único processo FastAPI e tarefas de background nativas. Isso atende ao
escopo sem introduzir banco, broker ou workers antes de haver necessidade comprovada.

## ADR-002 — Dependências pesadas importadas sob demanda

`yt-dlp` e `faster-whisper` são importados apenas no caminho de processamento. Assim,
health check, renderização da UI e testes unitários não carregam modelos ou runtimes
de mídia.

## ADR-003 — Downloads por nomes fixos

Somente quatro nomes exatos são servidos. O caminho final é resolvido e precisa
continuar diretamente dentro da pasta do job, evitando path traversal.

## ADR-004 — Um vídeo por job

O adaptador usa `noplaylist`. Playlists, autenticação, cookies, DRM e contorno de
restrições geográficas ficam explicitamente fora do escopo.
