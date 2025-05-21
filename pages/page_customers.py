import streamlit as st
from utils.db import get_connection, init_db, reset_customers, insert_customers, fetch_customers
from utils.generator import generate_customers

st.title("👥 Клиенты (CRM)")

# Подготовка БД
conn = get_connection()
init_db(conn)
reset_customers(conn)

# Генерация и сохранение
clients = generate_customers(100)
insert_customers(conn, clients)

# Загрузка и показ
df = fetch_customers(conn)
st.dataframe(df)

# Скачать CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Скачать CSV", data=csv, file_name="customers.csv", mime="text/csv")
