"""
Auto-Generated Code by sqlacodegen
https://pypi.org/project/sqlacodegen/
"""
from sqlalchemy import Column, DateTime, Float, ForeignKey, ForeignKeyConstraint, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Pool(Base):
    __tablename__ = 'Pool'

    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<Pool(id={self.id})>"


class Node(Base):
    __tablename__ = 'Node'

    id = Column(Integer, primary_key=True, nullable=False)
    pool_id = Column(ForeignKey('Pool.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)

    pool = relationship('Pool')

    def __repr__(self):
        return f"<Node(id={self.id}, pool_id={self.pool_id})>"


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
    ram_total_virtual = Column(Integer)
    ram_used_virtual = Column(Integer)
    ram_available_virtual = Column(Integer)
    ram_free_virtual = Column(Integer)
    ram_total_swap = Column(Integer)
    ram_used_swap = Column(Integer)
    ram_free_swap = Column(Integer)
    ram_percent_swap = Column(Float)
    disk_read_count = Column(Integer)
    disk_write_count = Column(Integer)
    disk_read_bytes = Column(Integer)
    disk_write_bytes = Column(Integer)
    disk_read_time = Column(Integer)
    disk_write_time = Column(Integer)
    battery_available_percent = Column(Float)
    battery_est_remain = Column(Integer)
    battery_plugged_in = Column(TINYINT(1))
    session_boot_time = Column(DateTime)
    session_uptime = Column(Integer)

    node = relationship('Node')

    def __repr__(self):
        return f"<Update(id={self.id}, pool_id={self.pool_id}, node_id={self.node_id}, timestamp={self.timestamp})>"


class DiskUpdate(Base):
    __tablename__ = 'Disk_Update'

    id = Column(Integer, primary_key=True)
    update_id = Column(ForeignKey('Update.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    partition_id = Column(String(50))
    mount_point = Column(String(50))
    fstype = Column(String(20))
    total_storage = Column(Integer)
    used_storage = Column(Integer)
    free_storage = Column(Integer)
    percentage_used = Column(Float)

    update = relationship('Update')


class GPUUpdate(Base):
    __tablename__ = 'GPU_Update'

    id = Column(Integer, primary_key=True)
    update_id = Column(ForeignKey('Update.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    uuid = Column(String(50))
    load = Column(Float)
    memory_percentage = Column(Float)
    memory_total = Column(Integer)
    memory_used = Column(Integer)
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
