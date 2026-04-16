from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from src.database.db import Base


class Machine(Base):
    # Each class maps to one table in the database.
    # __tablename__ sets the actual table name in the database file.
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # running, idle, fault
    location = Column(String, nullable=True)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_code = Column(String, unique=True, nullable=False)
    # ForeignKey links this column to the id column in the machines table.
    # This means every job must reference a real machine.
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    part_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # queued, in_progress, complete
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String, unique=True, nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    quantity_planned = Column(Integer, nullable=False)
    quantity_completed = Column(Integer, default=0)
    due_date = Column(DateTime, nullable=True)


class DowntimeEvent(Base):
    __tablename__ = "downtime_events"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    reason = Column(String, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    event_time = Column(DateTime, default=datetime.utcnow)


class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    defect_type = Column(String, nullable=False)
    defect_count = Column(Integer, nullable=False)
    severity = Column(String, nullable=True)  # low, medium, high
    event_time = Column(DateTime, default=datetime.utcnow)


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)
    quote_code = Column(String, unique=True, nullable=False)
    customer_name = Column(String, nullable=False)
    material = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    status = Column(String, nullable=False)  # draft, sent, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)


class BOMItem(Base):
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    item_code = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # kg, metres, hours, units
    unit_cost = Column(Float, nullable=False)


class MachineEvent(Base):
    # This table stores real-time events from machines.
    # Used by the MQTT simulator and predictive maintenance module.
    __tablename__ = "machine_events"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    event_type = Column(String, nullable=False)  # status, sensor_reading, alert
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_anomaly = Column(Integer, default=0)  # 0 = normal, 1 = anomaly flagged