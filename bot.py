import tempfile
import os

import telebot
from dotenv import load_dotenv

from telebot import types

from core.scraper import LUNRentScraper
from core.utils import save_order, remove_order

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}


@bot.message_handler(commands=["start"])
def start(message):
    user_states[message.from_user.id] = "waiting_for_filters"
    bot.send_message(
        message.from_user.id, "👋 Привіт! Я допоможу тобі з пошуком квартири на ЛУН"
    )
    bot.send_message(
        message.from_user.id,
        "🔗Надішли мені посилання на сторінку з фільтрами на сайті ЛУН",
    )


@bot.message_handler(commands=["debug_link"])
def debug_link(message):
    if "https://lun.ua/" in message.text:
        if len(message.text.split()) < 2 or not message.text.split()[1].startswith(
            "https://lun.ua/"
        ):
            bot.send_message(message.from_user.id, "❗️Неправильний формат")
            return
        link = message.text.split()[1]
        content = debug_process_order([message.from_user.id, link, -1])
        send_temp_html(message.from_user.id, content)


@bot.message_handler(content_types=["text"])
def make_order(message):
    if user_states.get(message.from_user.id) == "waiting_for_filters":
        if message.text.startswith("https://lun.ua/"):
            save_order(message.from_user.id, message.text, -1)
            user_states[message.from_user.id] = "waiting_for_results"
            bot.send_message(
                message.from_user.id, "✅Отримав посилання на сторінку з фільтрами"
            )
            realties = process_order([message.from_user.id, message.text, -1])[::-1]
            if not realties:
                remove_order(message.from_user.id)
                user_states[message.from_user.id] = "waiting_for_filters"
                bot.send_message(
                    message.from_user.id,
                    "❗️На жаль, за даним запитом нічого не знайдено. Надішли мені інше посилання",
                )
            else:
                save_order(
                    int(message.from_user.id), message.text, int(realties[-1]["id"])
                )
                send_notifications(message.from_user.id, realties)
        else:
            bot.send_message(
                message.from_user.id,
                "❗️Надішли мені посилання на сторінку з фільтрами на сайті ЛУН."
                " Формат: https://lun.ua/...",
            )


def process_order(order: list[str]) -> list[dict]:
    _, search_url, last_scraped_id = order

    scraper = LUNRentScraper(search_url, int(last_scraped_id))
    realties = scraper.scrape()

    return realties


def debug_process_order(order: list[str]) -> str:
    _, search_url, last_scraped_id = order

    scraper = LUNRentScraper(search_url, int(last_scraped_id))
    content = scraper.get_full_html_page()

    return content


def send_temp_html(user_id, content: str):
    with tempfile.NamedTemporaryFile(
        mode="w+", delete=False, prefix="debug_", suffix=".html"
    ) as file:
        file.write(content)
        file.flush()
        temp_file_name = file.name

    with open(temp_file_name, "rb") as file_to_send:
        bot.send_document(user_id, file_to_send)
    os.remove(temp_file_name)


def send_notifications(user_id, realties):
    bot.send_message(
        user_id, "🔔 Ось нові оголошення, які відповідають вашим фільтрам:"
    )
    for realty in realties:
        picture_url = realty.get("picture")

        desc = (
            f"🏠 **Адреса:** {realty.get('address', 'Не вказано')}\n"
            f"💰 **Ціна:** {realty.get('price', 'Не вказано')}\n"
            f"📄 **Опис:** {realty.get('description', 'Опис відсутній')}\n"
        )

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(
            "Перейти до оголошення", url=f"https://lun.ua/realty/{realty['id']}"
        )
        markup.add(button)
        shortened_desc = desc[:200] + "..."
        if picture_url:
            bot.send_photo(
                user_id,
                picture_url,
                caption=shortened_desc,
                parse_mode="Markdown",
                reply_markup=markup,
            )
        else:
            bot.send_message(
                user_id, shortened_desc, parse_mode="Markdown", reply_markup=markup
            )


if __name__ == "__main__":
    bot.infinity_polling(timeout=60)
