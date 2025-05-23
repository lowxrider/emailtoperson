# pages/page_prompting.py

import streamlit as st
from openai import OpenAI

def get_openai_client():
    api_key = st.session_state.get("openai_api_key", "")
    if not api_key:
        st.warning("Укажите OpenAI API Key в настройках LLM")
        return None
    return OpenAI(api_key=api_key)

def send_prompt():
    """Callback для отправки промпта при нажатии Enter."""
    client = get_openai_client()
    if client is None:
        return
    prompt = st.session_state.prompt_input.strip()
    if not prompt:
        st.error("Промпт не может быть пустым.")
        return

    # Параметры модели
    model       = st.session_state.get("model",      "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature", 0.7)
    top_p       = st.session_state.get("top_p",       0.9)
    max_tokens  = st.session_state.get("max_tokens",  256)

    # Выполняем запрос
    with st.spinner("Генерируем ответ..."):
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
    answer = resp.choices[0].message.content

    # Сохраняем ответ в session_state и очищаем поле ввода
    st.session_state.last_answer = answer
    st.session_state.prompt_input = ""

def main():
    st.title("🔍 Тестирование промптов")

    # Инициализация клиента (и ранний выход, если нет ключа)
    client = get_openai_client()
    if client is None:
        return

    # Поле для последнего ответа
    last = st.session_state.get("last_answer", "")
    st.text_area(
        label="Ответ модели",
        value=last,
        height=200,
        key="last_answer_area",
        disabled=True
    )

    st.markdown("---")

    # Поле ввода нового промпта: отправка по Enter
    st.text_input(
        label="Введите промпт и нажмите Enter",
        key="prompt_input",
        on_change=send_prompt
    )

if __name__ == "__main__":
    main()
