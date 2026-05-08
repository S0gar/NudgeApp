import configparser

config = configparser.ConfigParser()
config.read('config.ini')

bot_key = config["BOT"]["key"]
