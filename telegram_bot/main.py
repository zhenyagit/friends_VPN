import time
from telebot import TeleBot
from telegram.model import Model, KafkaManager
from telegram.view import View
from telegram.controller import Controller
from same_files.repository import Repository
from same_files.kafka_master import KafkaReader, KafkaWriter
import logging
import os


def main():
	debug_st = os.getenv("DEBUG")
	if debug_st == "no":
		logging.basicConfig(level=logging.INFO)
		print("logging in INFO mode")
	else:
		logging.basicConfig(level=logging.DEBUG)
		print("logging in DEBUG mode")
	delay = os.getenv("DELAY")
	if delay is not None:
		time.sleep(int(delay))
	token = os.getenv("TELEGRAM_TOKEN")
	db_name = os.getenv("DB_NAME")
	db_user = os.getenv("DB_USER")
	db_pass = os.getenv("DB_PASS")
	db_host = os.getenv("DB_HOST")
	kafka_servers = os.getenv("KAFKA_SERVERS").split(";")
	kafka_jobs_topic = os.getenv("KAFKA_JOBS_TOPIC")
	kafka_done_topic = os.getenv("KAFKA_DONE_TOPIC")

	bot = TeleBot(token)
	repo = Repository(db_name, db_user, db_pass, db_host)
	kafka_reader = KafkaReader(kafka_done_topic, kafka_servers)
	kafka_writer = KafkaWriter(kafka_jobs_topic, kafka_servers)

	view = View(bot)
	model = Model(view, kafka_writer, repo)
	controller = Controller(bot, model)
	kafka_mgr = KafkaManager(kafka_reader, view)

	kafka_mgr.setup_handler()
	controller.run()


if __name__ == '__main__':
	main()