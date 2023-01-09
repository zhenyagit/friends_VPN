import ipaddress
import logging
import os
from same_files.kafka_master import KafkaReader, KafkaWriter
from same_files.repository import Repository, Telegram, WireguardClientConfs
from .view import View
from same_files.config_master import WgPeerClient, WgInterfaceClient
from configurer.client_config_builder import ClientConfigCreator, ConfWriterCli
import random

logging = logging.getLogger(__name__)


class KafkaManager:
	def __init__(self, reader: KafkaReader, view: View):
		self.reader = reader
		self.view = view

	def setup_handler(self):
		self.reader.subscribe(self.handler)

	def handler(self, message):
		chat_id = int(message.key)
		data = message.value
		if data["status"] == 1:
			self.view.send_config_done(chat_id, data["config_id"])
		else:
			self.view.send_error(chat_id)


class Model:
	def __init__(self, view: View, kafka_writer: KafkaWriter, repo: Repository,
				 server_ip: ipaddress.IPv4Address, server_port: int):
		self.view = view
		self.writer = kafka_writer
		self.repo = repo
		self.server_keys = self.repo.get_server_keys()
		self.server_ip = server_ip
		self.server_port = server_port

	def check_user(self, u_id):
		return self.repo.user_exist(u_id)

	def create_file(self, config: WireguardClientConfs, name, u_id):
		wic = WgInterfaceClient(config.private_key, config.ip, config.ip_mask, config.dns)
		wpc = WgPeerClient(self.server_keys.public_key, self.server_ip, self.server_port, 20)
		ccc = ClientConfigCreator(wic, wpc)
		text = ccc.create_text()
		cwc = ConfWriterCli("/tmp/")
		file_name = name + "_" + str(u_id) + ".conf"
		cwc.write_file(text, "/tmp/" + file_name)
		return file_name

	def kafka_send_job(self, message):
		u_id = message.from_user.id
		ch_id = message.chat.id
		job = {"user_id": u_id,
			   "chat_id": ch_id,
			   "job_id": random.getrandbits(128),
			   "job_type": 1}
		self.writer.write(str(job["job_id"]), job)

	def no_in_db(self, message):
		self.view.send_hello(message.chat.id)
		u_id = message.from_user.id
		fn = message.from_user.full_name
		un = message.from_user.username
		ch_id = message.chat.id
		temp_user = Telegram(u_id, fn, un, ch_id)
		self.repo.write_object(temp_user)
		self.view.send_how_to_create_config(message.chat.id)

	def start(self, message):
		u_id = message.from_user.id
		if not self.check_user(u_id):
			self.no_in_db(message)
		else:
			if self.repo.config_exist(u_id):
				self.view.send_help(message.chat.id)
			else:
				self.view.send_how_to_create_config(message.chat.id)

	def get_new_config(self, message):
		u_id = message.from_user.id
		logging.info("check user: " + str(u_id) + " in db return : " + str(self.check_user(u_id)))
		if not self.check_user(u_id):
			self.no_in_db(message)
		else:
			logging.info("check user: " + str(u_id) + " config_exist return : " + str(self.repo.config_exist(u_id)))
			if self.repo.config_exist(u_id):
				if len(self.repo.get_configs_by_tg_id(u_id)) > 4:
					self.view.send_too_many_configs(message.chat.id)
				# todo wait while creating
				else:
					self.view.send_wait_sec(message.chat.id)
					self.kafka_send_job(message)
			else:
				self.view.send_wait_sec(message.chat.id)
				self.kafka_send_job(message)

	def show_configs(self, message):
		u_id = message.from_user.id
		if not self.check_user(u_id):
			self.no_in_db(message)
		else:
			if not self.repo.config_exist(u_id):
				self.view.send_no_configs_yet(message.chat.id)
				self.view.send_how_to_create_config(message.chat.id)
			else:
				self.view.send_config_list(message.chat.id, self.repo.get_configs_by_tg_id(u_id))

	def get_config(self, message):
		u_id = message.from_user.id
		try:
			config_id = int(message.text.split(" ")[1])
		except Exception:
			self.view.send_error(message.chat.id)
			return
		logging.info("Send config file {} to chat {}".format(config_id, message.chat.id))
		if not self.check_user(u_id):
			self.no_in_db(message)
		else:
			if self.repo.config_exist(u_id):
				config_list = self.repo.get_configs_by_tg_id(u_id)
				temp_conf = None
				for config in config_list:
					if config.id == config_id:
						temp_conf = config
				if temp_conf is not None:
					logging.info("Send config file {} to chat {}, config founded".format(config_id, message.chat.id))
					file_name = self.create_file(temp_conf, message.from_user.full_name, config_id)
					logging.info("Send config file {} to chat {}, send".format(config_id, message.chat.id))
					self.view.send_dock(message.chat.id, "/tmp/" + file_name)
					os.remove("/tmp/" + file_name)
				else:
					self.view.send_wrong_conf_id(message.chat.id)
			else:
				self.view.send_no_configs_yet(message.chat.id)

	def help(self, message):
		self.view.send_help(message.chat.id)
