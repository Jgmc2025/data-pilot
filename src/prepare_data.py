"""Clean the raw sales CSV and save it in the project's standard format."""

from pathlib import Path
import unicodedata

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT_DIR / "data" / "sales.csv"
OUTPUT_PATH = ROOT_DIR / "data" / "processed" / "sales_clean.csv"

SOURCE_COLUMN_MAP = {
    "pedido_id": "order_id",
    "data": "order_date",
    "produto": "product",
    "categoria": "category",
    "cliente_id": "customer_id",
    "cidade": "city",
    "canal": "channel",
    "quantidade": "quantity",
    "preco_unitario": "unit_price",
}

REQUIRED_COLUMNS = {
    "order_id",
    "customer_id",
    "order_date",
    "status",
    "category",
    "quantity",
    "unit_price",
}

COMPLETED_STATUSES = {
    "complete",
    "completed",
    "delivered",
    "entregue",
    "entregues",
    "concluido",
    "concluida",
    "finalizado",
    "finalizada",
}
CANCELLED_STATUSES = {
    "cancel",
    "canceled",
    "cancelled",
    "cancelado",
    "cancelada",
}


def _normalize_status(value: object) -> str:
    """Trim and lowercase a status, then unify common status variants."""
    status = str(value).strip().lower()
    status = "".join(
        character
        for character in unicodedata.normalize("NFKD", status)
        if not unicodedata.combining(character)
    )

    if status in COMPLETED_STATUSES:
        return "concluido"
    if status in CANCELLED_STATUSES:
        return "cancelado"
    return status


def prepare_sales_data() -> pd.DataFrame:
    """Read, clean, save, and reload sales data using the standard CSV format."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {INPUT_PATH}. "
            "Coloque sales.csv na pasta data/."
        )

    sales = pd.read_csv(INPUT_PATH)
    sales.columns = sales.columns.str.strip().str.lower()
    sales = sales.rename(columns=SOURCE_COLUMN_MAP)
    missing_columns = REQUIRED_COLUMNS - set(sales.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            "O sales.csv precisa ter as colunas do exemplo do desafio "
            "(pedido_id, data, produto, categoria, cliente_id, cidade, canal, "
            "quantidade, preco_unitario e status). "
            f"Colunas ausentes: {missing}."
        )

    sales["order_date"] = pd.to_datetime(sales["order_date"], errors="coerce")
    sales["status"] = sales["status"].map(_normalize_status)
    sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce")
    sales["unit_price"] = pd.to_numeric(sales["unit_price"], errors="coerce")

    sales = sales.drop_duplicates().copy()
    sales["revenue"] = sales["quantity"] * sales["unit_price"]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    sales.to_csv(OUTPUT_PATH, sep=";", decimal=",", index=False)

    # Read the saved file with the same separator and decimal settings used above.
    return pd.read_csv(
        OUTPUT_PATH,
        sep=";",
        decimal=",",
        parse_dates=["order_date"],
    )


if __name__ == "__main__":
    cleaned_sales = prepare_sales_data()
    print(f"Arquivo limpo salvo em: {OUTPUT_PATH}")
    print(f"Linhas carregadas: {len(cleaned_sales)}")
