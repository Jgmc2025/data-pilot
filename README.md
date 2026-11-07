# Data Pilot

Painel de vendas em Python com uma conversa em português apoiada por métricas calculadas pelo próprio código.

## Etapa 1 — Preparação dos dados

Coloque a planilha original em `data/raw/sales.csv`. A entrada deve ser um CSV separado por vírgulas e conter estas colunas:

`order_id`, `customer_id`, `order_date`, `status`, `category`, `quantity`, `unit_price`

O script padroniza os nomes e status, converte data e valores numéricos, remove linhas duplicadas e calcula `revenue` como quantidade multiplicada pelo preço unitário. O resultado é salvo em `data/processed/sales_clean.csv`, com `;` como separador e `,` como separador decimal, e então relido com as mesmas configurações.

Instale a dependência e execute na raiz do projeto:

```powershell
python -m pip install -r requirements.txt
python src/prepare_data.py
```

## Etapa 2 — Métricas

O módulo `src/metrics.py` calcula receita, pedidos, ticket médio e clientes únicos considerando somente pedidos concluídos. O ticket médio é a receita concluída dividida pela quantidade de pedidos concluídos. A taxa de cancelamento é a proporção de pedidos distintos cancelados sobre todos os pedidos distintos e retorna um valor entre `0` e `1`.

## Etapa 3 — Painel

Com os dados preparados, inicie a aplicação com:

```powershell
streamlit run app.py
```

O painel permite filtrar uma categoria e exibe receita total, pedidos concluídos, ticket médio, clientes únicos e receita mensal.

## Etapa 4 — Chat com OpenRouter

Copie `.env.example` para `.env`, preencha `OPENROUTER_API_KEY` com sua chave e mantenha `OPENROUTER_MODEL=openrouter/free` para usar o roteador gratuito. O menu **Conversa** envia perguntas ao modelo pela API do OpenRouter.

```powershell
Copy-Item .env.example .env
```

## Etapa 5 — Ferramentas de métricas

O chat disponibiliza ferramentas para receita, pedidos concluídos, ticket médio, clientes únicos e taxa de cancelamento. O modelo escolhe a ferramenta pela pergunta, mas cada valor é calculado pela função Python correspondente.

## Etapa 6 — Receita média por cliente

Como melhoria, o projeto calcula a receita média por cliente a partir da receita dos pedidos concluídos dividida pela quantidade de clientes distintos com pedido concluído. A métrica aparece no painel e também está disponível como ferramenta no chat.
