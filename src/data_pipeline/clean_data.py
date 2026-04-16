import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime


# Validation rules — acceptable ranges for each numeric column
VALIDATION_RULES = {
    "temperature_c": (40.0, 100.0),
    "spindle_speed_rpm": (2000, 4000),
    "cycle_time_seconds": (20.0, 180.0),
    "quantity_produced": (0, 200),
    "defect_count": (0, 50),
    "downtime_minutes": (0.0, 120.0)
}


def clean_production_data(input_path: str, output_path: str) -> dict:
    """
    Cleans a raw production CSV file and writes a cleaned version.
    Returns a validation report as a dictionary.
    """
    print(f"Loading raw data from: {input_path}")
    df = pd.read_csv(input_path)

    report = {
        "input_file": input_path,
        "output_file": output_path,
        "timestamp": datetime.utcnow().isoformat(),
        "rows_input": len(df),
        "issues_found": {},
        "actions_taken": {}
    }

    # --- STEP 1: REMOVE DUPLICATES ---
    n_duplicates = df.duplicated().sum()
    df = df.drop_duplicates()
    report["issues_found"]["duplicate_rows"] = int(n_duplicates)
    report["actions_taken"]["duplicates_removed"] = int(n_duplicates)
    print(f"  Duplicates removed: {n_duplicates}")

    # --- STEP 2: STANDARDISE SHIFT COLUMN ---
    # Convert all shift values to lowercase for consistency
    # "MORNING", "Morning", "morning" all become "morning"
    df["shift"] = df["shift"].str.lower().str.strip()
    unique_shifts_before = ["morning", "afternoon", "night", "MORNING", "Night"]
    report["actions_taken"]["shift_standardised"] = "converted to lowercase"
    print(f"  Shift column standardised to lowercase")

    # --- STEP 3: HANDLE MISSING VALUES ---
    # operator_id: fill with "UNKNOWN" — we know a record exists,
    # we just don't know who made it
    missing_operator = df["operator_id"].isna().sum()
    df["operator_id"] = df["operator_id"].fillna("UNKNOWN")
    report["issues_found"]["missing_operator_id"] = int(missing_operator)
    report["actions_taken"]["missing_operator_filled"] = "UNKNOWN"

    # cycle_time_seconds: fill with the median of the column
    # Median is better than mean here because outliers skew the mean
    missing_cycle = df["cycle_time_seconds"].isna().sum()
    median_cycle = df["cycle_time_seconds"].median()
    df["cycle_time_seconds"] = df["cycle_time_seconds"].fillna(median_cycle)
    report["issues_found"]["missing_cycle_time"] = int(missing_cycle)
    report["actions_taken"]["missing_cycle_time_filled"] = f"median ({median_cycle:.2f}s)"

    # temperature_c: fill missing with median before range check
    missing_temp = df["temperature_c"].isna().sum()
    median_temp = df["temperature_c"][
        df["temperature_c"].between(40, 100)
    ].median()
    df["temperature_c"] = df["temperature_c"].fillna(median_temp)
    report["issues_found"]["missing_temperature"] = int(missing_temp)
    report["actions_taken"]["missing_temperature_filled"] = f"median ({median_temp:.2f}°C)"

    print(f"  Missing values handled")

    # --- STEP 4: FIX OUT-OF-RANGE VALUES ---
    for column, (min_val, max_val) in VALIDATION_RULES.items():
        if column not in df.columns:
            continue

        # Count values outside the valid range
        out_of_range = ((df[column] < min_val) | (df[column] > max_val)).sum()

        if out_of_range > 0:
            # Replace out-of-range values with the column median
            # calculated only from valid in-range values
            valid_median = df[column][
                df[column].between(min_val, max_val)
            ].median()

            df.loc[
                (df[column] < min_val) | (df[column] > max_val),
                column
            ] = valid_median

            report["issues_found"][f"{column}_out_of_range"] = int(out_of_range)
            report["actions_taken"][f"{column}_replaced_with_median"] = f"{valid_median:.2f}"
            print(f"  {column}: {out_of_range} out-of-range values replaced with median ({valid_median:.2f})")

    # --- STEP 5: FIX DATA TYPES ---
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["record_id"] = df["record_id"].astype(int)
    df["quantity_produced"] = df["quantity_produced"].astype(int)
    df["defect_count"] = df["defect_count"].astype(int)
    df["spindle_speed_rpm"] = df["spindle_speed_rpm"].astype(int)
    report["actions_taken"]["data_types_enforced"] = "timestamp, integers corrected"
    print(f"  Data types enforced")

    # --- STEP 6: ADD DERIVED COLUMNS ---
    # defect_rate = defects per unit produced
    # Useful KPI for quality monitoring
    df["defect_rate"] = (
        df["defect_count"] / df["quantity_produced"].replace(0, np.nan)
    ).round(4)

    # efficiency_flag: flag rows where cycle time exceeds 1.5x the median
    # These may indicate process problems worth investigating
    cycle_median = df["cycle_time_seconds"].median()
    df["efficiency_flag"] = (df["cycle_time_seconds"] > cycle_median * 1.5).astype(int)
    flagged = df["efficiency_flag"].sum()
    report["actions_taken"]["derived_columns_added"] = "defect_rate, efficiency_flag"
    report["issues_found"]["efficiency_flags"] = int(flagged)
    print(f"  Derived columns added (defect_rate, efficiency_flag)")
    print(f"  Efficiency flags raised: {flagged}")

    # --- FINAL REPORT ---
    report["rows_output"] = len(df)
    report["rows_removed"] = report["rows_input"] - report["rows_output"]

    # Save cleaned data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nCleaned data saved to: {output_path}")
    print(f"Rows: {report['rows_input']} input → {report['rows_output']} output")

    return report


if __name__ == "__main__":
    report = clean_production_data(
        input_path="data/raw/production_raw.csv",
        output_path="data/cleaned/production_cleaned.csv"
    )

    print("\n--- VALIDATION REPORT ---")
    print(f"Input rows:  {report['rows_input']}")
    print(f"Output rows: {report['rows_output']}")
    print(f"Rows removed: {report['rows_removed']}")
    print("\nIssues found:")
    for k, v in report["issues_found"].items():
        print(f"  {k}: {v}")
    print("\nActions taken:")
    for k, v in report["actions_taken"].items():
        print(f"  {k}: {v}")