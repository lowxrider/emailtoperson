from faker import Faker
from datetime import date


def generate_customers(n: int = 100) -> list[tuple]:
    """
    Генерирует список из n клиентов с полным набором полей для CRM интернет-магазина кофе.
    Поля: first_name, patronymic, last_name, email, preferred_language, birth_date,
           segment, favorite_roast, bean_type, favorite_coffee, brewing_method,
           signup_date, last_purchase_date, last_purchased_coffee
    """
    fake = Faker("ru_RU")
    languages = ["Русский", "Английский", "Немецкий", "Французский"]
    segments = ["Новый", "Постоянный", "VIP", "Ушел"]
    roasts = ["Светлая", "Средняя", "Темная"]
    bean_types = ["Арабика", "Бленд", "Робуста"]
    coffees = [
        "Бразилия Могиана", "Бразилия Сантос",
        "Бразилия Бурбон", "Бразилия Кашиа",
        "Колумбия Уила", "Колумбия Супремо",
        "Колумбия Эксельсо", "Колумбия Буэна Виста",
        "Эфиопия Иргачеффе", "Эфиопия Сидамо",
        "Эфиопия Харар", "Эфиопия Гудж",
        "Кения AA", "Кения AB",
        "Кения PB", "Кения C",
        "Суматра Мандхелинг", "Суматра Линтонг",
        "Суматра Гайа", "Суматра Тоба",
        "Гватемала Антигуа", "Гватемала УЭУ",
        "Коста-Рика Тарразу", "Коста-Рика Брюаго",
        "Перу Кахаматс", "Гондурас Копан",
        "Индонезия Суматра", "Индонезия Ява",
        "Ямайка Блю Маунтин", "Мексика Пантаналь"
    ]
    methods = ["Эспрессо", "Френч-пресс", "Капельная", "Пуровер"]

    records = []
    for _ in range(n):
        first = fake.first_name()
        patro = fake.middle_name()
        last = fake.last_name()
        email = fake.email()
        lang = fake.random_element(languages)
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
        seg = fake.random_element(segments)
        roast = fake.random_element(roasts)
        bean = fake.random_element(bean_types)
        fav_cof = fake.random_element(coffees)
        method = fake.random_element(methods)
        signup_date = fake.date_between(start_date="-2y", end_date="today")
        last_purchase_date = fake.date_between(start_date=signup_date, end_date="today")
        last_c = fake.random_element(coffees)

        # Преобразуем даты в ISO-строки
        birth_str = birth_date.isoformat()
        signup_str = signup_date.isoformat()
        last_p_str = last_purchase_date.isoformat()

        records.append((
            first, patro, last, email, lang, birth_str,
            seg, roast, bean, fav_cof, method,
            signup_str, last_p_str, last_c
        ))

    return records


def generate_prompts() -> list[tuple]:
    """
    Генерирует набор базовых промптов для email-рассылок на разные темы.
    Возвращает список кортежей (description, prompt).
    """
    topics = {
        "День рождения": "Напиши персонализированное поздравление с днём рождения клиента {first_name}, упомяни его любимый сорт кофе и предложи специальную скидку.",
        "Чёрная пятница": "Создай email для Чёрной пятницы с эксклюзивным предложением на обжарку {favorite_roast} и призывом к покупке.",
        "Новый год": "Составь праздничный новогодний email, в котором рассказывается о специальном наборе кофейных подарков.",
        "Рождество": "Напиши тёплое рождественское письмо с рекомендациями по подбору кофе для праздника.",
        "Новый клиент": "Создай приветственный email для нового клиента с описанием преимуществ и первым промокодом.",
        "Брошенная корзина": "Сгенерируй напоминание о брошенной корзине с информацией о товарах и предложением бесплатной доставки."
    }
    records = []
    for desc, prompt in topics.items():
        records.append((desc, prompt))
    return records