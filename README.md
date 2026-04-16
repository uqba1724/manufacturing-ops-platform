# ECAM Manufacturing Operations Platform

An AI-enabled manufacturing operations platform built as part of a 
Knowledge Transfer Partnership (KTP) preparation project.

## What This Platform Does

- Captures and stores structured manufacturing data (machines, jobs, 
  production orders, downtime, defects, quotations, BOM items)
- Exposes live data via a REST API with 12 endpoints
- Visualises operational KPIs on an interactive dashboard
- Parses RFQ documents using AI to extract structured data and generate 
  BoM and cost estimates
- Detects machine anomalies using ML-based predictive maintenance
- Simulates industrial IoT machine events via MQTT

## Tech Stack

Python 3.11, FastAPI, SQLAlchemy, SQLite, Streamlit, Plotly, 
Anthropic Claude API, scikit-learn, paho-mqtt

## How to Run

1. Clone the repo
2. Create and activate a virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Create the database: `python src/database/init_db.py`
5. Seed sample data: `python src/database/seed_data.py`
6. Start the API: `uvicorn src.api.main:app --reload`
7. Start the dashboard: `streamlit run src/dashboard/app.py`

## Project Structure

```
src/
  database/      # Schema, models, seed data
  api/           # FastAPI endpoints and schemas
  dashboard/     # Streamlit KPI dashboard
  data_pipeline/ # Data cleaning and validation
  rfq_parser/    # AI-powered RFQ document parser
  predictive_maintenance/  # ML anomaly detection
  mqtt_simulator/          # IoT machine event simulation
```
