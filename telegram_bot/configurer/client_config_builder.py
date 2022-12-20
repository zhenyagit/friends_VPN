import ipaddress

from same_files.config_master import WgPeerClient, WgInterfaceClient
import os

class ClientConfigCreator:
	def __init__(self, interface:WgInterfaceClient, peer:WgPeerClient):
		self.interface = interface
		self.peer = peer

	def create_interface(self, interface:WgInterfaceClient= None):
		if interface is None:
			interface = self.interface
		text = "[Interface]\n"
		text = text + " = ".join(["PrivateKey", interface.private_key]) + "\n"
		text = text + " = ".join(["Address", "/".join([str(interface.address), str(interface.address_mask)])]) + "\n"
		text = text + " = ".join(["DNS", str(interface.DNS)]) + "\n\n"
		return text

	def create_peer(self, peer:WgPeerClient= None):
		if peer is None:
			peer = self.peer
		text = "[Peer]\n"
		text = text + " = ".join(["PublicKey", peer.public_key]) + "\n"
		text = text + " = ".join(["AllowedIPs", str(peer.allowed_ip)]) + "\n"
		text = text + " = ".join(["Endpoint", ":".join([str(peer.endpoint),str(peer.endpoint_port)])]) + "\n"
		text = text + " = ".join(["PersistentKeepalive", str(peer.persistent_keepalive)]) + "\n\n"
		return text

	def create_text(self, interface= None, peer=None):
		if interface is None or peer is None:
			interface = self.interface
			peer = self.peer
		text = self.create_interface(interface)
		text = text + self.create_peer(peer)
		return text


class ConfWriterCli:
	def __init__(self, folder_path):
		self.folder_path = folder_path
		self.check_folder(folder_path)

	def check_folder(self, folder_path=None):
		if folder_path is None:
			folder_path = self.folder_path
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)

	def write_file(self, text, filename, folder_path=None):
		if folder_path is None:
			folder_path = self.folder_path
		with open(folder_path + filename, "w") as file:
			file.write(text)

#  todo check exist configs exceptions


def test():
	wic = WgInterfaceClient("asdadw", ipaddress.IPv4Address("10.0.0.6"), 32, ipaddress.IPv4Address("8.8.8.8"))
	wpc = WgPeerClient("pkey", ipaddress.IPv4Address("5.187.3.41"), 51830, 20)
	ccc = ClientConfigCreator(wic, wpc)
	text = ccc.create_text()
	print(text)
	cwc = ConfWriterCli("../temp/")
	cwc.write_file(text, "test.conf")


if __name__=="__main__":
	test()


