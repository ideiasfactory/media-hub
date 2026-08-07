# Política de Privacidade

**Última atualização:** 6 de agosto de 2026  
**Software:** Media Hub (Ideias Factory)

Esta política descreve como o Media Hub trata dados quando você instala e
executa o software. Complementa o [README](README.md), a
[Isenção de Responsabilidade](DISCLAIMER.md) e a [licença](LICENSE).

Em caso de conflito com a lei aplicável (incluindo a LGPD no Brasil), prevalece
a lei.

---

## 1. Resumo

O Media Hub é um aplicativo **local, single-tenant**. Na versão atual (v0.2.x):

- **não** cria contas de usuário;
- **não** envia áudio ou transcrições para serviços de nuvem de STT;
- **não** inclui telemetria, analytics ou rastreamento publicitário;
- processa o que **você** solicita no computador (ou servidor) onde o processo
  Uvicorn está rodando;
- grava artefatos em disco local (`output/`) e mantém o estado dos jobs **em
  memória** até o reinício do processo.

Quem opera a instância (você ou sua organização) é, em regra, o responsável pelo
tratamento dos dados gerados nessa execução.

---

## 2. Controlador / operador

| Situação | Quem trata os dados |
|----------|---------------------|
| Você executa o Media Hub na sua máquina | Você (operador da instância) |
| Alguém disponibiliza uma instância para terceiros | Quem hospeda/opera essa instância |

A Ideias Factory, como autora do código-fonte público, **não recebe**
automaticamente os dados processados pelas instalações de terceiros. Não há
backend central do produto coletando jobs, URLs ou transcrições.

Se você redistribuir ou hospedar o Media Hub para outras pessoas, você assume as
obrigações de transparência e segurança perante esses usuários.

---

## 3. Quais dados são tratados

### 3.1 Dados que você envia

- URL do vídeo (YouTube, vídeo público individual);
- opções de processamento: modelo Whisper (`tiny` / `base` / `small`) e idioma;
- opcionalmente, a API Key configurada (`MEDIA_HUB_API_KEY`), via header
  `X-API-Key`, `Authorization: Bearer` ou cookie da UI.

### 3.2 Dados obtidos ou gerados no processamento

- metadados públicos do vídeo (ex.: id, título, canal/uploader, duração);
- arquivo de áudio (`audio.mp3`);
- transcrição em texto e legendas temporizadas (`transcript.txt`,
  `transcript.srt`);
- `metadata.json` (inclui `source_url`, modelo, idiomas, carimbo de
  processamento);
- estado do job em memória (`job_id`, status, progresso, mensagem, artefatos).

Áudio e fala transcrita **podem conter dados pessoais** de pessoas que aparecem
ou são mencionadas no conteúdo. Isso depende do vídeo que você processar.

### 3.3 O que não coletamos no código do aplicativo

- cadastro, e-mail, nome ou perfil de usuário final;
- endereço IP armazenado pela aplicação (o servidor HTTP/Uvicorn pode registrar
  access logs no nível do processo/sistema);
- cookies ou credenciais de login do YouTube / plataformas de mídia;
- identificadores publicitários ou pixels de analytics;
- telemetria enviada à Ideias Factory.

---

## 4. Onde os dados ficam armazenados

| Local | Conteúdo | Persistência |
|-------|----------|--------------|
| Memória do processo | Jobs e resultados enquanto o Uvicorn está ativo | Perdidos ao reiniciar |
| `output/{job_id}/` | MP3, TXT, SRT, JSON | Permanecem no disco até exclusão manual |
| `.env` (local) | `MEDIA_HUB_API_KEY` (opcional) | Enquanto o arquivo existir; não versionar |
| Cookie do navegador | `media_hub_api_key` (se a key estiver ativa) | Até 30 dias ou remoção |
| Cache do faster-whisper | Pesos do modelo Whisper | Cache local padrão (Hugging Face), fora de `output/` |

Não há banco de dados, Redis, fila externa nem armazenamento em nuvem no escopo
atual do produto local.

---

## 5. Cookies

Quando `MEDIA_HUB_API_KEY` está definido, a interface web pode gravar o cookie:

