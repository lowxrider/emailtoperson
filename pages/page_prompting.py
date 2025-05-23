# pages/page_prompting.py

import streamlit as st
from openai import OpenAI

def get_openai_client():
    """Возвращает клиента OpenAI, если указан API-ключ."""
    api_key = st.session_state.get("openai_api_key", "").strip()
    if not api_key:
        st.warning("Укажите ваш OpenAI API Key в настройках LLM")
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Ошибка при инициализации клиента OpenAI: {e}")
        return None

def main():
    st.title("💬 Чат для опытного маркетолога")

    # 1. Инициализируем клиента
    client = get_openai_client()
    if client is None:
        return

    # 2. Параметры модели из сайдбара
    model       = st.session_state.get("model",      "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature", 0.7)
    top_p       = st.session_state.get("top_p",       0.9)
    max_tokens  = st.session_state.get("max_tokens",  256)

    # 3. Инициализируем историю
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": (
                    "Вы — опытный маркетолог с многолетним опытом создания "
                    "продающих и мотивирующих на покупку текстов. "
                    "Помогайте формулировать привлекательные заголовки, описания "
                    "товаров и рекламные сообщения."
                )
            }
        ]

    # 4. Отрисовываем историю
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    # 5. Принимаем ввод пользователя
    user_input = st.chat_input("Введите промпт и нажмите Enter…")
    if user_input:
        # Добавляем сообщение пользователя
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # 6. Запрашиваем ответ у модели
        with st.spinner("Генерирую ответ..."):
            resp = client.chat.completions.create(
                model=model,
                messages=st.session_state.chat_history,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        assistant_msg = resp.choices[0].message.content

        # 7. Отображаем и сохраняем ответ
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_msg})
        st.chat_message("assistant").write(assistant_msg)

if __name__ == "__main__":
    main()
