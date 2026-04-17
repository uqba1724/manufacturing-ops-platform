import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime

# --- BROKER CONFIGURATION ---
# We use HiveMQ's free public broker for demonstration
# In production this would be a private broker inside ECAM's network
BROKER_HOST = "localhost"
BROKER_PORT = 1883

# Topic structure: ecam/machines/{machine_code}/{sensor_type}
# This mirrors real industrial MQTT topic conventions
TOPIC_BASE = "ecam/machines"

# --- MACHINE DEFINITIONS ---
# Each machine has sensors with defined normal operating ranges
MACHINES = {
    "MC001": {
        "name": "CNC Lathe 1",
        "sensors": {
            "spindle_speed": {"min": 2800, "max": 3200, "unit": "rpm"},
            "temperature": {"min": 55, "max": 75, "unit": "°C"},
            "vibration": {"min": 0.5, "max": 1.5, "unit": "mm/s"}
        }
    },
    "MC002": {
        "name": "CNC Milling Centre",
        "sensors": {
            "spindle_speed": {"min": 2500, "max": 3500, "unit": "rpm"},
            "temperature": {"min": 50, "max": 80, "unit": "°C"},
            "vibration": {"min": 0.3, "max": 2.0, "unit": "mm/s"}
        }
    }
}

# Probability of generating an anomalous reading
ANOMALY_PROBABILITY = 0.08  # 8% chance per reading


def generate_sensor_reading(machine_code: str, sensor_type: str) -> dict:
    """
    Generates a single sensor reading for a given machine and sensor.
    Has a small probability of generating an anomalous value.
    """
    sensor = MACHINES[machine_code]["sensors"][sensor_type]
    is_anomaly = random.random() < ANOMALY_PROBABILITY

    if is_anomaly:
        # Anomalous reading: 30-50% above the normal maximum
        value = round(
            sensor["max"] * random.uniform(1.3, 1.5), 2
        )
    else:
        # Normal reading: within the defined range
        value = round(
            random.uniform(sensor["min"], sensor["max"]), 2
        )

    return {
        "machine_code": machine_code,
        "machine_name": MACHINES[machine_code]["name"],
        "sensor_type": sensor_type,
        "value": value,
        "unit": sensor["unit"],
        "is_anomaly": int(is_anomaly),
        "timestamp": datetime.utcnow().isoformat()
    }


def on_connect(client, userdata, flags, rc):
    """Called when the client connects to the broker."""
    if rc == 0:
        print(f"Connected to MQTT broker: {BROKER_HOST}")
    else:
        print(f"Connection failed with code: {rc}")


def run_simulator(n_cycles: int = 5, interval_seconds: float = 2.0):
    """
    Runs the simulator for a specified number of cycles.
    Each cycle publishes one reading per sensor per machine.
    """
    # Create MQTT client
    client = mqtt.Client(client_id=f"ecam_simulator_{random.randint(1000,9999)}")
    client.on_connect = on_connect

    print(f"Connecting to MQTT broker at {BROKER_HOST}:{BROKER_PORT}...")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    # Start the network loop in a background thread
    # This handles reconnections and message delivery automatically
    client.loop_start()

    # Wait for connection to establish
    time.sleep(1)

    print(f"Starting simulation: {n_cycles} cycles, "
          f"{interval_seconds}s interval")
    print("-" * 50)

    for cycle in range(n_cycles):
        print(f"\nCycle {cycle + 1}/{n_cycles}")

        for machine_code, machine_data in MACHINES.items():
            for sensor_type in machine_data["sensors"]:

                # Generate a reading
                reading = generate_sensor_reading(machine_code, sensor_type)

                # Build the MQTT topic
                topic = f"{TOPIC_BASE}/{machine_code}/{sensor_type}"

                # Publish the reading as JSON
                # json.dumps converts the Python dictionary to a JSON string
                payload = json.dumps(reading)
                client.publish(topic, payload, qos=1)

                anomaly_tag = " *** ANOMALY ***" if reading["is_anomaly"] else ""
                print(f"  Published → {topic}")
                print(f"    Value: {reading['value']} {reading['unit']}"
                      f"{anomaly_tag}")

        time.sleep(interval_seconds)

    client.loop_stop()
    client.disconnect()
    print("\nSimulator finished.")


if __name__ == "__main__":
    run_simulator(n_cycles=5, interval_seconds=2.0)