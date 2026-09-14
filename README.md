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