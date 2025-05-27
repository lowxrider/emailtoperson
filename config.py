# config.py

DB_PATH = "data/app.db"

DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.3
DEFAULT_MAX_TOKENS = 600

PAGES = {
    "Email Generator":     "page_email_generator",
    "CRM Клиенты":         "page_customers",
    "Библиотека промптов": "page_library_prompts",
    "Тест промптов":       "page_prompting",
}