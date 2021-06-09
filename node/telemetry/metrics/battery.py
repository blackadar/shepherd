"""
Battery Metrics from psutil.
"""
from node.telemetry.metric import Metric
import psutil
import time


class Battery(Metric):
    """
    Wrapper for psutil Battery information.
    """

    def metric_name(self) -> str:
        return "battery"

    def measure(self) -> dict:
        try:
            psubattery = psutil.sensors_battery()
            if psubattery is None:
                return {
                        'percent': None,
                        'secs_left': None,
                        'power_plugged': None,
                }
            data = {
                    'percent': psubattery.percent,
                    'secs_left': psubattery.secsleft,
                    'power_plugged': psubattery.power_plugged,
            }
            return data
        except Exception as e:
            raise ValueError(f'Unable to collect Battery metrics: {e}')
