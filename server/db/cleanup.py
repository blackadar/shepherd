"""
Database Cleanup to be run every day.
Condenses high resolution report data into averages and anomalies.
Stores the averages and anomalies in separate DB table.

Data to Clean
    | |
    v v
__________________________________________
Previous 48H | Previous 24H | Now        |
xxx          | xxx          |            |
xxx          | xxx          |            |
"""
import datetime

import sqlalchemy as sa
import pandas as pd
import numpy as np
from sqlalchemy import and_
from sqlalchemy.orm import Session
from server.db.mappings import HistoricalData, Node, Update, DiskUpdate, SessionUpdate, GPUUpdate, Pool


def clean(host: str, port: int, user: str, password: str, dbname: str, pool: int, verbose=False) -> bool:
    """
    Reads through all current database entries, and condenses all entries older than 48 hours old.
    Condensed data will be entered into the historical database.
    :return:
    """
    # Create DB Session
    print("Connecting to Database...")
    engine = sa.create_engine(f"mysql://{user}:{password}@{host}:{port}/"
                              f"{dbname}", echo=verbose)
    session = Session(engine)
    pool = session.get(Pool, {'id': pool})
    hr_cutoff = datetime.datetime.now() - datetime.timedelta(days=1)

    print(f"Condensing all data before {hr_cutoff}")

    def _clean(data):
        return None if np.isnan(data) else data

    for node in pool.nodes:
        node: Node
        print(f"Condensing {node.pool_id}:{node.id}")
        # General Updates
        query = session.query(Update).filter(and_(Update.node_id == node.id, Update.timestamp <= hr_cutoff))
        updates = pd.read_sql(query.statement, query.session.bind)
        # Disk Updates
        disk_query = session.query(DiskUpdate).filter(and_(DiskUpdate.update.has(node_id=node.id), DiskUpdate.update.has(Update.timestamp <= hr_cutoff)))
        disk_updates = pd.read_sql(disk_query.statement, disk_query.session.bind)
        # GPU Updates
        gpu_query = session.query(GPUUpdate).filter(and_(GPUUpdate.update.has(node_id=node.id), GPUUpdate.update.has(Update.timestamp <= hr_cutoff)))
        gpu_updates = pd.read_sql(gpu_query.statement, gpu_query.session.bind)
        historical = HistoricalData()
        historical.node_id = node.id
        historical.pool_id = node.pool_id
        historical.avg_cpu_curr_freq = _clean(updates['cpu_current_frequency'].mean())
        historical.avg_cpu_percent_usage = _clean(updates['cpu_percent_usage'].mean())
        historical.avg_cpu_load_1 = _clean(updates['cpu_load_1'].mean())
        historical.avg_cpu_load_5 = _clean(updates['cpu_load_5'].mean())
        historical.avg_cpu_load_15 = _clean(updates['cpu_load_15'].mean())
        historical.avg_ram_used_virt = _clean(updates['ram_used_virtual'].mean())
        historical.avg_ram_used_swap = _clean(updates['ram_used_swap'].mean())
        historical.avg_battery_avail = _clean(updates['battery_available_percent'].mean())

        disks = disk_updates['partition_id'].unique()
        avail_avgs = []
        used_avgs = []
        for disk in disks:
            avail_avgs.append(disk_updates.loc[disk_updates['partition_id'] == disk]['free_storage'].mean())
            used_avgs.append(disk_updates.loc[disk_updates['partition_id'] == disk]['used_storage'].mean())
        historical.total_disk_avail = _clean(sum(avail_avgs))
        historical.total_disk_used = _clean(sum(used_avgs))

        gpus = gpu_updates['uuid'].unique()
        loads = []
        memory_useds = []
        for gpu in gpus:
            loads.append(gpu_updates.loc[gpu_updates['uuid'] == gpu]['load'].mean())
            memory_useds.append(gpu_updates.loc[gpu_updates['uuid'] == gpu]['memory_used'].mean())
        historical.avg_gpu_load = _clean(np.average(loads))
        historical.avg_gpu_memory_used = _clean(np.average(memory_useds))
        session.add(historical)

    print("Committing changes to Historical DB.")
    session.commit()

    query = session.query(Update).filter(Update.timestamp <= hr_cutoff)
    query.delete()

    session.commit()

    return True


if __name__ == '__main__':
    clean('localhost', 3306, 'user', 'password', 'shepherd', 1, False)
