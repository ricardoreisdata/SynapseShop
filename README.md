# SynapseShop

**Squad:** Synapse One
**Integrante:** Ricardo — Tech Lead

**Domínio:** Loja de eletrônicos

## Visão do MVP

O SynapseShop é o backend de uma loja online de eletrônicos, voltado à gestão de produtos, pedidos, pagamentos simulados e notificações. Construído de forma incremental (SpecDD) e conteinerizado com Docker, o MVP é testado, documentado e integra capacidades reais de IA: um assistente de suporte (`/assist`), consulta de dados em linguagem natural (`/ask_sql`) e um assistente de documentação com resposta baseada nos próprios documentos do projeto (`/ask_docs`).

## Arquitetura-Alvo (6 camadas)

A infraestrutura do sistema é projetada em 6 camadas lógicas, conteinerizadas via Docker e orquestradas com Docker Compose:

1. **Clientes & Canais de Acesso** — Loja Web/Mobile, Painel do Administrador e Canal de Suporte com IA.
2. **Gateway de API & Autenticação** — API principal com Django REST Framework, microsserviços em FastAPI, autenticação JWT com papéis (roles) e throttling.
3. **Serviços de Negócio** — Order, Payment, Inventory e Notification services (fluxo Pedido → Pagamento → Notificação).
4. **Camada de Inteligência Artificial** — Assistente de Suporte, NL-to-SQL e RAG integrados a provedores de LLM externos (OpenAI/DeepSeek).
5. **Infraestrutura de Dados & Mensageria** — PostgreSQL (relacional + migrações), Redis (cache) e RabbitMQ/Kafka (eventos assíncronos com idempotência e DLQ).
6. **Observabilidade, Qualidade & Entrega** — Dashboards em Streamlit, testes com pytest, documentação OpenAPI/Swagger e pipeline de CI/CD com GitHub Actions.

## Ambiente Docker (Aula 3)

A infraestrutura é descrita por um único `docker-compose.yml` que orquestra dois serviços: `api` (aplicação) e `db` (PostgreSQL). Entre eles existe uma rede interna (`synapseshop-net`); apenas a API é exposta ao host, na porta `8000`. O banco permanece interno por segurança (para acessá-lo em desenvolvimento, veja a seção *Dicas*).

**Pré-requisitos:** Docker Desktop aberto (Engine ativo) e terminal PowerShell.

### Subir o ambiente completo

```powershell
docker compose up -d --build
```

O `--build` reconstrói a imagem quando o código muda (essencial no desenvolvimento). Para subir sem rebuildar: `docker compose up -d`.

### Validar e monitorar

```powershell
docker compose ps                       # status e saúde (healthy) dos serviços
curl.exe http://localhost:8000/health   # rota de disponibilidade da API
docker compose logs -f api              # logs da API em tempo real (Ctrl+C para sair)
docker compose logs -f db               # logs do PostgreSQL
docker stats                            # CPU/memória dos containers em tempo real
```

Esperado em `docker compose ps`: `api` como `Up ... (healthy)` e `db` como `Up`. A rota `/health` responde `{"status": "ok", "service": "synapseshop-api"}`.

### Derrubar o ambiente

```powershell
docker compose down        # para e remove containers + rede criada (os dados do banco PERMANECEM no volume)
docker compose down -v     # o -v apaga TAMBÉM os volumes (destrói os dados!) — usar com cuidado
```

### Dicas

- **Dados do banco:** ficam no volume `synapseshop_pgdata` (o compose prefixa o nome declarado `pgdata` com o nome do projeto), fora dos containers. `docker volume ls` e `docker volume inspect synapseshop_pgdata` para conferir.
- **Acessar o banco** de dentro da rede: `docker compose exec db psql -U synapseshop -d synapseshop`.
- **Imagem:** o `Dockerfile` usa *multistage build*, usuário não-root (`appuser`) e `HEALTHCHECK` apontando para `/health`. `docker history synapseshop-api:latest` para inspecionar as camadas.