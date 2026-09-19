# Checklist "IA-Safe"

Guia obrigatório de checagem para qualquer trecho de código gerado por assistentes de IA (opencode, ChatGPT, etc.) antes de ser aceito no repositório. Nenhum código de origem de IA entra sem revisão humana e sem passar por este checklist. Inspirado nas boas práticas da Aula 4 e no fluxo SpecDD do projeto.

## 1. Origem e escopo

- [ ] O código atende somente ao escopo da aula em andamento (sem features futuras antecipadas).
- [ ] A geração foi registrada no `PROMPTS.md` (data, objetivo, prompt, ferramenta e resultado).
- [ ] Intervenções manuais foram anotadas no `PROMPTS.md`.

## 2. Imports e dependências

- [ ] Todos os imports são efetivamente utilizados (nenhum import "só por garantia").
- [ ] Não há importação de pacotes fora do `requirements.txt` aprovado.
- [ ] O `requirements.txt` só contém dependências necessárias, sem versões soltas ao ponto de quebrar o cache do build.

## 3. Tipos de dados e campos

- [ ] Dinheiro é sempre `DecimalField` (nunca `FloatField`) — Série: preço, impostos, valores.
- [ ] Campos de texto têm `max_length` e campos únicos possuem `unique=True` (ex.: `sku`).
- [ ] Campos numéricos de contagem usam tipos sem sinal e/ou validadores (ex.: `PositiveIntegerField`, `MinValueValidator`).
- [ ] Relacionamentos usam o `on_delete` adequado (ex.: `PROTECT` para dados referenciais).
- [ ] Timestamps padrão (`auto_now_add`/`auto_now`) presentes onde relevante.

## 4. Validações customizadas

- [ ] Validações de regra de negócio vivem no Serializer (ou Model), não soltas em rotas.
- [ ] Payload inválido retorna `400 Bad Request` (a validação do DRF cuida disso).
- [ ] Mensagens de erro são claras e em pt-br quando aplicável.

## 5. Status codes HTTP

- [ ] `GET` list/detail → `200 OK`
- [ ] `POST` (create) → `201 Created`
- [ ] `PUT`/`PATCH` (update) → `200 OK`
- [ ] `DELETE` (destroy) → `204 No Content`
- [ ] Validação falhou → `400 Bad Request`
- [ ] Recurso inexistente → `404 Not Found`
- [ ] Verbos e rotas expostos conforme padrão REST (via `ModelViewSet`/`DefaultRouter`, versão em `/api/v1/`).

## 6. Segurança

- [ ] Nenhum segredo/chave real no código-fonte ou no `docker-compose.yml` (valores de dev são explícitos e documentados como tal; `.env`/`.env.*` estão no `.gitignore`).
- [ ] Permissões de autenticação são **explícitas** (AllowAny declarado — JWT chega só na Aula 7).
- [ ] Banco de dados não fica exposto ao host (rede interna).
- [ ] Container roda como usuário não-root.

## 7. Estrutura e boas práticas DRF

- [ ] Padrão seguido: `Model` → `ModelSerializer` → `ModelViewSet` → `DefaultRouter`.
- [ ] Rotas versionadas sob `/api/v1/`.
- [ ] Sem lógica repetida entre ViewSets (herança de `ModelViewSet` já cobre CRUD).
- [ ] Migrações iniciais geradas pelo framework (não escritas à mão).

## Como aplicar

1. Ao receber código de IA, revisar arquivo por arquivo contra as seções 2 a 7.
2. Marcar os itens ou justificar por escrito por que um item não se aplica.
3. Validar em runtime (subir o ambiente e exercitar os endpoints/status codes da seção 5).
4. Só então commitar — com mensagem no padrão **Conventional Commits**.