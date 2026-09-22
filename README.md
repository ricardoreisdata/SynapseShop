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
curl.exe http://localhost:8000/health/  # rota de disponibilidade da API
docker compose logs -f api              # logs da API em tempo real (Ctrl+C para sair)
docker compose logs -f db               # logs do PostgreSQL
docker stats                            # CPU/memória dos containers em tempo real
```

Esperado em `docker compose ps`: `api` como `Up ... (healthy)` e `db` como `Up`. A rota `/health/` responde `{"status": "ok", "service": "synapseshop-api"}`.

### Derrubar o ambiente

```powershell
docker compose down        # para e remove containers + rede criada (os dados do banco PERMANECEM no volume)
docker compose down -v     # o -v apaga TAMBÉM os volumes (destrói os dados!) — usar com cuidado
```

### Dicas

- **Dados do banco:** ficam no volume `synapseshop_pgdata` (o compose prefixa o nome declarado `pgdata` com o nome do projeto), fora dos containers. `docker volume ls` e `docker volume inspect synapseshop_pgdata` para conferir.
- **Acessar o banco** de dentro da rede: `docker compose exec db psql -U synapseshop -d synapseshop`.
- **Imagem:** o `Dockerfile` usa *multistage build*, usuário não-root (`appuser`) e `HEALTHCHECK` apontando para `/health/`. `docker history synapseshop-api:latest` para inspecionar as camadas.

## API principal — Django REST Framework (Aula 4)

A API é um projeto Django que sobe no container `api`. O app `store` expõe as entidades base do catálogo (`Category` e `Item`) como recursos RESTful versionados sob `/api/v1/`. O código-fonte é sincronizado com o host via *bind mount* (`./api:/app`), então mudanças refletem com auto-reload.

### Endpoints

| Método | Rota | Descrição | Status esperado |
|---|---|---|---|
| GET | `/api/v1/categories/` | Lista categorias | 200 OK |
| POST | `/api/v1/categories/` | Cria categoria | 201 Created |
| GET | `/api/v1/categories/{id}/` | Detalha categoria | 200 OK / 404 |
| PUT/PATCH | `/api/v1/categories/{id}/` | Atualiza categoria | 200 OK |
| DELETE | `/api/v1/categories/{id}/` | Exclui categoria | 204 No Content |
| GET | `/api/v1/items/` | Lista itens | 200 OK |
| POST | `/api/v1/items/` | Cria item (valida preço > 0) | 201 Created / 400 |
| GET | `/api/v1/items/{id}/` | Detalha item | 200 OK / 404 |
| PUT/PATCH | `/api/v1/items/{id}/` | Atualiza item | 200 OK |
| DELETE | `/api/v1/items/{id}/` | Exclui item | 204 No Content |

### Primeira subida (banco vazio)

```powershell
docker compose up -d --build                 # sobe api + db (db aguarda ficar healthy)
docker compose run --rm api python manage.py makemigrations store   # gera migrations (grava em ./api via bind mount)
docker compose run --rm api python manage.py migrate                # aplica as migrations
docker compose restart api                                          # o entrypoint também faz migrate automaticamente
```

O `entrypoint.sh` já executa `migrate --noinput` a cada start da API; o passo manual acima só é necessário na criação inicial das migrations.

### Testar a API

```powershell
curl.exe http://localhost:8000/api/v1/categories/                                   # lista (ou cria via POST abaixo)
curl.exe -X POST http://localhost:8000/api/v1/categories/ -H "Content-Type: application/json" -d "{\"name\": \"Eletronicos\"}"
curl.exe -X POST http://localhost:8000/api/v1/items/ -H "Content-Type: application/json" -d "{\"name\": \"Notebook\", \"sku\": \"NB-01\", \"category\": 1, \"price\": \"4599.90\"}"
```

Payloads inválidos (ex.: preço `0`) retornam `400 Bad Request`; ids inexistentes retornam `404 Not Found`.

### Coleção no Postman

O arquivo `postman/SynapseShop.postman_collection.json` contém todos os CRUDs (`Categories`, `Items`) e o `/health/`, com a variável `baseUrl` = `http://localhost:8000`. Importe pelo Postman: **Import → arquivo JSON**. Os exemplos de `POST`/`PUT` já trazem os corpos esperados.

### Interface administrativa (extra)

O Django Admin fica em `http://localhost:8000/admin/` — útil para inspecionar os dados gerados via API (não faz parte do escopo de autenticação da Aula 4).

## Microsserviço de Estoque — FastAPI (Aula 5)

O serviço `inventory` é um microsserviço complementar em **FastAPI** que gerencia o estoque dos itens. Nesta aula o foco é a camada de API: **modelos Pydantic, tipagem estática, validações e documentação automática** — ainda **sem banco de dados** (Aula 6) e sem autenticação (Aula 7), conforme o SpecDD. O armazenamento é em memória, com itens de demonstração (`NB-01` e `MOUSE-RGB-01`) semeados no startup.

### Rotas mínimas alinhadas

| Método | Rota | Descrição | Status esperado |
|---|---|---|---|
| GET | `/health` | Disponibilidade do serviço | 200 OK |
| GET | `/inventory` | Lista itens do estoque | 200 OK |
| GET | `/inventory/{sku}` | Consulta item por SKU | 200 OK / 404 |
| PUT | `/inventory/{sku}` | Registra/atualiza item (upsert) | 200 OK |
| POST | `/inventory/{sku}/adjust` | Ajusta estoque (delta ≠ 0) | 200 OK / 400 / 404 |
| DELETE | `/inventory/{sku}` | Remove item | 204 No Content / 404 |

