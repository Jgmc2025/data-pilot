"""Generate a reproducible synthetic sales CSV based on the lesson screenshot."""

import csv
from datetime import date, timedelta
from pathlib import Path
import random


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT_DIR / "data" / "sales.csv"
RANDOM_SEED = 2025
ROW_COUNT = 120

FIELDS = [
    "pedido_id",
    "data",
    "produto",
    "categoria",
    "cliente_id",
    "cidade",
    "canal",
    "quantidade",
    "preco_unitario",
    "status",
]

PRODUCTS = [
    ("Luminária Smart", "Casa Inteligente", 149.90, 399.90),
    ("Smart Speaker Mini", "Casa Inteligente", 399.90, 899.90),
    ("Cadeira Ergonômica", "Móveis", 899.90, 2399.90),
    ("Mochila Urban", "Utilidades", 129.90, 349.90),
    ("Suporte para Notebook", "Utilidades", 59.90, 189.90),
    ("Headset Cloud", "Acessórios", 199.90, 1265.90),
    ("Mouse Precision", "Acessórios", 89.90, 315.91),
    ("Webcam Full HD", "Acessórios", 179.90, 597.90),
    ("Notebook Pulse 14", "Eletrônicos", 2499.90, 4999.90),
    ("Teclado Mecânico Pro", "Eletrônicos", 299.90, 849.90),
]
CITIES = [
    "São Paulo",
    "Recife",
    "Rio de Janeiro",
    "Brasília",
    "Curitiba",
    "Fortaleza",
    "Salvador",
    "Belo Horizonte",
]
CHANNELS = ["loja física", "marketplace", "e-commerce", "site"]
STATUSES = ["CONCLUIDO", "Concluído", "concluido", "Cancelado"]


def generate_rows() -> list[dict[str, str | int | float]]:
    rng = random.Random(RANDOM_SEED)
    start_date = date(2025, 1, 1)
    rows = []

    for index in range(1, ROW_COUNT + 1):
        product, category, min_price, max_price = rng.choice(PRODUCTS)
        order_date = start_date + timedelta(days=rng.randrange(365))
        price = round(rng.uniform(min_price, max_price), 2)
        status = rng.choices(STATUSES, weights=[60, 15, 15, 10], k=1)[0]
        rows.append(
            {
                "pedido_id": f"PED-{index:04d}",
                "data": order_date.isoformat(),
                "produto": product,
                "categoria": category,
                "cliente_id": f"CLI-{rng.randint(1, 90):03d}",
                "cidade": rng.choice(CITIES),
                "canal": rng.choice(CHANNELS),
                "quantidade": rng.randint(1, 6),
                "preco_unitario": price,
                "status": status,
            }
        )

    # Include a few repeated rows so the preparation step demonstrates deduplication.
    rows.extend(rows[index].copy() for index in (8, 32, 77))
    return rows


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(generate_rows())
    print(f"Amostra sintética criada: {OUTPUT_PATH}")
    print(f"Linhas de dados: {ROW_COUNT + 3} (inclui 3 duplicatas para limpeza)")


if __name__ == "__main__":
    main()
