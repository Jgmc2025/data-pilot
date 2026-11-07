"""Streamlit app with a sales dashboard and an OpenRouter chat."""

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from src.chat import ask_openrouter
from src.metrics import (
    get_average_ticket,
    get_total_orders,
    get_total_revenue,
    get_unique_customers,
    load_sales_data,
)


load_dotenv()
st.set_page_config(page_title="Data Pilot | Vendas", page_icon="📊", layout="wide")


def format_brl(value: float) -> str:
    """Format a number as Brazilian Real without relying on OS locale settings."""
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def render_dashboard(sales: pd.DataFrame) -> None:
    st.title("Data Pilot — Análise de Vendas")
    st.caption("Métricas calculadas pelo código a partir dos pedidos concluídos.")

    categories = sorted(sales["category"].dropna().astype(str).unique().tolist())
    selected_category = st.selectbox("Categoria", ["Todas"] + categories)

    filtered_sales = sales
    if selected_category != "Todas":
        filtered_sales = sales.loc[sales["category"].astype(str).eq(selected_category)]

    revenue = get_total_revenue(filtered_sales)
    orders = get_total_orders(filtered_sales)
    average_ticket = get_average_ticket(filtered_sales)
    customers = get_unique_customers(filtered_sales)

    revenue_card, orders_card, ticket_card, customers_card = st.columns(4)
    revenue_card.metric("Receita total", format_brl(revenue))
    orders_card.metric("Pedidos concluídos", f"{orders:,}".replace(",", "."))
    ticket_card.metric("Ticket médio", format_brl(average_ticket))
    customers_card.metric("Clientes únicos", f"{customers:,}".replace(",", "."))

    completed_sales = filtered_sales.loc[filtered_sales["status"].eq("concluido")].copy()
    st.subheader("Receita por mês")

    if completed_sales.empty:
        st.info("Não há pedidos concluídos para a categoria selecionada.")
        return

    completed_sales["month"] = completed_sales["order_date"].dt.to_period("M").astype(str)
    monthly_revenue = (
        completed_sales.groupby("month", as_index=False)["revenue"]
        .sum()
        .sort_values("month")
    )
    chart = px.line(
        monthly_revenue,
        x="month",
        y="revenue",
        markers=True,
        labels={"month": "Mês", "revenue": "Receita (R$)"},
    )
    chart.update_layout(
        xaxis_title=None,
        yaxis_title="Receita (R$)",
        hovermode="x unified",
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
    )
    st.plotly_chart(chart, use_container_width=True)


def render_chat(sales: pd.DataFrame) -> None:
    st.title("Converse com os dados")
    st.caption(
        "O modelo escolhe qual cálculo do Python usar para responder."
    )

    if not os.getenv("OPENROUTER_API_KEY", "").strip():
        st.info(
            "Configure sua chave no arquivo `.env`. Copie `.env.example` para `.env` "
            "e substitua `cole_sua_chave_aqui` pela sua chave do OpenRouter."
        )

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Pergunte sobre as vendas")
    if not question:
        return

    st.session_state.chat_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    history = st.session_state.chat_messages[:-1]
    with st.chat_message("assistant"):
        with st.spinner("Consultando o modelo..."):
            try:
                answer = ask_openrouter(
                    question,
                    sales,
                    history,
                )
            except Exception as error:
                answer = f"Não consegui consultar o OpenRouter: {error}"
        st.markdown(answer)
    st.session_state.chat_messages.append({"role": "assistant", "content": answer})


st.sidebar.title("Data Pilot")
section = st.sidebar.radio("Menu", ["Painel", "Conversa"])

try:
    sales = load_sales_data()
except FileNotFoundError as error:
    st.warning(str(error))
    st.info(
        "Prepare os dados primeiro: coloque `sales.csv` em `data/raw/` e execute "
        "`python src/prepare_data.py`. Depois rode `streamlit run app.py`."
    )
    st.stop()

if section == "Painel":
    render_dashboard(sales)
else:
    render_chat(sales)
