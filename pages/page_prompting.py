# pages/page_prompting.py

import streamlit as st
import datetime
from openai import OpenAI
from utils.db import get_connection

def init_db():
    """Инициализирует таблицы для истории и библиотеки промптов."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS last_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            response TEXT,
            timestamp TEXT
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS library_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            prompt TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn

def get_openai_client():
    """Проверяет наличие API-ключа и возвращает клиент OpenAI."""
    api_key = st.session_state.get("openai_api_key", "")
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return None
    return OpenAI(api_key=api_key)

def render_chat_history():
    """Отрисовывает историю чата из session_state."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "Вы — помощник по генерации email-рассылок."}
        ]
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

def process_user_input(client, conn):
    """Принимает ввод пользователя, отправляет в LLM, сохраняет историю и выводит ответ."""
    user_input = st.chat_input("Введите сообщение…")
    if not user_input:
        return None, None

    # Сохраняем и выводим
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Запрос к LLM
    model       = st.session_state.get("model", "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature", 0.7)
    top_p       = st.session_state.get("top_p", 0.9)
    max_tokens  = st.session_state.get("max_tokens", 256)

    with st.spinner("Генерирую ответ..."):
        resp = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
    assistant_msg = resp.choices[0].message.content

    # Сохраняем и выводим
    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
    st.chat_message("assistant").write(assistant_msg)

    # Фиксируем в истории
    conn.execute(
        "INSERT INTO last_prompts (prompt, response, timestamp) VALUES (?, ?, ?);",
        (user_input, assistant_msg, datetime.datetime.now().isoformat())
    )
    conn.commit()

    return user_input, assistant_msg

def save_prompt_to_library(conn, text: str, description: str = ""):
    """Сохраняет переданный текст в библиотеку промптов."""
    conn.execute(
        "INSERT INTO library_prompts (description, prompt) VALUES (?, ?);",
        (description, text)
    )
    conn.commit()
    st.success("Промпт сохранён в библиотеку промптов")

def main():
    st.title("🤖 Чат с LLM")

    # 1. Инициализация БД
    conn = init_db()

    # 2. Инициализация OpenAI
    client = get_openai_client()
    if client is None:
        return

    # 3. Отрисовка истории
    render_chat_history()

    # 4. Обработка ввода пользователя
    user_input, assistant_msg = process_user_input(client, conn)
    if user_input is None:
        return

    # 5. Кнопка сохранения запроса пользователя
    if st.button("➕ Сохранить запрос в библиотеку"):
        save_prompt_to_library(conn, user_input)

if __name__ == "__main__":
    main()
