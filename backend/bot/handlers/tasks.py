import os
from datetime import datetime
import logging

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
    try_to_get_by_id,
)

_logger = logging.getLogger(__name__)

# абсолютный путь к папке, где лежит текущий файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_logger.info("ищу путь к файлу с конфигами")
# абсолютный путь к файлу bot_phrases.yaml относительно текущего файла
PHRASES_PATH = os.path.join(CURRENT_DIR, "bot phrases.yaml")
_logger.info("обращаюсь к конфигу с фразами")
# обращаемся к файлу с фразами бота
with open(PHRASES_PATH, "r", encoding="utf-8") as file:
    PHRASES_CONFIG = yaml.safe_load(file)


class Create_new_task(StatesGroup):
    title = State()
    text = State()
    deadline = State()


def displayed_task_text(task):
    _logger.info("опредляю по статусу задачи кнопку выполнение или обратную ей")
    if task.status == "completed":
        return PHRASES_CONFIG["bot_messages"]["completed_task_withdraw_format"]
    elif task.status == "active":
        return PHRASES_CONFIG["bot_messages"]["task_withdraw_format"]


# передаем функции объект бота для инициализации функций требующих это
def register_tasks_handlers(bot: TeleBot):

    # команда new_task для работы с ботом в отсутствие miniapp
    @bot.message_handler(commands=["new_task"])
    def create_new_task_handler(message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        with Session() as session:
            try:
                _logger.info(f"ищу пользователя {user_id}")
                user_info = try_to_get_by_id(user_id, session)
                if user_id == None:
                    _logger.info(f"пользователь {user_id} не найден")
                    user_not_found_error = PHRASES_CONFIG["bot_messages"]["user_not_found"]
                    bot.send_message(chat_id, user_not_found_error)
                else:
                    _logger.info(f"пользователь {user_id} найден, \
                                 запрашиваю название задачи")
                    bot.set_state(user_id, Create_new_task.title, chat_id)
                    new_task_title_request = PHRASES_CONFIG["bot_messages"][
                        "new_task_title_request"
                    ]
                    bot.send_message(message.chat.id, new_task_title_request)
            except:
                _logger.exception(f"неизвестная ошибка при попытке создать \
                                  новоую задачу пользователя {user_id}")

    @bot.message_handler(state=Create_new_task.title)
    def create_new_task_title_request(message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        with bot.retrieve_data(user_id, chat_id) as data:
            data["title"] = message.text

        _logger.info(f"запрашиваю у пользователя {user_id} текст задачи")
        bot.set_state(user_id, Create_new_task.text, chat_id)
        new_task_text_request = PHRASES_CONFIG["bot_messages"]["new_task_text_request"]
        bot.send_message(chat_id, new_task_text_request)

    @bot.message_handler(state=Create_new_task.text)
    def create_new_task_text_request(message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        with bot.retrieve_data(user_id, chat_id) as data:
            data["text"] = message.text

        _logger.info(f"запрашиваю у пользователя {user_id} дедлайн задачи")
        bot.set_state(user_id, Create_new_task.deadline, chat_id)
        new_task_deadline_request = PHRASES_CONFIG["bot_messages"][
            "new_task_deadline_request"
        ]
        bot.send_message(chat_id, new_task_deadline_request)

    @bot.message_handler(state=Create_new_task.deadline)
    def create_new_task_deadline_request(message):
        user_tg_id = message.from_user.id
        chat_id = message.chat.id
        with bot.retrieve_data(user_tg_id, chat_id) as data:
            title = data["title"]
            text = data["text"]
            deadline = message.text

        _logger.info("меняю типа дедлайна из str в datatime")
        try:
            parsed_deadline = datetime.strptime(deadline, "%d.%m.%Y")
        except:
            _logger.info(f"ошибка при переводе типа дедлайна пользователя {user_tg_id}")



        with Session() as session:
            _logger.info(f"беру id пользователя {user_tg_id} по его tg id")
            try:
                user_id = get_by_id(user_tg_id, session).id
            except:
                _logger.exception("ошибка при взятии id у пользователя по его tg id")
            else:
                _logger.info("id пользователя получен успешно")
                try:
                    create_task(
                        TasksBase(
                            user_id=user_id,
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
                    _logger.info(f"задача пользователя {user_tg_id}")
                    session.commit()

                message_text = f"Тест создания задачи:\nНазвание: {title}\n\
                    Текст: {text}\nДедлайн: {deadline}"
                bot.send_message(chat_id, message_text)

        bot.delete_state(user_tg_id, chat_id)

    _logger.info("добавляю кастомный фильтр StateFilter")
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
        user_id = message.from_user.id
        _logger.info(f"вывожу задачу №0 пользователя {user_id}")
        with Session() as session:
            tasks = get_user_tasks(message.from_user.id, session)

            current_index = 0
            keyboard = InlineKeyboardMarkup(row_width=2)

            completed_and_not_completed_button(keyboard=keyboard, task=tasks[current_index], index=0)
            next_and_prew_buttons(keyboard=keyboard, index=current_index, num_of_tasks=len(tasks))
            delete_button(keyboard=keyboard, index=current_index)

            text = displayed_task_text(tasks[current_index])

            bot.send_message(
                message.chat.id,
                text.format(
                    title=tasks[current_index].title, 
                    text=tasks[current_index].text, 
                    deadline=tasks[current_index].deadline
                ),
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        return 0

    @bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
    def next_task_and_withdraw_users_tasks(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        target_index = int(call.data.split("_")[1])
        _logger.info(f"вывожу задачу №{target_index} пользователя {user_id}")
        with Session() as session:
            tasks = get_user_tasks(user_id, session)
            keyboard = InlineKeyboardMarkup(row_width=2)

            completed_and_not_completed_button(
                    keyboard=keyboard, 
                    task=tasks[target_index], 
                    index=target_index
            )
            next_and_prew_buttons(
                    keyboard=keyboard, 
                    index=target_index, 
                    num_of_tasks=len(tasks)
            )
            delete_button(keyboard=keyboard, index=target_index)

            text = displayed_task_text(tasks[target_index])
            # Обновляем текст сообщения и клавиатуру
            bot.edit_message_text(
                    text=text.format(
                            title=tasks[target_index].title,
                            text=tasks[target_index].text,
                            deadline=tasks[target_index].deadline,
                    ),
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=keyboard,
                    parse_mode="HTML",
            )
            bot.answer_callback_query(call.id)

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("ask_for_confirm_delete_task_")
    )
    def ask_for_confirm_delete_task_and_withdraw_users_tasks(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id

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
        _logger.info(f"обращаюсь в БД за задачами пользователя {user_id}")
        with Session() as session:
            tasks = get_user_tasks(user_id, session)

            bot.edit_message_text(
                text=text.format(title=tasks[target_index].title),
                chat_id=chat_id,
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
