import configparser
import pathlib

CONFIG_FILE = pathlib.Path('spd_server.ini')

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

BROKER_FILE = pathlib.Path('broker_memory.pkl')
POOL_ID = check_config("POOL", "POOL_ID", 0, int)
BROKER_PORT = 3030
COLLECTOR_PORT = 3031