Validações Pydantic: `quantity >= 0`, `delta != 0` e resultado nunca negativo (`400 Bad Request`).

### Documentação interativa (`/docs`)

O FastAPI gera a documentação automaticamente a partir dos tipos e `response_model`:

```powershell
docker compose up -d --build            # sobe api + db + inventory
curl.exe http://localhost:8001/health   # 200 (healthcheck do container)
curl.exe http://localhost:8001/docs     # Swagger UI automatizado
curl.exe http://localhost:8001/openapi.json   # spec OpenAPI do serviço
```

### Testar o estoque (PowerShell)

```powershell
Invoke-WebRequest -Uri http://localhost:8001/inventory -UseBasicParsing | Select-Object -ExpandProperty Content
Invoke-WebRequest -Uri http://localhost:8001/inventory/NB-01 -UseBasicParsing | Select-Object -ExpandProperty Content
$body = '{"name": "Teclado Mecanico", "quantity": 30}'
Invoke-WebRequest -Uri http://localhost:8001/inventory/KB-01 -Method Put -ContentType "application/json" -Body $body -UseBasicParsing | Select-Object StatusCode
Invoke-WebRequest -Uri http://localhost:8001/inventory/NB-01/adjust -Method Post -ContentType "application/json" -Body '{"delta": -5}' -UseBasicParsing | Select-Object -ExpandProperty Content
```

O serviço roda na porta `8001` e permanece na rede interna `synapseshop-net` (integrável à API principal nas próximas aulas).

### Template de prompts da squad

O arquivo `PROMPTS-TEMPLATE.md` padroniza como descrever requisitos, restrições e formatos de saída ao acionar ferramentas de IA — requisito da Aula 5. Todo prompt usado no projeto segue esse padrão e é registrado em `PROMPTS.md`.

## Microsserviço de Estoque — Modelagem Relacional (Aula 6)

Na Aula 6 o `inventory` ganhou **persistência relacional** no PostgreSQL, orquestrada por **SQLAlchemy** (ORM) e **Alembic** (migrações), substituindo o armazenamento em memória da Aula 5. As rotas da API foram preservadas; a camada interna agora segue o padrão **Repository → Service** transacional.

### Modelagem: entidade `inventory`

| Campo | Tipo | Regra de integridade |
|---|---|---|
| `id` | integer (PK, serial) | Chave primária |
| `sku` | varchar(50) | `NOT NULL` + **`UNIQUE`** (índice) |
| `name` | varchar(200) | `NOT NULL` |
| `quantity` | integer | `NOT NULL` + **CHECK `quantity >= 0`** |
| `created_at` | timestamptz | `NOT NULL`, default `now()` |
| `updated_at` | timestamptz | `NOT NULL`, default `now()` |

Índices: `inventory_pkey` (PK em `id`) e `ix_inventory_sku` (único em `sku`) — atendem à busca por SKU e garantem a unicidade da chave de negócio. O versionamento do schema fica na tabela `alembic_version`.

### Migrações e rollback (Alembic)

O `CMD` da imagem já executa `alembic upgrade head` antes de subir o `uvicorn`, então a migração é aplicada automaticamente a cada start (o `db` é aguardado via `depends_on: service_healthy`). Para operar o versionamento manualmente:

```powershell
docker compose run --rm inventory alembic upgrade head       # aplica migrações pendentes
docker compose run --rm inventory alembic downgrade base     # rollback seguro (remove o schema)
docker compose run --rm inventory alembic downgrade -1       # retrocede 1 revisão
docker compose run --rm inventory alembic current            # revisão ativa no banco
```

O rollback é **transacional e seguro** (componentes `upgrade`/`downgrade` completos por revisão).

### Arquitetura interna (Repository → Service)

```
inventory/app/db.py         conexão/engine (postgresql+psycopg) e SessionLocal
inventory/app/entity.py     modelo ORM SQLAlchemy (InventoryRecord) + constraints
inventory/app/repository.py repositório transacional (get/list/upsert/adjust/delete)
inventory/app/service.py    serviço que consome o repositório (regras de negócio)
inventory/app/main.py       FastAPI: sessão por request, rotas delegam ao service
inventory/alembic/          config + migrações (revisão 2026092101 cria a tabela)
```

- **Transacional:** cada request abre uma `Session` (fechada ao final via dependency); `upsert` faz flush+commit com rollback em `IntegrityError`; `adjust` usa `SELECT ... FOR UPDATE` e aborta (rollback) se o estoque ficar negativo.
- **Sessão por request:** dependency `get_service()` cria a sessão, injeta `InventoryRepository` no `InventoryService` e garante o fechamento no `finally`.

### Testes transacionais e tempos

O script `inventory/scripts/run_transactional_tests.py` exercita 9 operações (upsert, leitura, update, ajustes válidos/inválidos, unicidade de SKU, listagem e delete) e mede o tempo de cada uma:

```powershell
docker compose run --rm inventory python scripts/run_transactional_tests.py
```

Resultado de referência (2026-09-21): tempo médio por transação **~18 ms** (mais lenta: primeiro upsert, ~73 ms — warm-up/connection pool).

### Comandos rápidos de validação

```powershell
curl.exe http://localhost:8001/health                          # 200
curl.exe http://localhost:8001/inventory                       # lista (persistido)
curl.exe -X PUT http://localhost:8001/inventory/GPU-01 -H "Content-Type: application/json" -d "{\"sku\": \"GPU-01\", \"name\": \"Placa de Video\", \"quantity\": 7}"
curl.exe -X POST http://localhost:8001/inventory/NB-01/adjust -H "Content-Type: application/json" -d "{\"delta\": -5}"
```