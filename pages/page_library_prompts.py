# pages/page_library_prompts.py

import streamlit as st
import sqlite3
import pandas as pd
from utils.db import get_connection
from utils.generator import generate_prompts

def init_prompts_table(conn: sqlite3.Connection):
    """Создаёт таблицу library_prompts, если её нет."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS library_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            prompt TEXT NOT NULL
        );
    """)
    conn.commit()

def populate_initial_prompts(conn: sqlite3.Connection):
    """
    Если таблица пуста, заполнить её базовыми промптами
    из функции generate_prompts().
    """
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) FROM library_prompts;")
    if cur.fetchone()[0] == 0:
        records = generate_prompts()  # [(description, prompt), ...]
        cur.executemany(
            "INSERT INTO library_prompts (description, prompt) VALUES (?, ?);",
            records
        )
        conn.commit()

def fetch_prompts(conn: sqlite3.Connection) -> pd.DataFrame:
    """Загружает все промпты из БД."""
    return pd.read_sql_query(
        "SELECT id, description, prompt FROM library_prompts ORDER BY id;",
        conn
    )

def update_prompt(conn: sqlite3.Connection, prompt_id: int, desc: str, text: str):
    """Обновляет запись промпта в БД."""
    conn.execute(
        "UPDATE library_prompts SET description = ?, prompt = ? WHERE id = ?;",
        (desc, text, prompt_id)
    )
    conn.commit()

def delete_prompt(conn: sqlite3.Connection, prompt_id: int):
    """Удаляет промпт из БД."""
    conn.execute(
        "DELETE FROM library_prompts WHERE id = ?;",
        (prompt_id,)
    )
    conn.commit()

def main():
    st.title("📚 Библиотека промптов")

    # 1. Подключаемся к БД и инициализируем таблицу
    conn = get_connection()
    init_prompts_table(conn)
    populate_initial_prompts(conn)

    # 2. Загружаем данные
    df = fetch_prompts(conn)
    st.session_state["library_prompts_df"] = df  # делают доступными во всём приложении

    # 3. Если пусто — подсказка
    if df.empty:
        st.info("В библиотеке промптов пока нет записей.")
        return

    # 4. Отображаем каждый промпт с возможностью редактировать/удалять
    for row in df.itertuples(index=False):
        with st.expander(f"#{row.id}: {row.description}", expanded=False):
            # Инпуты для редактирования
            new_desc = st.text_input(
                "Краткое описание",
                value=row.description,
                key=f"desc_{row.id}"
            )
            new_text = st.text_area(
                "Текст промпта",
                value=row.prompt,
                key=f"text_{row.id}",
                height=120
            )
            # Кнопки
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Сохранить", key=f"save_{row.id}"):
                    update_prompt(conn, row.id, new_desc, new_text)
                    st.success(f"Промпт #{row.id} обновлён")
                    st.rerun()
            with col2:
                if st.button("🗑️ Удалить", key=f"del_{row.id}"):
                    delete_prompt(conn, row.id)
                    st.success(f"Промпт #{row.id} удалён")
                    st.rerun()

if __name__ == "__main__":
    main()
