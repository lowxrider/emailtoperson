# pages/page_prompting.py

import streamlit as st
import datetime
from openai import OpenAI
from utils.db import get_connection

# Диалог для добавления промпта в библиотеку
@st.dialog("Добавить промпт в библиотеку")
def show_add_prompt_dialog(prompt_text: str):
    st.write("Добавить следующий промпт в библиотеку:")
    st.text_area("Промпт (только чтение)", value=prompt_text, disabled=True, height=150)
    desc = st.text_input("Краткое описание", key="add_prompt_desc")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Сохранить"):
            conn = get_connection()
            conn.execute(
                "INSERT INTO library_prompts (description, prompt) VALUES (?, ?);",
                (desc, prompt_text),
            )
            conn.commit()
            st.success("Промпт добавлен в библиотеку")
            # Закрываем диалог, удаляя флаг
            del st.session_state["add_prompt_text"]
    with col2:
        if st.button("Отмена"):
            # Просто закрываем диалог
            del st.session_state["add_prompt_text"]

def main():
    st.title("🤖 Чат с LLM")

    # Проверка API-ключа
    api_key = st.session_state.get("openai_api_key", "")
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return

    # Инициализация клиента OpenAI
    client = OpenAI(api_key=api_key)
    model       = st.session_state.get("model", "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature", 0.7)
    top_p       = st.session_state.get("top_p", 0.9)
    max_tokens  = st.session_state.get("max_tokens", 256)

    # Подготовка БД истории и библиотеки
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

    # Инициализируем историю чата
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "Вы — помощник по генерации email-рассылок."}
        ]

    # Отображаем историю диалога
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Поле ввода от пользователя
    user_input = st.chat_input("Введите сообщение...")
    if user_input:
        # Добавляем сообщение пользователя
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Отправляем в LLM
        with st.spinner("Генерирую ответ..."):
            resp = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        assistant_msg = resp.choices[0].message.content

        # Показываем ответ
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
        st.chat_message("assistant").write(assistant_msg)

        # Сохраняем в историю запросов
        conn.execute(
            "INSERT INTO last_prompts (prompt, response, timestamp) VALUES (?, ?, ?);",
            (user_input, assistant_msg, datetime.datetime.now().isoformat())
        )
        conn.commit()

        # Кнопка для добавления в библиотеку
        if st.button("➕ Добавить этот промпт в библиотеку", key="add_prompt_btn"):
            st.session_state["add_prompt_text"] = assistant_msg

    # Если флаг установлен — показываем диалог
    if "add_prompt_text" in st.session_state:
        show_add_prompt_dialog(st.session_state["add_prompt_text"])


if __name__ == "__main__":
    main()
