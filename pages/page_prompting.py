# pages/page_prompting.py

import streamlit as st
from openai import OpenAI

def get_openai_client():
    """Проверяет, что API-ключ введён, и возвращает клиента."""
    api_key = st.session_state.get("openai_api_key", "")
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return None
    return OpenAI(api_key=api_key)

def main():
    st.title("🔍 Тестирование промптов")

    # 1) Инициализация клиента
    client = get_openai_client()
    if client is None:
        return

    # 2) Параметры модели из сайдбара
    model       = st.session_state.get("model",      "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature", 0.7)
    top_p       = st.session_state.get("top_p",       0.9)
    max_tokens  = st.session_state.get("max_tokens",  256)

    # 3) Поле ввода промпта
    prompt = st.text_area(
        label="Введите промпт для тестирования",
        value="",
        height=150
    )

    # 4) Кнопка отправки
    if st.button("🚀 Отправить промпт"):
        if not prompt.strip():
            st.error("Промпт не может быть пустым.")
        else:
            with st.spinner("Генерируем ответ..."):
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens
                )
            answer = resp.choices[0].message.content
            st.markdown("**Ответ модели:**")
            st.write(answer)

if __name__ == "__main__":
    main()
