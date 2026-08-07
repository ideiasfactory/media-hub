# Isenção de Responsabilidade — Uso de Conteúdo e Conduta Ilegal

**Última atualização:** 6 de agosto de 2026  
**Software:** Media Hub (Ideias Factory)

Este documento complementa a [licença do software](LICENSE), a
[Política de Privacidade](PRIVACY.md) e a seção
[Uso responsável](README.md#uso-responsável) do README. Em caso de conflito
entre este aviso e a lei aplicável, prevalece a lei.

---

## 1. Natureza da ferramenta

O Media Hub é um software local que permite baixar áudio de vídeos públicos,
transcrevê-lo e gerar artefatos (MP3, TXT, SRT, metadados). Trata-se de uma
ferramenta técnica: **não concede, transfere nem implica qualquer direito
autoral** sobre o conteúdo processado e **não autoriza** qualquer uso ilícito.

A licença Apache-2.0 cobre apenas o **código-fonte do Media Hub**.
Não autoriza o uso de obras de terceiros nem qualquer atividade criminosa.

---

## 2. Responsabilidade exclusiva do usuário

Ao usar o Media Hub, você declara e concorda que:

1. Processará **somente** conteúdo:
   - de sua autoria; ou
   - para o qual possui licença, autorização expressa ou outro fundamento legal
     válido (incluindo usos admitidos pela legislação aplicável, quando
     cabíveis);
2. Cumprirá a legislação aplicável no seu país (direitos autorais, proteção de
   crianças e adolescentes, crimes cibernéticos, privacidade etc.) e os
   **termos de serviço** das plataformas de origem (por exemplo, YouTube);
3. Não usará o software para piratear, redistribuir, comercializar ou explorar
   ilegalmente obras protegidas;
4. Não usará o software para fins ilegais, ilícitos ou para facilitar crimes
   (detalhados nas seções 3 e 4);
5. É o **único responsável** pelas URLs enviadas, pelos arquivos gerados e pelo
   destino dado a esses arquivos.

Os mantenedores, contribuidores e a Ideias Factory **não verificam** previamente
se o conteúdo processado é autorizado ou lícito. Em instalações locais, quem
opera o processo tem controle exclusivo sobre as URLs e os artefatos em
`output/`.

---

## 3. Tolerância zero — exploração e abuso de crianças e adolescentes

É **absolutamente proibido** utilizar o Media Hub para criar, baixar, copiar,
transcrever, armazenar, analisar, indexar, redistribuir, comercializar,
promover ou de qualquer forma facilitar material ou conduta envolvendo:

- exploração sexual, abuso sexual ou pornografia infantil (incluindo CSAM /
  CSEM — *Child Sexual Abuse / Exploitation Material*);
- sexualização de menores de 18 anos, ainda que “simulada”, gerada por IA,
  desenhada, deepfake ou “aparentemente adulta” quando a pessoa for ou possa
  ser menor;
- aliciamento, grooming, sequestro, tráfico ou qualquer forma de vitimização
  de crianças ou adolescentes;
- solicitação de dados pessoais, imagens íntimas ou contato sexual com menores;
- produção ou circulação de conteúdo que incentive, normalize ou instrua abuso
  ou exploração de menores.

Essa proibição é **irrevogável**, não pode ser contornada por acordo particular
e aplica-se independentemente da jurisdição em que o usuário esteja. Violações
podem constituir crime grave (no Brasil, entre outras normas, o Estatuto da
Criança e do Adolescente e legislação penal correlata; em outras jurisdições,
equivalentes como leis sobre CSAM).

A Ideias Factory e os mantenedores **não endossam**, **não hospedam** e
**não cooperam** com esse tipo de uso. Quando legalmente obrigados ou quando
tiverem conhecimento efetivo de uso ilícito no contexto do projeto (ex.: issue,
PR ou comunicação), poderão preservar evidências, negar suporte e **comunicar
às autoridades competentes**.

Canais de denúncia úteis (exemplos; use o adequado à sua jurisdição):

- Brasil: [SaferNet](https://new.safernet.org.br/) / Disque 100;
- Internacional (referência): autoridades locais de proteção à criança e
  canais equivalentes ao CyberTipline / NCMEC, quando aplicável.

---

## 4. Outros usos ilegais expressamente proibidos

Além da seção 3 e das restrições de direitos autorais, é proibido usar o
Media Hub para, entre outros:

### 4.1 Crimes e conteúdos ilícitos

- terrorismo, extremismo violento ou incitação a crimes violentos;
- tráfico de pessoas, exploração sexual de adultos sem consentimento, ou
  facilitação dessas práticas;
- imagens íntimas não consentidas (*revenge porn*, “vazamento”, deepfakes
  sexuais sem autorização);
- assédio, stalking, extorsão, ameaça ou doxxing;
- discurso ou material destinado a promover ódio, genocídio ou violência
  contra grupos protegidos, quando isso constituir ilícito na jurisdição
  aplicável;
- fraude, phishing, engenharia social ou obtenção ilícita de dados;
- tráfico ilícito de drogas, armas ou outros bens controlados;
- espionagem, interceptação ilegal de comunicações ou vigilância ilícita de
  pessoas.

### 4.2 Segurança e integridade de sistemas

- contornar DRM, autenticação, paywall, restrições territoriais ou outros
  controles de acesso;
- usar cookies, credenciais ou sessões de plataformas de mídia sem autorização;
- desenvolver, testar ou distribuir malware, ransomware ou exploits com o
  auxílio desta ferramenta;
- violar termos de uso de serviços de terceiros;
- facilitar ou automatizar infração em escala (ex.: scraping sistemático de
  catálogos protegidos).

O projeto **não implementa** e **não endossa** mecanismos para esses fins
(ver [ADR-013](docs/DECISIONS.md#adr-013--sem-contorno-de-drm-auth-ou-geo)).

### 4.3 Consequências

O uso ilícito:

- viola este disclaimer e o [Código de Conduta](CODE_OF_CONDUCT.md);
- pode resultar em recusa de suporte, bloqueio de contribuições e denúncia às
  autoridades;
- é de **responsabilidade integral do usuário**, que assume riscos penais e
  civis decorrentes.

---

## 5. Ausência de garantia sobre conteúdo e conformidade

O software é fornecido **“como está”**, sem garantia de que:

- determinado vídeo ou áudio possa ser processado legalmente na sua jurisdição;
- o resultado da transcrição seja completo, preciso ou adequado a qualquer fim;
- o uso esteja em conformidade com contratos, políticas de plataforma ou leis
  locais;
- a ferramenta detecte automaticamente conteúdo ilegal (o MVP **não** inclui
  moderação automática de CSAM ou filtros equivalentes).

A disponibilidade técnica de uma URL pública **não** significa permissão legal
para download, cópia, transcrição ou redistribuição, nem que o conteúdo seja
lícito.

---

## 6. Limitação de responsabilidade

Na máxima extensão permitida pela lei aplicável, a Ideias Factory, os
mantenedores e os contribuidores **não se responsabilizam** por:

- infrações a direitos autorais ou direitos de terceiros decorrentes do uso do
  software;
- crimes, ilícitos civis ou administrativos praticados pelo usuário com o
  software (incluindo, sem limitação, exploração infantil e demais condutas da
  seção 3 e 4);
- reclamações, notificações (incluindo DMCA ou equivalentes), processos ou
  sanções decorrentes de conteúdo processado pelo usuário;
- danos diretos, indiretos, incidentais, especiais, consequenciais ou lucros
  cessantes relacionados ao uso ou à impossibilidade de uso do Media Hub;
- perda de dados, indisponibilidade de plataformas ou alterações em APIs /
  extratores de terceiros (ex.: mudanças no YouTube ou no `yt-dlp`).

Nada neste documento limita responsabilidade que **não possa** ser excluída por
lei (por exemplo, dolo dos mantenedores quando a lei assim exigir). O uso do
software é **por sua conta e risco**.

---

## 7. Conteúdo de terceiros e plataformas

Metadados, títulos, miniaturas, áudio e texto obtidos de plataformas externas
permanecem propriedade de seus respectivos titulares. O Media Hub não é
afiliado, endossado ou patrocinado pelo YouTube, Google ou outros serviços de
mídia, salvo indicação explícita em contrário.

Respeite sempre:

- leis de direitos autorais e direitos conexos;
- termos de serviço e políticas de uso justo / fair use da plataforma;
- restrições de privacidade e dados pessoais eventualmente presentes no
  conteúdo;
- normas de proteção a crianças, adolescentes e demais vulneráveis.

---

## 8. Artefatos gerados (`output/`)

Arquivos em `output/{job_id}/` (áudio, transcrições, metadados) são resultado
do processamento solicitado por você. Cabe a você:

- armazená-los de forma segura e lícita;
- não redistribuí-los sem direito;
- excluí-los quando o fundamento legal deixar de existir;
- não gerar, manter nem compartilhar conteúdo ilícito (especialmente o da
  seção 3).

Quem opera uma instância compartilhada deve impedir usos ilegais e cooperar com
autoridades quando a lei exigir.

---

## 9. Relação com a licença do software

| Documento | Escopo |
|-----------|--------|
| [LICENSE](LICENSE) | Direitos sobre o **código** do Media Hub (Apache-2.0) |
| Este DISCLAIMER | Uso de **conteúdo**, conduta ilegal e limitação de responsabilidade |
| [PRIVACY.md](PRIVACY.md) | Tratamento de dados na instância local |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Conduta da comunidade |

A licença do **software** (Apache-2.0) **não** substitui a necessidade de
direitos sobre o **conteúdo** nem autoriza qualquer uso ilícito.

---

## 10. Aceite

Ao instalar, executar, modificar ou disponibilizar o Media Hub (incluindo via
API ou interface web), você reconhece ter lido este aviso — em especial as
seções **3** e **4** — e assume a responsabilidade integral pelo conteúdo que
processar e pelo cumprimento da lei.

Se não concordar, **não utilize** o software.

---

## 11. Contato e denúncias

Dúvidas sobre licenciamento comercial do software: Ideias Factory — via canais
indicados no repositório.

Para remoção de conteúdo ou disputas de direitos autorais relativas a obras de
terceiros, dirija-se aos titulares dos direitos ou às plataformas de origem;
os mantenedores do Media Hub não hospedam nem publicam o conteúdo processado
pelos usuários.

Suspeita de exploração infantil ou outro crime grave envolvendo o projeto
(código, issues, PRs ou comunicações oficiais): reporte aos mantenedores pelo
canal privado do GitHub **e** às autoridades / SaferNet conforme o caso. Não
anexe nem publique material ilícito no repositório.
