import os

import yaml
from telebot import TeleBot

from backend.db.models import UserBase
from backend.db.session import create_user, Session, get_by_id, delete_user


# абсолютный путь к папке, где лежит текущий файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# абсолютный путь к файлу bot_phrases.yaml относительно текущего файла
PHRASES_PATH = os.path.join(CURRENT_DIR, "bot phrases.yaml")

# обращаемся к файлу с фразами бота
with open(PHRASES_PATH, "r", encoding="utf-8") as file:
    PHRASES_CONFIG = yaml.safe_load(file)

# передаем функции объект бота для инициализации функций требующих это
def register_basic_handlers(bot: TeleBot):

    # приветсвие пользователя при получении от него /start
    @bot.message_handler(commands=["start"])
    def start_message(message):
        greetings_message_text = PHRASES_CONFIG["bot_messages"]["greeting"]

        _ = bot.send_message(message.chat.id, greetings_message_text)

    @bot.message_handler(commands=["reg"])
    def register_user(message):
        with Session() as session:
            try:
                create_user(
                    UserBase(
                        telegram_id=message.chat.id,
                        user_name=message.from_user.first_name,
                    ),
                   session,
                )
                register_message_text = PHRASES_CONFIG["bot_messages"]["register"]
                _ = bot.send_message(message.chat.id, register_message_text)
            except:
                session.rollback()
                raise
            else:
                session.commit()
    @bot.message_handler(commands=["info"])
    def user_info(message):
        with Session() as session:
            try:
                user_info= get_by_id(telegram_id=message.chat.id, session=session)
                print(user_info)
                bot.send_message(message.chat.id, user_info)
            except:
                user_not_found_message = PHRASES_CONFIG["bot_messages"]["user_not_found"]
                bot.send_message(message.chat.id, user_not_found_message)
                session.rollback()
                raise
            else:
                session.commit()
    
    @bot.message_handler(commands=["delete_me"])
    def user_info(message):
        with Session() as session:
            try:
                user_info= get_by_id(telegram_id=message.chat.id, session=session)
                delete_user(user_info, session)
                delete_successfull_message = PHRASES_CONFIG["bot_messages"]["delete_successfull"]
                bot.send_message(message.chat.id, delete_successfull_message)
            except:
                session.rollback()
                user_not_found_message = PHRASES_CONFIG["bot_messages"]["user_not_found"]
                bot.send_message(message.chat.id, user_not_found_message)
                raise
            else:
                session.commit()

