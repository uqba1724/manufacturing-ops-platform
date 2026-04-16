import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


def generate_raw_production_data(n_rows=200):
    """
    Generates a synthetic raw production dataset with realistic 
    data quality issues: missing values, duplicates, out-of-range 
    readings, inconsistent formats.
    """
    random.seed(42)
    np.random.seed(42)

    machines = ["MC001", "MC002", "MC003", "MC004"]
    operators = ["OP01", "OP02", "OP03", "OP04"]
    parts = ["Shaft Collar", "Mounting Bracket", "Bearing Housing",
             "Steel Panel", "Frame Assembly"]
    shifts = ["morning", "afternoon", "night", "MORNING", "Night"]
    # Note: shifts has inconsistent capitalisation — intentional dirty data

    rows = []
    base_time = datetime.utcnow() - timedelta(days=14)

    for i in range(n_rows):
        timestamp = base_time + timedelta(minutes=i * 100)

        row = {
            "record_id": i + 1,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "machine_code": random.choice(machines),
            "operator_id": random.choice(operators),
            "part_name": random.choice(parts),
            "shift": random.choice(shifts),
            "quantity_produced": random.randint(5, 50),
            "cycle_time_seconds": round(random.uniform(45, 120), 2),
            "temperature_c": round(random.uniform(55, 80), 2),
            "spindle_speed_rpm": random.randint(2500, 3500),
            "defect_count": random.randint(0, 5),
            "downtime_minutes": round(random.uniform(0, 30), 2)
        }

        # Inject missing values — 8% of rows
        if random.random() < 0.08:
            row["operator_id"] = None

        if random.random() < 0.05:
            row["cycle_time_seconds"] = None

        if random.random() < 0.06:
            row["temperature_c"] = None

        # Inject out-of-range values — sensor spikes
        if random.random() < 0.05:
            row["temperature_c"] = round(random.uniform(150, 300), 2)

        if random.random() < 0.04:
            row["spindle_speed_rpm"] = random.randint(8000, 12000)

        # Inject negative values — data entry errors
        if random.random() < 0.03:
            row["quantity_produced"] = random.randint(-10, -1)

        # Inject duplicate rows — 5% of rows are exact duplicates
        rows.append(row)
        if random.random() < 0.05 and i > 0:
            rows.append(rows[-2].copy())

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df = generate_raw_production_data()
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/production_raw.csv", index=False)
    print(f"Raw dataset generated: {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample issues:")
    print(f"  Missing operator_id: {df['operator_id'].isna().sum()}")
    print(f"  Missing cycle_time: {df['cycle_time_seconds'].isna().sum()}")
    print(f"  Negative quantities: {(df['quantity_produced'] < 0).sum()}")
    print(f"  High temperature (>100°C): {(df['temperature_c'] > 100).sum()}")
    print(f"  Duplicate rows: {df.duplicated().sum()}")