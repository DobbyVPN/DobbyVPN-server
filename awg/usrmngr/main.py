import re
import sys
import json
import decouple

from typing import List, Optional
from awg import InterfaceConfig, PeerConfig, AmneziaWGConfig


DEFAULT_AWG_CONFIG_PATH = "wg0.conf"


def print_help():
	program_name = sys.argv[0]
	help_message = f"""python3 {program_name} help
	prints script informations
python3 {program_name} add <user_name>
	add new user key
python3 {program_name} list [user_name]
	print list of all user keys or list of all possible keys if no user name provided
python3 {program_name} del <user_name>
	remove user keys"""

	print(help_message)

def help_command(arguments):
	print_help()

	if len(arguments) > 0:
		exit(1)
	else:
		exit(0)

def add_command(arguments):
	if len(arguments) > 1 or len(arguments) == 0:
		print_help()
		exit(1)
	else:
		user_name = arguments[0]
		add_command_logic(user_name)
		exit(0)

def add_command_logic(user_name: str, config_path: str = DEFAULT_AWG_CONFIG_PATH):
	config = AmneziaWGConfig.from_file(config_path)
	config.add_key(user_name)
	config.dump_to(config_path)

def del_command(arguments):
	if len(arguments) > 1 or len(arguments) == 0:
		print_help()
		exit(1)
	else:
		user_name = arguments[0]
		del_command_logic(user_name)
		exit(0)

def del_command_logic(user_name: str, config_path: str = DEFAULT_AWG_CONFIG_PATH):
	config = AmneziaWGConfig.from_file(config_path)
	config.del_key(user_name)
	config.dump_to(config_path)

def list_command(arguments):
	if len(arguments) == 1:
		user_name = arguments[0]
		result = list_command_logic(user_name)
		print(json.dumps(result, indent=4))
		exit(0)
	elif len(arguments) == 0:
		result = list_command_logic()
		print(json.dumps(result, indent=4))
		exit(0)
	else:
		print_help()
		exit(1)

def list_command_logic(user_name: Optional[str] = None, config_path: str = DEFAULT_AWG_CONFIG_PATH):
	config = AmneziaWGConfig.from_file(config_path)
	result = []

	for peer in config.peers:
		if user_name is None or peer.name == user_name:
			key_dict = {
				"key": peer.client_config(config.interface)
			}

			result.append(key_dict)

	result_dics = {
		"keys": result
	}

	return result_dics

SUPPORTED_COMMANDS = {
	"help": help_command,
	"add": add_command,
	"del": del_command,
	"list": list_command,
}

if __name__ == "__main__":
	if len(sys.argv) <= 1:
		print_help()
		exit(1)

	command_name = sys.argv[1]

	if command_name not in SUPPORTED_COMMANDS.keys():
		print_help()
		exit(1)

	SUPPORTED_COMMANDS[command_name](sys.argv[2:])
