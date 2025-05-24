# utils/db.py

import sqlite3
import pandas as pd
from pathlib import Path
from config import DB_PATH
from utils.generator import generate_customers, generate_prompts

def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db_and_data():
    conn = get_connection()
    c = conn.cursor()
    # Таблица клиентов
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT, last_name TEXT, patronymic TEXT,
            language TEXT, birth_date TEXT, segment TEXT,
            favorite_roast TEXT, favorite_coffee_type TEXT,
            favorite_coffee TEXT, brew_method TEXT,
            signup_date TEXT, last_purchase TEXT, last_coffee_bought TEXT
        )
    """)
    c.execute("SELECT COUNT(*) FROM customers")
    if c.fetchone()[0] == 0:
        customers = generate_customers(100)
        c.executemany("""
            INSERT INTO customers (
                first_name, last_name, patronymic, language, birth_date,
                segment, favorite_roast, favorite_coffee_type, favorite_coffee,
                brew_method, signup_date, last_purchase, last_coffee_bought
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, customers)
        conn.commit()

    # Таблица промптов
    c.execute("""
        CREATE TABLE IF NOT EXISTS library_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            prompt TEXT NOT NULL
        )
    """)
    c.execute("SELECT COUNT(*) FROM library_prompts")
    if c.fetchone()[0] == 0:
        prompts = generate_prompts()
        c.executemany(
            "INSERT INTO library_prompts (description, prompt) VALUES (?, ?)", prompts
        )
        conn.commit()

def fetch_customers():
    return pd.read_sql("SELECT * FROM customers", get_connection())

def fetch_prompts():
    return pd.read_sql("SELECT * FROM library_prompts", get_connection())

def insert_prompt(description, prompt):
    conn = get_connection()
    conn.execute("INSERT INTO library_prompts (description, prompt) VALUES (?, ?)", (description, prompt))
    conn.commit()

def update_prompt(prompt_id, description, prompt):
    conn = get_connection()
    conn.execute("UPDATE library_prompts SET description=?, prompt=? WHERE id=?", (description, prompt, prompt_id))
    conn.commit()

def delete_prompt(prompt_id):
    conn = get_connection()
    conn.execute("DELETE FROM library_prompts WHERE id=?", (prompt_id,))
    conn.commit()
