"""
Manages the post-negotiation portion of node communications.
After assignment of a Node and Pool ID, ALL nodes report to this class, publishing updates.
ZMQ handles the connects/disconnects/fair queueing.
"""
import timeit

import zmq
import threading
import proto.report_pb2 as proto_report
import server.constants as const
from server.util import MessageToDict

from server.processor import Processor


class Collector:
    """

    """

    def __init__(self):
        self.run = True
        self.port = const.COLLECTOR_PORT
        self._processors = []
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.bind(f"tcp://*:{self.port}")
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.work_thread = threading.Thread(target=self._work)
        self.work_thread.start()

    def _work(self):
        while self.run:
            message = self.socket.recv()
            report = proto_report.Report()
            report.ParseFromString(message)

            for p in self._processors:
                p: Processor
                a = timeit.default_timer()
                p.update(report.pool_id, report.node_id, MessageToDict(report))
                b = timeit.default_timer()
                print(f"{p.processor_name()}: {b - a}s")

    def add_processor(self, processor: Processor):
        """
        Adds an implementation of the Processor interface to the list of Processors.
        :param processor: Processor implementation
        :return: None
        """
        self._processors.append(processor)

