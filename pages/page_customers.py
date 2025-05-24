# pages/page_customers.py

import streamlit as st
import pandas as pd
from utils.db import fetch_customers, get_connection
from datetime import datetime

def main():
    st.title("👥 CRM Клиенты")

    df = fetch_customers()
    if df.empty:
        st.info("В базе данных нет клиентов.")
        return

    st.dataframe(df, use_container_width=True)

    # Кнопка для скачивания клиентов в csv
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Скачать как CSV",
        data=csv,
        file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
