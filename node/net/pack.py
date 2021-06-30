"""
Facilitates packing the Metric data into Protobuf messages, sent via 0MQ
"""
from node.telemetry.subscriber import Subscriber
import proto.report_pb2 as proto_report
from proto.negotiation_pb2 import Negotiation
import node.constants as const
import zmq
import node.memory


class NetworkSubscriber(Subscriber):
    """
    Accepts subscriber updates and packages into Protobuf messages.
    The message is then sent to a target via 0MQ Pub-Sub Pairs.
    """

    def __init__(self, heart):
        super().__init__()
        self.context = zmq.Context()

        print(f"Broker Handshake -> {const.SERVER_IP}:{const.BROKER_PORT}")
        # Handle Broker Handshake
        negotiation = Negotiation()
        mem = node.memory.read_ids()
        if mem is False:
            print("No memory found, requesting new ID.")
            negotiation.node_proposes_id = False
        else:
            node_id, pool_id = mem
            print(f"Requesting reposession of {pool_id}:{node_id}.")
            negotiation.node_proposes_id = True
            negotiation.node_id = node_id
            negotiation.pool_id = pool_id

        broker = self.context.socket(zmq.REQ)
        broker.connect(f"tcp://{const.SERVER_IP}:{const.BROKER_PORT}")
        broker.send(negotiation.SerializeToString())
        broker_response = broker.recv()
        broker_negotiation = Negotiation()
        broker_negotiation.ParseFromString(broker_response)

        if broker_negotiation.server_approve:
            self.node_id = broker_negotiation.node_id
            self.pool_id = broker_negotiation.pool_id
            self.port = broker_negotiation.collector_port
            print(f"Broker Handshake complete. {self.pool_id}:{self.node_id}")
            node.memory.write_ids(self.node_id, self.pool_id)
            heart.update_assignment(self.node_id, self.pool_id)
        else:
            raise IOError("Broker handshake unsuccessful. This node may need to be reconfigured.")
            # TODO: Handle file clear or prompt user to do so.

        broker.close()

        print(f"Collector Publishing -> {const.SERVER_IP}:{self.port}")
        self.socket = self.context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.SNDHWM, 2)
        self.socket.connect(f"tcp://{const.SERVER_IP}:{self.port}")

    def subscriber_name(self) -> str:
        """
        Provides the subscriber name.
        :return: str name
        """
        return f"zmq:{str(self.socket)}"

    def update(self, update: dict) -> None:
        """
        Updates the network client with a Heart pulse.
        Packages to Protobuf, serializes, and sends via ZeroMQ Socket.
        :param update: dict Update from Heart
        :return: None
        """
        report = proto_report.Report()
        report.pool_id = update['pool_id']
        report.node_id = update['node_id']
        report.time_stamp = update['time']

        report.cpu.logical_cores = update['cpu']['logical_cores']
        report.cpu.current_freq = update['cpu']['current_frequency']
        report.cpu.max_freq = update['cpu']['max_frequency']
        report.cpu.percent = update['cpu']['percent']
        report.cpu.load_1 = update['cpu']['load_1']
        report.cpu.load_5 = update['cpu']['load_5']
        report.cpu.load_15 = update['cpu']['load_15']

        report.ram.virt_total = update['ram']['virt_total']
        report.ram.virt_available = update['ram']['virt_available']
        report.ram.virt_used = update['ram']['virt_used']
        report.ram.virt_free = update['ram']['virt_free']
        report.ram.swap_total = update['ram']['swap_total']
        report.ram.swap_percent = update['ram']['swap_percent']
        report.ram.swap_used = update['ram']['swap_used']
        report.ram.swap_free = update['ram']['swap_free']

        devices = []
        mount_points = []
        fstypes = []
        totals = []
        useds = []
        frees = []
        percents = []

        for part in update['disk']['partitions'].values():
            devices.append(part['device'])
            mount_points.append(part['mount_point'])
            fstypes.append(part['fstype'])
            totals.append(part['total'])
            useds.append(part['used'])
            frees.append(part['free'])
            percents.append(part['percent'])

        report.disk.partition_ids.extend(devices)
        report.disk.mount_points.extend(mount_points)
        report.disk.fstypes.extend(fstypes)
        report.disk.totals.extend(totals)
        report.disk.useds.extend(useds)
        report.disk.frees.extend(frees)
        report.disk.percents.extend(percents)

        report.disk.read_cnt = update['disk']['io']['read_count']
        report.disk.write_cnt = update['disk']['io']['write_count']
        report.disk.read_bytes = update['disk']['io']['read_bytes']
        report.disk.write_bytes = update['disk']['io']['write_bytes']
        report.disk.read_time = update['disk']['io']['read_time']
        report.disk.write_time = update['disk']['io']['write_time']

        if update['battery']['power_plugged'] is not None:
            report.battery.percent = update['battery']['percent']
            report.battery.secs_left = update['battery']['secs_left']
            report.battery.power_plugged = update['battery']['power_plugged']

        report.session.boot_time = update['session']['boot_time']
        report.session.uptime = update['session']['uptime']

        users = []
        terminals = []
        hosts = []
        started_times = []
        pids = []
        for user, attribs in update['session']['users'].items():
            users.append(user)
            terminals.append(attribs['terminal'] if attribs['terminal'] is not None else '')
            hosts.append(attribs['host'] if attribs['host'] is not None else '')
            started_times.append(attribs['started'])
            pids.append(attribs['pid'] if attribs['pid'] is not None else 0)

        report.session.users.extend(users)
        report.session.terminals.extend(terminals)
        report.session.hosts.extend(hosts)
        report.session.started_times.extend(started_times)
        report.session.pids.extend(pids)

        uuids = []
        loads = []
        mem_percents = []
        mem_totals = []
        mem_useds = []
        drivers = []
        products = []
        serials = []
        display_modes = []
        for gpu in update['gpu'].values():
            uuids.append(gpu['uuid'])
            loads.append(gpu['load'])
            mem_percents.append(gpu['mem_percent'])
            mem_totals.append(gpu['mem_total'])
            mem_useds.append(gpu['mem_used'])
            drivers.append(gpu['driver'])
            products.append(gpu['product'])
            serials.append(gpu['serial'])
            display_modes.append(gpu['display_mode'])

        report.gpu.uuids.extend(uuids)
        report.gpu.loads.extend(loads)
        report.gpu.mem_percents.extend(mem_percents)
        report.gpu.mem_totals.extend(mem_totals)
        report.gpu.mem_useds.extend(mem_useds)
        report.gpu.drivers.extend(drivers)
        report.gpu.products.extend(products)
        report.gpu.serials.extend(serials)
        report.gpu.display_modes.extend(display_modes)

        self.socket.send(report.SerializeToString())
