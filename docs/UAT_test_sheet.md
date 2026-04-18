# UAT Test Sheet — ECAM Manufacturing Operations Platform
**Version:** 1.0  
**Date:** April 2026  
**Prepared by:** Uqba Othman  
**Platform URL:** https://manufacturing-ops-platform.onrender.com

---

## Instructions
For each test case, perform the action described, check the expected result, 
and mark the outcome as PASS or FAIL. Note any issues in the comments column.

---

## Module 1 — API Endpoints

| ID | Test Case | Steps | Expected Result | Outcome | Comments |
|----|-----------|-------|-----------------|---------|----------|
| T01 | API documentation loads | Open /docs in browser | Swagger UI shows all 12 endpoints | | |
| T02 | Get all machines | GET /machines | Returns list of 4 machines with correct codes | | |
| T03 | Get single machine | GET /machines/1 | Returns CNC Lathe 1 details | | |
| T04 | Get invalid machine | GET /machines/999 | Returns 404 with "Machine not found" | | |
| T05 | Get all jobs | GET /jobs | Returns list of 5 jobs | | |
| T06 | Get production orders | GET /orders | Returns 5 orders with quantities | | |
| T07 | Get downtime events | GET /downtime | Returns 5 downtime events | | |
| T08 | Get defects | GET /defects | Returns defect records | | |
| T09 | Get quotations | GET /quotations | Returns 2 quotations | | |
| T10 | Get BOM for quotation | GET /quotations/1/bom | Returns BOM items for QT001 | | |
| T11 | Get machine events | GET /machine-events | Returns timestamped sensor events | | |
| T12 | Get anomalies only | GET /machine-events/anomalies | Returns only flagged anomaly events | | |
| T13 | Get KPI summary | GET /kpis/summary | Returns all KPIs including plan attainment | | |

---

## Module 2 — KPI Values Verification

| ID | Test Case | Expected Value | Actual Value | Outcome |
|----|-----------|----------------|--------------|---------|
| T14 | Total machines | 4 | | |
| T15 | Machines running | 2 | | |
| T16 | Machines in fault | 1 | | |
| T17 | Total jobs | 5 | | |
| T18 | Total downtime minutes | 220 | | |
| T19 | Total defects | 7 | | |
| T20 | Plan attainment % | 52.2 | | |
| T21 | Active orders | 3 | | |

---

## Module 3 — Data Pipeline

| ID | Test Case | Steps | Expected Result | Outcome |
|----|-----------|-------|-----------------|---------|
| T22 | Generate raw data | Run generate_raw_data.py | 200+ rows CSV with injected errors | | 
| T23 | Clean data | Run clean_data.py | Cleaned CSV, duplicates removed | |
| T24 | Validation report | Check report output | Issues found and actions taken listed | |
| T25 | Derived columns | Check cleaned CSV | defect_rate and efficiency_flag columns present | |

---

## Module 4 — RFQ Parser

| ID | Test Case | Steps | Expected Result | Outcome |
|----|-----------|-------|-----------------|---------|
| T26 | Parse RFQ001 | Run parser.py | Extracts part, material, quantity, delivery | |
| T27 | Confidence flag | Check RFQ001 result | Confidence shows "high" | |
| T28 | Missing field detection | Check RFQ002 result | Missing fields listed in output | |
| T29 | BOM generation | Check any result | BOM items with costs generated | |
| T30 | Cost estimate | Check any result | Subtotal, margin, total, per unit cost | |
| T31 | Material rate matching | Check RFQ003 | 316L stainless shows £18/kg not £5/kg | |

---

## Module 5 — Predictive Maintenance

| ID | Test Case | Steps | Expected Result | Outcome |
|----|-----------|-------|-----------------|---------|
| T32 | Load events | Run anomaly_detector.py | 40 events loaded from database | |
| T33 | Feature engineering | Check output | 6 features including rolling stats | |
| T34 | Anomaly detection | Check predictions | 3-5 anomalies predicted | |
| T35 | Alert log | Check alert output | Alerts with severity levels generated | |
| T36 | Known anomaly recall | Check evaluation | At least 1 known anomaly detected | |

---

## Module 6 — MQTT IoT Simulator

| ID | Test Case | Steps | Expected Result | Outcome |
|----|-----------|-------|-----------------|---------|
| T37 | Start listener | Run listener.py | Connects and subscribes to ecam/machines/# | |
| T38 | Run simulator | Run simulator.py | Publishes 5 cycles × 6 readings | |
| T39 | Message receipt | Check listener output | 30 messages received | |
| T40 | DB storage | Check listener output | 30 events stored to DB | |
| T41 | Anomaly detection | Check listener output | Anomalies flagged and counted | |

---

## Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| KTP Associate | Uqba Othman | | |
| Academic Supervisor | | | |
| ECAM Engineering Lead | | | |