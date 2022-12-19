import telebot
from repository import User,Repository,StatLogs,Telegram
from telebot import types
import os

token = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id, 'Привет')


@bot.message_handler(commands=['button'])
def button_message(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton("Кнопка")
	markup.add(item1)
	bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)


@bot.message_handler(content_types='text')
def message_reply(message):
	if message.text == "Кнопка":
		bot.send_message(message.chat.id, "https://habr.com/ru/users/lubaznatel/")


bot.infinity_polling()
