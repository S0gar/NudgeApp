from telebot.types import Message
import yaml
import os

# абсолютный путь к папке, где лежит текущий файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# абсолютный путь к файлу bot_phrases.yaml относительно текущего файла
PHRASES_PATH = os.path.join(CURRENT_DIR, 'bot phrases.yaml')

# обращаемся к файлу с фразами бота
with open(PHRASES_PATH, 'r', encoding='utf-8') as file:
    PHRASES_CONFIG = yaml.safe_load(file)

# передаем функции объект бота для инициализации функций требующих это
def register_basic_handlers(bot):

    # приветсвие пользователя при получении от него /start
    @bot.message_handler(commands=["start"])
    def start_message(message):
        greetings_message_text = PHRASES_CONFIG["bot_messages"]["greeting"]
        bot.send_message(message.chat.id, greetings_message_text)