import logging
import os.path
import subprocess
import ipaddress
import random
from same_files.config_master import WgConfig, WgPeer, WgInterface


class WireguardKeys:
	@staticmethod
	def gen_private_key():
		return subprocess.getoutput("wg genkey")

	@staticmethod
	def gen_public_key(private_key):
		return subprocess.getoutput("echo {} | wg pubkey".format(private_key))

	@staticmethod
	def get_serv_public_key(path_to_config=None):
		if path_to_config is None:
			path_to_config = "/etc/wireguard/"
		return subprocess.getoutput("cat " + path_to_config + "publickey")

	@staticmethod
	def get_serv_private_key(path_to_config=None):
		if path_to_config is None:
			path_to_config = "/etc/wireguard/"
		return subprocess.getoutput("cat " + path_to_config + "privatekey")

	@staticmethod
	def write_serv_public_key(pub_key, path_to_config=None):
		if path_to_config is None:
			path_to_config = "/etc/wireguard/"
		with open(path_to_config + "publickey", "w") as file:
			file.write(pub_key)

	@staticmethod
	def write_serv_private_key(pri_key, path_to_config=None):
		if path_to_config is None:
			path_to_config = "/etc/wireguard/"
		with open(path_to_config + "privatekey", "w") as file:
			file.write(pri_key)


class WireguardControl:
	# todo logging pls
	@staticmethod
	def stop():
		subprocess.getoutput("wg-quick down")

	@staticmethod
	def start():
		subprocess.getoutput("wg-quick up")

	@staticmethod
	def restart():
		subprocess.getoutput("wg-quick down && wg-quick up")


class ConfigParserWg:
	def __init__(self, path_to_file):
		self.path_to_file = path_to_file

	# todo change . to ..
	def read_config(self, path=None):
		if path is None:
			path = self.path_to_file
		with open(path, "r") as file:
			data = file.read()
		return data

	@staticmethod
	def get_main_info(line):
		line = line[line.find("=") + 1:]
		i = 0
		while line[i] == " ":
			i = i + 1
		return line[i:]

	def parse_interface_part(self, part):
		private_key, address, address_mask, listen_port, post_up, post_down = None, None, None, None, None, None
		for line in part:
			# print(line)
			# print(self.get_main_info(line))
			if "PrivateKey" in line: private_key = self.get_main_info(line)
			if "Address" in line:
				temp = self.get_main_info(line).split("/")
				address, address_mask = ipaddress.IPv4Address(temp[0]), int(temp[1])
			if "ListenPort" in line: listen_port = int(self.get_main_info(line))
			if "PostUp" in line: post_up = self.get_main_info(line)
			if "PostDown" in line: post_down = self.get_main_info(line)
		interface = WgInterface(private_key, address, address_mask, listen_port, post_up, post_down)
		return interface

	@staticmethod
	def peer_to_peer(part):
		peers = []
		part = part[1:]
		temp = []
		for item in part:
			if "Peer" in item:
				peers.append(temp)
				temp = []
				continue
			temp.append(item)
		return peers

	def parse_peers(self, part):
		public_key, allowed_ip, allowed_ip_mask = None, None, None
		packed = self.peer_to_peer(part)
		peers = []
		for item in packed:
			for i in item:
				if "PublicKey" in i: public_key = self.get_main_info(i)
				if "AllowedIPs" in i:
					temp = self.get_main_info(i).split("/")
					allowed_ip, allowed_ip_mask = ipaddress.IPv4Address(temp[0]), int(temp[1])
			peers.append(WgPeer(public_key, allowed_ip, allowed_ip_mask))
		return peers

	def parse_config(self, text=None):
		if text is None:
			text = self.read_config()
		text = text.split("\n")
		text = list(filter(None, text))
		interface_lines = text[0:text.index("[Peer]")]
		peers_lines = text[text.index("[Peer]"):]
		interface = self.parse_interface_part(interface_lines)
		peers = self.parse_peers(peers_lines)
		return WgConfig(interface, peers)


class ConfigWriterWg:
	def __init__(self, path_to_file):
		self.path_to_file = path_to_file

	@staticmethod
	def build_interface_text(interface):
		text = '[Interface]\n'
		text = text + " = ".join(["PrivateKey", interface.private_key]) + "\n"
		text = text + " = ".join(
			["Address", "/".join([interface.address.compressed, str(interface.address_mask)])]) + "\n"
		text = text + " = ".join(["ListenPort", str(interface.listen_port)]) + "\n"
		text = text + " = ".join(["PostUp", interface.post_up]) + "\n"
		text = text + " = ".join(["PostDown", interface.post_down]) + "\n\n"
		return text

	@staticmethod
	def build_peers_text(peers):
		text = ""
		for peer in peers:
			text = text + '[Peer]\n'
			text = text + " = ".join(["PublicKey", peer.public_key]) + "\n"
			text = text + " = ".join(
				["AllowedIPs", "/".join([peer.allowed_ip.compressed, str(peer.allowed_ip_mask)])]) + "\n\n"
		return text

	def build_text(self, wg_config):
		text = self.build_interface_text(wg_config.interface)
		text = text + self.build_peers_text(wg_config.peers)
		return text

	def write(self, wg_config):
		text = self.build_text(wg_config)
		with open(self.path_to_file, "w") as file:
			file.write(text)


class ConfigPersonManager:
	def __init__(self, path_to_config):
		self.path_to_config = path_to_config
		self.writer = ConfigWriterWg(path_to_config)
		self.reader = ConfigParserWg(path_to_config)
		self.controller = WireguardControl()
		self.key_master = WireguardKeys()
		self.check_and_create_config()

	def check_and_create_config(self):
		if not os.path.exists(self.path_to_config):
			logging.info("Creating init wg config file")
			pri_key = self.key_master.gen_private_key()
			pub_key = self.key_master.gen_public_key(pri_key)
			self.key_master.write_serv_private_key(pri_key)
			self.key_master.write_serv_public_key(pub_key)
			peer_pri = self.key_master.gen_private_key()
			peer_pub = self.key_master.gen_public_key(peer_pri)
			# todo change ports to env var
			interface = WgInterface(pri_key, ipaddress.IPv4Address("10.0.0.1"), 24, 51832)
			peer = WgPeer(peer_pub, ipaddress.IPv4Address("10.0.0.4"), 32)
			conf = WgConfig(interface, [peer])
			self.writer.write(conf)

	def add_person(self, ip=None):
		config = self.reader.parse_config()
		ips = config.get_ips_simple()
		if ip is None:
			ip = random.randint(0, 255)
			while ip in ips:
				ip = random.randint(0, 255)
		pri = self.key_master.gen_private_key()
		pub = self.key_master.gen_public_key(pri)
		ip_add = ipaddress.IPv4Address('10.0.0.{0}'.format(ip))
		new_peer = WgPeer(pub, ip_add, 32)
		config.add_peer(new_peer)
		self.writer.write(config)
		self.restart()
		return pub, pri, ip_add

	def remove_person_by_ip(self, ip):
		config = self.reader.parse_config()
		config.remove_peer_by_ip(ip)
		self.writer.write(config)

	def restart(self):
		self.controller.restart()


def test():
	cpm = ConfigPersonManager("../config/wg0.conf")
	pri = cpm.key_master.gen_private_key()
	pub = cpm.key_master.gen_public_key(pri)
	print(pub)
	print(pri)
	config = cpm.reader.parse_config()
	print(cpm.add_person())


if __name__ == "__main__":
	test()
