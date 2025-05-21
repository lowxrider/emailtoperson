# pages/page_prompting.py

import streamlit as st
import datetime
from openai import OpenAI
from utils.db import get_connection

# Диалог для добавления промпта в библиотеку
@st.dialog("Добавить промпт в библиотеку")
def show_add_prompt_dialog(prompt_text: str):
    st.write("Добавить следующий промпт в библиотеку:")
    st.text_area("Промпт (не редактировать)", value=prompt_text, disabled=True, height=150)
    desc = st.text_input("Краткое описание", "")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Сохранить"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO library_prompts (description, prompt) VALUES (?, ?);",
                (desc, prompt_text),
            )
            conn.commit()
            st.success("Промпт добавлен в библиотеку")
            st.rerun()
    with col2:
        if st.button("Отмена"):
            st.rerun()

def main():
    st.title("🤖 Чат с LLM")

    # Проверяем, что API-ключ задан
    api_key = st.session_state.get("openai_api_key", "")
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return

    client = OpenAI(api_key=api_key)
    model       = st.session_state.get("model", "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature", 0.7)
    top_p       = st.session_state.get("top_p", 0.9)
    max_tokens  = st.session_state.get("max_tokens", 256)

    # Инициализация БД истории и библиотеки промптов
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS last_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            response TEXT,
            timestamp TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS library_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            prompt TEXT NOT NULL
        );
    """)
    conn.commit()

    # История чата
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "Вы — помощник по генерации email-рассылок."}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Введите сообщение...")
    if not user_input:
        return

    # Отображаем и отправляем в LLM
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.spinner("Генерирую ответ..."):
        resp = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
    assistant_msg = resp.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
    st.chat_message("assistant").write(assistant_msg)

    # Сохраняем историю
    cursor.execute(
        "INSERT INTO last_prompts (prompt, response, timestamp) VALUES (?, ?, ?);",
        (user_input, assistant_msg, datetime.datetime.now().isoformat())
    )
    conn.commit()

    # Кнопка добавления в библиотеку промптов
    if st.button("➕ Добавить этот промпт в библиотеку"):
        show_add_prompt_dialog(assistant_msg)

if __name__ == "__main__":
    main()
