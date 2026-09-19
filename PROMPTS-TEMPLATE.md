# PROMPTS-TEMPLATE.md — Template Padrão de Prompts (Synapse One)

Este arquivo padroniza como a squad descreve requisitos, restrições e formatos de saída esperados ao acionar ferramentas de IA generativa. O objetivo é garantir prompts reproduzíveis, auditáveis e aderentes ao fluxo SpecDD. Depois de usar um prompt baseado neste template, registrar o resultado em `PROMPTS.md`.

## Estrutura do template

Use o preenchimento abaixo como coluna dorsal do prompt enviado à IA.

```text
CONTEXTO
- Projeto: SynapseShop (empresa simulada SynapseTech)
- Papel que estou exercendo: <Product Owner / Tech Lead / Desenvolvedor / DevOps / SRE / Arquiteto / Especialista em IA>
- Spec ativa (Aula X): <resumo em 1 linha da spec vigente>

OBJETIVO
<O que deve ser entregue nesta etapa, em 1–3 frases>

RESTRIÇÕES DE ESCOPO (SpecDD — Anti-Hallucination Rule)
- Implementar SOMENTE os critérios da spec da aula ativa.
- PROIBIDO antecipar: <listar o que fica para aulas futuras — ex.: banco de dados, autenticação JWT, cache, mensageria, testes>.
- Sem segredos no código nem commits; valores de dev explícitos e documentados.

STACK E CONVENÇÕES
- Linguagem/frameworks: <Python, Django REST Framework, FastAPI, ...>
- Contêiner: Docker/multistage, usuário não-root, HEALTHCHECK
- Padrão de código: tipagem estática, sem comentários redundantes, sem imports não utilizados

FORMATO DE SAÍDA ESPERADO
- Estrutura de arquivos/pastas desejada
- Modelos de dados (campos, tipos, validações) — ex.: Pydantic `BaseModel`, `Decimal` para dinheiro
- Endpoints/rotas com método, path, request e response (status codes padrão: 200/201/204/400/404)
- Respostas padrão esperadas (schema de sucesso e de erro)

CRITÉRIOS DE ACEITE
- <como validar: comandos docker, curls, status esperados>
- Documentação a atualizar: README.md, PROMPTS.md, (coleção Postman se aplicável)
- Checklist IA-safe deve ser aplicado ao código gerado antes de aceitar
```

## Exemplo preenchido

```text
CONTEXTO
- Projeto: SynapseShop
- Papel: Desenvolvedor
- Spec ativa (Aula 5): microsserviço complementar de estoque em FastAPI com tipagem estática e /docs.

OBJETIVO
Criar o scaffold de um microsserviço `inventory` em FastAPI com modelos Pydantic, rotas mínimas (listar, consultar, registrar, ajustar estoque e excluir) e integração ao docker-compose.

RESTRIÇÕES DE ESCOPO
- Implementar somente o escopo da Aula 5.
- PROIBIDO: banco de dados (Aula 6), autenticação JWT (Aula 7), Redis, mensageria.

STACK E CONVENÇÕES
- Python + FastAPI + Pydantic v2; container com usuário não-root e HEALTHCHECK; tipagem estática nos endpoints.

FORMATO DE SAÍDA
- Estrutura: inventory/app/ (main.py, models.py, store.py) + inventory/Dockerfile + requirements.txt
- Models: InventoryItem (sku, name, quantity >= 0) e AdjustRequest (delta != 0)
- Rotas: GET /health; GET /inventory; GET /inventory/{sku}; PUT /inventory/{sku} (200); POST /inventory/{sku}/adjust (200/400/404); DELETE /inventory/{sku} (204/404)

CRITÉRIOS DE ACEITE
- docker compose up -d --build sobe o inventory na porta 8001, com /docs acessível
- curls: listar, registrar, ajustar (entrada e saída), 400 em delta 0 / estoque negativo, 404 em sku inexistente
- Atualizar README.md e registrar o prompt em PROMPTS.md
```

## Regras

- Prompts transcritos literalmente em `PROMPTS.md` para reprodutibilidade.
- Revisar o código gerado com o `specs/IA_SAFE_CHECKLIST.md` antes de aceitar.
- Nunca aceitar código fora do escopo da aula ativa, mesmo que "útil" para o futuro.