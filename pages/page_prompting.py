# pages/page_prompting.py

import streamlit as st
from openai import OpenAI
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MAX_TOKENS

def main():
    st.title("🤖 Тест промптов (чат)")

    api_key = st.session_state.get("openai_api_key", "").strip()
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return
    client = OpenAI(api_key=api_key)

    model = st.session_state.get("model", DEFAULT_MODEL)
    temperature = st.session_state.get("temperature", DEFAULT_TEMPERATURE)
    top_p = st.session_state.get("top_p", DEFAULT_TOP_P)
    max_tokens = st.session_state.get("max_tokens", DEFAULT_MAX_TOKENS)

    # Инициализация истории чата
    if "prompt_chat_history" not in st.session_state:
        st.session_state.prompt_chat_history = []

    # История чата сверху
    for m in st.session_state.prompt_chat_history:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    # Поле ввода
    prompt = st.chat_input("Введите промпт...")
    if prompt:
        st.session_state.prompt_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.spinner("Генерирую ответ..."):
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Вы — опытный маркетолог, создающий продающие тексты."}
                ] + st.session_state.prompt_chat_history,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        answer = resp.choices[0].message.content
        st.session_state.prompt_chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)

if __name__ == "__main__":
    main()
