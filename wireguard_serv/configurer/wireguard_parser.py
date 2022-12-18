import subprocess
# subprocess.getoutput("sudo wg show all dump")


class OutputData:
	# !private-key, public-key, listen-port, fwmark
	# !public - key, preshared - key, endpoint, allowed - ips,
	# latest - handshake, transfer - rx, transfer - tx, persistent - keepalive.
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
		output = subprocess.getoutput("sudo wg show all dump")
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
	test_str = 'wg0\tSLm+rkdeY91cBmnyLZXNviChaaVr9ZnKd+8KgnPmW3A=\tYycCBW8UqvQcPzZZ9/gzdgbJWRgf96i2pLToA96hY0o=\t51830\toff\nwg0\twWMzwVhCIbe+0zp9FQhf2uTg5CIHwipSjL+t40Pw0HU=\t(none)\t(none)\t10.0.0.2/32\t0\t0\t0\toff\nwg0\tttM+TSfdJFhFnIIK4o7KSYwCapdeFuCF3jBrySRPIHE=\t(none)\t(none)\t10.0.0.3/32\t0\t0\t0\toff\nwg0\tEDNQBYfzbUiTSTrJ9Zn+cu1pH0ORcx1JqDAZ0su8Ih0=\t(none)\t(none)\t10.0.0.4/32\t0\t0\t0\toff\nwg0\ttc+pANYYrtu8acd6oHfjnjno983H2VaeckgcyC4/TAs=\t(none)\t(none)\t10.0.0.5/32\t0\t0\t0\toff\nwg0\tthl9mYp1PVAyJIYlJrChrvqxJM8naNWtkUKNijwUVlo=\t(none)\t188.243.231.169:47514\t10.0.0.6/32\t1671392183\t265829580\t5403307672\toff\nwg0\tjRQ3diYYSgH7bzkFHS+jO+Qz50J4Zne2a0ZLwA/jBlY=\t(none)\t95.161.248.77:49795\t10.0.0.7/32\t1671311397\t5311696\t96384740\toff\nwg0\tVr0s5QygBhkujUIhJFI1KBw+fSn+xiXFbHOqJ6vZMTs=\t(none)\t188.170.85.223:14855\t10.0.0.8/32\t1671391966\t76786724\t572717312\toff\nwg0\tP7eNvz2k+Vh1No3tmCtk0/ClwG1Q94b6Zg9Q1dcrGVM=\t(none)\t(none)\t10.0.0.9/32\t0\t0\t0\toff\nwg0\tjM+HSGjj5BwMS1QccZucMbs1r4KTU5z5DWX5PQCOgTE=\t(none)\t85.143.70.8:63244\t10.0.0.10/32\t1671390659\t86297380\t3741823772\toff'
	parser = OutputParser()
	data = parser.get_data(test_str)
	print(data)
	for i in data:
		print(str(i))


if __name__=="__main__":
	demo()
