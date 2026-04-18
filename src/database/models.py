from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from src.database.db import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    location = Column(String(100), nullable=True)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_code = Column(String(50), unique=True, nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    part_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(50), unique=True, nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    customer_name = Column(String(100), nullable=False)
    quantity_planned = Column(Integer, nullable=False)
    quantity_completed = Column(Integer, default=0)
    due_date = Column(DateTime, nullable=True)


class DowntimeEvent(Base):
    __tablename__ = "downtime_events"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    reason = Column(String(200), nullable=False)
    duration_minutes = Column(Float, nullable=False)
    event_time = Column(DateTime, default=datetime.utcnow)


class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    defect_type = Column(String(100), nullable=False)
    defect_count = Column(Integer, nullable=False)
    severity = Column(String(20), nullable=True)
    event_time = Column(DateTime, default=datetime.utcnow)


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)
    quote_code = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    material = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class BOMItem(Base):
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    item_code = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    unit_cost = Column(Float, nullable=False)


class MachineEvent(Base):
    __tablename__ = "machine_events"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_anomaly = Column(Integer, default=0)