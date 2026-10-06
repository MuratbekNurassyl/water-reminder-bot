import telebot
import threading
import schedule
import time
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
bot = telebot.TeleBot(TOKEN)
water_data = {}
reminders = {}
last_reminder = {}
GOAL = 2000
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Бот-напоминание о воде\n\n"
        "Команды:\n"
        "/setreminder 1 - напоминание каждый час\n"
        "/setreminder 2 - напоминание каждые 2 часа\n"
        "/drank 300 - добавить выпитую воду\n"
        "/status - узнать прогресс")
@bot.message_handler(commands=['setreminder'])
def set_reminder(message):
    try:
        minutes = int(message.text.split()[1])

        if minutes <= 0:
            raise ValueError

        reminders[message.chat.id] = minutes

        bot.send_message(
            message.chat.id,
            f"Напоминание установлено каждые {minutes} мин."
        )

    except:
        bot.send_message(
            message.chat.id,
            "Использование:\n/setreminder 1"
        )

@bot.message_handler(commands=['drank'])
def drank(message):
    try:
        amount = int(message.text.split()[1])
        user_id = message.from_user.id
        water_data[user_id] = water_data.get(user_id, 0) + amount
        total = water_data[user_id]
        if total >= GOAL:
            bot.send_message(
                message.chat.id,
                f" Отлично! Выпито {total} мл.\n" "Цель 2 литра достигнута!")
        else:
            remain = GOAL - total
            bot.send_message(message.chat.id,f"Добавлено {amount} мл.\n"
                f"Всего выпито: {total} мл.\n"
                f"Осталось: {remain} мл.")
    except:
        bot.send_message(message.chat.id,"Использование:\n/drank 300")


@bot.message_handler(commands=['status'])
def status(message):
    user_id = message.from_user.id
    total = water_data.get(user_id, 0)
    remain = max(0, GOAL - total)
    bot.send_message(message.chat.id,f" Выпито: {total} мл\n"
        f" Осталось: {remain} мл до цели" )
def send_reminders():
    current_time = int(time.time())

    for chat_id, interval in reminders.items():

        if current_time - last_reminder.get(chat_id, 0) >= interval * 60:

            try:
                bot.send_message(
                    chat_id,
                    "Не забывай пить воду!\n"
                    "Выпей стакан воды."
                )

                last_reminder[chat_id] = current_time

            except:
                pass
schedule.every(1).minutes.do(send_reminders)
def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
threading.Thread(
    target=scheduler,
    daemon=True
).start()
print("Бот работает")
bot.infinity_polling()