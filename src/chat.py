"""OpenRouter chat integration with Python-executed metric tools."""

import json
import os
from collections.abc import Callable

import pandas as pd
from openai import OpenAI

from src.metrics import (
    get_average_revenue_per_customer,
    get_average_ticket,
    get_cancellation_rate,
    get_total_orders,
    get_total_revenue,
    get_unique_customers,
)


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"
MAX_TOOL_ROUNDS = 5

METRIC_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_total_revenue",
            "description": "Retorna a receita total dos pedidos concluídos.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_total_orders",
            "description": "Conta os pedidos distintos com status concluído.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_average_ticket",
            "description": (
                "Retorna o ticket médio: receita dos pedidos concluídos dividida "
                "pelo número de pedidos distintos concluídos."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_unique_customers",
            "description": "Conta clientes distintos com ao menos um pedido concluído.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_average_revenue_per_customer",
            "description": (
                "Retorna a receita média por cliente: receita dos pedidos concluídos "
                "dividida pelo número de clientes distintos com pedido concluído."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_cancellation_rate",
            "description": (
                "Retorna a proporção de pedidos distintos cancelados sobre todos os "
                "pedidos distintos, como fração entre 0 e 1."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def _tool_functions(sales: pd.DataFrame) -> dict[str, Callable[[], int | float]]:
    """Bind the public tool names to calculations over the currently loaded data."""
    return {
        "get_total_revenue": lambda: get_total_revenue(sales),
        "get_total_orders": lambda: get_total_orders(sales),
        "get_average_ticket": lambda: get_average_ticket(sales),
        "get_unique_customers": lambda: get_unique_customers(sales),
        "get_average_revenue_per_customer": lambda: get_average_revenue_per_customer(
            sales
        ),
        "get_cancellation_rate": lambda: get_cancellation_rate(sales),
    }


def ask_openrouter(
    question: str,
    sales: pd.DataFrame,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    """Let the model choose metric tools and return a final answer."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key or api_key == "cole_sua_chave_aqui":
        raise ValueError(
            "Configure OPENROUTER_API_KEY no arquivo .env antes de usar o chat."
        )

    client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)
    messages = [
        {
            "role": "system",
            "content": (
                "Você é o assistente do Data Pilot. Responda em português, de forma "
                "clara e breve. Para responder com métricas, chame a ferramenta "
                "correspondente. Use os resultados das ferramentas como fonte dos "
                "números; não invente nem calcule valores por conta própria. Se nenhuma "
                "ferramenta responder à pergunta, diga isso com clareza."
            ),
        }
    ]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": question})

    functions = _tool_functions(sales)
    model = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=METRIC_TOOLS,
            tool_choice="auto",
        )
        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            if not assistant_message.content:
                raise RuntimeError("O modelo retornou uma resposta vazia.")
            return assistant_message.content

        messages.append(assistant_message.model_dump(exclude_none=True))
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            function = functions.get(tool_name)
            if function is None:
                result = {"error": f"Ferramenta desconhecida: {tool_name}"}
            else:
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    if arguments:
                        raise ValueError("Esta ferramenta não recebe parâmetros.")
                    result = {"result": function()}
                except (json.JSONDecodeError, ValueError) as error:
                    result = {"error": str(error)}

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    raise RuntimeError("O modelo excedeu o limite de chamadas de ferramentas.")
