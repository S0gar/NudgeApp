import configparser
import telebot

# обращаемся к конфигу и берем оттуда токкен бота
config = configparser.ConfigParser()
config.read('config.ini')
bot_token = config["BOT"]["key"]

bot=telebot.TeleBot(bot_token)
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Hello world!")
bot.infinity_polling()