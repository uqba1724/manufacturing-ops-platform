import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime

from src.database.db import SessionLocal
from src.database.models import MachineEvent, Machine


def load_machine_events() -> pd.DataFrame:
    """
    Loads machine events from the database into a DataFrame.
    """
    db = SessionLocal()
    try:
        events = db.query(MachineEvent).order_by(
            MachineEvent.timestamp.asc()
        ).all()

        rows = []
        for e in events:
            rows.append({
                "id": e.id,
                "machine_id": e.machine_id,
                "event_type": e.event_type,
                "value": e.value,
                "unit": e.unit,
                "timestamp": e.timestamp,
                "known_anomaly": e.is_anomaly  # ground truth from seed data
            })

        return pd.DataFrame(rows)
    finally:
        db.close()


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates features for the anomaly detection model.
    Raw sensor values alone are not enough — we also need
    to capture trends and variability over time.
    """
    df = df.copy()
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Encode event_type as a number so the model can use it
    # Models work with numbers, not strings
    event_type_map = {
        "spindle_speed": 0,
        "temperature": 1,
        "vibration": 2
    }
    df["event_type_encoded"] = df["event_type"].map(event_type_map).fillna(-1)

    # Rolling statistics — calculated over a window of 5 events
    # These capture whether values are trending or becoming more variable
    # min_periods=1 means we calculate even if fewer than 5 events exist
    df["rolling_mean"] = df["value"].rolling(window=5, min_periods=1).mean()
    df["rolling_std"] = df["value"].rolling(window=5, min_periods=1).std().fillna(0)

    # Deviation from rolling mean — how far is this reading from recent average?
    # A large deviation is a potential anomaly signal
    df["deviation_from_mean"] = abs(df["value"] - df["rolling_mean"])

    # Rate of change — how much did the value change from the previous reading?
    df["value_change"] = df["value"].diff().fillna(0)

    return df


def train_and_detect(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trains an Isolation Forest model and predicts anomalies.
    Returns the DataFrame with a predicted_anomaly column added.
    """

    # Select the features the model will use
    feature_columns = [
        "value",
        "event_type_encoded",
        "rolling_mean",
        "rolling_std",
        "deviation_from_mean",
        "value_change"
    ]

    X = df[feature_columns].values

    # StandardScaler normalises features to have mean=0 and std=1
    # This prevents features with large values (like spindle_speed at 3000 RPM)
    # from dominating features with small values (like vibration at 1.0 mm/s)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train the Isolation Forest model
    # contamination=0.1 tells the model to expect ~10% of data to be anomalous
    # n_estimators=100 means 100 isolation trees — more trees = more stable results
    # random_state=42 makes results reproducible
    model = IsolationForest(
        contamination=0.1,
        n_estimators=100,
        random_state=42
    )
    model.fit(X_scaled)

    # Predict: Isolation Forest returns -1 for anomalies, 1 for normal
    # We convert to 0/1 to match our database convention
    predictions = model.predict(X_scaled)
    df["predicted_anomaly"] = (predictions == -1).astype(int)

    # Anomaly score — more negative = more anomalous
    # Useful for ranking alerts by severity
    df["anomaly_score"] = model.score_samples(X_scaled)

    return df


def evaluate_detection(df: pd.DataFrame) -> dict:
    """
    Compares predicted anomalies against known anomalies from seed data.
    This is how we verify the model is working correctly.
    """
    known = df["known_anomaly"].values
    predicted = df["predicted_anomaly"].values

    # True positives: model correctly identified a known anomaly
    tp = sum(1 for k, p in zip(known, predicted) if k == 1 and p == 1)
    # False positives: model flagged something that was not an anomaly
    fp = sum(1 for k, p in zip(known, predicted) if k == 0 and p == 1)
    # False negatives: model missed a known anomaly
    fn = sum(1 for k, p in zip(known, predicted) if k == 1 and p == 0)
    # True negatives: model correctly identified normal readings
    tn = sum(1 for k, p in zip(known, predicted) if k == 0 and p == 0)

    # Precision: of all anomalies the model flagged, how many were real?
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0

    # Recall: of all real anomalies, how many did the model catch?
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    return {
        "total_events": len(df),
        "known_anomalies": int(sum(known)),
        "predicted_anomalies": int(sum(predicted)),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": round(precision, 3),
        "recall": round(recall, 3)
    }


def generate_alert_log(df: pd.DataFrame) -> list:
    """
    Generates a structured alert log from predicted anomalies.
    This is what would be sent to a maintenance engineer or dashboard.
    """
    alerts = []

    # Get only the predicted anomalies, sorted by severity
    anomalies = df[df["predicted_anomaly"] == 1].sort_values(
        "anomaly_score", ascending=True
    )

    severity_thresholds = {
        "critical": -0.15,
        "warning": -0.10,
    }

    for _, row in anomalies.iterrows():
        if row["anomaly_score"] < severity_thresholds["critical"]:
            severity = "CRITICAL"
        elif row["anomaly_score"] < severity_thresholds["warning"]:
            severity = "WARNING"
        else:
            severity = "INFO"

        alerts.append({
            "alert_id": f"ALT{int(row['id']):04d}",
            "machine_id": int(row["machine_id"]),
            "event_type": row["event_type"],
            "value": row["value"],
            "unit": row["unit"],
            "timestamp": str(row["timestamp"]),
            "severity": severity,
            "anomaly_score": round(row["anomaly_score"], 4),
            "deviation_from_mean": round(row["deviation_from_mean"], 4),
            "is_known_anomaly": bool(row["known_anomaly"])
        })

    return alerts


if __name__ == "__main__":
    print("ECAM Predictive Maintenance — Anomaly Detection")
    print("=" * 50)

    # Step 1: Load data
    print("\n1. Loading machine events from database...")
    df = load_machine_events()
    print(f"   Loaded {len(df)} events")

    # Step 2: Engineer features
    print("\n2. Engineering features...")
    df = engineer_features(df)
    print(f"   Features: {list(df.columns)}")

    # Step 3: Train model and detect anomalies
    print("\n3. Training Isolation Forest and detecting anomalies...")
    df = train_and_detect(df)
    print(f"   Predicted anomalies: {df['predicted_anomaly'].sum()}")

    # Step 4: Evaluate against known anomalies
    print("\n4. Evaluating detection performance...")
    metrics = evaluate_detection(df)
    print(f"   Known anomalies:     {metrics['known_anomalies']}")
    print(f"   Predicted anomalies: {metrics['predicted_anomalies']}")
    print(f"   True positives:      {metrics['true_positives']}")
    print(f"   False positives:     {metrics['false_positives']}")
    print(f"   False negatives:     {metrics['false_negatives']}")
    print(f"   Precision:           {metrics['precision']}")
    print(f"   Recall:              {metrics['recall']}")

    # Step 5: Generate alert log
    print("\n5. Generating alert log...")
    alerts = generate_alert_log(df)
    print(f"   {len(alerts)} alerts generated\n")

    for alert in alerts:
        known_tag = " [KNOWN]" if alert["is_known_anomaly"] else ""
        print(f"   [{alert['severity']}] {alert['alert_id']} — "
              f"Machine {alert['machine_id']} — "
              f"{alert['event_type']}: {alert['value']} {alert['unit']}"
              f"{known_tag}")

    print("\n" + "=" * 50)
    print("Predictive maintenance scan complete.")