from telebot import TeleBot

from backend.bot.handlers.basic import register_basic_handlers
from backend.bot.handlers.tasks import register_tasks_handlers


def register_all_handlers(bot: TeleBot) -> None:
    register_basic_handlers(bot)
    register_tasks_handlers(bot)
