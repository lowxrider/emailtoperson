# pages/page_email_generator.py

import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from utils.db import fetch_customers, fetch_prompts
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MAX_TOKENS
from datetime import datetime, timedelta

def main():
    st.title("✉️ Генератор HTML Email-рассылок")

    # 1) Проверка API-ключа
    api_key = st.session_state.get("openai_api_key", "").strip()
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return
    client = OpenAI(api_key=api_key)

    # 2) Параметры модели
    model       = st.session_state.get("model", DEFAULT_MODEL)
    temperature = st.session_state.get("temperature", DEFAULT_TEMPERATURE)
    top_p       = st.session_state.get("top_p", DEFAULT_TOP_P)
    max_tokens  = st.session_state.get("max_tokens", DEFAULT_MAX_TOKENS)

    # 3) Загрузка клиентов и промптов из БД
    customers_df = fetch_customers()
    if customers_df.empty:
        st.info("В базе нет клиентов для рассылки.")
        return

    prompts_df = fetch_prompts()
    if prompts_df.empty:
        st.info("В библиотеке промптов нет записей.")
        return

    # 4) Мультивыбор клиентов
    customer_map = {
        f"{r['first_name']} {r['last_name']} (ID {r['id']})": r['id']
        for _, r in customers_df.iterrows()
    }
    selected_clients = st.multiselect(
        "Выберите клиентов для рассылки",
        options=list(customer_map.keys())
    )
    selected_ids = [customer_map[name] for name in selected_clients]

    # 5) Выпадающий список промптов
    prompt_map = {
        r['description']: r['prompt']
        for _, r in prompts_df.iterrows()
    }
    chosen_desc   = st.selectbox("Выберите шаблон письма", list(prompt_map.keys()))
    prompt_template = prompt_map[chosen_desc]

    # 6) Генерация и вывод HTML-email
    if st.button("🚀 Сгенерировать Email"):
        if not selected_ids:
            st.error("Нужно выбрать хотя бы одного клиента.")
        else:
            html_blocks = []
            for cid in selected_ids:
                client_row = customers_df[customers_df.id == cid].iloc[0].to_dict()

                # вычисляем deadline — через неделю после дня рождения
                bd = datetime.fromisoformat(client_row['birth_date'])
                deadline = (bd + timedelta(days=7)).strftime("%d.%m.%Y")
                client_row['deadline'] = deadline

                # подставляем все поля в шаблон
                filled_prompt = prompt_template.format(**client_row)

                with st.spinner(f"Генерирую письмо для {client_row['first_name']}..."):
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content":
                                "Вы — опытный маркетолог, создающий HTML-email. "
                                "Верните готовый HTML-фрагмент письма: тема в <h1>, "
                                "тело в <div> с inline-CSS, без <html>/<body>."},
                            {"role": "user", "content": filled_prompt}
                        ],
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                    )
                html_content = resp.choices[0].message.content.strip()
                html_blocks.append(f"<section style='margin-bottom:24px'>{html_content}</section>")

            # объединяем и показываем результат
            final_html = "<div style='background:#f9f9f9;padding:16px;border-radius:8px'>" + "".join(html_blocks) + "</div>"
            components.html(final_html, height=600, scrolling=True)

if __name__ == "__main__":
    main()
