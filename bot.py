import telebot
from dotenv import load_dotenv
import os

from telebot import types

from scraper import LUNRentScraper
from utils import save_order, remove_order

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
def make_order(message):
    if user_states.get(message.from_user.id) == 'waiting_for_filters':
        if message.text.startswith("https://lun.ua/"):
            save_order(message.from_user.id, message.text, -1)
            user_states[message.from_user.id] = 'waiting_for_results'
            bot.send_message(message.from_user.id, "✅Отримав посилання на сторінку з фільтрами")
            bot.send_message(message.from_user.id, "⏳Ось останні оголошення по запиту. Тепер я буду повідомляти про нові")
            realties = process_order([message.from_user.id, message.text, -1])
            if not realties:
                remove_order(message.from_user.id)
                user_states[message.from_user.id] = 'waiting_for_filters'
                bot.send_message(message.from_user.id, "❗️На жаль, за даним запитом нічого не знайдено. Надішли мені інше посилання")
            else:
                send_notifications(message.from_user.id, realties)
        else:
            bot.send_message(message.from_user.id, "❗️Надішли мені посилання на сторінку з фільтрами на сайті ЛУН."
                                                   " Формат: https://lun.ua/...")

def process_order(order: list[str]) -> list[dict]:
    user_id, search_url, last_scraped_id = order

    scraper = LUNRentScraper(search_url, int(last_scraped_id))
    realties = scraper.scrape()

    return realties


def send_notifications(user_id, realties):

    for realty in realties:
        picture_url = realty.get('picture')

        caption = (
            f"🏠 **Адреса:** {realty.get('address', 'Не вказано')}\n"
            f"💰 **Ціна:** {realty.get('price', 'Не вказано')}\n"
            f"📄 **Опис:** {realty.get('description', 'Опис відсутній')}\n"
        )

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Перейти до оголошення", url=f"https://lun.ua/realty/{realty['id']}")
        markup.add(button)

        if picture_url:
            bot.send_photo(user_id, picture_url, caption=caption, parse_mode='Markdown',
                           reply_markup=markup)
        else:
            bot.send_message(user_id, caption, parse_mode='Markdown', reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