- **Nome:** `media_hub_api_key`
- **Finalidade:** autenticar chamadas same-origin da UI à API `/api/v1/*`
- **Atributos:** `HttpOnly`, `SameSite=Lax`, validade aproximada de 30 dias
- **Não é** cookie de rastreamento nem de sessão de plataformas de mídia

Sem API Key configurada, esse cookie não é necessário e a aplicação o remove nas
respostas HTML relevantes.

---

## 6. Compartilhamento com terceiros

O aplicativo **não vende** dados e **não** envia transcrições a APIs de nuvem.

Contatos de rede que ocorrem por natureza da ferramenta:

| Destino | Motivo | O que pode ser transmitido |
|---------|--------|----------------------------|
| YouTube (via `yt-dlp`) | Obter metadados e baixar áudio de URL pública | A URL/requisições de download; sujeito às políticas do YouTube |
| Hugging Face (via `faster-whisper`) | Download do modelo Whisper na primeira uso | Requisição de download dos pesos do modelo |

A transcrição em si roda **localmente** (CPU). Após o download do modelo, o
áudio processado não é enviado a um serviço remoto de speech-to-text pelo código
do Media Hub.

Quem opera a instância deve considerar também logs do sistema operacional,
proxies e firewalls sob seu controle.

---

## 7. Finalidades do tratamento

Os dados são tratados para:

1. executar o job solicitado (download de áudio + transcrição);
2. exibir status e resultados na UI / API;
3. permitir o download dos artefatos gerados;
4. (opcional) proteger a API com chave compartilhada em uso local.

Não há finalidade de marketing, perfilamento comercial ou venda de dados.

---

## 8. Retenção e exclusão

- **Jobs em memória:** sem TTL; somem ao reiniciar o processo.
- **Arquivos em `output/`:** **não** há limpeza automática nem endpoint de
  exclusão nesta versão; reiniciar o servidor **não** apaga esses arquivos.
- **API Key / cookie:** controlados por você (`.env` e navegador).

Para excluir dados: apague manualmente os diretórios em `output/`, remova a key
do `.env` se desejado, limpe o cookie no navegador e reinicie o processo se
quiser limpar o estado em memória.

---

## 9. Segurança

Medidas e limitações atuais:

- processamento local, sem conta multi-usuário;
- API Key opcional para `/api/v1/*` (`GET /health`, UI e docs permanecem
  públicos);
- cookie da UI com `HttpOnly` (uso adequado a cenário local single-tenant);
- execução documentada com `--host 0.0.0.0` expõe a porta na rede local se não
  houver firewall — use API Key e restrição de rede se a máquina for
  compartilhada.

Você é responsável por proteger o host, o `.env`, os artefatos em `output/` e o
acesso à porta do serviço.

---

## 10. Direitos do titular (LGPD e equivalentes)

Se o conteúdo processado contiver dados pessoais de terceiros, o operador da
instância deve observar a base legal e os direitos aplicáveis (acesso, correção,
eliminação, etc.).

Na prática, nesta versão:

- não há painel de “conta do titular”;
- a eliminação de artefatos é feita no sistema de arquivos (`output/`);
- a Ideias Factory não possui cópia dos dados da sua instância para atender
  solicitações sobre conteúdo que você processou localmente.

Se você hospeda o Media Hub para outros, disponibilize um canal de contato e
procedimentos próprios de atendimento a titulares.

---

## 11. Menores e conteúdo sensível

Não há controle etário no software. Não processe conteúdo que você não tenha
direito de tratar, especialmente envolvendo menores ou dados sensíveis, salvo
base legal adequada.

---

## 12. Alterações desta política

Esta política pode ser atualizada no repositório para refletir mudanças do
produto. A data no topo indica a versão vigente do documento no código.

---

## 13. Contato

Dúvidas sobre o **software** e esta política: Ideias Factory — canais indicados
no repositório.

Solicitações sobre **dados processados em uma instância específica** devem ser
dirigidas a quem opera essa instância (em geral, quem executa o Uvicorn e
possui o diretório `output/`).

Documentos relacionados: [DISCLAIMER.md](DISCLAIMER.md) · [LICENSE](LICENSE) ·
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
