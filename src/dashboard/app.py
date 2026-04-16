import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import Session

from src.database.db import SessionLocal
from src.database.models import (
    Machine, Job, ProductionOrder,
    DowntimeEvent, Defect, Quotation, BOMItem
)

# --- PAGE CONFIGURATION ---
# This must be the first Streamlit command in the script
st.set_page_config(
    page_title="ECAM Manufacturing Operations",
    page_icon="🏭",
    layout="wide"
)


def get_db():
    # Creates and returns a database session
    return SessionLocal()


def load_data():
    # Load all data from the database into pandas DataFrames.
    # DataFrames are tabular data structures — like spreadsheets in Python.
    # Streamlit and Plotly work natively with DataFrames.
    db = get_db()
    try:
        machines = pd.read_sql(db.query(Machine).statement, db.bind)
        jobs = pd.read_sql(db.query(Job).statement, db.bind)
        orders = pd.read_sql(db.query(ProductionOrder).statement, db.bind)
        downtime = pd.read_sql(db.query(DowntimeEvent).statement, db.bind)
        defects = pd.read_sql(db.query(Defect).statement, db.bind)
        quotations = pd.read_sql(db.query(Quotation).statement, db.bind)
        return machines, jobs, orders, downtime, defects, quotations
    finally:
        db.close()


# --- LOAD DATA ---
machines, jobs, orders, downtime, defects, quotations = load_data()

# --- HEADER ---
st.title("🏭 ECAM Manufacturing Operations Platform")
st.markdown("**Live operational dashboard — AI-enabled manufacturing visibility**")
st.divider()

# --- KPI SUMMARY ROW ---
# st.columns splits the page into equal-width columns side by side
st.subheader("Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate KPIs from the loaded DataFrames
machines_running = len(machines[machines["status"] == "running"])
machines_fault = len(machines[machines["status"] == "fault"])
total_downtime = downtime["duration_minutes"].sum()
total_defects = defects["defect_count"].sum()
total_planned = orders["quantity_planned"].sum()
total_completed = orders["quantity_completed"].sum()
plan_attainment = round((total_completed / total_planned * 100), 1) if total_planned > 0 else 0

# st.metric displays a number with a label — clean KPI card format
with col1:
    st.metric("Machines Running", f"{machines_running}/{len(machines)}")
with col2:
    st.metric("Machines in Fault", machines_fault)
with col3:
    st.metric("Plan Attainment", f"{plan_attainment}%")
with col4:
    st.metric("Total Downtime", f"{int(total_downtime)} mins")
with col5:
    st.metric("Total Defects", int(total_defects))

st.divider()

# --- MACHINE STATUS AND PRODUCTION ORDERS ---
# Two columns side by side
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Machine Status")

    # Colour-code the status column for readability
    def colour_status(val):
        colours = {
            "running": "background-color: #1a7a1a; color: white",
            "idle": "background-color: #7a7a1a; color: white",
            "fault": "background-color: #7a1a1a; color: white"
        }
        return colours.get(val, "")

    # Display only the relevant columns
    machine_display = machines[["machine_code", "name", "status", "location"]]
    st.dataframe(
        machine_display.style.applymap(colour_status, subset=["status"]),
        use_container_width=True,
        hide_index=True
    )

    # Pie chart of machine status distribution
    status_counts = machines["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig_status = px.pie(
        status_counts,
        values="count",
        names="status",
        title="Machine Status Distribution",
        color="status",
        color_discrete_map={
            "running": "#2ecc71",
            "idle": "#f39c12",
            "fault": "#e74c3c"
        }
    )
    st.plotly_chart(fig_status, use_container_width=True)


with col_right:
    st.subheader("Production Orders")

    # Calculate completion percentage for each order
    orders["completion_pct"] = (
        orders["quantity_completed"] / orders["quantity_planned"] * 100
    ).round(1)

    order_display = orders[[
        "order_code", "customer_name",
        "quantity_planned", "quantity_completed", "completion_pct"
    ]].copy()
    order_display.columns = [
        "Order", "Customer", "Planned", "Completed", "% Complete"
    ]

    st.dataframe(order_display, use_container_width=True, hide_index=True)

    # Horizontal bar chart of order completion
    fig_orders = px.bar(
        orders,
        x="completion_pct",
        y="order_code",
        orientation="h",
        title="Order Completion (%)",
        labels={"completion_pct": "% Complete", "order_code": "Order"},
        color="completion_pct",
        color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"],
        range_x=[0, 100]
    )
    st.plotly_chart(fig_orders, use_container_width=True)

st.divider()

# --- DOWNTIME ANALYSIS ---
st.subheader("Downtime Analysis")
col_d1, col_d2 = st.columns(2)

with col_d1:
    # Bar chart: total downtime by reason
    downtime_by_reason = downtime.groupby("reason")["duration_minutes"].sum().reset_index()
    downtime_by_reason.columns = ["Reason", "Total Minutes"]
    downtime_by_reason = downtime_by_reason.sort_values("Total Minutes", ascending=False)

    fig_downtime = px.bar(
        downtime_by_reason,
        x="Reason",
        y="Total Minutes",
        title="Total Downtime by Reason (minutes)",
        color="Total Minutes",
        color_continuous_scale=["#f39c12", "#e74c3c"]
    )
    st.plotly_chart(fig_downtime, use_container_width=True)

with col_d2:
    # Downtime events table
    st.markdown("**Downtime Event Log**")
    downtime_display = downtime[[
        "reason", "duration_minutes", "event_time"
    ]].copy()
    downtime_display.columns = ["Reason", "Duration (mins)", "Time"]
    downtime_display = downtime_display.sort_values(
        "Time", ascending=False
    )
    st.dataframe(downtime_display, use_container_width=True, hide_index=True)

st.divider()

# --- QUOTATIONS ---
st.subheader("Quotations")
if not quotations.empty:
    quote_display = quotations[[
        "quote_code", "customer_name", "material",
        "quantity", "estimated_cost", "status"
    ]].copy()
    quote_display.columns = [
        "Quote", "Customer", "Material", "Qty", "Est. Cost (£)", "Status"
    ]
    st.dataframe(quote_display, use_container_width=True, hide_index=True)
else:
    st.info("No quotations found.")

st.divider()

# --- FOOTER ---
st.caption("ECAM Manufacturing Operations Platform | Built with FastAPI + SQLAlchemy + Streamlit")