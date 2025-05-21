import sqlite3
import os
import pandas as pd

# Путь к файлу базы данных
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "customers.db")

def get_connection() -> sqlite3.Connection:
    """Создаёт папку data/ при необходимости и возвращает соединение к SQLite."""
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db(conn: sqlite3.Connection):
    """Инициализирует таблицу customers (расширенная схема)."""
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        patronymic TEXT,
        last_name TEXT,
        email TEXT,
        preferred_language TEXT,
        birth_date TEXT,
        segment TEXT,
        favorite_roast TEXT,
        bean_type TEXT,
        favorite_coffee TEXT,
        brewing_method TEXT,
        signup_date TEXT,
        last_purchase_date TEXT,
        last_purchased_coffee TEXT
    );
    """)
    conn.commit()

def reset_customers(conn: sqlite3.Connection):
    """Очищает таблицу customers."""
    conn.execute("DELETE FROM customers;")
    conn.commit()

def insert_customers(conn: sqlite3.Connection, records: list[tuple]):
    """Вставляет список кортежей клиентов в БД."""
    conn.executemany("""
    INSERT INTO customers (
        first_name, patronymic, last_name, email,
        preferred_language, birth_date, segment,
        favorite_roast, bean_type, favorite_coffee,
        brewing_method, signup_date, last_purchase_date,
        last_purchased_coffee
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);
    """, records)
    conn.commit()

def fetch_customers(conn: sqlite3.Connection) -> pd.DataFrame:
    """Возвращает всех клиентов как pandas.DataFrame."""
    return pd.read_sql_query("SELECT * FROM customers;", conn)
