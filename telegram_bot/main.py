import telebot
from telebot import types
import os
import telegram.model

class Telegram:
	def __init__(self, token):
		self.token = token
		self.bot = telebot.TeleBot(self.token)

		@self.bot.message_handler(commands=['start'])
		def start_command(message):
			self.bot.send_message(message.chat.id, "Hello!")

		# @bot.message_handler(commands=['start'])
		# def start_message(message):
		# 	bot.send_message(message.chat.id, 'Привет')
		# 	chat_id = message.chat.id
		# 	user = message.from_user
		# 	full_name = user.full_name
		# 	username = user.username
		# 	user_id = user.id
		# 	print([chat_id, username, full_name, user_id])

		# @bot.message_handler(commands=['button'])
		# def button_message(message):
		# 	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		# 	item1 = types.KeyboardButton("Кнопка")
		# 	markup.add(item1)
		# 	bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)
		#
		# @bot.message_handler(commands=['get_new_config'])
		# def button_message(message):
		# 	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		# 	item1 = types.KeyboardButton("Кнопка")
		# 	markup.add(item1)
		# 	bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)
		#
		# @bot.message_handler(content_types='text')
		# def message_reply(message):
		# 	if message.text == "Кнопка":
		# 		bot.send_message(message.chat.id, "https://habr.com/ru/users/lubaznatel/")

	def run(self):
		self.bot.polling()


if __name__ == '__main__':
	token = os.getenv("TELEGRAM_TOKEN")
	Tele = Telegram(token)
	Tele.run()