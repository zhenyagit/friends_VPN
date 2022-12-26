import telebot
from telebot import types
import os


class Telegram:
	def __init__(self, token):
		self.token = token
		self.bot = telebot.TeleBot(self.token)

		@self.bot.message_handler(commands=['start'])
		def start_command(message):
			self.bot.send_message(message.chat.id, "Hello!")

	def run(self):
		self.bot.polling()


if __name__ == '__main__':
	token = os.getenv("TELEGRAM_TOKEN")
	Tele = Telegram(token)
	Tele.run()