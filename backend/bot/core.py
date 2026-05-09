import configparser
import telebot
import yaml

# обращаемся к конфигу и берем оттуда токкен бота
config = configparser.ConfigParser()
config.read('config.ini')
bot_token = config["BOT setup"]["key"]

# обращаемся к файлу с фразами бота
with open('backend/bot/bot phrases.yaml', 'r', encoding='utf-8') as file:
    phrases_config = yaml.safe_load(file)

bot=telebot.TeleBot(bot_token)

# приветсвие пользователя при получении от него /start
@bot.message_handler(commands=["start"])
def start_message(message):
    greetings_message_text = phrases_config["bot_messages"]["greeting"]
    bot.send_message(message.chat.id, greetings_message_text)


bot.infinity_polling()