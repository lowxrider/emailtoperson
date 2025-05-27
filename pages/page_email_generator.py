# pages/page_email_generator.py

import streamlit as st
from openai import OpenAI
from utils.db import fetch_customers, fetch_prompts
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MAX_TOKENS
import streamlit.components.v1 as components

def main():
    st.title("✉️ Генератор Email-рассылок (HTML-превью)")

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
    prompts_df   = fetch_prompts()

    # 4) Мультивыбор клиентов
    client_map = {
        f"{row['first_name']} {row['last_name']} (ID {row['id']})": row["id"]
        for _, row in customers_df.iterrows()
    }
    selected = st.multiselect(
        "Выберите клиентов для рассылки", options=list(client_map.keys())
    )
    selected_ids = [client_map[k] for k in selected]

    # 5) Выбор шаблона промпта
    prompt_map = {row["description"]: row["prompt"] for _, row in prompts_df.iterrows()}
    chosen_desc = st.selectbox("Выберите шаблон (промпт)", options=list(prompt_map.keys()))
    template    = prompt_map[chosen_desc]

    # 6) Генерация HTML-письма
    if st.button("🚀 Сгенерировать письмо"):
        if not selected_ids:
            st.error("Нужно выбрать хотя бы одного клиента.")
        else:
            html_blocks = []
            for cid in selected_ids:
                client_row = customers_df[customers_df.id == cid].iloc[0].to_dict()
                filled_prompt = template.format(**client_row)

                with st.spinner(f"Генерирую письмо для {client_row['first_name']}..."):
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Вы — опытный маркетолог, писатель продающих и мотивирующих email-рассылок."
                                )
                            },
                            {"role": "user", "content": filled_prompt}
                        ],
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                    )

                # Получаем текст ответа
                answer = resp.choices[0].message.content.strip()
                # Оборачиваем ответ в простой HTML-блок
                html = f"""
<div style="
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 24px;
    font-family: Arial, sans-serif;
">
  <h2 style="margin-top:0; color:#333;">
    Письмо для {client_row['first_name']} {client_row['last_name']}
  </h2>
  <div style="white-space: pre-wrap; line-height:1.5; color:#444;">
    {answer}
  </div>
</div>
"""
                html_blocks.append(html)

            # Собираем всё вместе и показываем в компоненте
            full_html = (
                "<div style='background:#f7f7f7; padding:20px;'>"
                + "".join(html_blocks) +
                "</div>"
            )
            components.html(full_html, height=700, scrolling=True)

if __name__ == "__main__":
    main()
