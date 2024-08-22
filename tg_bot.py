import telebot
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}


@bot.message_handler(commands=['start'])
def start(message):
    user_states[message.from_user.id] = 'waiting_for_filters'
    bot.send_message(message.from_user.id, "👋 Привіт! Я допоможу тобі з пошуком квартири на ЛУН")
    bot.send_message(message.from_user.id, "🔗Надішли мені посилання на сторінку з фільтрами на сайті ЛУН")


@bot.message_handler(content_types=['text'])
def get_filters(message):
    if user_states.get(message.from_user.id) == 'waiting_for_filters':
        if message.text.startswith("https://lun.ua/"):
            user_states[message.from_user.id] = 'waiting_for_results'
            bot.send_message(message.from_user.id, "✅Отримав посилання на сторінку з фільтрами")
            bot.send_message(message.from_user.id, "⏳Оброблю інформацію і надішлю тобі результати")
        else:
            bot.send_message(message.from_user.id, "❗️Надішли мені посилання на сторінку з фільтрами на сайті ЛУН."
                                                   " Формат: https://lun.ua/...")


bot.polling(none_stop=True, interval=0)
