import logging

import telebot
from telebot import custom_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.storage import StateMemoryStorage

# from backend.bot.handlers import register_all_handlers
#from backend.config import Config


_logger = logging.getLogger(__name__)

bot_token = Config.BOT_TOKEN

# объявляем объект для работы с машиной состояния (FSM - Finite State Machine)
state_storage = StateMemoryStorage()

bot = AsyncTeleBot(bot_token, state_storage=state_storage)
_logger.info(f"загрузка обработчиков команд")
# register_all_handlers(bot)

# ПРОБЛЕМА С ПОДКЛЮЧЕНИЕМ АСИНХРОННОГО БОТА К ДНС


async def start_bot():
    _logger.info("начало запросов к telegram")
    await bot.infinity_polling()
Ы