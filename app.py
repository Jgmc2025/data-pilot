"""Streamlit dashboard for the Data Pilot sales data."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.metrics import (
    get_average_ticket,
    get_total_orders,
    get_total_revenue,
    get_unique_customers,
    load_sales_data,
)


st.set_page_config(page_title="Data Pilot | Vendas", page_icon="📊", layout="wide")


def format_brl(value: float) -> str:
    """Format a number as Brazilian Real without relying on OS locale settings."""
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


st.title("Data Pilot — Análise de Vendas")
st.caption("Métricas calculadas pelo código a partir dos pedidos concluídos.")

try:
    sales = load_sales_data()
except FileNotFoundError as error:
    st.warning(str(error))
    st.info(
        "Prepare primeiro os dados: coloque `sales.csv` em `data/raw/` e execute "
        "`python src/prepare_data.py`. Depois rode `streamlit run app.py`."
    )
    st.stop()

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
else:
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
