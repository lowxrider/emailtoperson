# pages/page_email_generator.py

import streamlit as st
from openai import OpenAI
from utils.db import get_connection
import pandas as pd

def get_clients(conn):
    """Загружает клиентов из БД и возвращает DataFrame."""
    return pd.read_sql_query(
        "SELECT * FROM customers;",
        conn
    )

def get_prompts(conn):
    """Загружает промпты из БД и возвращает DataFrame."""
    return pd.read_sql_query(
        "SELECT id, description, prompt FROM library_prompts;",
        conn
    )

def main():
    st.title("✉️ Генератор Email-рассылок")

    # 1) Проверка API-ключа и инициализация OpenAI
    api_key = st.session_state.get("openai_api_key", "").strip()
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return
    client = OpenAI(api_key=api_key)

    # 2) Параметры модели
    model       = st.session_state.get("model",      "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature", 0.7)
    top_p       = st.session_state.get("top_p",       0.9)
    max_tokens  = st.session_state.get("max_tokens",  256)

    # 3) Подключение к БД и загрузка данных
    conn = get_connection()
    clients_df = get_clients(conn)
    prompts_df = get_prompts(conn)

    # 4) Выбор клиентов (мультивыбор)
    client_options = {
        f"{row.first_name} {row.last_name} (ID {row.id})": row.id
        for row in clients_df.itertuples()
    }
    selected = st.multiselect(
        "Выберите клиентов для рассылки",
        options=list(client_options.keys())
    )
    selected_ids = [client_options[k] for k in selected]

    # 5) Выбор промпта
    prompt_map = {
        row.description: row.prompt
        for row in prompts_df.itertuples()
    }
    prompt_desc = st.selectbox(
        "Выберите шаблон (промпт)",
        options=list(prompt_map.keys())
    )
    template = prompt_map[prompt_desc]

    # 6) Генерация
    if st.button("🚀 Сгенерировать тему и текст письма"):
        if not selected_ids:
            st.error("Нужно выбрать хотя бы одного клиента.")
        else:
            output = []
            for cid in selected_ids:
                # берём данные клиента как словарь
                client_row = clients_df[clients_df.id == cid].iloc[0].to_dict()
                # формируем промпт, подставляя поля клиента
                filled = template.format(**client_row)

                # отправляем в LLM
                with st.spinner(f"Генерирую для {client_row['first_name']} {client_row['last_name']}..."):
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content":
                                "Вы — опытный маркетолог, пишущий продающие email-рассылки."},
                            {"role": "user", "content":
                                f"Сгенерируй тему и тело письма по следующему запросу:\n\n{filled}"}
                        ],
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens
                    )
                ans = resp.choices[0].message.content.strip()
                output.append(f"---\nКлиент: {client_row['first_name']} {client_row['last_name']} (ID {cid})\n\n{ans}")

            # 7) Вывод результатов
            st.text_area(
                "Результаты генерации",
                value="\n\n".join(output),
                height=400
            )

if __name__ == "__main__":
    main()
