"""
Auto-Generated Code by sqlacodegen
https://pypi.org/project/sqlacodegen/
"""
from sqlalchemy import BigInteger, Column, DateTime, Enum, Float, ForeignKey, ForeignKeyConstraint, Index, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Pool(Base):
    __tablename__ = 'Pool'

    id = Column(Integer, primary_key=True)
    nodes = relationship('Node', back_populates="pool")


class Node(Base):
    __tablename__ = 'Node'

    id = Column(Integer, primary_key=True, nullable=False)
    pool_id = Column(ForeignKey('Pool.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    name = Column(String(100), server_default=text("'Node'"))
    pool = relationship('Pool', back_populates='nodes')
    updates = relationship('Update')


class AnomalyRecord(Base):
    __tablename__ = 'Anomaly_Record'
    __table_args__ = (
        ForeignKeyConstraint(['pool_id', 'node_id'], ['Node.pool_id', 'Node.id'], ondelete='CASCADE', onupdate='CASCADE'),
        Index('Anomaly_Record_Node__fk', 'pool_id', 'node_id')
    )

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, nullable=False)
    pool_id = Column(Integer, nullable=False)
    type = Column(Enum('cpu', 'ram', 'disk', 'gpu', 'session', 'battery', 'other'), nullable=False)
    time = Column(DateTime, nullable=False)
    resolved = Column(TINYINT(1), nullable=False)
    message = Column(String(250))
    severity = Column(Enum('low', 'medium', 'high', 'none'), nullable=False)

    node = relationship('Node')


class HistoricalData(Base):
    __tablename__ = 'Historical_Data'
    __table_args__ = (
        ForeignKeyConstraint(['pool_id', 'node_id'], ['Node.pool_id', 'Node.id'], ondelete='CASCADE', onupdate='CASCADE'),
        Index('Historical_Data_Node__fk', 'pool_id', 'node_id')
    )

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, nullable=False)
    pool_id = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False)
    avg_cpu_curr_freq = Column(Float)
    avg_cpu_percent_usage = Column(Float)
    avg_cpu_load_1 = Column(Float)
    avg_cpu_load_5 = Column(Float)
    avg_cpu_load_15 = Column(Float)
    avg_ram_used_virt = Column(BigInteger)
    avg_ram_used_swap = Column(BigInteger)
    total_disk_avail = Column(BigInteger)
    total_disk_used = Column(BigInteger)
    avg_battery_avail = Column(Float)
    avg_gpu_load = Column(Float)
    avg_gpu_memory_used = Column(BigInteger)

    node = relationship('Node')


class Update(Base):
    __tablename__ = 'Update'
    __table_args__ = (
        ForeignKeyConstraint(['pool_id', 'node_id'], ['Node.pool_id', 'Node.id'], ondelete='CASCADE', onupdate='CASCADE'),
        Index('Update_Node__fk', 'pool_id', 'node_id')
    )

    id = Column(Integer, primary_key=True)
    pool_id = Column(Integer, nullable=False)
    node_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    cpu_logical_cores = Column(Integer)
    cpu_current_frequency = Column(Float)
    cpu_max_frequency = Column(Float)
    cpu_percent_usage = Column(Float)
    cpu_load_1 = Column(Float)
    cpu_load_5 = Column(Float)
    cpu_load_15 = Column(Float)
    ram_total_virtual = Column(BigInteger)
    ram_used_virtual = Column(BigInteger)
    ram_available_virtual = Column(BigInteger)
    ram_free_virtual = Column(BigInteger)
    ram_total_swap = Column(BigInteger)
    ram_used_swap = Column(BigInteger)
    ram_free_swap = Column(BigInteger)
    ram_percent_swap = Column(Float)
    disk_read_count = Column(BigInteger)
    disk_write_count = Column(BigInteger)
    disk_read_bytes = Column(BigInteger)
    disk_write_bytes = Column(BigInteger)
    disk_read_time = Column(BigInteger)
    disk_write_time = Column(BigInteger)
    battery_available_percent = Column(Float)
    battery_est_remain = Column(BigInteger)
    battery_plugged_in = Column(TINYINT(1))
    session_boot_time = Column(DateTime)
    session_uptime = Column(BigInteger)

    node = relationship('Node', back_populates='updates')


class DiskUpdate(Base):
    __tablename__ = 'Disk_Update'

    id = Column(Integer, primary_key=True)
    update_id = Column(ForeignKey('Update.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    partition_id = Column(String(50))
    mount_point = Column(String(50))
    fstype = Column(String(20))
    total_storage = Column(BigInteger)
    used_storage = Column(BigInteger)
    free_storage = Column(BigInteger)
    percentage_used = Column(Float)

    update = relationship('Update')


class GPUUpdate(Base):
    __tablename__ = 'GPU_Update'

    id = Column(Integer, primary_key=True)
    update_id = Column(ForeignKey('Update.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    uuid = Column(String(50))
    load = Column(Float)
    memory_percentage = Column(Float)
    memory_total = Column(BigInteger)
    memory_used = Column(BigInteger)
    driver_version = Column(String(50))
    product_identifier = Column(String(50))
    serial = Column(String(50))
    display_mode = Column(String(20))

    update = relationship('Update')


class SessionUpdate(Base):
    __tablename__ = 'Session_Update'

    id = Column(Integer, primary_key=True)
    update_id = Column(ForeignKey('Update.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    user = Column(String(50))
    terminal = Column(String(50))
    host = Column(String(100))
    started_time = Column(DateTime)
    process_id = Column(Integer)

    update = relationship('Update')
