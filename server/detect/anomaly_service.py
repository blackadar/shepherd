"""
Detects anomalous Node updates.
Appends detected anomalous behaviour to the AnomalyRecord table.
Only performs detection relative to current run time.
That is, the current time and the window of inspection for the anomaly.

Intended to be run in a separate process to avoid taking up cycles in processing Node updates.

For Node in Updates since last evaluated timestamp (all new updates for each node):
    Check if values are anomalous
    Check if the anomaly was already detected and unresolved
        If an unresolved anomaly of the same type existed do nothing
        Else create a new unresolved anomaly
    Check if any unresolved anomalies exist which are now resolved
        Mark these as resolved
"""
import datetime
import time

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import and_
from server.db.mappings import Node, Pool, Update, DiskUpdate, GPUUpdate, AnomalyRecord
import server.constants as const


def setup(host: str, port: int, user: str, password: str, dbname: str, verbose=False):
    """
    Sets up connection to DB
    :param host:
    :param port:
    :param user:
    :param password:
    :param dbname:
    :param pool:
    :param verbose:
    :return:
    """
    # Create DB Session
    print("Connecting to Database...")
    engine = sa.create_engine(f"mysql://{user}:{password}@{host}:{port}/"
                              f"{dbname}", echo=verbose)
    session = Session(engine)
    return session


