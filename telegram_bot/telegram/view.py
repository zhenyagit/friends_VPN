import json
from typing import List

from same_files.repository import WireguardClientConfs
from telebot import TeleBot


class View:
	def __init__(self, bot: TeleBot):
		self.bot = bot
		self.saved_messages = self.load_messages()

	@staticmethod
	def load_messages():
		with open("message_texts.json", "r") as file:
			data = json.load(file)
		return data

	def send_hello(self, ch_id):
		self.bot.send_message(ch_id, self.saved_messages["hello"])

	def send_how_to_create_config(self, ch_id):
		self.bot.send_message(ch_id, self.saved_messages["how_to_create_config"])

	def send_forget_something(self, ch_id):
		self.bot.send_message(ch_id, self.saved_messages["forget_something"])

	def send_wait_sec(self, ch_id):
		self.bot.send_message(ch_id, self.saved_messages["wait_sec"])

	def send_too_many_configs(self, ch_id):
		self.bot.send_message(ch_id, self.saved_messages["too_many_configs"])

	def send_no_configs_yet(self, ch_id):
		self.bot.send_message(ch_id, self.saved_messages["no_configs_yet"])

	def send_help(self, ch_id):
		self.bot.send_message(ch_id, self.saved_messages["help"])

	def send_custom_message(self, chat_id, message):
		self.bot.send_message(chat_id, message)

	def send_dock(self, chat_id, file_name):
		with open(file_name, "r") as file:
			self.bot.send_document(chat_id, file)

	def send_config_list(self, chat_id, configs:List[WireguardClientConfs]):
		text = [self.saved_messages["show_configs"]]
		for config in configs:
			text.append("/get_config {}".format(config.id))
		self.bot.send_document(chat_id, "\n".join(text))

	def send_error(self, chat_id):
		self.bot.send_message(chat_id, self.saved_messages["error"])

	def send_wrong_conf_id(self, chat_id):
		self.bot.send_message(chat_id, self.saved_messages["wrong_conf_id"])





