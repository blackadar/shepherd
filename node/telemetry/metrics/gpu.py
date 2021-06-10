"""
GPU Metrics from GPUtil.
"""
from node.telemetry.metric import Metric
import GPUtil


class GPU(Metric):
    """
    Wrapper for GPUtil GPU information.
    """

    def metric_name(self) -> str:
        return "gpu"

    def measure(self) -> dict:
        try:
            data = {}
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                uuid = gpu.uuid
                data[uuid] = {}
                data[uuid]['uuid'] = gpu.uuid
                data[uuid]['load'] = gpu.load
                data[uuid]['mem_percent'] = gpu.memoryUtil
                data[uuid]['mem_total'] = int(gpu.memoryTotal)
                data[uuid]['mem_used'] = int(gpu.memoryUsed)
                data[uuid]['driver'] = gpu.driver
                data[uuid]['product'] = gpu.name
                data[uuid]['serial'] = gpu.serial
                data[uuid]['display_mode'] = gpu.display_mode
            return data
        except Exception as e:
            raise ValueError(f'Unable to collect GPU metrics: {e}')
