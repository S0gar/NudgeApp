import os
import logging

import yaml
from telebot import TeleBot

from backend.db.models import UserBase
from backend.db.session import create_user, Session, get_by_id, try_to_get_by_id, delete_user


_logger = logging.getLogger(__name__)


# абсолютный путь к папке, где лежит текущий файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# абсолютный путь к файлу bot_phrases.yaml относительно текущего файла
PHRASES_PATH = os.path.join(CURRENT_DIR, "bot phrases.yaml")

_logger.info("открытие конфига с фразами")
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
        user_id = message.from_user.id
        chat_id = message.chat.id
        with Session() as session:
            try:
                _logger.info(f"проверка существования пользователя {user_id} по его id")
                user = try_to_get_by_id(user_id, session)
                if user is not None:
                    _logger.info(f"пользователь {user_id} уже существует")
                    user_already_exists_error = PHRASES_CONFIG["bot_messages"][
                        "user_already_exists"
                    ]
                    bot.send_message(chat_id, user_already_exists_error)
                else:
                    _logger.info(f"пользователь {user_id} не существует, начинаем регистрацию")
                    register_UTC_request_text = PHRASES_CONFIG["bot_messages"][
                        "reg_UTC_request"
                    ]
                    msg = bot.send_message(chat_id, register_UTC_request_text)
                    bot.register_next_step_handler(msg, end_register_user)
            except Exception as e:
                _logger.exception(f"ошибка при проверке существования пользователя {user_id}: {e}")

    def end_register_user(message):
        users_time_zone = message.text
        chat_id = message.chat.id
        user_id = message.from_user.id
        username = message.from_user.first_name
        try:
            users_time_zone = int(users_time_zone)
        except:
            _logger.exception("ошибка формата данных")
            reg_UTC_format_error = PHRASES_CONFIG["bot_messages"][
                "reg_UTC_format_error"
            ]
            bot.send_message(chat_id, reg_UTC_format_error)

        if not (-12 <= users_time_zone <= 14):
            _logger.error(
                f"часовой пояс пользователя {user_id} \
                со значением {users_time_zone} некорректно"
            )
            reg_UTC_value_error = PHRASES_CONFIG["bot_messages"][
                "reg_UTC_value_error"
            ]
            bot.send_message(chat_id, reg_UTC_value_error)
        else:
            with Session() as session:
                try:
                    _logger.info("обращаюсь к базе данных для создания нового пользователя \
                                с id: {chat_id}, username: {username}, timezone: {users_time_zone}")
                    create_user(
                        UserBase(
                            telegram_id=user_id,
                            user_name=username,
                            time_zone=users_time_zone,
                        ),
                        session,
                    )
                    register_message_text = PHRASES_CONFIG["bot_messages"]["register"]
                    _ = bot.send_message(chat_id, register_message_text)
                except:
                    _logger.exception()
                    session.rollback()
                    raise
                else:
                    _logger.info("запись изменений в базу данных")
                    session.commit()

    # временная команда info для проверки работоспособности регистрации пользователя и БД
    @bot.message_handler(commands=["info"])
    def user_info_handler(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        with Session() as session:
            try:
                _logger.info(f"запрашиваю информацию о пользователе {user_id} из базы данных")
                user_info = try_to_get_by_id(telegram_id=user_id, session=session)
                if user_info == None:
                    _logger.info(f"пользователь {user_id} не был найден")
                    user_not_found_message = PHRASES_CONFIG["bot_messages"][
                            "user_not_found"
                    ]
                    bot.send_message(chat_id, user_not_found_message)
                else:
                    _logger.info(f"пользователь {user_id} был найден успешно")
                    bot.send_message(chat_id, user_info)
            except:
                _logger.exception("неизвестная ошибка при попытке найти информацию о пользователе")

    # временная команда delete_me для проверки работоспособности регистрации пользователя и БД
    @bot.message_handler(commands=["delete_me"])
    def delete_user_handler(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        with Session() as session:
            try:
                _logger.info(f"запрос данных о пользователе {user_id} по его id")
                user_info = get_by_id(telegram_id=user_id, session=session)
                _logger.info(f"удаляю пользователя {user_id}")
                delete_user(user_info, session)
                delete_successfull_message = PHRASES_CONFIG["bot_messages"][
                    "delete_successfull"
                ]
                bot.send_message(chat_id, delete_successfull_message)
            except:
                _logger.exception(f"неизвестная ошибка при попытке удалить пользователя {user_id}")
                session.rollback()
                user_not_found_message = PHRASES_CONFIG["bot_messages"][
                    "user_not_found"
                ]
                bot.send_message(chat_id, user_not_found_message)
                raise
            else:
                _logger.info("фиксирую изменения в базе данных")
                session.commit()
