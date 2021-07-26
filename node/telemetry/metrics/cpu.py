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
            cpu_count = psutil.cpu_count(logical=True)
            data = {
                'logical_cores': cpu_count,
                'current_frequency': cpufreq.current,
                'max_frequency': cpufreq.max,
                'percent': psutil.cpu_percent(interval=0.1, percpu=False),
                'load_1': loadavg[0] / cpu_count,
                'load_5': loadavg[1] / cpu_count,
                'load_15': loadavg[2] / cpu_count,
            }
            return data
        except Exception as e:
            raise ValueError(f'Unable to collect CPU metrics: {e}')
