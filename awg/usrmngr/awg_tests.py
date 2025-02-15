import os
import unittest
import tempfile

from main import *

class TestStringMethods(unittest.TestCase):
    def test_list_logic(self):
        config_path = "test_awg.conf"
        config_value = """[Interface]
"""

        with open(config_path, 'w') as temp_config:
            temp_config.write(config_value)

        self.assertEqual(list_command_logic(config_path=config_path), { "keys": [] })
        self.assertEqual(list_command_logic("User", config_path=config_path), { "keys": [] })

        os.remove(config_path)

    def test_add_logic(self):
        config_path = "test_awg.conf"
        config_value = """[Interface]
"""

        with open(config_path, 'w') as temp_config:
            temp_config.write(config_value)

        self.assertEqual(list_command_logic("User", config_path=config_path), { "keys": [] })
        add_command_logic("User1", config_path=config_path)
        add_command_logic("User2", config_path=config_path)
        self.assertEqual(list_command_logic("User", config_path=config_path), { "keys": [] })
        self.assertEqual(len(list_command_logic("User1", config_path=config_path)["keys"]), 1)
        self.assertEqual(len(list_command_logic("User2", config_path=config_path)["keys"]), 1)
        self.assertEqual(len(list_command_logic(config_path=config_path)["keys"]), 2)

        os.remove(config_path)

    def test_del_logic(self):
        config_path = "test_awg.conf"
        config_value = """[Interface]
"""

        with open(config_path, 'w') as temp_config:
            temp_config.write(config_value)

        self.assertEqual(list_command_logic(config_path=config_path), { "keys": [] })
        self.assertEqual(list_command_logic("User", config_path=config_path), { "keys": [] })
        add_command_logic("User", config_path=config_path)
        add_command_logic("User", config_path=config_path)
        self.assertEqual(len(list_command_logic(config_path=config_path)["keys"]), 2)
        self.assertEqual(len(list_command_logic("User", config_path=config_path)["keys"]), 2)
        del_command_logic("User", config_path=config_path)
        self.assertEqual(len(list_command_logic(config_path=config_path)["keys"]), 0)
        self.assertEqual(len(list_command_logic("User", config_path=config_path)["keys"]), 0)

        os.remove(config_path)

    def test_add_config_empty_modification(self):
        config_path = "test_awg.conf"
        config_value = """[Interface]
"""

        with open(config_path, 'w') as temp_config:
            temp_config.write(config_value)

        add_command_logic("User", config_path=config_path)
        with open(config_path, 'r') as temp_config:
            new_config_lines = temp_config.read().splitlines()
            self.assertEqual(len(new_config_lines), 8)
            self.assertEqual(new_config_lines[0], "[Interface]")
            self.assertEqual(new_config_lines[1], "")
            self.assertEqual(new_config_lines[2], "[Peer]")
            self.assertEqual(new_config_lines[3], "# Name = User")
            self.assertTrue(new_config_lines[4].startswith("# PrivateKey = "))
            self.assertTrue(new_config_lines[5].startswith("PublicKey = "))
            self.assertEqual(new_config_lines[6], "AllowedIPs = 10.9.9.2/32")
            self.assertEqual(new_config_lines[7], "")

        os.remove(config_path)

    def test_add_config_complex_modification(self):
        config_path = "test_awg.conf"
        config_value = """[Interface]
Address = 10.9.9.1/32
ListenPort = 12645
PrivateKey = AFn7srlgz+gxv7OUOPIPAFR5zCSvlFGdAWQo5/KoPnE=

Jc = 49
Jmin = 50
Jmax = 65
S1 = 1268
S2 = 662
H1 = 4976
H2 = 20587
H3 = 32469
H4 = 12739

PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
"""

        with open(config_path, 'w') as temp_config:
            temp_config.write(config_value)

        add_command_logic("User", config_path=config_path)
        keys_result = list_command_logic("User", config_path=config_path)
        self.assertEqual(len(keys_result["keys"]), 1)
        key_result = keys_result["keys"][0]["key"].splitlines()
        self.assertEqual(len(key_result), 19)
        self.assertEqual(key_result[0], "[Interface]")
        self.assertRegex(key_result[1], r"PrivateKey = .+")
        self.assertRegex(key_result[2], r"# PublicKey = .+")
        self.assertEqual(key_result[3], "Address = 10.9.9.2/32")
        self.assertEqual(key_result[4], "Jc = 49")
        self.assertEqual(key_result[5], "Jmin = 50")
        self.assertEqual(key_result[6], "Jmax = 65")
        self.assertEqual(key_result[7], "S1 = 1268")
        self.assertEqual(key_result[8], "S2 = 662")
        self.assertEqual(key_result[9], "H1 = 4976")
        self.assertEqual(key_result[10], "H2 = 20587")
        self.assertEqual(key_result[11], "H3 = 32469")
        self.assertEqual(key_result[12], "H4 = 12739")
        self.assertEqual(key_result[13], "")
        self.assertEqual(key_result[14], "[Peer]")
        self.assertEqual(key_result[15], "AllowedIPs = 0.0.0.0/0")
        self.assertRegex(key_result[16], r"Endpoint = \d+.\d+.\d+.\d+:12645")
        self.assertEqual(key_result[17], "PersistentKeepalive = 60")
        self.assertEqual(key_result[18], "PublicKey = pFCNs4B01zG3ATCseJs3bPZ6m+CPq2GtfEiPVGVHFRc=")

        os.remove(config_path)

if __name__ == '__main__':
    unittest.main()
