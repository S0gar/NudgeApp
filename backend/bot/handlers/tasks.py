import os
from datetime import datetime

import yaml

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import TeleBot
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

from backend.db.models import TasksBase
from backend.db.session import (
    get_by_id,
    Session,
    create_task,
    get_user_tasks,
    delete_task,
    get_task_by_id,
)

# абсолютный путь к папке, где лежит текущий файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# абсолютный путь к файлу bot_phrases.yaml относительно текущего файла
PHRASES_PATH = os.path.join(CURRENT_DIR, "bot phrases.yaml")

# обращаемся к файлу с фразами бота
with open(PHRASES_PATH, "r", encoding="utf-8") as file:
    PHRASES_CONFIG = yaml.safe_load(file)


class Create_new_task(StatesGroup):
    title = State()
    text = State()
    deadline = State()


# передаем функции объект бота для инициализации функций требующих это
def register_tasks_handlers(bot: TeleBot):

    # команда new_task для работы с ботом в отсутствие miniapp
    @bot.message_handler(commands=["new_task"])
    def create_new_task_handler(message):
        with Session() as session:
            try:
                user_info = get_by_id(message.from_user.id, session)
            except:
                user_not_found_error = PHRASES_CONFIG["bot_messages"]["user_not_found"]
                bot.send_message(message.chat.id, user_not_found_error)
                return "user not found"

        bot.set_state(message.from_user.id, Create_new_task.title, message.chat.id)

        new_task_title_request = PHRASES_CONFIG["bot_messages"][
            "new_task_title_request"
        ]
        bot.send_message(message.chat.id, new_task_title_request)

    @bot.message_handler(state=Create_new_task.title)
    def create_new_task_title_request(message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["title"] = message.text

        bot.set_state(message.from_user.id, Create_new_task.text, message.chat.id)
        new_task_text_request = PHRASES_CONFIG["bot_messages"]["new_task_text_request"]
        bot.send_message(message.chat.id, new_task_text_request)

    @bot.message_handler(state=Create_new_task.text)
    def create_new_task_text_request(message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["text"] = message.text

        bot.set_state(message.from_user.id, Create_new_task.deadline, message.chat.id)
        new_task_deadline_request = PHRASES_CONFIG["bot_messages"][
            "new_task_deadline_request"
        ]
        bot.send_message(message.chat.id, new_task_deadline_request)

    @bot.message_handler(state=Create_new_task.deadline)
    def create_new_task_deadline_request(message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            title = data["title"]
            text = data["text"]
            deadline = message.text

        parsed_deadline = datetime.strptime(deadline, "%d.%m.%Y")

        with Session() as session:
            try:
                create_task(
                    TasksBase(
                        user_id=message.from_user.id,
                        title=title,
                        text=text,
                        deadline=parsed_deadline,
                        status="active",
                    ),
                    session,
                )
            except:
                session.rollback()
                raise
            else:
                session.commit()

        message_text = f"Тест создания задачи:\nНазвание: {title}\nТекст: {text}\nДедлайн: {deadline}"
        bot.send_message(message.chat.id, message_text)

        bot.delete_state(message.from_user.id, message.chat.id)

    bot.add_custom_filter(custom_filters.StateFilter(bot))

    @bot.message_handler(commands=["my_tasks"])
    def withdraw_users_tasks(message):
        with Session() as session:
            tasks = get_user_tasks(message.from_user.id, session)

            current_index = 0
            keyboard = InlineKeyboardMarkup(row_width=2)

            buttonNext = InlineKeyboardButton(
                "==>", callback_data=f"task_{current_index + 1}"
            )
            buttonDelete = InlineKeyboardButton(
                "Удалить", callback_data=f"delete_task_{current_index}"
            )
            keyboard.add(buttonNext)
            keyboard.add(buttonDelete)

            text = PHRASES_CONFIG["bot_messages"]["task_withdraw_format"]
            bot.send_message(
                message.chat.id,
                text.format(
                    title=tasks[0].title, text=tasks[0].text, deadline=tasks[0].deadline
                ),
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        return 0

    @bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
    def next_task_and_withdraw_users_tasks(call):
        target_index = int(call.data.split("_")[1])
        with Session() as session:
            tasks = get_user_tasks(call.from_user.id, session)
            keyboard = InlineKeyboardMarkup(row_width=2)

            buttonNext = InlineKeyboardButton(
                "==>", callback_data=f"task_{target_index + 1}"
            )
            buttonPrev = InlineKeyboardButton(
                "<==", callback_data=f"task_{target_index - 1}"
            )
            buttonDelete = InlineKeyboardButton(
                "Удалить", callback_data=f"delete_task_{target_index}"
            )
            if target_index > 0:
                keyboard.add(buttonPrev)
            keyboard.add(buttonDelete)
            if target_index < len(tasks) - 1:
                keyboard.add(buttonNext)

            text = PHRASES_CONFIG["bot_messages"]["task_withdraw_format"]
            # Обновляем текст сообщения и клавиатуру
            bot.edit_message_text(
                text=text.format(
                    title=tasks[target_index].title,
                    text=tasks[target_index].text,
                    deadline=tasks[target_index].deadline,
                ),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
            bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_task_"))
    def delete_task_and_withdraw_users_tasks(call):
        target_index = int(call.data.split("_")[2])
        with Session() as session:
            tasks = get_user_tasks(call.from_user.id, session)
            deleted_task = get_task_by_id(tasks[target_index].id, session)
            delete_task(deleted_task, session)
            session.commit()
            keyboard = InlineKeyboardMarkup(row_width=2)

            buttonNext = InlineKeyboardButton(
                "==>", callback_data=f"task_{target_index + 1}"
            )
            buttonPrev = InlineKeyboardButton(
                "<==", callback_data=f"task_{target_index - 1}"
            )
            if target_index > 0:
                keyboard.add(buttonPrev)
            if target_index < len(tasks) - 1:
                keyboard.add(buttonNext)

            text = PHRASES_CONFIG["bot_messages"]["deleted_task"]
            # Обновляем текст сообщения и клавиатуру
            bot.edit_message_text(
                text=text.format(
                    title=tasks[target_index].title,
                    text=tasks[target_index].text,
                    deadline=tasks[target_index].deadline,
                ),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
            # баг, если из двух задач удалить одну, при нажатии на кнопку другого така выдаст ошибку выход за пределы
            bot.answer_callback_query(call.id)
