"""
Session Metrics from psutil.
"""
from node.telemetry.metric import Metric
import psutil
import time


class Session(Metric):
    """
    Wrapper for psutil Session (Other) information.
    """

    def metric_name(self) -> str:
        return "session"

    def measure(self) -> dict:
        try:
            psusers = psutil.users()
            users = {}
            for user in psusers:
                users[user.name] = {
                        'terminal': user.terminal,
                        'host': user.host,
                        'started': int(user.started),
                        'pid': user.pid
                }
            data = {
                    'boot_time': int(psutil.boot_time()),
                    'uptime': int(time.time() - psutil.boot_time()),
                    'users': users,
            }
            return data
        except Exception as e:
            raise ValueError(f'Unable to collect Session metrics: {e}')
