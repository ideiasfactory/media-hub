# Documentação — Media Hub

Índice da documentação de produto e arquitetura.

| Documento | Conteúdo |
|-----------|----------|
| [ROADMAP.md](ROADMAP.md) | Visão estratégica, releases e status dos épicos |
| [EPICS.md](EPICS.md) | Catálogo detalhado EPIC-001 … EPIC-041 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Arquitetura atual (v0.1) e alvo da plataforma |
| [DECISIONS.md](DECISIONS.md) | Architecture Decision Records (ADRs) |
| [CICD.md](CICD.md) | CI/CD público: self-host + publish GHCR (promote IHL no ops) |
| [OPEN_CORE_AND_OPS.md](OPEN_CORE_AND_OPS.md) | Open core, fronteira OSS/ops, produto multi-repo |
| [REPO_SEGMENTATION.md](REPO_SEGMENTATION.md) | Topologia 3 repos (core/ops/cloud) + DAG de segmentação |
| [ADAPTERS.md](ADAPTERS.md) | Contrato para propor novos Source Adapters |
| [VERSIONING.md](VERSIONING.md) | SemVer do produto, contrato `/api/vN` e checklist de release (ADR-021) |

## Como manter

1. Atualizar o **status** do épico em `ROADMAP.md` e `EPICS.md` ao iniciar/concluir.
2. Registrar decisões relevantes em `DECISIONS.md` (novo ADR ou revisão de status).
3. Manter `ARCHITECTURE.md` alinhado ao código entregue (estado atual) e ao alvo
   autorizado pelo roadmap.
4. Não expandir escopo de implementação sem épico autorizado e aprovação humana.

Guia operacional de instalação e execução: [../README.md](../README.md).  
Isenção de responsabilidade (conteúdo / direitos autorais): [../DISCLAIMER.md](../DISCLAIMER.md).  
Política de privacidade (dados na instância local): [../PRIVACY.md](../PRIVACY.md).  
Regras para agentes: [../AGENTS.md](../AGENTS.md).
