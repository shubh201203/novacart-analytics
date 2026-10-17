"""
NovaCart Data Cleaning Module — Customers Table
Deduplicates, standardizes casing, handles missing values, normalizes state codes/names,
and corrects outlier age values with full audit logging.
"""

import pandas as pd
import numpy as np

STATE_MAP = {
    "KA": ("Karnataka", "KA"), "KARNATAKA": ("Karnataka", "KA"),
    "TG": ("Telangana", "TG"), "TELANGANA": ("Telangana", "TG"),
    "TN": ("Tamil Nadu", "TN"), "TAMIL NADU": ("Tamil Nadu", "TN"),
    "KL": ("Kerala", "KL"), "KERALA": ("Kerala", "KL"),
    "AP": ("Andhra Pradesh", "AP"), "ANDHRA PRADESH": ("Andhra Pradesh", "AP"),
    "MH": ("Maharashtra", "MH"), "MAHARASHTRA": ("Maharashtra", "MH"),
    "GJ": ("Gujarat", "GJ"), "GUJARAT": ("Gujarat", "GJ"),
    "RJ": ("Rajasthan", "RJ"), "RAJASTHAN": ("Rajasthan", "RJ"),
    "DL": ("Delhi", "DL"), "DELHI": ("Delhi", "DL"),
    "UP": ("Uttar Pradesh", "UP"), "UTTAR PRADESH": ("Uttar Pradesh", "UP"),
    "PB": ("Punjab", "PB"), "PUNJAB": ("Punjab", "PB"),
    "HR": ("Haryana", "HR"), "HARYANA": ("Haryana", "HR"),
    "WB": ("West Bengal", "WB"), "WEST BENGAL": ("West Bengal", "WB"),
    "OD": ("Odisha", "OD"), "ODISHA": ("Odisha", "OD"),
    "BR": ("Bihar", "BR"), "BIHAR": ("Bihar", "BR"),
    "JH": ("Jharkhand", "JH"), "JHARKHAND": ("Jharkhand", "JH"),
    "MP": ("Madhya Pradesh", "MP"), "MADHYA PRADESH": ("Madhya Pradesh", "MP"),
    "AS": ("Assam", "AS"), "ASSAM": ("Assam", "AS")
}

def clean_customers(df_raw, audit_log=None):
    df = df_raw.copy()
    raw_count = len(df)
    
    # 1. Deduplication
    dupes_count = df.duplicated().sum()
    if dupes_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "customers", "field_name": "all_fields",
                "issue_type": "duplicate_rows", "action_taken": "drop_duplicates",
                "records_affected": dupes_count, "notes": "Removed identical duplicate customer records."
            })
            
    # 2. Customer Name Casing & Missing Handling
    missing_names = df["customer_name"].isnull().sum()
    if missing_names > 0:
        df["customer_name"] = df["customer_name"].fillna("Unknown Customer")
        if audit_log is not None:
            audit_log.append({
                "table_name": "customers", "field_name": "customer_name",
                "issue_type": "missing_value", "action_taken": "fillna('Unknown Customer')",
                "records_affected": missing_names, "notes": "Imputed missing customer names."
            })
            
    # Normalize name casing (Title Case)
    df["customer_name"] = df["customer_name"].astype(str).str.title()
    
    # 3. Missing City Handling
    missing_cities = df["city"].isnull().sum()
    if missing_cities > 0:
        df["city"] = df["city"].fillna("Unknown City")
        if audit_log is not None:
            audit_log.append({
                "table_name": "customers", "field_name": "city",
                "issue_type": "missing_value", "action_taken": "fillna('Unknown City')",
                "records_affected": missing_cities, "notes": "Imputed missing customer city names."
            })
    df["city"] = df["city"].astype(str).str.title()

    # 4. Gender Standardization
    def normalize_gender(g):
        if pd.isnull(g):
            return "Other"
        g_str = str(g).strip().upper()
        if g_str in ["MALE", "M"]:
            return "Male"
        elif g_str in ["FEMALE", "F"]:
            return "Female"
        else:
            return "Non-binary"
            
    df["gender"] = df["gender"].apply(normalize_gender)
    
    # 5. Outlier Age Handling (Replace invalid age <= 0 or > 100 with median age ~34)
    invalid_ages = ((df["age"] <= 0) | (df["age"] > 100)).sum()
    if invalid_ages > 0:
        valid_median_age = int(df[(df["age"] > 0) & (df["age"] <= 100)]["age"].median())
        df.loc[(df["age"] <= 0) | (df["age"] > 100), "age"] = valid_median_age
        if audit_log is not None:
            audit_log.append({
                "table_name": "customers", "field_name": "age",
                "issue_type": "outlier_value", "action_taken": f"replace_with_median({valid_median_age})",
                "records_affected": invalid_ages, "notes": f"Replaced invalid age values with median age {valid_median_age}."
            })
            
    # 6. State & Region Standardization
    def standardize_state(st):
        if pd.isnull(st):
            return "Unknown State", "UN"
        st_clean = str(st).strip().upper()
        if st_clean in STATE_MAP:
            return STATE_MAP[st_clean][0], STATE_MAP[st_clean][1]
        return str(st).title(), str(st).upper()[:2]
        
    state_results = df["state"].apply(standardize_state)
    df["state_name"] = [r[0] for r in state_results]
    df["state_code"] = [r[1] for r in state_results]
    df["state"] = df["state_code"]  # Standardize primary state column to state code
    
    print(f"Cleaned customers: {raw_count} raw -> {len(df)} processed (dupes removed: {dupes_count}, missing names filled: {missing_names})")
    return df
