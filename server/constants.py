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
Instantaneous Anomaly Limits
"""
A_CPU_LOAD_5 = 95  # >= 95% 5m CPU load
A_CPU_LOAD_15 = 90  # >= 90% 15m CPU load
A_RAM_VIRT_PERCENT = 90  # >= 90% virtual ram used
A_RAM_SWAP_PERCENT = 90  # >= 90% swap used
A_BATTERY_AVAIL = 10  # <= 10% battery available
A_SESSION_UPTIME_INTERVAL = 60 * 60 * 24 * 7  # > 7 days uptime
A_GPU_MEMORY_PERCENT = 90  # >= 90% GPU memory utilization
A_GPU_LOAD = 100  # GPU load 100% saturated
A_DISK_PERCENT_USED = 90  # >= 90% disk utilization
