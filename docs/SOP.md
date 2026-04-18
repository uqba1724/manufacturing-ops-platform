# Standard Operating Procedure
## ECAM Manufacturing Operations Platform
**Version:** 1.0  
**Date:** April 2026  
**Author:** Uqba Othman

---

## 1. Purpose

This SOP describes how to operate the ECAM Manufacturing Operations Platform 
on a day-to-day basis. It covers starting the system, using the dashboard, 
interpreting KPIs, and basic troubleshooting.

---

## 2. System Overview

The platform consists of three components:

- **API Backend** — serves manufacturing data over HTTP endpoints
- **KPI Dashboard** — visualises operational performance in real time
- **Data Pipeline** — cleans and validates incoming production data

The platform is hosted at:
- Cloud API: https://manufacturing-ops-platform.onrender.com
- Local dashboard: run `streamlit run src/dashboard/app.py`

---

## 3. Daily Startup Procedure

### 3.1 Cloud API (always running)
The API runs continuously on Render. No startup required.
If the API is unresponsive, open:
https://manufacturing-ops-platform.onrender.com/docs
The free tier may take 60 seconds to wake up after inactivity.

### 3.2 Local Dashboard
1. Open VS Code
2. Open terminal and navigate to project folder
3. Activate virtual environment:
.venv\Scripts\Activate.ps1
4. Start the dashboard:
streamlit run src/dashboard/app.py
5. Dashboard opens at http://localhost:8501

### 3.3 MQTT Machine Event Listener
To capture live machine events:
1. Open terminal 1 and run:
python src/mqtt_simulator/listener.py
2. Confirm "Subscribed to: ecam/machines/#" appears
3. Leave running during shift

---

## 4. KPI Interpretation Guide

| KPI | Green | Amber | Red |
|-----|-------|-------|-----|
| Plan Attainment | >85% | 70-85% | <70% |
| Machines Running | All | 75%+ | <75% |
| Machines in Fault | 0 | 1 | 2+ |
| Total Downtime | <60 mins | 60-120 mins | >120 mins |

### 4.1 Plan Attainment Below Target
1. Check Production Orders table — identify which orders are behind
2. Check Machine Status — identify any faults or idle machines
3. Check Downtime Log — identify reason and duration
4. Escalate to production manager if fault machine is on critical path

### 4.2 Machine Fault Detected
1. Check which machine is in fault status
2. Check Downtime Event Log for reason
3. Check Machine Events for anomaly alerts
4. Contact maintenance team with machine code and fault reason

---

## 5. Weekly Data Pipeline Run

Run the data cleaning pipeline weekly to process accumulated production data:

```bash
python src/data_pipeline/generate_raw_data.py
python src/data_pipeline/clean_data.py
```

Review the validation report output and escalate any recurring data quality 
issues to the relevant department.

---

## 6. RFQ Processing Procedure

When a new RFQ is received:

1. Save the RFQ text to a variable in `src/rfq_parser/sample_rfqs.py`
2. Run the parser:
```bash
   python src/rfq_parser/parser.py
```
3. Review extracted fields and check confidence level
4. Address any flagged missing fields with the customer before quoting
5. Review BOM and cost estimate — adjust unit costs if needed
6. Issue quotation based on validated output

---

## 7. Predictive Maintenance Scan

Run weekly or when machine behaviour is suspected abnormal:

```bash
python src/predictive_maintenance/anomaly_detector.py
```

Review the alert log. CRITICAL alerts require immediate maintenance review.
WARNING alerts should be monitored and scheduled for inspection.

---

## 8. Contacts

| Role | Responsibility |
|------|----------------|
| KTP Associate | Platform operation, development, support |
| Academic Supervisor | Technical guidance, research reporting |
| ECAM Production Manager | Operational decisions based on KPI data |
| ECAM IT | Infrastructure, network, access management |