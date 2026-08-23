from telebot import TeleBot

from backend.bot.handlers.basic import register_basic_handlers


def register_all_handlers(bot: TeleBot) -> None:
    register_basic_handlers(bot)
