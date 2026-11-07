"""Business metrics calculated from the cleaned sales data."""

from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
SALES_PATH = ROOT_DIR / "data" / "processed" / "sales_clean.csv"
COMPLETED_STATUS = "concluido"
CANCELLED_STATUS = "cancelado"


def load_sales_data() -> pd.DataFrame:
    """Load the cleaned sales CSV using its semicolon/comma format."""
    if not SALES_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo limpo não encontrado: {SALES_PATH}. "
            "Execute primeiro: python src/prepare_data.py"
        )

    return pd.read_csv(
        SALES_PATH,
        sep=";",
        decimal=",",
        parse_dates=["order_date"],
    )


def _get_sales(sales: pd.DataFrame | None) -> pd.DataFrame:
    data = load_sales_data() if sales is None else sales
    required_columns = {"order_id", "customer_id", "status", "revenue"}
    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dados de vendas sem as colunas necessárias: {missing}.")
    return data


def _completed_sales(sales: pd.DataFrame | None = None) -> pd.DataFrame:
    data = _get_sales(sales)
    return data.loc[data["status"].eq(COMPLETED_STATUS)]


def get_total_revenue(sales: pd.DataFrame | None = None) -> float:
    """Return revenue from completed orders only."""
    completed = _completed_sales(sales)
    return float(pd.to_numeric(completed["revenue"], errors="coerce").sum())


def get_total_orders(sales: pd.DataFrame | None = None) -> int:
    """Return the number of distinct completed orders."""
    completed = _completed_sales(sales)
    return int(completed["order_id"].nunique())


def get_average_ticket(sales: pd.DataFrame | None = None) -> float:
    """Return completed-order revenue divided by distinct completed orders."""
    completed = _completed_sales(sales)
    order_count = completed["order_id"].nunique()
    if order_count == 0:
        return 0.0
    revenue = pd.to_numeric(completed["revenue"], errors="coerce").sum()
    return float(revenue / order_count)


def get_unique_customers(sales: pd.DataFrame | None = None) -> int:
    """Return distinct customers with at least one completed order."""
    completed = _completed_sales(sales)
    return int(completed["customer_id"].nunique())


def get_average_revenue_per_customer(sales: pd.DataFrame | None = None) -> float:
    """Return completed-order revenue divided by distinct completed-order customers."""
    completed = _completed_sales(sales)
    customer_count = completed["customer_id"].nunique()
    if customer_count == 0:
        return 0.0
    revenue = pd.to_numeric(completed["revenue"], errors="coerce").sum()
    return float(revenue / customer_count)


def get_cancellation_rate(sales: pd.DataFrame | None = None) -> float:
    """Return canceled distinct orders divided by all distinct orders."""
    data = _get_sales(sales)
    order_count = data["order_id"].nunique()
    if order_count == 0:
        return 0.0
    canceled_order_count = data.loc[
        data["status"].eq(CANCELLED_STATUS), "order_id"
    ].nunique()
    return float(canceled_order_count / order_count)
