import configparser
import os

import telebot
from telebot import custom_filters
from telebot.storage import StateMemoryStorage

from backend.bot.handlers import register_all_handlers

# абсолютный путь к папке, где лежит текущий файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# абсолютный путь к файлу config.ini относительно текущего файла
CONFIG_PATH = os.path.join(CURRENT_DIR, "..", "..", "config.ini")

# обращаемся к конфигу и берем оттуда токкен бота
CONFIG = configparser.ConfigParser()
_ = CONFIG.read(CONFIG_PATH)
bot_token = CONFIG["BOT setup"]["key"]

# объявляем объект для работы с машиной состояния (FSM - Finite State Machine)
state_storage = StateMemoryStorage()


bot = telebot.TeleBot(bot_token, state_storage=state_storage)
register_all_handlers(bot)


def start_bot():
    print(f"DEBUG: Token loaded: '{bot_token}'")
    bot.infinity_polling()
