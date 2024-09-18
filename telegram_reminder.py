import telebot, os
from telebot.types import Message
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from apscheduler.triggers.date import DateTrigger
from dotenv import load_dotenv
from colorama import Fore, init, Style
import pytz

load_dotenv()
init(convert=True)

jadwal = {}
owner = 
bot = telebot.TeleBot(os.getenv("TOKEN"))

if bot:
    scheduler = BackgroundScheduler()
    scheduler.start()

    def is_admin(message: Message) -> bool:
        return message.from_user.id == owner

    @bot.message_handler(commands=["start"])
    def welcomeUser(message: Message):
        if is_admin(message):
            bot.reply_to(message, "You can use me as reminder bot!")
        else:
            bot.reply_to(message, "You are not authorized to use this bot.")

    @bot.message_handler(commands=["reminder"])
    def setReminder(message: Message):
        if is_admin(message):
            try:
                content = message.text.split(" ", 1)[1]
                username, order_time_str, expiry_time_str, isi_pesan = content.split("|")
                order_time = datetime.strptime(order_time_str.strip(), '%d-%m-%Y %H:%M')
                expiry_time = datetime.strptime(expiry_time_str.strip(), '%d-%m-%Y %H:%M')
                local_tz = pytz.timezone('Asia/Jakarta')
                order_time = local_tz.localize(order_time)
                expiry_time = local_tz.localize(expiry_time)
                expiry_time_awal = expiry_time - timedelta(days=3)
                expiry_time_tengah = expiry_time - timedelta(days=7)
                jadwal[username.strip()] = (message.chat.id, isi_pesan, expiry_time, order_time)
                scheduler.add_job(send_reminder, 'date', run_date=expiry_time, args=[message.chat.id, isi_pesan, username, expiry_time, order_time])
                scheduler.add_job(send_reminder_tengah, 'date', run_date=expiry_time_tengah, args=[message.chat.id, isi_pesan, username, expiry_time, order_time])
                scheduler.add_job(send_reminder_awal, 'date', run_date=expiry_time_awal, args=[message.chat.id, isi_pesan, username, expiry_time, order_time])
                bot.reply_to(message, f"Pengingat terpasang untuk {username} pada {expiry_time.strftime('%d-%m-%Y %H:%M')}")
            except Exception as e:
                bot.reply_to(message, "Format salah, gunakan /reminder @username|DD-MM-YY HH:MM|DD-MM-YY HH:MM|Pesan \n\nPesan akan dikirimkan pada tanggal berakhir")
                print(f"Error: {e}")

    @bot.message_handler(commands=["listreminders"])
    def listReminders(message: Message):
        if is_admin(message):
            if jadwal:
                reminders_list = "\n".join(
                    [f"{username}: {isi_pesan} pada {waktu.strftime('%d-%m-%Y %H:%M')}"
                     for username, (_, isi_pesan, waktu, _) in jadwal.items()]
                )
                with open("listReminders.txt", "w") as file:
                    file.write(f"Daftar Pengingat:\n{reminders_list}")
                bot.reply_to(message, f"Daftar Pengingat:\n{reminders_list}")
            else:
                bot.reply_to(message, "Tidak ada pengingat yang terdaftar saat ini.")
        else:
            bot.reply_to(message, "You are not authorized to use this command.")

    @bot.message_handler(commands=["hapus"])
    def removeReminder(message: Message):
        if is_admin(message):
            try:
                content = message.text.split(" ", 1)[1]
                username = content.strip()
                if username in jadwal:
                    del jadwal[username]
                    bot.reply_to(message, f"Pengingat untuk {username} telah dihapus.")
                else:
                    bot.reply_to(message, f"Tidak ada pengingat untuk {username}.")
            except Exception as e:
                bot.reply_to(message, "Format salah, gunakan /hapus @username")
                print(f"Error: {e}")

    def send_reminder(chat_id, isi_pesan, username, expiry_time, order_time):
        message_text = (f"Buyer: {username}\n"
                        f"Pesan: {isi_pesan}\n"
                        f"Order: {order_time.strftime('%d-%m-%Y %H:%M')}\n"
                        f"Expiry: {expiry_time.strftime('%d-%m-%Y %H:%M')}")
        bot.send_message(chat_id, message_text)
        for user, (stored_chat_id, _, _, _) in list(jadwal.items()):
            if stored_chat_id == chat_id:
                del jadwal[user]
                break

    def send_reminder_awal(chat_id, isi_pesan, username, expiry_time, order_time):
        message_text = (f"Reminder 3 hari sebelum expiry:\n"
                        f"Buyer: {username}\n"
                        f"Pesan: {isi_pesan}\n"
                        f"Order: {order_time.strftime('%d-%m-%Y %H:%M')}\n"
                        f"Expiry: {expiry_time.strftime('%d-%m-%Y %H:%M')}\n\n"
                        f"Silahkan melakukan renewal apabila anda ingin")
        bot.send_message(chat_id, message_text)
        for user, (stored_chat_id, _, _, _) in list(jadwal.items()):
            if stored_chat_id == chat_id:
                del jadwal[user]
                break

    def send_reminder_tengah(chat_id, isi_pesan, username, expiry_time, order_time):
        message_text = (f"Reminder 7 hari sebelum expiry:\n"
                        f"Buyer: {username}\n"
                        f"Pesan: {isi_pesan}\n"
                        f"Order: {order_time.strftime('%d-%m-%Y %H:%M')}\n"
                        f"Expiry: {expiry_time.strftime('%d-%m-%Y %H:%M')}\n\n"
                        f"Silahkan melakukan renewal apabila anda ingin")
        bot.send_message(chat_id, message_text)
        for user, (stored_chat_id, _, _, _) in list(jadwal.items()):
            if stored_chat_id == chat_id:
                del jadwal[user]
                break

    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Bot starting.. ")
    bot.polling(non_stop=True)
