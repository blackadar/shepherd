"""
Facilitates packing the Metric data into Protobuf messages.
"""
from node.telemetry.subscriber import Subscriber
import node.net.proto.report_pb2 as proto_report


class NetworkSubscriber(Subscriber):
    """
    Accepts subscriber updates and packages into Protobuf messages.
    The message is then sent to a target via 0MQ.
    """

    def subscriber_name(self) -> str:
        """
        Provides the subscriber name.
        :return: str name
        """
        return "protobuf"

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
        report.disk.read_cnt = update['disk']['io']['write_count']
        report.disk.read_cnt = update['disk']['io']['read_bytes']
        report.disk.read_cnt = update['disk']['io']['write_bytes']
        report.disk.read_cnt = update['disk']['io']['read_time']
        report.disk.read_cnt = update['disk']['io']['write_time']

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

        # TODO: Replace this Debug Print statement with ZeroMQ Network call.
        print(report.SerializeToString())
