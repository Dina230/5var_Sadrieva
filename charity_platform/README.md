# Благотворительная платформа ВТБ

Веб-платформа для сбора средств на благотворительные цели.

## Технологии
- Python 3.10+
- Django 4.2.7
- SQLite
- Chart.js (через CDN)

## Установка и запуск

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py flush --noinput #это очистка бд
python manage.py loaddata fixtures/initial_data.json #запуск

python manage.py createsuperuser
пароль и логин: admin
python manage.py runserver
