"""
RAM Metrics from psutil.
"""
from node.telemetry.metric import Metric
import psutil


class RAM(Metric):
    """
    Wrapper for psutil RAM information.
    """

    def metric_name(self) -> str:
        return "ram"

    def measure(self) -> dict:
        try:
            vmem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            data = {
                    'virt_total': vmem.total,
                    'virt_available': vmem.available,
                    'virt_used': vmem.used,
                    'virt_free': vmem.free,
                    # 'virt_cached': vmem.cached,  # Linux/BSD Only
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_free': swap.free,
                    'swap_percent': swap.percent,
            }
            return data
        except Exception as e:
            raise ValueError(f'Unable to collect RAM metrics: {e}')
