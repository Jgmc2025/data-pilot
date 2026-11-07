# Data Pilot

Painel de vendas em Python com um chat em português. O Streamlit mostra indicadores e receita mensal; no chat, um modelo do OpenRouter escolhe uma ferramenta para consultar os cálculos feitos pelo Python.

## Dados

O desafio usa o arquivo `sales.csv` indicado pelo Expert nas aulas. Ele ainda não está incluído neste checkout. Obtenha o arquivo pelo material das aulas e coloque-o em `data/raw/sales.csv`.

O CSV de entrada deve ter estas colunas:

| Coluna | Uso |
| --- | --- |
| `order_id` | Identifica o pedido |
| `customer_id` | Identifica o cliente |
| `order_date` | Data do pedido |
| `status` | Situação do pedido |
| `category` | Categoria do produto |
| `quantity` | Quantidade vendida |
| `unit_price` | Preço unitário |

O preparo padroniza status concluídos como `concluido` e cancelados como `cancelado`, remove linhas duplicadas e calcula `revenue` (`quantity × unit_price`). O resultado fica em `data/processed/sales_clean.csv`, separado por `;` e com vírgula decimal. A pasta processada é gerada pelo script e não é versionada.

## Instalação e configuração

Requer Python 3.10 ou mais recente. No PowerShell, execute na raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copie o exemplo de configuração e adicione sua chave do OpenRouter ao arquivo `.env`:

```powershell
Copy-Item .env.example .env
```

Edite `.env`:

```dotenv
OPENROUTER_API_KEY=sua_chave_aqui
OPENROUTER_MODEL=openrouter/free
```

O `.env` está no `.gitignore`; não publique sua chave.

## Preparar e executar

Depois de colocar `sales.csv` em `data/raw/`, gere os dados limpos e inicie o painel:

```powershell
python src/prepare_data.py
streamlit run app.py
```

Use o menu lateral para alternar entre **Painel** e **Conversa**. O painel filtra por categoria e exibe indicadores de pedidos concluídos e receita por mês.

## Métricas e ferramentas do chat

As métricas de receita, pedidos, ticket médio, clientes únicos e receita média por cliente consideram apenas pedidos concluídos. Pedidos são contados por `order_id` distinto. A taxa de cancelamento é a quantidade de pedidos distintos cancelados dividida pelo total de pedidos distintos e retorna uma fração entre `0` e `1`.

O modelo pode escolher estas ferramentas:

| Ferramenta | Cálculo |
| --- | --- |
| `get_total_revenue` | Soma a receita dos pedidos concluídos |
| `get_total_orders` | Conta pedidos distintos concluídos |
| `get_average_ticket` | Receita concluída dividida por pedidos concluídos |
| `get_unique_customers` | Conta clientes distintos com pedido concluído |
| `get_average_revenue_per_customer` | Receita concluída dividida por clientes distintos com pedido concluído |
| `get_cancellation_rate` | Pedidos distintos cancelados divididos por todos os pedidos distintos |

O modelo decide qual ferramenta pedir; a aplicação executa o cálculo em Python e devolve o resultado para o modelo explicar. A melhoria escolhida para o projeto foi a receita média por cliente, disponível no painel e no chat.

## Estrutura

```text
data-pilot/
├── app.py                  # Aplicação Streamlit
├── data/
│   └── raw/README.md       # Instrução sobre o CSV de entrada
├── src/
│   ├── chat.py             # Integração OpenRouter e ferramentas
│   ├── metrics.py          # Cálculos de negócio
│   └── prepare_data.py     # Limpeza e preparação do CSV
├── .env.example            # Modelo das variáveis de ambiente
└── requirements.txt        # Dependências Python
```
