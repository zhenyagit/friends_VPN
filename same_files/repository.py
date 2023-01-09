import ipaddress
import json
import os
import string
from enum import Enum
from typing import List
import logging
import psycopg2
from dataclasses import dataclass
import datetime
logging = logging.getLogger(__name__)

# todo change to env variable

@dataclass
class ServerKey:
	public_key: string
	private_key: string

@dataclass
class Telegram:
	id: int
	telegram_name: string
	telegram_nickname: string
	telegram_chat_id: int


@dataclass
class StatLogs:
	conf_id: int
	log_time: datetime.datetime
	last_handshake: datetime.datetime
	transfer_rx: int
	transfer_tx: int


@dataclass
class ConfStats:
	conf_id: int
	stat: int
	time: datetime.datetime


@dataclass
class WireguardClientConfs:
	id: int
	telegram_id: int
	ip: ipaddress.IPv4Address
	ip_mask: int
	dns: ipaddress.IPv4Address
	private_key: string
	public_key: string

	@staticmethod
	def constructor_from_tuple(data):
		conf_id = data[0]
		tg_id = data[1]
		ip = ipaddress.IPv4Address(data[2].split("/")[0])
		ip_mask = data[3]
		dns = ipaddress.IPv4Address(data[4].split("/")[0])
		pri_k = data[5]
		pub_k = data[6]
		return WireguardClientConfs(conf_id,tg_id,ip,ip_mask,dns,pri_k,pub_k)


class RequestBuilder:
	class RequestTypes(Enum):
		insert = 0
		select = 1
		remove = 2
		get_id = 3

	def __init__(self):
		with open(os.path.dirname(os.path.abspath(__file__))+"/queries.json", "r") as file:
			self.queries = json.load(file)

	@staticmethod
	def class_values_to_str(obj):
		list_val = list(obj.values())
		str_line = ", ".join(map(lambda x: "'" + str(x) + "'", list_val))
		return str_line

	@staticmethod
	def class_keys_to_str(obj):
		list_val = list(obj.keys())
		str_line = ", ".join(map(lambda x: str(x), list_val))
		return str_line

	@staticmethod
	def get_only_need_values(keys, obj):
		new_obj = {}
		for key in keys:
			new_obj[key] = obj[key]
		return new_obj

	@staticmethod
	def remove_none(obj_dict):
		filtered = {k: v for k, v in obj_dict.items() if v is not None}
		obj_dict.clear()
		obj_dict.update(filtered)
		return obj_dict

	def get_insert(self, table, obj_values):
		add_postfix = False
		obj_values = obj_values.__dict__
		if "id" in obj_values.keys():
			if obj_values.get("id") is None:
				add_postfix = True
		self.remove_none(obj_values)
		keys = self.class_keys_to_str(obj_values)
		values = self.class_values_to_str(obj_values)
		req = self.queries["insert"].format(table, keys, values)
		if add_postfix:
			req = req + "\n" + self.queries["get_last_id"].format(table)
		return req

	def get_user_by_id(self, u_id):
		req = self.queries["get_user_by_id"].format(u_id)
		return req

	def get_configs_by_tg_id(self, u_id):
		req = self.queries["get_configs_by_user_id"].format(u_id)
		return req

	def get_server_keys(self):
		req = self.queries["get_server_keys"]
		return req


class Repository:
	class Tables(Enum):
		user = "users"
		telegram = "telegrams"
		stat_log = "stat_logs"
		conf_stat = "conf_stats"
		wireguard_client_conf = "wireguard_client_confs"
		server_keys = "server_keys"


	object_table = {
		"User": Tables.user.value,
		"Telegram": Tables.telegram.value,
		"StatLogs": Tables.stat_log.value,
		"ConfStats": Tables.conf_stat.value,
		"WireguardClientConfs": Tables.wireguard_client_conf.value,
		"ServerKey": Tables.server_keys.value,
	}

	def __init__(self, dbname, user, password, host):
		self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
		self.cursor = self.conn.cursor()
		self.req_build = RequestBuilder()

	def exec_command(self, command):
		ans = None
		logging.info(command)
		try:
			self.cursor.execute(command)
			if self.cursor.pgresult_ptr is not None:
				ans = self.cursor.fetchall()
			self.conn.commit()
		except Exception as ex:
			logging.error(ex)
		return ans

	def write_object(self, obj):
		table = self.object_table[obj.__class__.__name__]
		command = self.req_build.get_insert(table, obj)
		ans = self.exec_command(command)
		if ans is not None:
			return ans[0][0]
		return ans

	def get_user(self, u_id):
		req = self.req_build.get_user_by_id(u_id)
		ans = self.exec_command(req)
		if len(ans) == 0:
			return None
		user = Telegram(*ans[0])
		logging.info("Get user: " + str(user))
		return user

	def user_exist(self, u_id):
		req = self.req_build.get_user_by_id(u_id)
		ans = self.exec_command(req)
		if len(ans) == 0:
			return False
		return True

	def config_exist(self, u_id):
		req = self.req_build.get_configs_by_tg_id(u_id)
		ans = self.exec_command(req)
		if len(ans) == 0:
			return False
		return True

	def get_configs_by_tg_id(self, u_id)->List[WireguardClientConfs]:
		req = self.req_build.get_configs_by_tg_id(u_id)
		ans = self.exec_command(req)
		configs = []
		for item in ans:
			configs.append(WireguardClientConfs.constructor_from_tuple(item))
		return configs

	def get_server_keys(self):
		req = self.req_build.get_server_keys()
		ans = self.exec_command(req)
		if len(ans) == 0:
			return None
		return ServerKey(*ans[0])




def test():
	rep = Repository("friends_vpn", "postgres", "2846", "localhost")

	print("-" * 20, end="")
	print("WRITE TELEGRAM", end="")
	print("-" * 20)
	tel = Telegram(2543648, "tel_name", "tel_nick")
	tel_id = rep.write_object(tel)
	print(tel_id)

	print("-" * 20, end="")
	print("WRITE WireGuardConf", end="")
	print("-" * 20)
	wcc = WireguardClientConfs(None, 2543648, ipaddress.IPv4Address("10.0.0.6"), 24, ipaddress.IPv4Address("8.8.8.8"),
							   "private_key", "pub_key")
	wcc_id = rep.write_object(wcc)
	print(wcc_id)

	print("-" * 20, end="")
	print("WRITE WGS", end="")
	print("-" * 20)
	cs = ConfStats(wcc_id, 1, None)
	cs_id = rep.write_object(cs)
	print(cs_id)

	print("-" * 20, end="")
	print("WRITE STAT LOG", end="")
	print("-" * 20)
	log = StatLogs(wcc_id, None, datetime.datetime.now(), 12321415, 0)
	log_id = rep.write_object(log)
	print(log_id)


def test2():
	rep = Repository("friends_vpn", "postgres", "2846", "localhost")
	data = rep.get_user(2543648)
	print(data)
	data = rep.get_configs_by_tg_id(2543648)
	print(data)


if __name__ == "__main__":
	# test()
	test2()
