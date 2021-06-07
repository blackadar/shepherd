"""
Disk Metrics from psutil.
"""
from node.telemetry.metric import Metric
import psutil


class Disk(Metric):
    """
    Wrapper for psutil Disk information.
    """

    def metric_name(self) -> str:
        return "disk"

    def measure(self) -> dict:
        try:
            partitions = psutil.disk_partitions(all=False)  # Exclude virtual appliances and duplicates
            data = {}
            for part in partitions:
                usage = psutil.disk_usage(part.mountpoint)
                data[part] = {
                        'device': part.device,
                        'mount_point': part.mountpoint,
                        'fstype': part.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent,
                }
            return data
        except Exception as e:
            raise ValueError(f'Unable to collect Disk metrics: {e}')
