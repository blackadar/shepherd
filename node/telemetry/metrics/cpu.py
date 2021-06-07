"""
CPU Metrics from psutil.
"""
from node.telemetry.metric import Metric
import psutil


class CPU(Metric):
    """
    Wrapper for psutil CPU information.
    """

    def metric_name(self) -> str:
        return "cpu"

    def measure(self) -> dict:
        try:
            cpufreq = psutil.cpu_freq(percpu=False)
            loadavg = psutil.getloadavg()
            data = {
                'logical_cores': psutil.cpu_count(logical=True),
                'current_frequency': cpufreq.current,
                'max_frequency': cpufreq.max,
                'percent': psutil.cpu_percent(interval=0.1, percpu=False),
                'load_1': loadavg[0],
                'load_5': loadavg[1],
                'load_15': loadavg[2],
            }
            return data
        except Exception as e:
            raise ValueError(f'Unable to collect CPU metrics: {e}')
