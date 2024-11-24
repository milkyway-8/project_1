import telebot
import main_module_bot
import os
from dotenv import load_dotenv, find_dotenv


def main():
    load_dotenv(find_dotenv()) #прячем TOKEN
    bot = telebot.TeleBot(os.getenv('TOKEN')) #создаем сам бот, присваивая ему токен
    main_module_bot.main_module_bot_function(bot)


if __name__ == "__main__":
    main()

