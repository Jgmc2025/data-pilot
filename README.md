# Data Pilot

Painel de vendas em Python com uma conversa em português apoiada por métricas calculadas pelo próprio código.

## Etapa 1 — Preparação dos dados

Coloque a planilha original em `data/raw/sales.csv`. A entrada deve ser um CSV separado por vírgulas e conter estas colunas:

`order_id`, `order_date`, `status`, `category`, `quantity`, `unit_price`

O script padroniza os nomes e status, converte data e valores numéricos, remove linhas duplicadas e calcula `revenue` como quantidade multiplicada pelo preço unitário. O resultado é salvo em `data/processed/sales_clean.csv`, com `;` como separador e `,` como separador decimal, e então relido com as mesmas configurações.

Instale a dependência e execute na raiz do projeto:

```powershell
python -m pip install -r requirements.txt
python src/prepare_data.py
```
