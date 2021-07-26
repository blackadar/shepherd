"""
Defines a MySQL Database Processor to publish updates to a connected DB.
Leverages SQLAlchemy to abstract into ORM.
"""

from server.processor import Processor
import sqlalchemy as sa
from sqlalchemy.orm import Session
import datetime

from server.db.mappings import Node, Update, SessionUpdate, DiskUpdate, GPUUpdate


class MySQLProcessor(Processor):
    """
    Push Updates to a DB through SQLAlchemy Engine
    """

    def __init__(self, host, port, user, password, dbname, verbose=False):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.engine = sa.create_engine(f"mysql://{self.user}:{self.password}@{self.host}:{self.port}/"
                                       f"{self.dbname}", echo=verbose)
        self.session = Session(self.engine)

    def processor_name(self) -> str:
        return f"mysql://{self.user}@{self.host}:{self.port}/{self.dbname}"

    def update(self, pool_id: int, node_id: int, update: dict) -> None:
        node = self.session.get(Node, {'pool_id': pool_id, 'id': node_id})
        pool = node.pool

        db_update = Update(pool_id=pool.id, node_id=node.id,
                           timestamp=datetime.datetime.fromtimestamp(update['time_stamp']))

        db_update.cpu_logical_cores = update['cpu']['logical_cores']
        db_update.cpu_current_frequency = update['cpu']['current_freq']
        db_update.cpu_max_frequency = update['cpu']['max_freq']
        db_update.cpu_percent_usage = update['cpu']['percent']
        db_update.cpu_load_1 = update['cpu']['load_1']
        db_update.cpu_load_5 = update['cpu']['load_5']
        db_update.cpu_load_15 = update['cpu']['load_15']

        db_update.ram_total_virtual = update['ram']['virt_total']
        db_update.ram_used_virtual = update['ram']['virt_available']
        db_update.ram_available_virtual = update['ram']['virt_used']
        db_update.ram_free_virtual = update['ram']['virt_free']
        db_update.ram_total_swap = update['ram']['swap_total']
        db_update.ram_used_swap = update['ram']['swap_used']
        db_update.ram_free_swap = update['ram']['swap_free']
        db_update.ram_percent_swap = update['ram']['swap_percent']

        db_update.disk_read_count = update['disk']['read_cnt']
        db_update.disk_write_count = update['disk']['write_cnt']
        db_update.disk_read_bytes = update['disk']['read_bytes']
        db_update.disk_write_bytes = update['disk']['write_bytes']
        db_update.disk_read_time = update['disk']['read_time']
        db_update.disk_write_time = update['disk']['write_time']

        db_update.battery_available_percent = update['battery']['percent']
        db_update.battery_est_remain = update['battery']['secs_left']
        db_update.battery_plugged_in = update['battery']['power_plugged']

        db_update.session_uptime = update['session']['uptime']
        db_update.session_boot_time = datetime.datetime.fromtimestamp(update['session']['boot_time'])

        self.session.add(db_update)
        self.session.commit()

        n_gpus = len(update['gpu']['uuids'])
        for i in range(n_gpus):
            gpu_update = GPUUpdate(update_id=db_update.id)
            gpu_update.uuid = update['gpu']['uuids'][i]
            gpu_update.load = update['gpu']['loads'][i]
            gpu_update.memory_percentage = update['gpu']['mem_percents'][i]
            gpu_update.memory_total = update['gpu']['mem_totals'][i]
            gpu_update.memory_used = update['gpu']['mem_useds'][i]
            gpu_update.driver_version = update['gpu']['drivers'][i]
            gpu_update.product_identifier = update['gpu']['products'][i]
            gpu_update.serial = update['gpu']['serials'][i]
            gpu_update.display_mode = update['gpu']['display_modes'][i]
            self.session.add(gpu_update)

        n_disks = len(update['disk']['partition_ids'])
        for i in range(n_disks):
            disk_update = DiskUpdate(update_id=db_update.id)
            disk_update.partition_id = update['disk']['partition_ids'][i]
            disk_update.mount_point = update['disk']['mount_points'][i]
            disk_update.fstype = update['disk']['fstypes'][i]
            disk_update.total_storage = update['disk']['totals'][i]
            disk_update.used_storage = update['disk']['useds'][i]
            disk_update.free_storage = update['disk']['frees'][i]
            disk_update.percentage_used = update['disk']['percents'][i]
            self.session.add(disk_update)

        n_sessions = len(update['session']['users'])
        for i in range(n_sessions):
            session_update = SessionUpdate(update_id=db_update.id)
            session_update.user = update['session']['users'][i]
            session_update.terminal = update['session']['terminals'][i]
            session_update.host = update['session']['hosts'][i]
            session_update.started_time = datetime.datetime.fromtimestamp(update['session']['started_times'][i])
            session_update.process_id = update['session']['pids'][i]
            self.session.add(session_update)

        self.session.commit()
