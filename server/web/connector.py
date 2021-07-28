import datetime
from threading import Lock

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from server.db.mappings import Update, AnomalyRecord, GPUUpdate, DiskUpdate, HistoricalData


class ShepherdConnection:
    """
    Establishes and maintains a connection to the Shepherd database.
    Facilitates gathering data based on a Node ID, live or historical.
    """

    def __init__(self, host: str, port: int, user: str, password: str, dbname: str):
        """
        Sets up the Shepherd connection.
        :param host:
        :param port:
        :param user:
        :param password:
        :param dbname:
        """
        # Create DB Session
        print("Connecting to Database...")
        engine = sa.create_engine(f"mysql://{user}:{password}@{host}:{port}/"
                                  f"{dbname}", echo=False)
        self.session = Session(engine)
        print("Database connected.")
        self.lock = Lock()

    def get_combined_updates(self, node_id: int, gpu_uuid: str, disk_id: str, num_updates: int, no_gpu=False,
                             no_disks=False):
        """
        Retrieves most num_updates recent Update objects for Node node_id, joining on Disk and GPU.
        :param no_disks: bool No Disks in Query
        :param no_gpu: bool No GPUs in Query
        :param node_id: int Node ID
        :param gpu_uuid: GPU UUID from an update. See get_gpus()
        :param disk_id: Disk ID from an update. See get_disks()
        :param num_updates: int # Updates to fetch, most n recent
        :return: pd.DataFrame
        """
        relevant_cutoff = datetime.datetime.now() - datetime.timedelta(hours=1)
        with self.lock:
            if not no_gpu and not no_disks:
                query = self.session.query(Update, GPUUpdate, DiskUpdate).filter(
                        Update.timestamp >= relevant_cutoff).filter(Update.node_id == node_id).join(
                        GPUUpdate).filter(GPUUpdate.uuid == gpu_uuid).join(DiskUpdate).filter(
                        DiskUpdate.partition_id == disk_id).order_by(desc(Update.timestamp)).limit(num_updates)
            elif no_gpu and not no_disks:
                query = self.session.query(Update, DiskUpdate).filter(
                        Update.timestamp >= relevant_cutoff).filter(Update.node_id == node_id).join(
                        DiskUpdate).filter(
                        DiskUpdate.partition_id == disk_id).order_by(desc(Update.timestamp)).limit(num_updates)
            elif no_disks and not no_gpu:
                query = self.session.query(Update, GPUUpdate).filter(
                        Update.timestamp >= relevant_cutoff).filter(Update.node_id == node_id).join(
                        GPUUpdate).filter(GPUUpdate.uuid == gpu_uuid).order_by(desc(Update.timestamp)).limit(
                        num_updates)
            else:
                query = self.session.query(Update).filter(
                        Update.timestamp >= relevant_cutoff).filter(Update.node_id == node_id).order_by(
                        desc(Update.timestamp)).limit(num_updates)
            return pd.read_sql(query.statement, query.session.bind)

    def get_updates(self, node_id: int, num_updates: int):
        """
        Retrieves most num_updates recent Update objects for Node node_id.
        :param node_id: int Node ID
        :param num_updates: int # Updates to fetch, most n recent
        :return: pd.DataFrame
        """
        relevant_cutoff = datetime.datetime.now() - datetime.timedelta(hours=1)
        with self.lock:
            query = self.session.query(Update).filter(
                    Update.timestamp >= relevant_cutoff).filter(Update.node_id == node_id).order_by(
                desc(Update.timestamp)).limit(
                    num_updates)
            return pd.read_sql(query.statement, query.session.bind)

    def get_gpu_updates(self, node_id: int, gpu_uuid: str, num_updates: int):
        """
        Retrieves most num_updates recent GPUUpdate objects for Node node_id's GPU uuid.
        :param num_updates: int # Updates to fetch, most n recent
        :param node_id: int Node ID
        :param gpu_uuid: GPU UUID from an update. See get_gpus()
        :return: pd.DataFrame
        """
        relevant_cutoff = datetime.datetime.now() - datetime.timedelta(hours=1)
        with self.lock:
            query = self.session.query(GPUUpdate, Update).join(Update).filter(
                    Update.timestamp >= relevant_cutoff). \
                filter(and_(GPUUpdate.update.has(node_id=node_id), GPUUpdate.uuid == gpu_uuid)) \
                .order_by(desc(Update.timestamp)).limit(num_updates)
            return pd.read_sql(query.statement, query.session.bind)

    def get_disk_updates(self, node_id: int, disk_id: str, num_updates: int):
        """
        Retrieves most num_updates recent DiskUpdate objects for Node node_id's Disk ID.
        :param num_updates: int # Updates to fetch, most n recent
        :param node_id: int Node ID
        :param disk_id: Disk ID from an update. See get_disks()
        :return: pd.DataFrame
        """
        relevant_cutoff = datetime.datetime.now() - datetime.timedelta(hours=1)
        with self.lock:
            query = self.session.query(DiskUpdate, Update).join(Update).filter(
                    Update.timestamp >= relevant_cutoff). \
                filter(and_(DiskUpdate.update.has(node_id=node_id), DiskUpdate.partition_id == disk_id)) \
                .order_by(desc(Update.timestamp)).limit(num_updates)
            return pd.read_sql(query.statement, query.session.bind)

    def get_unresolved_anomalies(self):
        """
        Retrieves all unresolved Anomalies
        :return: pd.DataFrame
        """
        with self.lock:
            query = self.session.query(AnomalyRecord).filter(AnomalyRecord.resolved == 0)
            return pd.read_sql(query.statement, query.session.bind)

    def get_num_unresolved_anomalies(self):
        """
        Counts unresolved Anomalies
        :return: int
        """
        with self.lock:
            unresolved = self.session.query(AnomalyRecord).filter(AnomalyRecord.resolved == 0).count()
            return unresolved

    def get_resolved_anomalies(self):
        """
        Retrieves all resolved Anomalies
        :return: pd.DataFrame
        """
        with self.lock:
            query = self.session.query(AnomalyRecord).filter(AnomalyRecord.resolved == 1)
            return pd.read_sql(query.statement, query.session.bind)

    def get_num_unresolved_anomalies_node(self, node_id: int):
        """
        Counts the number of unresolved node anomalies
        :param node_id: int Node ID
        :return: int Number of unresolved anomalies
        """
        with self.lock:
            query = self.session.query(AnomalyRecord).filter(AnomalyRecord.node_id == node_id).filter(AnomalyRecord.resolved == 0).count()
            return query

    def get_historical(self, node_id: int):
        """
        Retrieves all historical data
        :return: pd.DataFrame
        """
        with self.lock:
            query = self.session.query(HistoricalData).filter(HistoricalData.node_id == node_id).order_by(
                    desc(HistoricalData.time))
            return pd.read_sql(query.statement, query.session.bind)

    def get_nodes(self):
        """
        Gets all Node IDs with Update records.
        :return: list of ints
        """
        with self.lock:
            self.session.commit()
            nodes = self.session.query(Update.node_id).distinct()
            return [node[0] for node in nodes]

    def get_num_nodes(self):
        """
        Gets the number of Nodes in the table.
        :return: int
        """
        with self.lock:
            self.session.commit()
            nodes = self.session.query(Update.node_id).distinct().count()
            return nodes

    def get_gpus(self, node_id: int):
        """
        Gets all GPU IDs relevant to a Node
        :param node_id: int Node ID
        :return: list of str
        """
        with self.lock:
            self.session.commit()
            gpus = self.session.query(GPUUpdate.uuid).filter(
                    GPUUpdate.update.has(node_id=node_id)).distinct().join(Update)
            return [gpu[0] for gpu in gpus]

    def get_disks(self, node_id: int):
        """
        Gets all Disk IDs relevant to a Node
        :param node_id: int Node ID
        :return: list of str
        """
        with self.lock:
            self.session.commit()
            disks = self.session.query(DiskUpdate.partition_id).filter(
                    DiskUpdate.update.has(node_id=node_id)).distinct().join(Update)
            return [disk[0] for disk in disks]


def format_nodes(connection):
    """
    Returns Nodes formatted in Dash friendly manner.
    :return: list of Dicts
    """
    nodes = connection.get_nodes()
    res = []
    for node in nodes:
        res.append({'label': f'Node {node}', 'value': node})
    return res


def format_gpus(connection, node_id: int):
    """
    Returns GPUs formatted in Dash friendly manner.
    :return: list of Dicts
    """
    gpus = connection.get_gpus(node_id)
    res = []
    for gpu in gpus:
        res.append({'label': f'{gpu}', 'value': gpu})
    return res


def format_disks(connection, node_id: int):
    """
    Returns Nodes formatted in Dash friendly manner.
    :return: list of Dicts
    """
    disks = connection.get_disks(node_id)
    res = []
    for disk in disks:
        res.append({'label': f'{disk}', 'value': disk})
    return res
