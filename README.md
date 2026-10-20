# AppNudge
[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org/)
[![Telegram API](https://img.shields.io/badge/Telegram_Bot_API-blue.svg?logo=telegram)](https://core.telegram.org/bots/api)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)](https://www.sqlite.org/)

## Содержание
- [О проекте](#ℹ️-о-проекте)
- [Возможности](#-возможности)
- [Стек технологий](#-стек-технологий)
- [Установка и запуск](#️-установка-и-запуск)
- [Команда проекта](#-команда-проекта)

##ℹ️ О проекте
Телеграм-бот, который выполняет функцию персонального ежедневника 
и умной системы напоминаний. Проект позволяет удобно управлять расписанием 
и задачами прямо через мессенджер с использованием Web App интерфейса

#### status: Work in progress

## 🚀 Возможности
* **Управление задачами** Создание, просмотр, удаление задач, выставления статуса "выполнено"

## 🛠 Стек технологий
* **Язык**: Python 3.14.4
* **Фреймворк**: FastAPI (сервер uvicorn)
* **Telegram API**: pyTelegramBotAPI
* **База данных и ORM**: SQLite + SQLAlchemy 2.0
* **Конфигурация**: python-dotenv, PyYAML

## ⚙️ Установка и запуск
### 1. Клонирование репозитория
### 2. Настройка виртуального окружения
**Для Linux/macOS:**
```sh
python3 -m venv venv
source venv/bin/activate
```
### 3. Установка зависимостей
```sh
pip install -r requirements.txt
```
### 4. Конфигурация
В корне проекта находится шаблон конфигурации config.example.ini
Для работы программы необходимо переименовать его в config.ini и заполнить необходимые параметры - добавить токен бота
### 5. Запуск бота
```sh
python main.py
```

## 👥 Команда проекта
- [Сарматов Игорь s0gar](https://github.com/s0gar)
- [Захаров Владислав haruno-o](https://github.com/haruno-o)
