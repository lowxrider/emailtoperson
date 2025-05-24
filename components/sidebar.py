# components/sidebar.py

import streamlit as st
from config import (
    DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MAX_TOKENS
)
from openai import OpenAI

def fetch_models():
    key = st.session_state.get("openai_api_key", "")
    if not key:
        return [DEFAULT_MODEL]
    try:
        client = OpenAI(api_key=key)
        resp = client.models.list()
        return [m.id for m in resp.data]
    except Exception:
        return [DEFAULT_MODEL]

def render_sidebar(llm_settings_only=False):
    st.sidebar.header("Настройки LLM")
    st.session_state.setdefault("openai_api_key", "")
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key)
    if api_key != st.session_state.openai_api_key:
        st.session_state.openai_api_key = api_key

    model_list = fetch_models()
    st.session_state.setdefault("model", DEFAULT_MODEL)
    st.session_state.model = st.sidebar.selectbox("Модель", model_list, index=0)

    st.session_state.setdefault("temperature", DEFAULT_TEMPERATURE)
    st.session_state.temperature = st.sidebar.slider(
        "Температура", 0.0, 1.0, st.session_state.temperature, 0.01
    )
    st.session_state.setdefault("top_p", DEFAULT_TOP_P)
    st.session_state.top_p = st.sidebar.slider(
        "Top-p", 0.0, 1.0, st.session_state.top_p, 0.01
    )
    st.session_state.setdefault("max_tokens", DEFAULT_MAX_TOKENS)
    st.session_state.max_tokens = st.sidebar.number_input(
        "Max tokens", 1, 4096, st.session_state.max_tokens
    )
