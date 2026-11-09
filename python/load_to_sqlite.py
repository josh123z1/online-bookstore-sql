"""
Load the generated Excel workbook into a SQLite database built from sql/01_schema.sql.

Usage (from the repo root):
    python python/load_to_sqlite.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "bookstore_synth_final.xlsx"
SCHEMA = ROOT / "sql" / "01_schema.sql"
DB = ROOT / "wbs_bookstore.db"

# Excel sheet name -> SQLite table name, in foreign-key order
TABLES = {
    "Genre": "genre",
    "Customer": "customer",
    "Author": "author",
    "Book": "book",
    "Book_Author": "book_author",
    "Order": "orders",
    "Order_Item": "order_item",
    "Payment": "payment",
    "Shipping_Details": "shipping_details",
}
DATE_COLS = {"join_date", "order_date", "payment_date", "shipped_date", "delivery_date"}

if DB.exists():
    DB.unlink()

sheets = pd.read_excel(XLSX, sheet_name=None, dtype={"phone": str, "isbn": str})

with sqlite3.connect(DB) as conn:
    conn.executescript(SCHEMA.read_text())
    for sheet, table in TABLES.items():
        df = sheets[sheet]
        for col in DATE_COLS & set(df.columns):
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")  # ISO text dates
        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"{table:<18}{len(df):>6} rows")

print(f"\nSaved → {DB.name}")
