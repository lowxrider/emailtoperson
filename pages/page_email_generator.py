# pages/page_email_generator.py

import streamlit as st
from openai import OpenAI
from utils.db import fetch_customers, fetch_prompts
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MAX_TOKENS

def main():
    st.title("✉️ Генератор Email-рассылок")

    api_key = st.session_state.get("openai_api_key", "").strip()
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return
    client = OpenAI(api_key=api_key)

    model = st.session_state.get("model", DEFAULT_MODEL)
    temperature = st.session_state.get("temperature", DEFAULT_TEMPERATURE)
    top_p = st.session_state.get("top_p", DEFAULT_TOP_P)
    max_tokens = st.session_state.get("max_tokens", DEFAULT_MAX_TOKENS)

    # Клиенты
    clients_df = fetch_customers()
    if clients_df.empty:
        st.info("Нет клиентов для рассылки.")
        return
    client_options = {
        f"{row['first_name']} {row['last_name']} (ID {row['id']})": row['id']
        for idx, row in clients_df.iterrows()
    }
    selected = st.multiselect("Выберите клиентов для рассылки", list(client_options.keys()))
    selected_ids = [client_options[k] for k in selected]

    # Промпты
    prompts_df = fetch_prompts()
    if prompts_df.empty:
        st.info("Нет промптов в библиотеке.")
        return
    prompt_map = {row['description']: row['prompt'] for idx, row in prompts_df.iterrows()}
    prompt_desc = st.selectbox("Выберите шаблон (промпт)", list(prompt_map.keys()))
    template = prompt_map[prompt_desc]

    # Генерация писем
    if st.button("🚀 Сгенерировать письма"):
        if not selected_ids:
            st.error("Нужно выбрать хотя бы одного клиента.")
        else:
            results = []
            for cid in selected_ids:
                client_row = clients_df[clients_df.id == cid].iloc[0].to_dict()
                filled_prompt = template.format(**client_row)
                with st.spinner(f"Генерируем для {client_row['first_name']} {client_row['last_name']}..."):
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "Вы — опытный маркетолог, пишущий продающие email-рассылки."},
                            {"role": "user", "content": filled_prompt}
                        ],
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens
                    )
                ans = resp.choices[0].message.content.strip()
                results.append(
                    f"---\nКлиент: {client_row['first_name']} {client_row['last_name']} (ID {cid})\n\n{ans}"
                )
            st.text_area("Результаты генерации", value="\n\n".join(results), height=400)

if __name__ == "__main__":
    main()
