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

    def __init__(self):
        super().__init__()
        self.users = psutil.users()
        self.last_called = time.time()
        self.frequency = 60 * 15  # 15 minutes
        self.num_calls = 0

    def metric_name(self) -> str:
        return "session"

    def measure(self) -> dict:
        try:
            self.safe_users()
            psusers = self.users
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

    def safe_users(self):
        now = time.time()
        if now >= self.last_called + self.frequency:
            if self.num_calls < 4800:  # https://github.com/giampaolo/psutil/issues/1965
                print(f"Measuring psutil.users() (Call {self.num_calls})")
                self.users = psutil.users()
                self.last_called = now
                self.num_calls += 1
            else:
                print("Unable to update psutil.users()! Avoiding Fatal Python error. Restart the service.")
