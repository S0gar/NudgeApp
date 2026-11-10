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


def displayed_task_text(task):
    if task.status == "completed":
        return PHRASES_CONFIG["bot_messages"]["completed_task_withdraw_format"]
    elif task.status == "active":
        return PHRASES_CONFIG["bot_messages"]["task_withdraw_format"]


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

    def next_and_prew_buttons(
        keyboard: InlineKeyboardMarkup, index: int, num_of_tasks: int
    ) -> None:
        buttonNext = InlineKeyboardButton("==>", callback_data=f"task_{index + 1}")
        buttonPrev = InlineKeyboardButton("<==", callback_data=f"task_{index - 1}")
        need_button_prev = index > 0
        need_button_next = index < num_of_tasks - 1
        if need_button_prev and need_button_next:
            keyboard.add(buttonPrev, buttonNext)
        elif need_button_prev and not need_button_next:
            keyboard.add(buttonPrev)
        elif not need_button_prev and need_button_next:
            keyboard.add(buttonNext)

    def completed_and_not_completed_button(keyboard: InlineKeyboardMarkup, task, index):

        if task.status == "active":
            buttonCompleped = InlineKeyboardButton(
                "Выполнено", callback_data=f"completed_task_{index}"
            )
            keyboard.add(buttonCompleped)
        elif task.status == "completed":
            buttonNOTCompleped = InlineKeyboardButton(
                "Не выполнено", callback_data=f"not_completed_task_{index}"
            )
            keyboard.add(buttonNOTCompleped)

    def delete_button(keyboard: InlineKeyboardMarkup, index: int) -> None:
        buttonDelete = InlineKeyboardButton(
            "Удалить", callback_data=f"ask_for_confirm_delete_task_{index}"
        )
        keyboard.add(buttonDelete)

    @bot.message_handler(commands=["my_tasks"])
    def withdraw_users_tasks(message):
        with Session() as session:
            tasks = get_user_tasks(message.from_user.id, session)

            current_index = 0
            keyboard = InlineKeyboardMarkup(row_width=2)

            buttonCompleped = InlineKeyboardButton(
                "Выполнено", callback_data=f"completed_task_{current_index}"
            )
            next_and_prew_buttons(keyboard=keyboard, index=0, num_of_tasks=len(tasks))
            keyboard.add(buttonCompleped)
            delete_button(keyboard=keyboard, index=current_index)

            text = displayed_task_text(tasks[current_index])
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

            buttonCompleped = InlineKeyboardButton(
                "Выполнено", callback_data=f"completed_task_{target_index}"
            )
            next_and_prew_buttons(
                keyboard=keyboard, index=target_index, num_of_tasks=len(tasks)
            )
            keyboard.add(buttonCompleped)
            delete_button(keyboard=keyboard, index=target_index)

            text = displayed_task_text(tasks[target_index])
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

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("ask_for_confirm_delete_task_")
    )
    def ask_for_confirm_delete_task_and_withdraw_users_tasks(call):
        target_index = int(call.data.split("_")[5])
        keyboard = InlineKeyboardMarkup(row_width=2)
        button_conf = InlineKeyboardButton(
            "удалить", callback_data=f"delete_task_{target_index}"
        )
        button_cancel = InlineKeyboardButton(
            "отмена", callback_data=f"task_{target_index}"
        )
        keyboard.add(button_conf, button_cancel)
        text = PHRASES_CONFIG["bot_messages"]["ask_for_confirm_delete"]
        with Session() as session:
            tasks = get_user_tasks(call.from_user.id, session)

            bot.edit_message_text(
                text=text.format(title=tasks[target_index].title),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML",
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_task_"))
    def delete_task_and_withdraw_users_tasks(call):
        target_index = int(call.data.split("_")[2])
        with Session() as session:
            tasks = get_user_tasks(call.from_user.id, session)
            deleted_task = get_task_by_id(tasks[target_index].id, session)
            delete_task(deleted_task, session)
            session.commit()
            keyboard = InlineKeyboardMarkup(row_width=2)

            next_and_prew_buttons(
                keyboard=keyboard, index=target_index, num_of_tasks=len(tasks)
            )

            text = PHRASES_CONFIG["bot_messages"]["deleted_task"]
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

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("completed_task_")
    )
    def complete_task_and_withdraw_users_tasks(call):
        target_index = int(call.data.split("_")[2])
        with Session() as session:
            tasks = get_user_tasks(call.from_user.id, session)
            taaks = tasks[target_index].status = "completed"
            session.commit()
            keyboard = InlineKeyboardMarkup(row_width=2)

            next_and_prew_buttons(
                keyboard=keyboard, index=target_index, num_of_tasks=len(tasks)
            )

            text = displayed_task_text(tasks[target_index])

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
