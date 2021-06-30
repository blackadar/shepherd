"""
Manages the network negotiation portion of a client connection.
Node connects here first to get the node and Pool ID, then is redirected to the PUB/SUB ZMQ interface.
"""
import zmq
import sqlalchemy as sa
from sqlalchemy.orm import Session
import server.constants as const
import threading
import pickle
from proto.negotiation_pb2 import Negotiation
from server.db.mappings import Pool, Node


class Broker:
    """

    """

    def __init__(self, host, port, user, password, dbname, verbose=False):
        self.run = True
        self.pool_id = const.POOL_ID

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{const.BROKER_PORT}")

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.engine = sa.create_engine(f"mysql://{self.user}:{self.password}@{self.host}:{self.port}/"
                                       f"{self.dbname}", echo=verbose)
        self.session = Session(self.engine)

        self.pool = self.session.get(Pool, self.pool_id)
        if self.pool is None:
            self.pool = Pool(id=self.pool_id)
            self.session.add(self.pool)
            self.session.commit()

        self.work_thread = threading.Thread(target=self._work)
        self.work_thread.start()

    def _work(self):
        while self.run:
            message = self.socket.recv()
            negotiation = Negotiation()
            negotiation.ParseFromString(message)
            response = Negotiation()
            if negotiation.node_proposes_id:
                valid = Broker.check_id_exists(negotiation.node_id) and negotiation.pool_id == self.pool_id and\
                    self.session.get(Node, {'id': negotiation.node_id, 'pool_id': self.pool_id}) is not None
                print(f"Node connection proposes ID {negotiation.node_id}. Valid: {valid}.")
                if valid:
                    response.server_approve = True
                    response.node_id = negotiation.node_id
                    response.pool_id = negotiation.pool_id
                    response.collector_port = const.COLLECTOR_PORT
                else:
                    response.server_approve = False
            else:
                node_id = Broker.generate_new_id()
                self.session.add(Node(id=node_id, pool_id=self.pool_id))
                self.session.commit()
                response.server_approve = True
                response.pool_id = self.pool_id
                response.node_id = node_id
                response.collector_port = const.COLLECTOR_PORT
            self.socket.send(response.SerializeToString())

    @staticmethod
    def generate_new_id():
        """
        Checks the BROKER_FILE if the current node has an id, if not creates a new id at the end of the file.
        :return: ID generated for the node
        """
        if not const.BROKER_FILE.exists():
            data = [0, ]
            Broker.to_broker_file(data)
            return 0
        else:
            try:
                data = Broker.from_broker_file()
                assert type(data) is list
            except Exception as e:
                print(f"Broker unable to load existing Node ID file at {const.BROKER_FILE}")
                raise e
            last_id = max(data)
            allocated_id = last_id + 1
            data.append(allocated_id)
            Broker.to_broker_file(data)
            return allocated_id

    @staticmethod
    def check_id_exists(node_id: int):
        """
        Checks if node_id exists and is taken by another node in the pool.
        :param node_id: ID that will be checked
        :return: True if exists, false if not
        """
        if not const.BROKER_FILE.exists():
            return False
        data = Broker.from_broker_file()
        assert type(data) is list
        return node_id in data

    @staticmethod
    def release_id(node_id: int):
        """
        Releases node_id if the node is removed from the pool.
        :param node_id: ID to be removed
        """
        if not const.BROKER_FILE.exists():
            raise IOError("Broker File {const.BROKER_FILE} does not exist!")
        data = Broker.from_broker_file()
        assert type(data) is list
        data: list
        data.remove(node_id)
        Broker.to_broker_file(data)

    @staticmethod
    def from_broker_file():
        """
        :return:
        """
        with open(const.BROKER_FILE, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def to_broker_file(data):
        """
        :param data:
        """
        with open(const.BROKER_FILE, 'wb') as f:
            pickle.dump(data, f)


