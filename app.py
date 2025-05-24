# app.py

import streamlit as st
from utils.db import init_db_and_data
from config import PAGES
from components.sidebar import render_sidebar

st.set_page_config(page_title="Email to Person App", layout="wide")
init_db_and_data()

pages = [
    st.Page(f"pages/{mod}.py", title=name)
    for name, mod in PAGES.items()
]
render_sidebar(llm_settings_only=True)
st.navigation(pages=pages, position="sidebar", expanded=True).run()
