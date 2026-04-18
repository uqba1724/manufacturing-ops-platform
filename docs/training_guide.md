# Training Guide — ECAM Manufacturing Operations Platform
**Version:** 1.0  
**Date:** April 2026  
**Author:** Uqba Othman

---

## Role-Based Usage Guide

This guide provides instructions for three user roles:
- **Production Operator** — monitors daily output and machine status
- **Estimator** — processes RFQ documents and generates quotations
- **Production Manager** — reviews KPIs and makes operational decisions

---

## Role 1 — Production Operator

### What you use: KPI Dashboard

**Daily tasks:**
1. Open the dashboard at http://localhost:8501
2. Check machine status — all machines should show "running"
3. Check plan attainment — should be above 85% by end of shift
4. Check downtime log — note any new entries and reasons
5. Report any machine showing "fault" status to maintenance immediately

**What the colours mean:**
- Green machine status = running normally
- Yellow = idle (not producing but no fault)
- Red = fault (requires attention)

**What to do if plan attainment is low:**
- Check which orders are behind in the Production Orders table
- Report to shift manager with order code and completion percentage

---

## Role 2 — Estimator

### What you use: RFQ Parser

**When a new RFQ arrives:**
1. Open `src/rfq_parser/sample_rfqs.py`
2. Add the RFQ text as a new entry in the RFQ_SAMPLES list
3. Run: `python src/rfq_parser/parser.py`
4. Check the output:
   - Is confidence "high"? If "low", the RFQ is unclear — contact customer
   - Are there missing fields? If yes, request clarification before quoting
   - Review the BOM items — do the materials and processes look correct?
   - Review the cost estimate — apply any known adjustments
5. Issue quotation based on validated output

**Important:** The cost estimate is a starting point only. Always review 
material weights, machining hours, and treatment costs against your 
experience before issuing a formal quote.

---

## Role 3 — Production Manager

### What you use: KPI Dashboard + API

**Daily review (5 minutes):**
1. Open dashboard at http://localhost:8501
2. Check the five KPI cards at the top
3. Review the Production Orders table — identify any at risk of missing deadline
4. Check the Downtime Analysis chart — identify recurring reasons
5. Note any machines in fault status

**Weekly review (15 minutes):**
1. Run the data pipeline and review the validation report
2. Run the predictive maintenance scan and review alerts
3. Review plan attainment trend — is it improving or declining?
4. Identify top downtime reasons and assign corrective actions

**Using the API for custom queries:**
Open https://manufacturing-ops-platform.onrender.com/docs
You can query any data directly using the Swagger interface without 
needing to write code.

---

## Frequently Asked Questions

**Q: The dashboard shows no data**  
A: Check that the database exists at `data/manufacturing.db`. 
Run `python src/database/init_db.py` then `python src/database/seed_data.py`.

**Q: The API is slow to respond**  
A: The free hosting tier sleeps after inactivity. Wait 60 seconds and retry.

**Q: The RFQ parser returns low confidence**  
A: The RFQ document is unclear or missing key fields. 
Contact the customer for clarification before proceeding.

**Q: A machine shows fault status but maintenance says it is fine**  
A: Update the machine status in the database. Contact the KTP Associate 
to update the record.

**Q: I want to add a new machine to the system**  
A: Contact the KTP Associate. Adding a machine requires a database update 
and is not currently self-service.