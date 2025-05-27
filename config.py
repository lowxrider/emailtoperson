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

css_guidelines = (
    "Дизайн письма (inline-CSS):\n"
    "- <div> контейнер: background-color: #ffffff; border-radius: 8px; "
    "box-shadow: 0 2px 6px rgba(0,0,0,0.1); padding: 20px; max-width:600px; margin:auto;\n"
    "- <h1>: font-family: 'Arial', sans-serif; font-size:24px; color:#333333; margin-bottom:12px;\n"
    "- <p>: font-family: 'Georgia', serif; font-size:16px; color:#555555; line-height:1.5; margin-bottom:16px;\n"
    "- <a> (CTA-кнопка): display:inline-block; text-decoration:none; "
    "background-color:#D2691E; color:#ffffff; padding:12px 24px; border-radius:4px; font-weight:bold;\n"
    "- Адаптивность: @media (max-width:600px) {{ div padding:10px; h1 font-size:20px; p font-size:14px; a padding:10px 20px; }}\n"
)