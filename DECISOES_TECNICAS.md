# Decisões Técnicas — SynapseShop (Synapse One)

Registro formal (formato ADR) das decisões técnicas tomadas durante o desenvolvimento incremental (SpecDD). Cada entrada descreve o contexto, a decisão e as consequências, para histórico rastreável.

## ADR-001 — Persistência relacional do microsserviço inventory via SQLAlchemy + Alembic (Aula 6)

- **Status:** Aceita
- **Data:** 2026-09-21
- **Aula:** 6 — Modelagem Relacional, Índices e Migrações

### Contexto

O `inventory` (FastAPI) operava com estado em memória (Aula 5), sem persistência. O DoD da Aula 6 exige modelagem relacional de ao menos uma entidade, definição de índices e integridade, migrações com SQLAlchemy/Alembic no PostgreSQL, repositórios transacionais, serviço consumindo transações, testes transacionais iniciais e coleta de tempos.

Entidades candidatas sugeridas na spec (`User`, `Token`, `Pedido`) conflitam com a regra anti-antecipação do SpecDD: `User`/`Token` são base do JWT com roles (Aula 7) e `Pedido` pertence ao fluxo Pedido→Pagamento→Notificação (Aulas 9–11).

### Decisão

- Evoluir o **inventory** de memória para **PostgreSQL com SQLAlchemy 2.0 (ORM) + Alembic**, única base aderente ao DoD sem antecipar aulas futuras.
- Entidade relacional `inventory` com: PK serial (`id`), `sku` varchar(50) `UNIQUE`+índice, `name` varchar(200) `NOT NULL`, `quantity` integer com CHECK `quantity >= 0`, `created_at`/`updated_at` (timestamptz, default `now()`, update automático).
- Migração inicial criada manualmente (revisão `2026092101`) e aplicada automaticamente no `CMD` da imagem (`alembic upgrade head` antes do `uvicorn`), com `depends_on: service_healthy` no compose.
- Camada interna reestruturada para **Repository → Service**: `InventoryRepository` (sessão transacional) e `InventoryService` (regras de negócio), preservando as rotas da API da Aula 5.
- Testes transacionais como script (`inventory/scripts/run_transactional_tests.py`) com medição de tempos — **sem pytest**, cuja suíte formal é escopo das Aulas 12–13.

### Consequências

- Rota/SKU passam a ser consultas indexadas de fato (índice único em `sku`).
- Transações protegidas: `adjust` usa `SELECT ... FOR UPDATE` e aborta estoque negativo; `upsert` com rollback em `IntegrityError`.
- O `inventory` compartilha o mesmo PostgreSQL do `api` (DB `synapseshop`), em tabela e versionamento próprios (`alembic_version`), sem colisão com as `django_migrations`.
- Tempo médio medido por transação: ~18 ms (9 operações; a primeira mais lenta por warm-up do pool).

### Alternativas consideradas

- **Refatorar a camada de dados do Django (DRF) para SQLAlchemy/Alembic** — rejeitada: conflita com o sistema de migrações nativo do Django e foge das ferramentas exigidas.
- **Criar entidade `Pedido` do zero** — rejeitada: antecipa o fluxo transacional das Aulas 9–11.
- **Granularidade da migração em `downgrade` de `base`** — escolhida para demonstrar rollback completo e seguro do schema.

## ADR-002 — Sessão SQLAlchemy por request (dependency injection no FastAPI)

- **Status:** Aceita
- **Data:** 2026-09-21
- **Aula:** 6

### Decisão

Cada request abre uma `Session` via dependency `get_service()` (que injeta `InventoryRepository` no `InventoryService`) e a fecha em `finally`. O `lifespan` do FastAPI reidrata o estoque de demonstração (`NB-01`, `MOUSE-RGB-01`) apenas se a tabela existir — seeds idempotentes via `register` (upsert).

### Consequências

- Ciclo de vida da sessão curto e previsível (sem session leak).
- Regra de negócio isolada no service; o repositório só executa SQL/commit/rollback.