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

    # регистрация пользователя после команды /reg
    @bot.message_handler(commands=["reg"])
    def start_register_user(message):
        with Session() as session:
            try:
                _ = get_by_id(message.from_user.id, session)
                user_already_exists_error = PHRASES_CONFIG["bot_messages"][
                    "user_already_exists"
                ]
                bot.send_message(message.chat.id, user_already_exists_error)
                return user_already_exists_error
            except:
                pass

        register_UTC_request_text = PHRASES_CONFIG["bot_messages"]["reg_UTC_request"]

        msg = bot.send_message(message.chat.id, register_UTC_request_text)
        bot.register_next_step_handler(msg, end_register_user)

    def end_register_user(message):
        users_time_zone = message.text
        try:
            users_time_zone = int(users_time_zone)
            if not (-12 <= users_time_zone <= 14):
                reg_UTC_value_error = PHRASES_CONFIG["bot_messages"][
                    "reg_UTC_value_error"
                ]
                bot.send_message(message.chat.id, reg_UTC_value_error)
            with Session() as session:
                try:
                    create_user(
                        UserBase(
                            telegram_id=message.chat.id,
                            user_name=message.from_user.first_name,
                            time_zone=users_time_zone,
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

        except Exception as e:
            reg_UTC_format_error = PHRASES_CONFIG["bot_messages"][
                "reg_UTC_format_error"
            ]
            print(Exception)
            bot.send_message(message.chat.id, reg_UTC_format_error)

    # временная команда info для проверки работоспособности регистрации пользователя и БД
    @bot.message_handler(commands=["info"])
    def user_info_handler(message):
        with Session() as session:
            try:
                user_info = get_by_id(telegram_id=message.chat.id, session=session)
                print(user_info)
                bot.send_message(message.chat.id, user_info)
            except:
                user_not_found_message = PHRASES_CONFIG["bot_messages"][
                    "user_not_found"
                ]
                bot.send_message(message.chat.id, user_not_found_message)
                session.rollback()
                raise
            else:
                session.commit()

    # временная команда delete_me для проверки работоспособности регистрации пользователя и БД
    @bot.message_handler(commands=["delete_me"])
    def delete_user_handler(message):
        with Session() as session:
            try:
                user_info = get_by_id(telegram_id=message.chat.id, session=session)
                delete_user(user_info, session)
                delete_successfull_message = PHRASES_CONFIG["bot_messages"][
                    "delete_successfull"
                ]
                bot.send_message(message.chat.id, delete_successfull_message)
            except:
                session.rollback()
                user_not_found_message = PHRASES_CONFIG["bot_messages"][
                    "user_not_found"
                ]
                bot.send_message(message.chat.id, user_not_found_message)
                raise
            else:
                session.commit()
