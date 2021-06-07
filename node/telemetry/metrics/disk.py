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
            pts = psutil.disk_partitions(all=False)  # Exclude virtual appliances and duplicates
            io = psutil.disk_io_counters(perdisk=False)
            partitions = {}
            for part in pts:
                usage = psutil.disk_usage(part.mountpoint)
                partitions[part] = {
                        'device': part.device,
                        'mount_point': part.mountpoint,
                        'fstype': part.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent,
                }
            data = {
                    'partitions': partitions,
                    'io': {
                            'read_count': io.read_count,
                            'write_count': io.write_count,
                            'read_bytes': io.read_bytes,
                            'write_bytes': io.write_bytes,
                            'read_time': io.read_time,
                            'write_time': io.write_time,
                    }
            }
            return data
        except Exception as e:
            raise ValueError(f'Unable to collect Disk metrics: {e}')
