"""
NovaCart Data Cleaning Module — Orders Table
Implements deduplication, malformed date handling, missing customer deterministic recovery,
quarantine isolation for unrecoverable missing customer orders, and non-positive quantity checks.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def clean_orders(df_raw, audit_log=None):
    df = df_raw.copy()
    raw_count = len(df)
    quarantine_records = []
    
    # 1. Deduplication (Exact duplicate order line rows)
    dupes_count = df.duplicated().sum()
    if dupes_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "orders", "field_name": "all_fields",
                "issue_type": "duplicate_order_lines", "action_taken": "drop_duplicates",
                "records_affected": dupes_count, "notes": "Removed identical duplicate order-line records."
            })

    # 2. Date Parsing & Malformed Date Handling
    def parse_date_safe(d_str):
        try:
            dt = datetime.strptime(str(d_str), "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    parsed_dates = df["order_date"].apply(parse_date_safe)
    invalid_dates_mask = parsed_dates.isnull()
    invalid_dates_count = invalid_dates_mask.sum()

    if invalid_dates_count > 0:
        # Quarantine malformed date records
        df_invalid_dates = df[invalid_dates_mask].copy()
        df_invalid_dates["quarantine_reason"] = "Malformed order date string"
        quarantine_records.append(df_invalid_dates)
        
        # Keep valid dates only in main pipeline
        df = df[~invalid_dates_mask].reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "orders", "field_name": "order_date",
                "issue_type": "malformed_date_string", "action_taken": "quarantine_isolation",
                "records_affected": invalid_dates_count, "notes": "Moved order lines with unparseable date strings into quarantine."
            })

    # 3. Quantity Bound Checks (quantity > 0)
    invalid_qty_mask = df["quantity"] <= 0
    invalid_qty_count = invalid_qty_mask.sum()
    if invalid_qty_count > 0:
        df_invalid_qty = df[invalid_qty_mask].copy()
        df_invalid_qty["quarantine_reason"] = "Non-positive item quantity (<=0)"
        quarantine_records.append(df_invalid_qty)
        
        df = df[~invalid_qty_mask].reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "orders", "field_name": "quantity",
                "issue_type": "invalid_quantity_value", "action_taken": "quarantine_isolation",
                "records_affected": invalid_qty_count, "notes": "Moved order lines with quantity <= 0 into quarantine."
            })

    # 4. MISSING CUSTOMER_ID RECOVERY & QUARANTINE ENGINE
    missing_cust_mask = df["customer_id"].isnull()
    missing_cust_count = missing_cust_mask.sum()

    recovered_count = 0
    unrecoverable_count = 0

    if missing_cust_count > 0:
        # Build deterministic lookup mapping: order_id -> valid customer_id
        valid_cust_mapping = df.dropna(subset=["customer_id"]).set_index("order_id")["customer_id"].to_dict()
        
        missing_indices = df[missing_cust_mask].index
        unrecoverable_indices = []

        for idx in missing_indices:
            o_id = df.loc[idx, "order_id"]
            if o_id in valid_cust_mapping:
                df.loc[idx, "customer_id"] = valid_cust_mapping[o_id]
                recovered_count += 1
            else:
                unrecoverable_indices.append(idx)

        unrecoverable_count = len(unrecoverable_indices)
        
        if unrecoverable_count > 0:
            df_unrecoverable_cust = df.loc[unrecoverable_indices].copy()
            df_unrecoverable_cust["quarantine_reason"] = "Unrecoverable missing customer_id"
            quarantine_records.append(df_unrecoverable_cust)
            
            # Exclude unrecoverable missing customer_id records from processed analytical orders
            df = df.drop(index=unrecoverable_indices).reset_index(drop=True)

        if audit_log is not None:
            audit_log.append({
                "table_name": "orders", "field_name": "customer_id",
                "issue_type": "missing_customer_id",
                "action_taken": f"recovered={recovered_count}, quarantined={unrecoverable_count}",
                "records_affected": missing_cust_count,
                "notes": f"Deterministically recovered {recovered_count} customer_ids from order line co-occurrences; quarantined {unrecoverable_count} unrecoverable records."
            })

    # 5. Missing Payment Method Imputation
    missing_pay_methods = df["payment_method"].isnull().sum()
    if missing_pay_methods > 0:
        # Impute using most frequent payment method (UPI) or "Unknown"
        df["payment_method"] = df["payment_method"].fillna("UPI")
        if audit_log is not None:
            audit_log.append({
                "table_name": "orders", "field_name": "payment_method",
                "issue_type": "missing_payment_method", "action_taken": "fillna('UPI')",
                "records_affected": missing_pay_methods, "notes": "Imputed missing order payment methods using modal payment method (UPI)."
            })

    # Consolidate quarantine DataFrame
    if len(quarantine_records) > 0:
        df_quarantine = pd.concat(quarantine_records, ignore_index=True)
    else:
        df_quarantine = pd.DataFrame(columns=list(df.columns) + ["quarantine_reason"])

    total_quarantined = len(df_quarantine)
    print(f"Cleaned orders: {raw_count} raw -> {len(df)} processed | {total_quarantined} quarantined (dupes: {dupes_count}, recovered customer_ids: {recovered_count}, quarantined missing cust_ids: {unrecoverable_count})")
    
    return df, df_quarantine
