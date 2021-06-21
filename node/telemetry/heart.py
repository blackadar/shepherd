"""
The "heart" of the Node module.
Each "beat" will update selected metrics.
Subscribers can be notified (on "Pulse") when the data has been updated.
"""
import threading
import time
from node.telemetry.metric import Metric
from node.telemetry.subscriber import Subscriber


class Heart:
    """
    Made with <3 at WIT
    """

    def __init__(self, pool_id: int, node_id: int, rate: float = 1):
        self.pool_id = pool_id
        self.node_id = node_id
        self.rate = rate  # Hz  (Cycles per Second)
        assert 0.1 <= self.rate <= 2  # SW Req. 2.1

        self._metrics = []  # List of Metrics (Interface)
        self._subscribers = []  # List of Subscribers (Interface)
        self._alive = True
        self._data = {
                'node_id': self.node_id,
                'pool_id': self.pool_id,
                'time': 0
        }
        self._impulse = threading.Thread(target=self._beat)
        self._impulse_lock = threading.Lock()
        self._impulse_death_ack = False
        self._impulse_irregular = False

        # It's alive!
        self._impulse.start()

    def _beat(self):
        """
        Heartbeat! Update all metrics.
        :return:
        """
        while self._alive:
            # Start timing the beat
            beat_start = time.perf_counter()

            # Get all the updated info
            with self._impulse_lock:
                for metric in self._metrics:
                    self._data[metric.metric_name()] |= metric.measure()
                self._data['time'] = int(time.time())

                self._pulse()

            # Stop timing and calculate the remaining time until the next beat (if any)
            beat_end = time.perf_counter()
            elapsed = beat_end - beat_start
            # print(elapsed)
            if elapsed < (1/self.rate):
                self._impulse_irregular = False
                time.sleep((1/self.rate) - elapsed)
            else:
                print(f"Warning: Metric measurement ({elapsed: .4f}s) exceeds requested heart rate of {self.rate} Hz!")
                self._impulse_irregular = True

        self._impulse_death_ack = True
        print(f"{self} stopped.")

    def _pulse(self):
        """
        The data is ready to move to the subscribers.
        Send it away!
        :return:
        """
        for sub in self._subscribers:
            sub.update(self._data)

    def kill(self, block=True):
        """
        Stop the Heart.
        Optionally blocks until it's really stopped.
        :return:
        """
        self._alive = False
        if block:
            # Wait for a cycle to realize it's supposed to be over...
            while not self._impulse_death_ack:
                self._alive = False
                time.sleep(0.1)

    def register_metric(self, metric: Metric):
        """
        Register a metric to be measured by this Heart.
        :param metric: telemetry.Metric implementation
        :return:
        """
        assert isinstance(metric, Metric), f"{type(metric)} is not an implementation of telemetry.Metric."
        with self._impulse_lock:
            self._metrics.append(metric)
            self._data[metric.metric_name()] = {}

    def register_subscriber(self, subscriber: Subscriber):
        """
        Register a subscriber to be notified with metric updates.
        :param subscriber: telemetry.Subscriber implementation
        :return:
        """
        assert isinstance(subscriber, Subscriber), f"{type(subscriber)} is not an " \
                                                   f"implementation of telemetry.Subscriber."
        with self._impulse_lock:
            self._subscribers.append(subscriber)

    def update_assignment(self, node_id: int, pool_id: int):
        """

        :param node_id:
        :param pool_id:
        :return:
        """
        self.pool_id = pool_id
        self.node_id = node_id
        with self._impulse_lock:
            self._data['node_id'] = node_id
            self._data['pool_id'] = pool_id

