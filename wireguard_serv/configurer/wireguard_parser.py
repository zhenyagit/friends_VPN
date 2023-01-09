import subprocess
# subprocess.getoutput("sudo wg show all dump")


class OutputData:
	def __init__(self, interface, public_key, pre_shared_key,
				 device_ip, localnet_ip,
				 latest_handshake, transfer_rx,
				 transfer_tx, persistent_keepalive):
		self.interface = interface
		self.public_key = public_key
		self.pre_shared_key = pre_shared_key
		self.device_ip = device_ip
		self.localnet_ip = localnet_ip
		self.latest_handshake = latest_handshake
		self.transfer_rx = transfer_rx
		self.transfer_tx = transfer_tx
		self.persistent_keepalive = persistent_keepalive

	def __str__(self):
		out = [self.interface, self.public_key,
			   self.pre_shared_key,self.device_ip,
			   self.localnet_ip,self.latest_handshake,
			   self.transfer_rx, self.transfer_tx,
			   self.persistent_keepalive]
		temp = []
		for i in out:
			if i is None:
				temp.append("none")
			else:
				temp.append(i)
		ans = "\t".join(temp)
		return ans


class OutputParser:

	@staticmethod
	def get_info():
		output = subprocess.getoutput("wg show all dump")
		return output

	@staticmethod
	def split_info(str_line):
		output = str_line.split("\n")[1:]
		output = list(map(lambda x: x.split("\t"), output))
		return output

	def get_data(self, raw_str=None):
		if raw_str is None:
			info = self.get_info()
		else:
			info = raw_str
		info = self.split_info(info)
		if len(info) < 2:
			return None
		data = []
		for line in info:
			temp = self.parse_line(line)
			if temp!=None:
				data.append(temp)
		return data

	@staticmethod
	def check_none(word):
		if word == "(none)":
			return None
		return word

	def parse_line(self, line):
		if len(line) != 9:
			return None
		new_line = []
		for item in line:
			new_line.append(self.check_none(item))
		return OutputData(*new_line)


def demo():
	test_str = 'dump output text '
	parser = OutputParser()
	data = parser.get_data(test_str)
	print(data)
	for i in data:
		print(str(i))


if __name__=="__main__":
	demo()
