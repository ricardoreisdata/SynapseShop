# PROMPTS.md — Histórico de Uso de IA (Synapse One)

Registro auditável e reproduzível de todo uso de IA generativa no projeto SynapseShop, conforme diretriz do curso (SpecDD + transparência).

## Como registrar

| Data | Contexto | Objetivo | Prompt usado | Modelo/Provedor | Resultado & Observações |
|---|---|---|---|---|---|
| — | Spec/Aula que motivou o uso | O que se queria alcançar | Texto literal do prompt | Modelo/Provedor | O que foi aceito, corrigido ou aprendido |

**Regras:**
- Nenhum uso de IA sem registro.
- Prompts transcritos literalmente, para reprodutibilidade.
- Resultado descreve o que foi aceito, corrigido ou descartado.

## Histórico

| Data | Contexto | Objetivo | Prompt usado | Modelo/Provedor | Resultado & Observações |
|---|---|---|---|---|---|
| 2026-09-14 | Aula 1 — Kick-off, formação e repositório | Entender a metodologia do curso e planejar a estrutura inicial do repositório (`README.md` e `PROMPTS.md`) | "Preciso aprender o que o curso tem a oferecer... Antes de fazer qualquer etapa do spec, faça uma pequena introdução, explicando de forma didática cada processo, o porquê, melhores práticas." | opencode/big-pickle | Definidos SpecDD, anatomia do README e template do PROMPTS.md. Criados `README.md` (visão do MVP de eletrônicos + arquitetura em 6 camadas), `PROMPTS.md` e `.gitignore`. Decisões: squad Synapse One, Ricardo como Tech Lead, domínio loja de eletrônicos. Repositório vinculado ao GitHub e marco zero publicado (`commit 1c74f27` → `push -u origin main`). |

| 2026-09-14 | Aula 1 — Git | Publicar o repositório no GitHub com segurança | "Este é o endereço do repositório: https://github.com/ricardoreisdata/SynapseShop.git" | opencode/big-pickle | Conectado `origin`, configurado `.gitignore` (exclui node_modules, segredos e artefatos), realizado commit do marco zero e push publicado em `main`. Sem segredos no repositório. |

| 2026-09-14 | Aula 2 — Esqueleto do projeto e conteinerização | Criar a estrutura em camadas (api/services/repositories) e conteinerizar um script dummy com Docker Compose | "Guie-me na criação do esqueleto em camadas, Dockerfile e docker-compose de um container Python simples (mensagem + loop idle)." | opencode/big-pickle | Estrutura de pastas criada com `.gitkeep`; criados `app.py` (print com `flush=True` para log imediato), `Dockerfile` (FROM python:3.12.10-slim, WORKDIR /app, COPY app.py ., CMD), `docker-compose.yml` (serviço api, build: .) e `.dockerignore`. Validado `docker compose up --build -d`: imagem construída, container Up e log "esqueleto ativo" exibido. Encerrado com `docker compose down`. |