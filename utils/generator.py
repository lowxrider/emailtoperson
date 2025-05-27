# utils/generator.py

import random
from faker import Faker

from datetime import date

def generate_customers(n=100):
    fake = Faker('ru_RU')
    segments = [
        'Новичок', 'Классик', 'Гурман', 'Крепкий вкус', 'Фильтровик',
        'Премиум', 'Оптовик', 'Подарочный', 'Постоянный', 'Сезонный'
    ]
    roasts = ['Светлая', 'Средняя', 'Тёмная']
    coffee_types = ['Арабика', 'Бленд', 'Робуста']
    brew_methods = ['Френч-пресс', 'Воронка', 'Турка', 'Гейзер', 'Автомат']
    coffees = [
        "Бразилия Можиана", "Бразилия Сантос", "Колумбия Хуила", "Колумбия Супремо",
        "Эфиопия Иргачефф", "Эфиопия Сидамо", "Кения AA", "Кения AB",
        "Суматра Манделинг", "Суматра Линтонг", "Уганда Бугишу", "Гватемала Антигуа"
    ]
    sources = ["мобильное приложение", "веб-сайт"]
    customers = []
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        patronymic = fake.middle_name()
        language = 'ru'
        birth_date_dt = fake.date_of_birth(minimum_age=18, maximum_age=65)
        birth_date = birth_date_dt.isoformat()
        segment = random.choice(segments)
        favorite_roast = random.choice(roasts)
        favorite_coffee_type = random.choice(coffee_types)
        favorite_coffee = random.choice(coffees)
        brew_method = random.choice(brew_methods)
        signup_date_dt = fake.date_between(start_date='-3y', end_date='-1y')
        signup_date = signup_date_dt.isoformat()
        last_purchase_dt = fake.date_between(start_date=signup_date_dt, end_date=date.today())
        last_purchase = last_purchase_dt.isoformat()
        last_coffee_bought = random.choice(coffees)
        discount = random.choice([0, 5, 10, 15, 20, 25, 30])
        email = "testforproject123456789@gmail.com"
        total_orders = random.randint(1, 50)
        recommendations = ', '.join(random.sample(coffees, k=random.choice([2, 3])))
        order_source = random.choice(sources)
        customers.append((
            first_name, last_name, patronymic, language, birth_date,
            segment, favorite_roast, favorite_coffee_type, favorite_coffee,
            brew_method, signup_date, last_purchase, last_coffee_bought,
            discount, email, total_orders, recommendations, order_source
        ))
    return customers


def generate_prompts():
    """
    Генерирует набор базовых промптов для HTML-email с инлайн-CSS дизайном.
    Каждый промпт возвращает кортеж (description, prompt_text).
    """
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

    return [
        (
            "День рождения",
            f"Ты — маркетолог в e-commerce компании зернового кофе. Создай полностью готовый HTML-email с инлайн-CSS для поздравления с днём рождения.\n"
            f"Данные клиента: имя {first_name}, канал заказа {order_source}, скидка {discount}%, дата рождения {birth_date}, срок акции до {deadline}.\n"
            "Требования:\n"
            "- Тема (<h1>): если мобильное приложение — ≤40 символов, если веб-сайт — ≤60 символов.\n"
            "- Тело письма: не более 200 слов, с дружелюбным обращением, упоминанием подарка или скидки, яркой CTA-кнопкой и подписью команды.\n"
            f"{css_guidelines}"
        ),
        (
            "После покупки с кросс-селлом",
            f"Ты — маркетолог интернет-магазина зернового кофе. Создай персонализированный HTML-email с инлайн-CSS для кросс-продажи.\n"
            f"Данные клиента: имя {first_name}, канал заказа {order_source}, последний купленный кофе {last_coffee_bought}, "
            f"рекомендации {recommendations}, скидка {discount}%, всего заказов {total_orders}.\n"
            "Требования:\n"
            "- Тема (<h1>): мобильное приложение — ≤40 символов, веб-сайт — ≤60 символов.\n"
            "- Тело: до 200 слов, благодарность за предыдущий заказ, предложение нового товара, яркая кнопка «Купить сейчас».\n"
            f"{css_guidelines}"
        ),
        (
            "Активация неактивного клиента",
            f"Ты — маркетолог кофейного бренда. Нужно вернуть клиента, не открывавшего письма 30+ дней. Создай HTML-email с инлайн-CSS.\n"
            f"Данные клиента: имя {first_name}, канал заказа {order_source}, скидка {discount}%.\n"
            "Требования:\n"
            "- Тема (<h1>): мобильное приложение — ≤40 символов, веб-сайт — ≤60 символов.\n"
            "- Тело (до 180 слов): «Мы скучаем, {first_name}?», эксклюзивное предложение, отзывы, кнопка «Войти в магазин».\n"
            f"{css_guidelines}"
        ),
        (
            "Рождественское письмо",
            f"Ты — маркетолог премиального кафе. Создай тёплый HTML-email с инлайн-CSS к Рождеству.\n"
            f"Данные клиента: имя {first_name}, канал заказа {order_source}, выбери один кофе из рекомендации {recommendations}, "
            f"скидка {discount}%, до 08.01.\n"
            "Требования:\n"
            "- Тема (<h1>): мобильное приложение — ≤40 символов, веб-сайт — ≤60 символов.\n"
            "- Тело (≤200 слов): поздравление, подборка подарочных наборов, праздничные эмодзи, CTA-кнопка.\n"
            f"{css_guidelines}"
        ),
        (
            "Универсальный email",
            f"Ты — опытный маркетолог и дизайнер email-рассылок. Сгенерируй персонализированный HTML-email с инлайн-CSS.\n"
            f"Данные клиента: имя {first_name}, язык {language}, дата рождения {birth_date}, канал заказа {order_source}, "
            f"любимый кофе {favorite_coffee}, предпочитаемая обжарка {favorite_roast}б предпочитаемый метод заваривания кофе {brew_method}"
            f"дата последнего заказа {last_purchase}, последний заказанный кофе {last_coffee_bought}, всего заказов {total_orders}, "
            f"рекомендации {recommendations}, скидка {discount}%.\n"
            "Требования:\n"
            "- Тема (<h1>): мобильное приложение — ≤40 символов, веб-сайт — ≤60 символов.\n"
            "- Preheader (<p>): до 100 символов.\n"
            "- Тело (≤200 слов): обращение, упоминание предпочтений, яркая CTA-кнопка, подпись команды.\n"
            f"{css_guidelines}"
        ),
    ]
