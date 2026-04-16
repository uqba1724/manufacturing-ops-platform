import sys
import os
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.db import SessionLocal
from src.database.models import (
    Machine, Job, ProductionOrder,
    DowntimeEvent, Defect, Quotation, BOMItem, MachineEvent
)


def seed_data():
    # Create a session — our temporary connection to the database
    db = SessionLocal()

    try:
        # Check if data already exists — if so, skip seeding
        # This means the script is safe to run multiple times
        if db.query(Machine).first():
            print("Data already exists. Skipping seed.")
            return

        # --- MACHINES ---
        # Four machines typical of a precision engineering shop
        machines = [
            Machine(machine_code="MC001", name="CNC Lathe 1",
                    status="running", location="Shop Floor A"),
            Machine(machine_code="MC002", name="CNC Milling Centre",
                    status="running", location="Shop Floor A"),
            Machine(machine_code="MC003", name="Press Brake",
                    status="idle", location="Shop Floor B"),
            Machine(machine_code="MC004", name="TIG Welder",
                    status="fault", location="Shop Floor B"),
        ]
        db.add_all(machines)
        # commit() saves the records permanently to the database
        db.commit()

        # refresh() reloads each object so we can access
        # the auto-generated id values assigned by the database
        for m in machines:
            db.refresh(m)

        # --- JOBS ---
        # Jobs run on specific machines — machine_id is the foreign key
        jobs = [
            Job(job_code="JOB001", machine_id=machines[0].id,
                part_name="Shaft Collar", status="complete",
                start_time=datetime.utcnow() - timedelta(hours=8),
                end_time=datetime.utcnow() - timedelta(hours=5)),
            Job(job_code="JOB002", machine_id=machines[1].id,
                part_name="Mounting Bracket", status="in_progress",
                start_time=datetime.utcnow() - timedelta(hours=3)),
            Job(job_code="JOB003", machine_id=machines[0].id,
                part_name="Bearing Housing", status="queued",
                start_time=datetime.utcnow() - timedelta(hours=1)),
            Job(job_code="JOB004", machine_id=machines[2].id,
                part_name="Steel Panel", status="complete",
                start_time=datetime.utcnow() - timedelta(hours=6),
                end_time=datetime.utcnow() - timedelta(hours=4)),
            Job(job_code="JOB005", machine_id=machines[3].id,
                part_name="Frame Assembly", status="on_hold",
                start_time=datetime.utcnow() - timedelta(hours=2)),
        ]
        db.add_all(jobs)
        db.commit()
        for j in jobs:
            db.refresh(j)

        # --- PRODUCTION ORDERS ---
        orders = [
            ProductionOrder(order_code="PO001", job_id=jobs[0].id,
                            customer_name="Rolls-Royce Suppliers Ltd",
                            quantity_planned=50, quantity_completed=50,
                            due_date=datetime.utcnow() + timedelta(days=1)),
            ProductionOrder(order_code="PO002", job_id=jobs[1].id,
                            customer_name="Midlands Aerospace",
                            quantity_planned=120, quantity_completed=74,
                            due_date=datetime.utcnow() + timedelta(days=3)),
            ProductionOrder(order_code="PO003", job_id=jobs[2].id,
                            customer_name="Midlands Aerospace",
                            quantity_planned=80, quantity_completed=0,
                            due_date=datetime.utcnow() + timedelta(days=5)),
            ProductionOrder(order_code="PO004", job_id=jobs[3].id,
                            customer_name="TechFab Engineering",
                            quantity_planned=30, quantity_completed=30,
                            due_date=datetime.utcnow() + timedelta(days=2)),
            ProductionOrder(order_code="PO005", job_id=jobs[4].id,
                            customer_name="TechFab Engineering",
                            quantity_planned=15, quantity_completed=0,
                            due_date=datetime.utcnow() + timedelta(days=4)),
        ]
        db.add_all(orders)
        db.commit()

        # --- DOWNTIME EVENTS ---
        downtime_events = [
            DowntimeEvent(machine_id=machines[0].id,
                          reason="Tooling change",
                          duration_minutes=35.0,
                          event_time=datetime.utcnow() - timedelta(hours=6)),
            DowntimeEvent(machine_id=machines[1].id,
                          reason="Coolant refill",
                          duration_minutes=15.0,
                          event_time=datetime.utcnow() - timedelta(hours=4)),
            DowntimeEvent(machine_id=machines[3].id,
                          reason="Electrode replacement",
                          duration_minutes=90.0,
                          event_time=datetime.utcnow() - timedelta(hours=2)),
            DowntimeEvent(machine_id=machines[2].id,
                          reason="Scheduled maintenance",
                          duration_minutes=60.0,
                          event_time=datetime.utcnow() - timedelta(hours=5)),
            DowntimeEvent(machine_id=machines[0].id,
                          reason="Program error",
                          duration_minutes=20.0,
                          event_time=datetime.utcnow() - timedelta(hours=1)),
        ]
        db.add_all(downtime_events)
        db.commit()

        # --- DEFECTS ---
        defects = [
            Defect(job_id=jobs[0].id, defect_type="Dimensional deviation",
                   defect_count=2, severity="medium",
                   event_time=datetime.utcnow() - timedelta(hours=7)),
            Defect(job_id=jobs[1].id, defect_type="Surface finish failure",
                   defect_count=1, severity="low",
                   event_time=datetime.utcnow() - timedelta(hours=2)),
            Defect(job_id=jobs[3].id, defect_type="Edge burr",
                   defect_count=4, severity="low",
                   event_time=datetime.utcnow() - timedelta(hours=5)),
        ]
        db.add_all(defects)
        db.commit()

        # --- QUOTATIONS ---
        quote1 = Quotation(
            quote_code="QT001",
            customer_name="Midlands Aerospace",
            material="Aluminium 6082",
            quantity=200,
            estimated_cost=4800.0,
            status="sent"
        )
        quote2 = Quotation(
            quote_code="QT002",
            customer_name="TechFab Engineering",
            material="Mild Steel S275",
            quantity=50,
            estimated_cost=1950.0,
            status="draft"
        )
        db.add_all([quote1, quote2])
        db.commit()
        db.refresh(quote1)
        db.refresh(quote2)

        # --- BOM ITEMS ---
        # Bill of Materials: what goes into making the quoted parts
        bom_items = [
            BOMItem(quotation_id=quote1.id, item_code="MAT001",
                    description="Aluminium 6082 bar stock 50mm dia",
                    quantity=12.5, unit="kg", unit_cost=8.40),
            BOMItem(quotation_id=quote1.id, item_code="PROC001",
                    description="CNC turning and milling",
                    quantity=6.0, unit="hours", unit_cost=65.0),
            BOMItem(quotation_id=quote1.id, item_code="PROC002",
                    description="Anodising treatment",
                    quantity=200.0, unit="units", unit_cost=1.20),
            BOMItem(quotation_id=quote2.id, item_code="MAT002",
                    description="Mild Steel S275 plate 10mm",
                    quantity=8.0, unit="kg", unit_cost=3.20),
            BOMItem(quotation_id=quote2.id, item_code="PROC003",
                    description="Press braking and welding",
                    quantity=4.0, unit="hours", unit_cost=65.0),
        ]
        db.add_all(bom_items)
        db.commit()

        # --- MACHINE EVENTS ---
        # Simulated sensor readings over the last 2 hours
        # These will be used by the predictive maintenance module
        event_types = ["spindle_speed", "temperature", "vibration"]
        normal_ranges = {
            "spindle_speed": (2800, 3200),
            "temperature": (55, 75),
            "vibration": (0.5, 1.5)
        }

        events = []
        for i in range(40):
            machine = random.choice(machines[:2])  # CNC machines only
            etype = random.choice(event_types)
            low, high = normal_ranges[etype]

            # Inject 3 anomalies into the dataset
            if i in [12, 25, 37]:
                value = high * 1.4  # 40% above normal range
                is_anomaly = 1
            else:
                value = round(random.uniform(low, high), 2)
                is_anomaly = 0

            events.append(MachineEvent(
                machine_id=machine.id,
                event_type=etype,
                value=value,
                unit="rpm" if etype == "spindle_speed" else
                     "°C" if etype == "temperature" else "mm/s",
                timestamp=datetime.utcnow() - timedelta(minutes=40 - i),
                is_anomaly=is_anomaly
            ))

        db.add_all(events)
        db.commit()

        print("Seed data inserted successfully.")
        print(f"  Machines:       {len(machines)}")
        print(f"  Jobs:           {len(jobs)}")
        print(f"  Orders:         {len(orders)}")
        print(f"  Downtime events:{len(downtime_events)}")
        print(f"  Defects:        {len(defects)}")
        print(f"  Quotations:     2")
        print(f"  BOM items:      {len(bom_items)}")
        print(f"  Machine events: {len(events)}")

    except Exception as e:
        # If anything goes wrong, roll back all changes
        # so the database is not left in a broken state
        db.rollback()
        print(f"Error during seeding: {e}")
        raise

    finally:
        # Always close the session whether it succeeded or failed
        db.close()


if __name__ == "__main__":
    seed_data()