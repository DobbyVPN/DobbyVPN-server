import base64
import codecs
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives import serialization

def string_to_private_key(value: str) -> X25519PrivateKey:
	data = base64.b64decode(value)
	
	return X25519PrivateKey.from_private_bytes(data)

def private_key_to_string(value: X25519PrivateKey) -> str:
	data = value.private_bytes(
	    encoding=serialization.Encoding.Raw,
	    format=serialization.PrivateFormat.Raw,
	    encryption_algorithm=serialization.NoEncryption())
	
	return codecs.encode(data, 'base64').decode('utf8').strip()

def string_to_public_key(value: str) -> X25519PublicKey:
	data = base64.b64decode(value)
	
	return X25519PublicKey.from_public_bytes(data)

def public_key_to_string(value: X25519PublicKey) -> str:
	data = value.public_bytes(
		encoding=serialization.Encoding.Raw,
		format=serialization.PublicFormat.Raw)

	return codecs.encode(data, 'base64').decode('utf8').strip()

def generate_keypair() -> tuple[X25519PrivateKey, X25519PublicKey]:
	private_key = X25519PrivateKey.generate()
	public_key  = private_key.public_key()

	return (private_key, public_key)
