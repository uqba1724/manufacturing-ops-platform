import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime

from src.database.db import SessionLocal
from src.database.models import MachineEvent, Machine

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC_SUBSCRIBE = "ecam/machines/#"
# The # wildcard means subscribe to ALL topics under ecam/machines/
# This captures readings from all machines and all sensors

# Track statistics
stats = {
    "messages_received": 0,
    "anomalies_detected": 0,
    "stored_to_db": 0
}


def get_machine_id(machine_code: str) -> int:
    """Looks up the database ID for a machine code."""
    db = SessionLocal()
    try:
        machine = db.query(Machine).filter(
            Machine.machine_code == machine_code
        ).first()
        return machine.id if machine else None
    finally:
        db.close()


def store_event(reading: dict):
    """Stores a received MQTT message as a MachineEvent in the database."""
    machine_id = get_machine_id(reading["machine_code"])
    if not machine_id:
        print(f"  Warning: Machine {reading['machine_code']} not found in DB")
        return

    db = SessionLocal()
    try:
        event = MachineEvent(
            machine_id=machine_id,
            event_type=reading["sensor_type"],
            value=reading["value"],
            unit=reading["unit"],
            timestamp=datetime.fromisoformat(reading["timestamp"]),
            is_anomaly=reading["is_anomaly"]
        )
        db.add(event)
        db.commit()
        stats["stored_to_db"] += 1
    finally:
        db.close()


def on_connect(client, userdata, flags, rc):
    """Called when connected to the broker."""
    if rc == 0:
        print(f"Listener connected to broker: {BROKER_HOST}")
        # Subscribe after connecting
        client.subscribe(TOPIC_SUBSCRIBE, qos=1)
        print(f"Subscribed to: {TOPIC_SUBSCRIBE}")
    else:
        print(f"Connection failed: {rc}")


def on_message(client, userdata, msg):
    """
    Called every time a message arrives on a subscribed topic.
    This is the core of the subscriber pattern.
    """
    stats["messages_received"] += 1

    try:
        # Decode the JSON payload
        reading = json.loads(msg.payload.decode("utf-8"))

        anomaly_tag = " *** ANOMALY ***" if reading.get("is_anomaly") else ""
        print(f"  Received: {msg.topic}")
        print(f"    {reading['value']} {reading['unit']}"
              f" @ {reading['timestamp']}{anomaly_tag}")

        # Store to database
        store_event(reading)

        if reading.get("is_anomaly"):
            stats["anomalies_detected"] += 1
            print(f"  ! Anomaly stored — "
                  f"total anomalies: {stats['anomalies_detected']}")

    except Exception as e:
        print(f"  Error processing message: {e}")


def run_listener(duration_seconds: int = 20):
    """
    Runs the listener for a specified duration.
    Stores all received messages to the database.
    """
    client = mqtt.Client(
        client_id=f"ecam_listener_{__import__('random').randint(1000,9999)}"
    )
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Connecting listener to {BROKER_HOST}:{BROKER_PORT}...")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    print(f"Listening for {duration_seconds} seconds...")
    print("-" * 50)

    # loop_start runs the network loop in a background thread
    # We then wait for the specified duration
    client.loop_start()
    time.sleep(duration_seconds)
    client.loop_stop()
    client.disconnect()

    print(f"\nListener finished.")
    print(f"Messages received: {stats['messages_received']}")
    print(f"Anomalies detected: {stats['anomalies_detected']}")
    print(f"Events stored to DB: {stats['stored_to_db']}")


if __name__ == "__main__":
    run_listener(duration_seconds=20)