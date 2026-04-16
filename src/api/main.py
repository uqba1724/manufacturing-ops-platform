import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database.db import get_db
from src.database.models import (
    Machine, Job, ProductionOrder,
    DowntimeEvent, Defect, Quotation, BOMItem, MachineEvent
)
from src.api.schemas import (
    MachineSchema, JobSchema, ProductionOrderSchema,
    DowntimeEventSchema, DefectSchema, QuotationSchema,
    BOMItemSchema, MachineEventSchema, KPISummarySchema
)

# Create the FastAPI application instance
app = FastAPI(
    title="ECAM Manufacturing Operations API",
    description="AI-enabled manufacturing operations platform for ECAM Engineering",
    version="1.0.0"
)


# --- MACHINES ---

@app.get("/machines", response_model=List[MachineSchema])
def get_machines(db: Session = Depends(get_db)):
    # Depends(get_db) tells FastAPI to call get_db() and inject
    # the session it yields into this function automatically.
    # We never create or close sessions manually in endpoints.
    machines = db.query(Machine).all()
    return machines


@app.get("/machines/{machine_id}", response_model=MachineSchema)
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        # HTTPException returns a proper HTTP error response
        # with a status code and a message
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine


# --- JOBS ---

@app.get("/jobs", response_model=List[JobSchema])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


@app.get("/jobs/{job_id}", response_model=JobSchema)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# --- PRODUCTION ORDERS ---

@app.get("/orders", response_model=List[ProductionOrderSchema])
def get_orders(db: Session = Depends(get_db)):
    return db.query(ProductionOrder).all()


# --- DOWNTIME EVENTS ---

@app.get("/downtime", response_model=List[DowntimeEventSchema])
def get_downtime(db: Session = Depends(get_db)):
    return db.query(DowntimeEvent).all()


# --- DEFECTS ---

@app.get("/defects", response_model=List[DefectSchema])
def get_defects(db: Session = Depends(get_db)):
    return db.query(Defect).all()


# --- QUOTATIONS ---

@app.get("/quotations", response_model=List[QuotationSchema])
def get_quotations(db: Session = Depends(get_db)):
    return db.query(Quotation).all()


@app.get("/quotations/{quote_id}/bom", response_model=List[BOMItemSchema])
def get_bom(quote_id: int, db: Session = Depends(get_db)):
    # Check the quotation exists first
    quote = db.query(Quotation).filter(Quotation.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return db.query(BOMItem).filter(BOMItem.quotation_id == quote_id).all()


# --- MACHINE EVENTS ---

@app.get("/machine-events", response_model=List[MachineEventSchema])
def get_machine_events(db: Session = Depends(get_db)):
    return db.query(MachineEvent).order_by(MachineEvent.timestamp.desc()).all()


@app.get("/machine-events/anomalies", response_model=List[MachineEventSchema])
def get_anomalies(db: Session = Depends(get_db)):
    # Return only the events flagged as anomalies
    return db.query(MachineEvent).filter(MachineEvent.is_anomaly == 1).all()


# --- KPI SUMMARY ---

@app.get("/kpis/summary", response_model=KPISummarySchema)
def get_kpi_summary(db: Session = Depends(get_db)):
    # This endpoint calculates KPIs on the fly from the database
    # rather than storing them as static values

    machines = db.query(Machine).all()
    jobs = db.query(Job).all()
    orders = db.query(ProductionOrder).all()
    downtime = db.query(DowntimeEvent).all()
    defects = db.query(Defect).all()

    total_planned = sum(o.quantity_planned for o in orders)
    total_completed = sum(o.quantity_completed for o in orders)

    # Plan attainment = completed / planned * 100
    # Avoid division by zero with a conditional expression
    plan_attainment = (total_completed / total_planned * 100) if total_planned > 0 else 0.0

    return KPISummarySchema(
        total_machines=len(machines),
        machines_running=sum(1 for m in machines if m.status == "running"),
        machines_idle=sum(1 for m in machines if m.status == "idle"),
        machines_fault=sum(1 for m in machines if m.status == "fault"),
        total_jobs=len(jobs),
        jobs_in_progress=sum(1 for j in jobs if j.status == "in_progress"),
        jobs_complete=sum(1 for j in jobs if j.status == "complete"),
        total_downtime_minutes=sum(d.duration_minutes for d in downtime),
        total_defects=sum(d.defect_count for d in defects),
        active_orders=sum(1 for o in orders if o.quantity_completed < o.quantity_planned),
        plan_attainment_pct=round(plan_attainment, 1)
    )