import ipaddress

# todo add logging
# todo add exceptions
# todo mb change to dataclass

class WgInterfaceClient:
	def __init__(self, private_key, address, address_mask, DNS):
		self.private_key = private_key
		self.address = address
		self.address_mask = address_mask
		self.DNS = DNS


class WgInterface(WgInterfaceClient):
	def __init__(self, private_key, address, address_mask, listen_port, post_up=None, post_down=None):
		super().__init__(private_key, address, address_mask, DNS=None)
		self.listen_port = listen_port
		if post_up is None:
			self.post_up = "iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE"
		else:
			self.post_up = post_up
		if post_down is None:
			self.post_down = "iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE"
		else:
			self.post_down = post_down

class WgPeer:
	def __init__(self, public_key, allowed_ip, allowed_ip_mask):
		self.public_key = public_key
		self.allowed_ip = allowed_ip
		self.allowed_ip_mask = allowed_ip_mask


class WgPeerClient(WgPeer):
	def __init__(self, public_key, endpoint, endpoint_port, persistent_keepalive, allowed_ips=None):
		super().__init__(public_key, None, None)
		if allowed_ips is None:
			self.allowed_ip = "0.0.0.0/0"
		else:
			self.allowed_ip = allowed_ips
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
			ips.append(int(i.allowed_ip.compressed.split(".")[-1]))
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


