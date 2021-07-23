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


"""
Database Connection
"""
DB_URL = check_config("DATABASE", "URL", "localhost", str)
DB_PORT = check_config("DATABASE", "PORT", 3306, int)
DB_USER = check_config("DATABASE", "USER", "shepherd", str)
DB_PASSWORD = check_config("DATABASE", "PASSWORD", "shepherd", str)
DB_SCHEMA = check_config("DATABASE", "SCEMA", "shepherd", str)

"""
Instantaneous Anomaly Limits
"""
A_CPU_LOAD_5 = check_config("ANOMALY", "CPU_LOAD_5", 95, int)  # >= 95% 5m CPU load
A_CPU_LOAD_15 = check_config("ANOMALY", "CPU_LOAD_15", 90, int)  # >= 90% 15m CPU load
A_RAM_VIRT_PERCENT = check_config("ANOMALY", "RAM_VIRT_PERCENT", 90, int)  # >= 90% virtual ram used
A_RAM_SWAP_PERCENT = check_config("ANOMALY", "RAM_SWAP_PERCENT", 90, int)  # >= 90% swap used
A_BATTERY_AVAIL = check_config("ANOMALY", "BATTERY_AVAIL", 10, int)  # <= 10% battery available
A_SESSION_UPTIME_INTERVAL = check_config("ANOMALY", "SESSION_UPTIME_INTERVAL", 60 * 60 * 24 * 7, int)  # > 7 days uptime
A_GPU_MEMORY_PERCENT = check_config("ANOMALY", "GPU_MEMORY_PERCENT", 90, int)  # >= 90% GPU memory utilization
A_GPU_LOAD = check_config("ANOMALY", "GPU_LOAD", 100, int)  # GPU load 100% saturated
A_DISK_PERCENT_USED = check_config("ANOMALY", "DISK_PERCENT_USED", 90, int)  # >= 90% disk utilization

"""
E-Mail Alerts
"""
EMAIL_NEW = check_config("EMAIL", "SEND_NEW", True, bool)
EMAIL_RESOLVED = check_config("EMAIL", "SEND_RESOLVED", True, bool)
EMAIL_API_KEY = check_config("EMAIL", "API_KEY", "none", str)
EMAIL_DOMAIN = check_config("EMAIL", "DOMAIN", "none", str)
EMAIL_RECIPIENT = check_config("EMAIL", "RECIPIENT", "none", str)
