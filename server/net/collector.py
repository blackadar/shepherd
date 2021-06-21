"""
Manages the post-negotiation portion of node communications.
After assignment of a Node and Pool ID, ALL nodes report to this class, publishing updates.
ZMQ handles the connects/disconnects/fair queueing.
"""
import zmq
import threading
import proto.report_pb2 as proto_report
import server.constants as const
from google.protobuf.json_format import MessageToDict


class Collector:
    """

    """

    def __init__(self):
        self.run = True
        self.port = const.COLLECTOR_PORT
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
            print(f"{report.pool_id}:{report.node_id}  {MessageToDict(report)}")

            # TODO: Add data to Database

