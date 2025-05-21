# pages/page_prompting.py

import streamlit as st
import datetime
from openai import OpenAI
from utils.db import get_connection

def main():
    st.title("🤖 Чат с LLM")

    # Проверяем, что API-ключ задан
    api_key = st.session_state.get("openai_api_key", "")
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return

    # Создаём клиента OpenAI
    client = OpenAI(api_key=api_key)
    model       = st.session_state.get("model", "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature", 0.7)
    top_p       = st.session_state.get("top_p", 0.9)
    max_tokens  = st.session_state.get("max_tokens", 256)

    # Подготовка БД
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

    # Показываем историю
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Ввод нового сообщения
    user_input = st.chat_input("Введите сообщение...")
    if user_input:
        # Сохраняем и отображаем запрос пользователя
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Отправляем на LLM
        with st.spinner("Генерирую ответ..."):
            resp = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        assistant_msg = resp.choices[0].message.content

        # Сохраняем и отображаем ответ ассистента
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
        st.chat_message("assistant").write(assistant_msg)

        # Сохраняем в историю запросов и ответов
        conn.execute(
            "INSERT INTO last_prompts (prompt, response, timestamp) VALUES (?, ?, ?);",
            (user_input, assistant_msg, datetime.datetime.now().isoformat())
        )
        conn.commit()

        # Кнопка мгновенного добавления запроса (user_input) в библиотеку промптов
        if st.button("➕ Сохранить этот запрос в библиотеку", key="save_user_prompt"):
            conn.execute(
                "INSERT INTO library_prompts (description, prompt) VALUES (?, ?);",
                ("", user_input),
            )
            conn.commit()
            st.success("Запрос добавлен в библиотеку промптов")

    # (Опционально) кнопку перехода к странице library_prompts
    if st.button("Перейти к библиотеке промптов"):
        # если вы используете session_state для навигации
        st.session_state["_page"] = "page_library_prompts"
        st.rerun()


if __name__ == "__main__":
    main()
