# pages/page_customers.py

import streamlit as st
from utils.db import get_connection, init_db, reset_customers, insert_customers, fetch_customers
from utils.generator import generate_customers

def main():
    st.title("👥 Клиенты (CRM)")

    # 1. Подготовка БД
    conn = get_connection()
    init_db(conn)

    # 2. Проверяем, есть ли уже клиенты
    df = fetch_customers(conn)
    if df.empty:
        # Если таблица пуста, генерируем и сохраняем
        clients = generate_customers(100)
        insert_customers(conn, clients)
        # Перечитываем
        df = fetch_customers(conn)
    else:
        st.info("Загружены существующие данные клиентов из базы.")

    # 3. Показ данных
    st.dataframe(df)

    # 4. Скачать CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Скачать CSV",
        data=csv,
        file_name="customers.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
