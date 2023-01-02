from telebot import TeleBot
from .model import Model
import logging
logging = logging.getLogger(__name__)


class Controller:
	def __init__(self, bot: TeleBot, model: Model):
		self.bot = bot
		self.model = model

		@self.bot.message_handler(commands=['start'])
		def start_command(message):
			self.model.start(message)

		@self.bot.message_handler(commands=['get_new_config'])
		def start_command(message):
			self.model.get_new_config(message)

		@self.bot.message_handler(commands=['show_configs'])
		def start_command(message):
			self.model.show_configs(message)

		@self.bot.message_handler(commands=['get_config'])
		def start_command(message):
			self.model.get_config(message)

		@self.bot.message_handler(commands=['help'])
		def start_command(message):
			self.model.help(message)

	def run(self):
		self.bot.polling()
