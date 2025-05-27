# pages/page_email_generator.py

import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from utils.db import fetch_customers, fetch_prompts
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MAX_TOKENS
from datetime import datetime, timedelta
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, html_body: str):
    """
    Отправляет HTML-письмо через SMTP.
    Параметры SMTP должны быть заданы в st.secrets['smtp']:
    server, port, user, password, from_email.
    """
    smtp_conf = st.secrets["smtp"]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_conf["from_email"]
    msg["To"]   = to_email
    part = MIMEText(html_body, "html")
    msg.attach(part)
    with smtplib.SMTP_SSL(smtp_conf["server"], smtp_conf["port"]) as server:
        server.login(smtp_conf["user"], smtp_conf["password"])
        server.sendmail(smtp_conf["from_email"], to_email, msg.as_string())

def main():
    st.title("✉️ Генератор и рассылка HTML Email")

    # 1. Проверка API-ключа
    api_key = st.session_state.get("openai_api_key", "").strip()
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return
    client = OpenAI(api_key=api_key)

    # 2. Параметры модели
    model       = st.session_state.get("model", DEFAULT_MODEL)
    temperature = st.session_state.get("temperature", DEFAULT_TEMPERATURE)
    top_p       = st.session_state.get("top_p", DEFAULT_TOP_P)
    max_tokens  = st.session_state.get("max_tokens", DEFAULT_MAX_TOKENS)

    # 3. Загрузка данных
    customers_df = fetch_customers()
    prompts_df   = fetch_prompts()
    if customers_df.empty:
        st.info("В базе нет клиентов.")
        return
    if prompts_df.empty:
        st.info("В библиотеке промптов нет записей.")
        return

    # 4. Интерфейс выбора
    customer_map = {
        f"{r['first_name']} {r['last_name']} (ID {r['id']})": r['id']
        for _, r in customers_df.iterrows()
    }
    selected_clients = st.multiselect(
        "Выберите клиентов для рассылки", list(customer_map.keys())
    )
    selected_ids = [customer_map[name] for name in selected_clients]

    prompt_map = {
        r['description']: r['prompt']
        for _, r in prompts_df.iterrows()
    }
    chosen_desc     = st.selectbox("Выберите шаблон письма", list(prompt_map.keys()))
    prompt_template = prompt_map[chosen_desc]

    # 5. Опция отправки на почту
    send_via_email = st.checkbox("Отправить письма на email клиентов")

    # 6. Генерация и (опционально) отправка
    if st.button("🚀 Сгенерировать Email"):
        if not selected_ids:
            st.error("Нужно выбрать хотя бы одного клиента.")
        else:
            html_output = ""
            for cid in selected_ids:
                client_row = customers_df[customers_df.id == cid].iloc[0].to_dict()

                # Вычисляем deadline
                bd = datetime.fromisoformat(client_row['birth_date'])
                client_row['deadline'] = (bd + timedelta(days=7)).strftime("%d.%m")

                # Формируем промпт
                filled_prompt = prompt_template.format(**client_row)

                with st.spinner(f"Генерирую письмо для {client_row['first_name']}..."):
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content":
                                "Вы — опытный маркетолог и email-дизайнер. Верните готовый HTML-фрагмент письма: "
                                "тема в <h1>, тело в <div> с inline-CSS, без <html>/<body>."},
                            {"role": "user", "content": filled_prompt}
                        ],
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                    )
                html_block = resp.choices[0].message.content.strip()

                # Собираем общий вывод
                html_output += f"<section style='margin-bottom:24px'>{html_block}</section>"

                # При необходимости — отправляем письмо
                if send_via_email:
                    # Извлекаем subject из <h1>
                    m = re.search(r"<h1.*?>(.*?)</h1>", html_block, re.IGNORECASE|re.DOTALL)
                    subject = m.group(1).strip() if m else f"Email для {client_row['first_name']}"
                    # Отправка
                    try:
                        send_email(client_row['email'], subject, html_block)
                        st.success(f"Письмо отправлено: {client_row['email']}")
                    except Exception as e:
                        st.error(f"Ошибка при отправке на {client_row['email']}: {e}")

            # Выводим результат в окне HTML-превью
            final_html = (
                "<div style='background:#f9f9f9;padding:16px;border-radius:8px;max-width:800px;'>"
                + html_output +
                "</div>"
            )
            components.html(final_html, height=700, scrolling=True)

if __name__ == "__main__":
    main()
