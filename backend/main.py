from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv
import os

import psycopg
from psycopg.rows import dict_row

load_dotenv(Path(__file__).with_name(".env"))

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

def get_connection():
    return psycopg.connect(
        host=os.getenv("SHOP_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("SHOP_DB_PORT", "5432")),
        dbname=os.getenv("SHOP_DB_NAME", "shop"),
        user=os.environ["SHOP_DB_USER"],
        password=os.environ["SHOP_DB_PASSWORD"],
        row_factory=dict_row,
    )

@app.get("/products")
def list_products():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT product_id, name, category, price, stock_quantity
                FROM public.products
                ORDER BY product_id
                """
            )
            rows = cursor.fetchall()

    emoji_by_category = {
        "가방": "👜",
        "주방": "☕",
        "문구": "📒",
    }

    return [
        {
            "id": row["product_id"],
            "name": row["name"],
            "category": row["category"],
            "price": float(row["price"]),
            "stock_quantity": row["stock_quantity"],
            "emoji": emoji_by_category.get(row["category"], "🛍️"),
        }
        for row in rows
    ]