import zmq
import node.net.proto.report_pb2 as proto_report
from google.protobuf.json_format import MessageToDict

port = "3030"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:%s" % port)
socket.setsockopt(zmq.SUBSCRIBE, b'0000')


while True:
    msg = socket.recv()
    msg = msg[4:]
    print(msg)
    report = proto_report.Report()
    report.ParseFromString(msg)
    print(MessageToDict(report))
