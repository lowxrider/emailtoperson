import streamlit as st
from openai import OpenAI
from utils.db import get_connection

st.set_page_config(page_title="Email to Person App", layout="wide")

# --- Настройки LLM в сайдбаре ---
st.sidebar.header("Настройки LLM")

# API Key с подсветкой
st.session_state.setdefault("openai_api_key", "")
st.session_state.setdefault("api_saved", False)
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=st.session_state.openai_api_key
)
col1, col2 = st.sidebar.columns(2)
if col1.button("Сохранить"):
    st.session_state.openai_api_key = api_key
    st.session_state.api_saved = True
if col2.button("Очистить"):
    st.session_state.openai_api_key = ""
    st.session_state.api_saved = False

# Подсветка поля
if not st.session_state.openai_api_key:
    st.sidebar.markdown(
        """<style>
        div[data-testid="stTextInput"] input {
            border: 2px solid #f44336 !important;
            box-shadow: 0 0 5px rgba(244, 67, 54, .5);
        }
        </style>""",
        unsafe_allow_html=True
    )
elif st.session_state.api_saved:
    st.sidebar.markdown(
        """<style>
        div[data-testid="stTextInput"] input {
            border: 2px solid #4CAF50 !important;
            box-shadow: 0 0 5px rgba(76, 175, 80, .5);
        }
        </style>""",
        unsafe_allow_html=True
    )

# --- Выбор модели ---
fallback_models = ["gpt-3.5-turbo", "text-davinci-003"]
available_models = fallback_models.copy()
models_disabled = True

if st.session_state.openai_api_key:
    try:
        client = OpenAI(api_key=st.session_state.openai_api_key)
        resp = client.models.list()
        available_models = [m.id for m in resp.data] or fallback_models
        models_disabled = False
    except Exception:
        # оставляем fallback и помечаем как disabled
        available_models = fallback_models.copy()
        models_disabled = True

st.session_state.setdefault("model", available_models[0])
st.session_state.model = st.sidebar.selectbox(
    "Модель",
    available_models,
    index=available_models.index(st.session_state.model),
    disabled=models_disabled
)

# --- Параметры модели ---
for key, label, widget, opts in [
    ("temperature", "Температура (0–1)",      st.sidebar.slider,       {"min_value":0.0, "max_value":1.0, "step":0.01, "value":0.7}),
    ("top_p",       "Креативность (top_p)",   st.sidebar.slider,       {"min_value":0.0, "max_value":1.0, "step":0.01, "value":0.3}),
    ("max_tokens",  "Количество токенов",     st.sidebar.number_input, {"min_value":1,   "max_value":4096,  "step":1,   "value":256}),
]:
    st.session_state.setdefault(key, opts["value"])
    st.session_state[key] = widget(
        label,
        value=st.session_state[key],
        **{k:v for k,v in opts.items() if k!="value"}
    )

# --- Навигация ---
pages = [
    st.Page("pages/page_email_generator.py", title="✉️ Email Generator"),
    st.Page("pages/page_customers.py",       title="👥 Клиенты (CRM)"),
    st.Page("pages/page_library_prompts.py", title="📚 Библиотека промптов"),
    st.Page("pages/page_prompting.py",       title="🤖 Промптинг"),
]
st.navigation(pages=pages, position="sidebar", expanded=True).run()
