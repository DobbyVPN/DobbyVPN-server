import re
import json

from urllib.request import urlopen
from typing import List, Optional

from util import *


SERVER_CONFIG_PATTERN = """[Peer]
# Name = <Name>
# PrivateKey = <ClientPrivateKey>
PublicKey = <ClientPublicKey>
AllowedIPs = <ClientAddress>
"""


CLIENT_CONFIG_PATTERN = """[Interface]
PrivateKey = <ClientPrivateKey>
# PublicKey = <ClientPublicKey>
Address = <ClientAddress>
Jc = <Jc>
Jmin = <Jmin>
Jmax = <Jmax>
S1 = <S1>
S2 = <S2>
H1 = <H1>
H2 = <H2>
H3 = <H3>
H4 = <H4>

[Peer]
AllowedIPs = 0.0.0.0/0
Endpoint = <ServerHost>:<ServerPort>
PersistentKeepalive = 60
PublicKey = <ServerPublicKey>
"""


class InterfaceConfig:
	def __init__(
			self,
			value: str,
			private_key: Optional[str],
			public_key: Optional[str],
			hostname: str,
			address: str,
			listen_port: str,
			Jc: str,
			Jmin: str,
			Jmax: str,
			S1: str,
			S2: str,
			H1: str,
			H2: str,
			H3: str,
			H4: str):
		self.value = value
		self.private_key = private_key
		self.public_key = public_key
		self.hostname = hostname
		self.address = address
		self.listen_port = listen_port
		self.Jc = Jc
		self.Jmin = Jmin
		self.Jmax = Jmax
		self.S1 = S1
		self.S2 = S2
		self.H1 = H1
		self.H2 = H2
		self.H3 = H3
		self.H4 = H4

	@staticmethod
	def from_string(value: str):
		private_key = re.search(r"PrivateKey = (\S+)", value)

		if private_key is None:
			private_key_string = None
			public_key_string = None
		else:
			try:
				private_key_string = private_key.group(1)
				private_key_x25519 = string_to_private_key(private_key_string)
				public_key_x25519  = private_key_x25519.public_key()
				public_key_string = public_key_to_string(public_key_x25519)
			except Exception as ex:
				private_key_string = None
				public_key_string = None

		url = 'http://ipinfo.io/json'
		response = urlopen(url)
		data = json.load(response)
		hostname = data['ip']

		address = re.search(r"Address = (\S+)", value)
		listen_port = re.search(r"ListenPort = (\S+)", value)
		jc = re.search(r"Jc = (\S+)", value)
		jmin = re.search(r"Jmin = (\S+)", value)
		jmax = re.search(r"Jmax = (\S+)", value)
		s1 = re.search(r"S1 = (\S+)", value)
		s2 = re.search(r"S2 = (\S+)", value)
		h1 = re.search(r"H1 = (\S+)", value)
		h2 = re.search(r"H2 = (\S+)", value)
		h3 = re.search(r"H3 = (\S+)", value)
		h4 = re.search(r"H4 = (\S+)", value)

		return InterfaceConfig(
			value=value,
			private_key=private_key_string,
			public_key=public_key_string,
			hostname=hostname,
			address="10.9.9.1/32" if address is None else address.group(1),
			listen_port="51280" if listen_port is None else listen_port.group(1),
			Jc="0" if jc is None else jc.group(1),
			Jmin="0" if jmin is None else jmin.group(1),
			Jmax="0" if jmax is None else jmax.group(1),
			S1="0" if s1 is None else s1.group(1),
			S2="0" if s2 is None else s2.group(1),
			H1="1" if h1 is None else h1.group(1),
			H2="2" if h2 is None else h2.group(1),
			H3="3" if h3 is None else h3.group(1),
			H4="4" if h4 is None else h4.group(1))

	@property
	def interface_string(self):
		return self.value


