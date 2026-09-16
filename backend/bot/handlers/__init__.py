import logging

from telebot import TeleBot

from backend.bot.handlers.basic import register_basic_handlers
from backend.bot.handlers.tasks import register_tasks_handlers

_logger = logging.getLogger(__name__)


def register_all_handlers(bot: TeleBot) -> None:
    _logger.info("регистрация базового обработчика команд")
    register_basic_handlers(bot)
    _logger.info("регистрация обработчика команд задач")
    register_tasks_handlers(bot)
