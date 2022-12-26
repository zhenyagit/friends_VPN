from telebot import TeleBot
from model import Model


class Controller:
	def __init__(self, bot: TeleBot, model: Model):
		self.bot = bot

		@self.bot.message_handler(commands=['start'])
		def start_command(message):
			self.bot.send_message(message.chat.id, "Hello!")

		@self.bot.message_handler(commands=['get_new_config'])
		def start_command(message):
			self.bot.send_message(message.chat.id, "Hello!")

		@self.bot.message_handler(commands=['show_configs'])
		def start_command(message):
			self.bot.send_message(message.chat.id, "Hello!")

		@self.bot.message_handler(commands=['get_config'])
		def start_command(message):
			self.bot.send_message(message.chat.id, "Hello!")

		@self.bot.message_handler(commands=['help'])
		def start_command(message):
			self.bot.send_message(message.chat.id, "Hello!")

	def run(self):
		self.bot.polling()
