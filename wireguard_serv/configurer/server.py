import ipaddress

from same_files.repository import Repository, ServerKey, WireguardClientConfs
from same_files.kafka_master import KafkaReader, KafkaWriter
from .config_server import ConfigPersonManager,  WireguardKeys


class WireguardServ:
	def __init__(self, path_to_config, repo: Repository):
		self.repo = repo
		self.config_master = ConfigPersonManager(path_to_config)
		self.check_keys()

	def check_keys(self):
		keys = self.repo.get_server_keys()
		if keys is None:
			wg_keys = WireguardKeys()
			s_k = ServerKey(wg_keys.get_serv_public_key(), wg_keys.get_serv_private_key())
			self.repo.write_object(s_k)

	def add_person(self, tg_id):
		pub, pri, ip = self.config_master.add_person()
		wg_conf = WireguardClientConfs(None, tg_id, ip, 32, ipaddress.IPv4Address("8.8.8.8"), pri, pub)
		conf_id = self.repo.write_object(wg_conf)
		return conf_id


class KafkaManager:
	def __init__(self, reader: KafkaReader, writer: KafkaWriter, server: WireguardServ):
		self.server = server
		self.reader = reader
		self.writer = writer

	def setup_handler(self):
		self.reader.subscribe(self.handler)

	def handler(self, message):
		chat_id = message.value["chat_id"]
		user_id = message.value["user_id"]
		conf_id = self.server.add_person(user_id)
		data = {"status": 1,
				"config_id": conf_id}
		self.writer.write(chat_id, data)
