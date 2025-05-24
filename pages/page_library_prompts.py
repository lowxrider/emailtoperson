# pages/page_library_prompts.py

import streamlit as st
import sqlite3
import pandas as pd
from utils.db import get_connection
from utils.generator import generate_prompts

def init_prompts_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS library_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            prompt TEXT NOT NULL
        );
    """)
    conn.commit()

def populate_initial_prompts(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) FROM library_prompts;")
    if cur.fetchone()[0] == 0:
        records = generate_prompts()
        cur.executemany(
            "INSERT INTO library_prompts (description, prompt) VALUES (?, ?);",
            records
        )
        conn.commit()

def fetch_prompts(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT id, description, prompt FROM library_prompts ORDER BY id;",
        conn
    )

def update_prompt(conn: sqlite3.Connection, prompt_id: int, desc: str, text: str):
    conn.execute(
        "UPDATE library_prompts SET description = ?, prompt = ? WHERE id = ?;",
        (desc, text, prompt_id)
    )
    conn.commit()

def delete_prompt(conn: sqlite3.Connection, prompt_id: int):
    conn.execute(
        "DELETE FROM library_prompts WHERE id = ?;",
        (prompt_id,)
    )
    conn.commit()

def main():
    st.title("📚 Библиотека промптов")

    conn = get_connection()
    init_prompts_table(conn)
    populate_initial_prompts(conn)
    df = fetch_prompts(conn)

    # Показываем сообщение о последнем обновлении, если есть
    if "updated_prompt_id" in st.session_state:
        pid = st.session_state.pop("updated_prompt_id")
        st.info(f"✅ Промпт #{pid} успешно обновлён")

    if "deleted_prompt_id" in st.session_state:
        pid = st.session_state.pop("deleted_prompt_id")
        st.success(f"🗑️ Промпт #{pid} удалён")

    if df.empty:
        st.info("Библиотека промптов пуста.")
        return

    for row in df.itertuples(index=False):
        with st.expander(f"#{row.id} — {row.description}", expanded=False):
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

            col1, col2 = st.columns(2)
            # Сохранить изменения
            with col1:
                if st.button("💾 Сохранить", key=f"save_{row.id}"):
                    update_prompt(conn, row.id, new_desc, new_text)
                    # Устанавливаем флаг и перезагружаем
                    st.session_state["updated_prompt_id"] = row.id
                    st.rerun()
            # Удалить промпт
            with col2:
                if st.button("🗑️ Удалить", key=f"del_{row.id}"):
                    delete_prompt(conn, row.id)
                    st.session_state["deleted_prompt_id"] = row.id
                    st.rerun()

if __name__ == "__main__":
    main()
