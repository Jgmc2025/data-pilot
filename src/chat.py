"""OpenRouter chat integration using Python-computed sales context."""

import os

import pandas as pd
from openai import OpenAI

from src.metrics import (
    get_average_ticket,
    get_cancellation_rate,
    get_total_orders,
    get_total_revenue,
    get_unique_customers,
)


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"


def build_sales_context(sales: pd.DataFrame) -> str:
    """Create a compact context from metrics already calculated in Python."""
    return "\n".join(
        [
            f"Receita dos pedidos concluídos: R$ {get_total_revenue(sales):.2f}",
            f"Pedidos concluídos: {get_total_orders(sales)}",
            f"Ticket médio dos pedidos concluídos: R$ {get_average_ticket(sales):.2f}",
            f"Clientes com pedido concluído: {get_unique_customers(sales)}",
            f"Taxa de cancelamento: {get_cancellation_rate(sales):.2%}",
        ]
    )


def ask_openrouter(
    question: str,
    sales_context: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    """Ask the configured OpenRouter model to explain the provided metrics."""
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
                "clara e breve. Use somente os fatos numéricos do contexto calculado "
                "pelo Python. Não invente valores nem faça novos cálculos. Se o contexto "
                "não responder à pergunta, diga isso com clareza.\n\n"
                f"Contexto de vendas:\n{sales_context}"
            ),
        }
    ]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL,
        messages=messages,
    )
    answer = response.choices[0].message.content
    if not answer:
        raise RuntimeError("O modelo retornou uma resposta vazia.")
    return answer
