import configparser
import telebot
import os
from bot.handlers import register_all_handlers

# абсолютный путь к папке, где лежит текущий файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# абсолютный путь к файлу config.ini относительно текущего файла
CONFIG_PATH = os.path.join(CURRENT_DIR, '..', '..', 'config.ini')

# обращаемся к конфигу и берем оттуда токкен бота
CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_PATH)
bot_token = CONFIG["BOT setup"]["key"]

bot=telebot.TeleBot(bot_token)
register_all_handlers(bot)

def start_bot():
    bot.infinity_polling()