class PeerConfig:
	def __init__(self, name: str, client_private: str, client_public: str, client_address: str):
		self.name = name
		self.client_private = client_private
		self.client_public = client_public
		self.client_address = client_address

	@staticmethod
	def from_string(value: str):
		return PeerConfig(
			name=re.search(r"# Name = (\S+)", value).group(1),
			client_private=re.search(r"# PrivateKey = (\S+)", value).group(1),
			client_public=re.search(r"PublicKey = (\S+)", value).group(1),
			client_address=re.search(r"AllowedIPs = (\S+)", value).group(1))

	def server_config(self):
		return SERVER_CONFIG_PATTERN \
			.replace("<Name>", self.name) \
			.replace("<ClientPrivateKey>", self.client_private) \
			.replace("<ClientPublicKey>", self.client_public) \
			.replace("<ClientAddress>", self.client_address) \

	def client_config(self, interface_config: InterfaceConfig):
		return CLIENT_CONFIG_PATTERN \
			.replace("<ClientPrivateKey>", self.client_private) \
			.replace("<ClientPublicKey>", self.client_public) \
			.replace("<ClientAddress>", self.client_address) \
			.replace("<ServerPublicKey>", interface_config.public_key if interface_config.public_key is not None else "") \
			.replace("<ServerHost>", interface_config.hostname) \
			.replace("<ServerPort>", interface_config.listen_port) \
			.replace("<Jc>", interface_config.Jc) \
			.replace("<Jmin>", interface_config.Jmin) \
			.replace("<Jmax>", interface_config.Jmax) \
			.replace("<S1>", interface_config.S1) \
			.replace("<S2>", interface_config.S2) \
			.replace("<H1>", interface_config.H1) \
			.replace("<H2>", interface_config.H2) \
			.replace("<H3>", interface_config.H3) \
			.replace("<H4>", interface_config.H4)


class AmneziaWGConfig:
	def __init__(self, interface: InterfaceConfig, peers: List[PeerConfig]):
		self.interface = interface
		self.peers = peers

	@staticmethod
	def from_file(input_file: str):
		interface_read = False
		peer_read = False
		current_value = ""
		interface_config = None
		peers = []

		with open(input_file, 'r') as input:
			for line in input:
				stripped = line.rstrip()

				if stripped == "[Interface]":
					interface_read = True
					peer_read = False
					current_value = ""
				elif stripped == "[Peer]":
					if interface_read:
						interface_config = InterfaceConfig.from_string(current_value)
					elif peer_read:
						peers.append(PeerConfig.from_string(current_value))

					interface_read = False
					peer_read = True
					current_value = ""
				
				current_value += stripped
				current_value += "\n"

		if interface_read and current_value != "":
			interface_config = InterfaceConfig.from_string(current_value)
		elif peer_read and current_value != "":
			peers.append(PeerConfig.from_string(current_value))

		return AmneziaWGConfig(interface_config, peers)

	def free_address(self) -> str:
		x = 1

		while True:
			address = f"10.9.9.{x}/32"

			if address not in map(lambda p: p.client_address, self.peers) and address != self.interface.address:
				return address
			else:
				x += 1

	def add_key(self, user_name: str) -> PeerConfig:
		private_key_x25519, public_key_x25519 = generate_keypair()
		private_key_string = private_key_to_string(private_key_x25519)
		public_key_string = public_key_to_string(public_key_x25519)

		address = self.free_address()
		new_peer_config = PeerConfig(user_name, private_key_string, public_key_string, address)
		self.peers.append(new_peer_config)

		return new_peer_config

	def del_key(self, user_name: str) -> List[PeerConfig]:
		i = 0
		result = []

		while i < len(self.peers):
			if self.peers[i].name == user_name:
				peer_config = self.peers.pop(i)
				result.append(peer_config)
			else:
				i += 1

		return result


	def dump_to(self, output_file: str) -> str:
		with open(output_file, 'w') as output_file:
			output_file.write(self.interface.interface_string)
			output_file.write("\n")

			for peer_config in self.peers:
				output_file.write(peer_config.server_config())
				output_file.write("\n")
