from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Schemas define the shape of data the API returns.
# Pydantic validates that the data matches the expected types.
# This is separate from models.py which defines database tables.

class MachineSchema(BaseModel):
    id: int
    machine_code: str
    name: str
    status: str
    location: Optional[str] = None

    class Config:
        # This allows Pydantic to read data from SQLAlchemy objects
        # instead of only from plain dictionaries
        from_attributes = True


class JobSchema(BaseModel):
    id: int
    job_code: str
    machine_id: int
    part_name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductionOrderSchema(BaseModel):
    id: int
    order_code: str
    job_id: int
    customer_name: str
    quantity_planned: int
    quantity_completed: int
    due_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class DowntimeEventSchema(BaseModel):
    id: int
    machine_id: int
    reason: str
    duration_minutes: float
    event_time: datetime

    class Config:
        from_attributes = True


class DefectSchema(BaseModel):
    id: int
    job_id: int
    defect_type: str
    defect_count: int
    severity: Optional[str] = None
    event_time: datetime

    class Config:
        from_attributes = True


class QuotationSchema(BaseModel):
    id: int
    quote_code: str
    customer_name: str
    material: Optional[str] = None
    quantity: Optional[int] = None
    estimated_cost: Optional[float] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BOMItemSchema(BaseModel):
    id: int
    quotation_id: int
    item_code: str
    description: str
    quantity: float
    unit: str
    unit_cost: float

    class Config:
        from_attributes = True


class MachineEventSchema(BaseModel):
    id: int
    machine_id: int
    event_type: str
    value: Optional[float] = None
    unit: Optional[str] = None
    timestamp: datetime
    is_anomaly: int

    class Config:
        from_attributes = True


class KPISummarySchema(BaseModel):
    # This schema is not backed by a database table.
    # It is calculated and returned directly by the endpoint.
    total_machines: int
    machines_running: int
    machines_idle: int
    machines_fault: int
    total_jobs: int
    jobs_in_progress: int
    jobs_complete: int
    total_downtime_minutes: float
    total_defects: int
    active_orders: int
    plan_attainment_pct: float