# utils/generator.py

import random
from faker import Faker

from datetime import date

def generate_customers(n=100):
    fake = Faker('ru_RU')
    segments = ['A', 'B', 'C']
    roasts = ['Светлая', 'Средняя', 'Тёмная']
    coffee_types = ['Арабика', 'Бленд', 'Робуста']
    brew_methods = ['Френч-пресс', 'Воронка', 'Турка', 'Гейзер', 'Автомат']
    coffees = [
        "Бразилия Можиана", "Бразилия Сантос", "Колумбия Хуила", "Колумбия Супремо",
        "Эфиопия Иргачефф", "Эфиопия Сидамо", "Кения AA", "Кения AB",
        "Суматра Манделинг", "Суматра Линтонг", "Уганда Бугишу", "Гватемала Антигуа"
    ]
    customers = []
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        patronymic = fake.middle_name()
        language = 'ru'
        birth_date_dt = fake.date_of_birth(minimum_age=18, maximum_age=65)  # <--- это date!
        birth_date = birth_date_dt.isoformat()
        segment = random.choice(segments)
        favorite_roast = random.choice(roasts)
        favorite_coffee_type = random.choice(coffee_types)
        favorite_coffee = random.choice(coffees)
        brew_method = random.choice(brew_methods)
        signup_date_dt = fake.date_between(start_date='-3y', end_date='-1y')  # <--- это date!
        signup_date = signup_date_dt.isoformat()
        last_purchase_dt = fake.date_between(start_date=signup_date_dt, end_date=date.today())
        last_purchase = last_purchase_dt.isoformat()
        last_coffee_bought = random.choice(coffees)
        customers.append((
            first_name, last_name, patronymic, language, birth_date,
            segment, favorite_roast, favorite_coffee_type, favorite_coffee,
            brew_method, signup_date, last_purchase, last_coffee_bought
        ))
    return customers


def generate_prompts():
    return [
        ("День рождения", "Напиши персонализированное поздравление с днём рождения клиента {first_name}, упомяни его любимый сорт кофе и предложи специальную скидку."),
        ("Чёрная пятница", "Создай email для Чёрной пятницы с эксклюзивным предложением на обжарку {favorite_roast} и призывом к покупке."),
        ("Новый год", "Составь праздничный новогодний email, в котором рассказывается о специальном наборе кофейных подарков."),
        ("Рождество", "Напиши тёплое рождественское письмо с рекомендациями по подбору кофе для праздника."),
        ("Новый клиент", "Создай приветственный email для нового клиента с описанием преимуществ и первым промокодом."),
        ("Брошенная корзина", "Сгенерируй напоминание о брошенной корзине с информацией о товарах и предложением бесплатной доставки."),
    ]
