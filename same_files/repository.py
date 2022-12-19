import ipaddress
import string
from enum import Enum
import psycopg2
from dataclasses import dataclass
import datetime

# sudo docker run -d --name postgres -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=2846 -e POSTGRES_DB=friends_vpn postgres:14.3
# todo change to env variable

@dataclass
class User:
	id : int
	real_name: string


@dataclass
class Telegram:
	user_id : int
	telegram_name : string
	telegram_nickname : string
	telegram_id: string


@dataclass
class StatLogs:
	conf_id : int
	log_time: datetime.datetime
	last_handshake : datetime.datetime
	transfer_rx : int
	transfer_tx : int

@dataclass
class ConfStats:
	conf_id : int
	stat: int
	time: datetime.datetime

@dataclass
class WireguardClientConfs:
	id : int
	user_id: int
	ip : ipaddress.IPv4Address
	ip_mask : int
	dns : ipaddress.IPv4Address
	private_key : string
	public_key : string


class RequestBuilder:
	class RequestTypes(Enum):
		insert = 0
		select = 1
		remove = 2
		get_id = 3

	def __init__(self):
		self.prefixes = ["""insert into {} ({}) values ({});""",
						 """select {} from {};""",
						 """DELETE FROM {} WHERE {} = {};""",
						 """SELECT currval(pg_get_serial_sequence('{}', 'id'));"""
						 ]

	@staticmethod
	def class_values_to_str(obj):
		list_val = list(obj.values())
		str_line = ", ".join(map(lambda x: "'"+str(x)+"'", list_val))
		print("values =", str_line)
		return str_line

	@staticmethod
	def class_keys_to_str(obj):
		list_val = list(obj.keys())
		str_line = ", ".join(map(lambda x:str(x), list_val))
		print("keys =", str_line)
		return str_line

	@staticmethod
	def get_only_need_values(keys, obj):
		new_obj = {}
		for key in keys:
			new_obj[key] = obj[key]
		return new_obj

	def remove_none(self, obj_dict):
		filtered = {k: v for k, v in obj_dict.items() if v is not None}
		obj_dict.clear()
		obj_dict.update(filtered)
		return obj_dict

	def get_insert(self, table, obj_values):
		add_postfix = False
		obj_values = obj_values.__dict__
		if "id" in obj_values.keys():
			del obj_values["id"]
			add_postfix = True
		self.remove_none(obj_values)
		keys = self.class_keys_to_str(obj_values)
		values = self.class_values_to_str(obj_values)
		req =  self.prefixes[self.RequestTypes.insert.value].format(table, keys, values)
		if add_postfix:
			req = req + "\n" + self.prefixes[self.RequestTypes.get_id.value].format(table)
		return req


class Repository:
	class Tables(Enum):
		user = "users"
		telegram = "telegrams"
		stat_log = "stat_logs"
		conf_stat = "conf_stats"
		wireguard_client_conf = "wireguard_client_confs"

	object_table = {
		"User": Tables.user.value,
		"Telegram": Tables.telegram.value,
		"StatLogs": Tables.stat_log.value,
		"ConfStats": Tables.conf_stat.value,
		"WireguardClientConfs": Tables.wireguard_client_conf.value,
	}

	def __init__(self, dbname, user, password, host):
		self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
		self.cursor = self.conn.cursor()
		self.req_build = RequestBuilder()

	def exec_command(self, command):
		ans = None
		self.cursor.execute(command)
		if self.cursor.pgresult_ptr is not None:
			ans = self.cursor.fetchall()
		self.conn.commit()
		return ans

	def write_object(self, obj):
		table = self.object_table[obj.__class__.__name__]
		command = self.req_build.get_insert(table, obj)
		print(command)
		ans = self.exec_command(command)
		if ans is not None:
			return ans[0][0]
		return ans


def test():
	rep = Repository("friends_vpn", "postgres", "2846", "localhost")
	print("-"*20, end="")
	print("WRITE USER", end="")
	print("-"*20)
	user = User(None,  "zhenya")
	user_id = rep.write_object(user)
	print(user_id)

	print("-" * 20, end="")
	print("WRITE TELEGRAM", end="")
	print("-" * 20)
	tel = Telegram(user_id, "@imjs_man", "tel_nick", "tel_name")
	tel_id = rep.write_object(tel)
	print(tel_id)

	print("-" * 20, end="")
	print("WRITE WireGuardConf", end="")
	print("-" * 20)
	wcc = WireguardClientConfs(None, user_id, ipaddress.IPv4Address("10.0.0.6"), 24, ipaddress.IPv4Address("8.8.8.8"), "private_key", "pub_key")
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


if __name__=="__main__":
	test()