def detect(session: Session, last_run: datetime.datetime, pool: int):
    """
    Detects anomalies and resolutions in updates since last run time
    :param pool:
    :param last_run:
    :param session:
    :return:
    """

    pool = session.get(Pool, {'id': pool})
    new_anomalies = []
    resolved_anomalies = []
    for node in pool.nodes:
        node: Node

        """
        Checks for instantaneous anomalies since last detection cycle
        """

        # General Updates
        query = session.query(Update).filter(and_(Update.node_id == node.id, Update.timestamp >= last_run))
        updates = pd.read_sql(query.statement, query.session.bind)
        if len(updates) == 0:
            print(f"Detection for {node.pool_id}:{node.id} found no updates to consider this interval.")
            continue
        # Disk Updates
        disk_query = session.query(DiskUpdate, Update).join(Update).filter(
                and_(DiskUpdate.update.has(node_id=node.id), DiskUpdate.update.has(Update.timestamp >= last_run)))
        disk_updates = pd.read_sql(disk_query.statement, disk_query.session.bind)
        # GPU Updates
        gpu_query = session.query(GPUUpdate, Update).join(Update).filter(
                and_(GPUUpdate.update.has(node_id=node.id), GPUUpdate.update.has(Update.timestamp >= last_run)))
        gpu_updates = pd.read_sql(gpu_query.statement, gpu_query.session.bind)
        # Outstanding Anomalies
        anomaly_query = session.query(AnomalyRecord).filter(
                and_(AnomalyRecord.node_id == node.id, AnomalyRecord.resolved == False))
        node_outstanding_anomalies = pd.read_sql(anomaly_query.statement, anomaly_query.session.bind)
        node_outstanding_anomalies['found_ongoing'] = 0

        node_anomalies = []
        in_interval = []

        # Check for instantaneous general Update anomalies
        for index, row in updates.iterrows():
            if row['cpu_load_5'] >= const.A_CPU_LOAD_5 and 'cpu5' not in in_interval:
                node_anomalies.append(AnomalyRecord(node_id=node.id, pool_id=pool.id, type='cpu', time=row['timestamp'],
                                                    resolved=False, message=f'5 minute CPU load over threshold.',
                                                    severity='medium'))
                in_interval.append('cpu5')
            if row['cpu_load_15'] >= const.A_CPU_LOAD_15 and 'cpu15' not in in_interval:
                node_anomalies.append(AnomalyRecord(node_id=node.id, pool_id=pool.id, type='cpu', time=row['timestamp'],
                                                    resolved=False, message=f'15 minute CPU load over threshold.',
                                                    severity='medium'))
                in_interval.append('cpu15')
            if (row['ram_used_virtual'] / row['ram_total_virtual']) * 100 >= const.A_RAM_VIRT_PERCENT and 'ram_virt' not in in_interval:
                node_anomalies.append(AnomalyRecord(node_id=node.id, pool_id=pool.id, type='ram', time=row['timestamp'],
                                                    resolved=False, message=f'Virtual RAM usage over threshold.',
                                                    severity='medium'))
                in_interval.append('ram_virt')
            if row['ram_percent_swap'] >= const.A_RAM_SWAP_PERCENT and 'ram_swap' not in in_interval:
                node_anomalies.append(AnomalyRecord(node_id=node.id, pool_id=pool.id, type='ram', time=row['timestamp'],
                                                    resolved=False, message=f'Swap RAM usage over threshold.',
                                                    severity='medium'))
                in_interval.append('ram_swap')
            if 0 < row['battery_available_percent'] <= const.A_BATTERY_AVAIL and 'battery_avail' not in in_interval:
                node_anomalies.append(
                    AnomalyRecord(node_id=node.id, pool_id=pool.id, type='battery', time=row['timestamp'],
                                  resolved=False, message=f'Available Battery below threshold.',
                                  severity='high'))
                in_interval.append('battery_avail')
            if row['session_uptime'] >= const.A_SESSION_UPTIME_INTERVAL and 'uptime' not in in_interval:
                node_anomalies.append(
                    AnomalyRecord(node_id=node.id, pool_id=pool.id, type='session', time=row['timestamp'],
                                  resolved=False,
                                  message=f'Node uptime exceeds threshold. Consider reboot.',
                                  severity='low'))
                in_interval.append('uptime')

        for index, row in disk_updates.iterrows():
            if row['percentage_used'] >= const.A_DISK_PERCENT_USED and f'disk_percent_{row["partition_id"]}' not in in_interval:
                node_anomalies.append(
                    AnomalyRecord(node_id=node.id, pool_id=pool.id, type='disk', time=row['timestamp'],
                                  resolved=False,
                                  message=f'Disk {row["partition_id"]} usage exceeds threshold.',
                                  severity='high')
                )
                in_interval.append(f'disk_percent_{row["partition_id"]}')
        for index, row in gpu_updates.iterrows():
            if row['memory_percentage'] * 100 >= const.A_GPU_MEMORY_PERCENT and f'gpu_mem_{row["uuid"]}' not in in_interval:
                node_anomalies.append(
                        AnomalyRecord(node_id=node.id, pool_id=pool.id, type='gpu', time=row['timestamp'],
                                      resolved=False,
                                      message=f'GPU {row["uuid"]} memory usage exceeds threshold.',
                                      severity='medium')
                )
                in_interval.append(f'gpu_mem_{row["uuid"]}')
            if row['load'] * 100 >= const.A_GPU_LOAD and f'gpu_load_{row["uuid"]}' not in in_interval:
                node_anomalies.append(
                        AnomalyRecord(node_id=node.id, pool_id=pool.id, type='gpu', time=row['timestamp'],
                                      resolved=False,
                                      message=f'GPU {row["uuid"]} load exceeds threshold.',
                                      severity='medium')
                )
                in_interval.append(f'gpu_load_{row["uuid"]}')

            """
            Checks for contextual anomalies within a timed range
            """

            pass

            """
            Checks for contextual anomalies compared to historical entries
            """

            pass

        """
        Checks for anomalies which already exist and does not make new entries.
        Also checks for resolved anomalies.
        """
        new = 0
        resolved = 0
        for anomaly in node_anomalies:
            matching = node_outstanding_anomalies.loc[(node_outstanding_anomalies['message'] == anomaly.message) &
                                                      (node_outstanding_anomalies.type == anomaly.type)]
            node_outstanding_anomalies.loc[(node_outstanding_anomalies['message'] == anomaly.message) &
                                           (node_outstanding_anomalies.type == anomaly.type), 'found_ongoing'] = 1
            if len(matching) == 0:
                new_anomalies.append(anomaly)
                new += 1

        for index, row in node_outstanding_anomalies.loc[node_outstanding_anomalies['found_ongoing'] == 0].iterrows():
            resolved_anomalies.append(session.query(AnomalyRecord).get(row['id']))
            resolved += 1

        print(f"Detection for {node.pool_id}:{node.id} found {new} new and {resolved} resolved anomalies.")

    """
    Checks list of unresolved anomalies which are now considered resolved and marks them as such
    """

    for anomaly in new_anomalies:
        session.add(anomaly)

    for anomaly in resolved_anomalies:
        anomaly.resolved = True

    session.commit()


def main():
    session = setup('localhost', 3306, 'user', 'password', 'table')
    while True:
        last_run = datetime.datetime.now()
        detect(session, last_run, const.POOL_ID)
        time.sleep(10)


if __name__ == '__main__':
    main()
