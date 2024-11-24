import module_info
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json

"""Модуль, который хранит весь функционал тг бота"""

"""main_module_bot_function -функция, в которой находится весь функционал тг бота """


def main_module_bot_function(bot):
    """Функция выводит весь функционал бота, доступный пользователю"""
    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(message.chat.id, 'Привет! Я бот "Birthday Memory". Нажми\n/start\n'
                                          '/info\n/add_birthday\n/show_birthdays\n'
                                          '/help\n/delete\n/Postcard_female_friend\n/Postcard_male_friend\n'
                                          '/Postcard_family_member\n/Postcard_teacher')

    """функция выдает информацию о том, что делает бот"""
    @bot.message_handler(commands=["info"])
    def info(message):
        bot.send_message(message.chat.id, module_info.command_info(message.from_user.first_name)) #бот отправляет
        # сообщение пользователю из модуля module_info

    birthday_file = "birthdays.json" # birthdays.json можно будет открывать и смотреть, какие там записаны люди и ДР
    """функция читает файл и загружает дни рождения из этого файла"""
    def load_birthdays():
        try:
            with open(birthday_file, "r") as file:
                file_information = file.read().strip()
                return json.loads(file_information) if file_information else {} #словарь birthday
                # останется пустым, если файл пустой или загрузит оттуда информацию
        except FileNotFoundError:   #словарь birthday останется пустым, если файл не создан
            return {}
        except json.JSONDecodeError: #словарь birthday останется пустым, если файл содержит некорректный JSON
            print("Ошибка: файл содержит некорректный JSON.")
            return {}

    """функция сохраняет дни рождения в файл"""
    def save_birthdays(data):
        with open(birthday_file, "w") as file:
            json.dump(data, file, indent=4)

    birthdays = load_birthdays()  #в словарь birthdays загрузится вся информация либо он останется пустым

    """функция, отправляющая сообщение, в каком формате добавлять информацию о человеке и добавляет день рождение
    в словарь при помощи функции process_birthday"""
    @bot.message_handler(commands=["add_birthday"])
    def add_birthday(message):
        information = bot.reply_to(message, "Send the birthday in this format:\n\n'Name_Surname YYYY-MM-DD'",
                           parse_mode="Markdown")
        bot.register_next_step_handler(information, add_birthday_to_dictionary_birthdays)

    """функция, добавляющая день рождения в словарь birthday"""
    def add_birthday_to_dictionary_birthdays(message):
        try:
            name_surname, date_str = message.text.split()
            birthday = datetime.strptime(date_str, "%Y-%m-%d").date()
            birthdays[name_surname] = [date_str, message.chat.id]  #по ключу имя+фамилия в словарь добавляется др
            # и id сообщения(id сообщения будет нужно в функции show_birthdays)
            save_birthdays(birthdays)
            bot.reply_to(message, f"Birthday for {name_surname} on {date_str} has been added!")
        except ValueError:
            bot.reply_to(message, "Invalid format. Write or press /add_birthday again and use"
                                  "'Name_Surname YYYY-MM-DD'.")

    """функция выводит добавленную информацию из словаря при нажатии /list_birthdays либо сообщение о том, что ДР
    не добавлено"""
    @bot.message_handler(commands=["show_birthdays"])
    def show_birthdays(message):
        if birthdays:
            response = "🎂 Upcoming Birthdays:\n"
            for key, value in birthdays.items():    #key - name_surname, value[0]- date_str
                response += f"- {key}: {value[0]}\n"
        else:
            response = "No birthdays added yet."
        bot.reply_to(message, response)

    """функция удаляет всю загруженную информацию в словарь, делая его пустым при нажатии /delete """
    @bot.message_handler(commands=["delete"])
    def delete(message):
        birthdays.clear()
        with open('birthdays.json', 'w') as file:
            file.write('')

    """функция, отправляющая напоминание о ДР"""
    def send_birthday_reminders():
        today = datetime.now().date()
        for key, value in birthdays.items():
            birthday = datetime.strptime(value[0], "%Y-%m-%d").date()
            if birthday.month == today.month and birthday.day == today.day:  #сравнение сегодняшней даты и дат,
                # записанных в словаре
                bot.send_message(chat_id=value[1], text=f"🎉 Сегодня день рождения у {key}! 🎂") #бот отправляет
                # напоминание о ДР для конкретного name_surname

    """функция показывает, что делать, если нужна помощь с тг ботом"""
    @bot.message_handler(commands=["help"])
    def help_function(message):
        bot.send_message(message.chat.id, "Если у тебя возник вопрос, найди Дамиру и спроси у нее😊")

    """функция отправляет открытку, подходящую для подруги"""
    @bot.message_handler(commands=["Postcard_female_friend"])
    def postcard_female_friend(message):
        file_female = open("./friend female.jpg", "rb")  #открытие файла в бинарном режиме на чтение
        bot.send_photo(message.chat.id, file_female) #отправка фото

    """функция отправляет открытку, подходящую для друга"""
    @bot.message_handler(commands=["Postcard_male_friend"])
    def postcard_male_friend(message):
        file_male = open("./friend male.jpg", "rb")
        bot.send_photo(message.chat.id, file_male)

    """функция отправляет открытку, подходящую для члена семьи"""
    @bot.message_handler(commands=["Postcard_family_member"])
    def postcard_family_member(message):
        file_family = open("./family.jpg", "rb")
        bot.send_photo(message.chat.id, file_family)

    """функция отправляет открытку, подходящую для учителя"""
    @bot.message_handler(commands=["Postcard_teacher"])
    def postcard_teacher(message):
        file_teacher = open("./teacher.jpg", "rb")
        bot.send_photo(message.chat.id, file_teacher)

    scheduler = BackgroundScheduler()  #установка планировщика
    scheduler.add_job(send_birthday_reminders, "interval", seconds=30, start_date=datetime.now() +
                                                                                  timedelta(seconds=10))
    #напоминание о ДР человека будет приходить каждые 30 секунд! этот парамент можно изменить, поставив hours=...
    # 30 секунд я сделала для того, чтобы наглядно и быстро увидеть, как присылаются напоминания
    scheduler.start()
    bot.polling(none_stop=True)




