"""
Module level constants.
"""
import configparser
import pathlib

CONFIG_FILE = pathlib.Path('spd_node.ini')

config = None
try:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE.resolve())
except Exception as e:
    print(f"No config file found: {e}")


def check_config(cat: str, const: str, default, typ):
    if config.has_section(cat) and config.has_option(cat, const):
        return typ(config[cat][const])
    else:
        return typ(default)


"""
Constants Below Here
"""

SERVER_IP = check_config("NETWORK", "SERVER_IP", "localhost", str)
MEMORY_FILE = pathlib.Path('node_memory.pkl')
BROKER_PORT = 3030

