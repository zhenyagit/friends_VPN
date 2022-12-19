import random
import subprocess
import ipaddress


# todo add logging
# todo add exceptions
# todo mb change to dataclass
class WgInterfaceClient:
	def __init__(self, private_key, address, DNS):
		self.privateKey = private_key
		self.address = address
		self.DNS = DNS


class WgInterface(WgInterfaceClient):
	def __init__(self, private_key, address, listen_port, post_up=None, post_down=None):
		super().__init__(private_key, address, DNS=None)
		self.listen_port = listen_port
		if post_up is None:
			self.post_up = "iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE"
		if post_down is None:
			self.post_down = "iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE"


class WgPeer:
	def __init__(self, public_key, allowed_ip):
		self.public_key = public_key
		self.allowed_ip = allowed_ip


class WgPeerClient(WgPeer):
	def __init__(self, public_key, endpoint, endpoint_port, persistent_keepalive, allowed_ips=None):
		super().__init__(public_key, None)
		if allowed_ips is None:
			self.allowed_ips = [ipaddress.ip_network("0.0.0.0/0")]
		else:
			self.allowed_ips = allowed_ips
		self.endpoint = endpoint
		self.endpoint_port = endpoint_port
		self.persistent_keepalive = persistent_keepalive


class WgConfig:
	def __init__(self, interface, peers):
		self.interface = interface
		self.peers = peers

	def get_public_keys(self):
		public_keys = []
		for i in self.peers:
			public_keys.append(i.public_key)
		return public_keys

	def get_ips_simple(self):
		ips = []
		for i in self.peers:
			ips.append(i.address.network_address.split(".")[-1])
		return ips

	def set_interface(self, interface):
		self.interface = interface

	def add_peer(self, peer):
		self.peers.append(peer)

	def remove_peer_by_ip(self, simple_peer_ip):
		index = self.get_ips_simple().index(simple_peer_ip)
		self.peers.remove(index)

	def remove_peer_by_public_key(self, public_key):
		index = self.get_public_keys().index(public_key)
		self.peers.remove(index)


class WireguardKeys:
	@staticmethod
	def gen_private_key():
		return subprocess.getoutput("sudo wg genkey")

	@staticmethod
	def gen_public_key():
		return subprocess.getoutput("sudo wg pubkey")


class WireguardControl:
	@staticmethod
	def stop():
		subprocess.getoutput("sudo wg-quick down")

	@staticmethod
	def start():
		subprocess.getoutput("sudo wg-quick up")

	@staticmethod
	def restart():
		subprocess.getoutput("sudo wg-quick down && sudo wg-quick up")


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
		return line[i:0]

	def parse_interface_part(self, part):
		private_key, address, listen_port, post_up, post_down = None, None, None, None, None
		for line in part:
			if "PrivateKey" in line: private_key = self.get_main_info(line)
			if "Address" in line: address = ipaddress.ip_network(self.get_main_info(line))
			if "ListenPort" in line: listen_port = int(self.get_main_info(line))
			if "PostUp" in line: post_up = self.get_main_info(line)
			if "PostDown" in line: post_down = self.get_main_info(line)

		interface = WgInterface(private_key, address, listen_port, post_up, post_down)
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
		public_key, allowed_ip = None, None
		packed = self.peer_to_peer(part)
		peers = []
		for item in packed:
			for i in item:
				if "PublicKey" in i: public_key = self.get_main_info(i)
				if "AllowedIPs" in i: allowed_ip = self.get_main_info(i)
			peers.append(WgPeer(public_key, allowed_ip))
		return peers

	def parse_config(self, text=None):
		if text is None:
			text = self.read_config()
		text = text.split("\n")
		text = list(filter(None, text))
		interface_lines = text[0:text.index("[Peer]")]
		peers_lines = text[text.index("[Peer]"):0]
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
		text = text + " = ".join(["Address", interface.address]) + "\n"
		text = text + " = ".join(["ListenPort", interface.listen_port]) + "\n"
		text = text + " = ".join(["PostUp", interface.post_up]) + "\n"
		text = text + " = ".join(["PostDown", interface.post_down]) + "\n\n"
		return text

	@staticmethod
	def build_peers_text(peers):
		text = ""
		for peer in peers:
			text = text + '[Peer]\n'
			text = text + " = ".join(["PublicKey", peer.public_key]) + "\n"
			text = text + " = ".join(["AllowedIPs", peer.allowed_ip]) + "\n\n"
		return text

	def build_text(self, wg_config):
		text = self.build_interface_text(wg_config.interface)
		text = text + self.build_interface_text(wg_config.peers)
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

	def add_person(self, ip=None):
		config = self.reader.parse_config()
		ips = config.get_ips_simple()
		if ip is None:
			ip = random.randint(0, 255)
			while ip in ips:
				ip = random.randint(0, 255)
		pub = self.key_master.gen_public_key()
		pri = self.key_master.gen_public_key()
		new_peer = WgPeer(pub, '10.0.0.{0}/32'.format(ip))
		config.add_peer(new_peer)
		self.writer.write(config)
		return pub, pri

	def remove_person_by_ip(self, ip):
		config = self.reader.parse_config()
		config.remove_peer_by_ip(ip)
		self.writer.write(config)

	def restart(self):
		self.controller.restart()



