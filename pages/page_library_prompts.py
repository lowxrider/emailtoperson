# pages/page_library_prompts.py

import streamlit as st
from utils.db import fetch_prompts, insert_prompt, update_prompt, delete_prompt

def main():
    st.title("📚 Библиотека промптов")

    # Добавление нового промпта
    with st.expander("➕ Добавить новый промпт", expanded=False):
        new_desc = st.text_input("Краткое описание", key="new_desc")
        new_prompt = st.text_area("Текст промпта", key="new_prompt")
        if st.button("Добавить промпт"):
            if not new_desc or not new_prompt:
                st.error("Поля не могут быть пустыми")
            else:
                insert_prompt(new_desc, new_prompt)
                st.success("Промпт добавлен")
                st.rerun()

    df = fetch_prompts()
    if df.empty:
        st.info("Библиотека промптов пуста.")
        return

    for idx, row in df.iterrows():
        with st.expander(f"#{row['id']} — {row['description']}", expanded=False):
            desc = st.text_input("Краткое описание", value=row['description'], key=f"desc_{row['id']}")
            prompt = st.text_area("Текст промпта", value=row['prompt'], key=f"prompt_{row['id']}", height=100)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Сохранить", key=f"save_{row['id']}"):
                    update_prompt(row['id'], desc, prompt)
                    st.info(f"Промпт #{row['id']} обновлён")
                    st.rerun()
            with col2:
                if st.button("🗑️ Удалить", key=f"del_{row['id']}"):
                    delete_prompt(row['id'])
                    st.success(f"Промпт #{row['id']} удалён")
                    st.rerun()

if __name__ == "__main__":
    main()
