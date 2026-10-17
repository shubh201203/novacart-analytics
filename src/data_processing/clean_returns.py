"""
NovaCart Data Cleaning Module — Returns Table
Validates referential integrity against processed orders, date logic (return_date >= order_date),
and return quantity constraints (0 < returned <= purchased quantity).
Quarantines invalid returns.
"""

import pandas as pd
from datetime import datetime

def clean_returns(df_raw_returns, df_processed_orders, audit_log=None):
    df = df_raw_returns.copy()
    raw_count = len(df)
    quarantine_records = []

    # 1. Deduplication
    dupes_count = df.duplicated().sum()
    if dupes_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "returns", "field_name": "all_fields",
                "issue_type": "duplicate_returns", "action_taken": "drop_duplicates",
                "records_affected": dupes_count, "notes": "Removed duplicate return rows."
            })

    # 2. Referential Integrity Check (order_id must exist in processed orders)
    valid_order_ids = set(df_processed_orders["order_id"].dropna().unique())
    orphan_returns_mask = ~df["order_id"].isin(valid_order_ids)
    orphan_count = orphan_returns_mask.sum()

    if orphan_count > 0:
        df_orphan_returns = df[orphan_returns_mask].copy()
        df_orphan_returns["quarantine_reason"] = "Orphan return record (order_id not in processed orders)"
        quarantine_records.append(df_orphan_returns)
        
        df = df[~orphan_returns_mask].reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "returns", "field_name": "order_id",
                "issue_type": "orphan_foreign_key", "action_taken": "quarantine_isolation",
                "records_affected": orphan_count, "notes": "Quarantined return records referencing non-existent orders."
            })

    # 3. Date Logic Check (return_date >= order_date)
    # Merge order dates to validate
    order_dates = df_processed_orders.groupby("order_id")["order_date"].min().to_dict()
    
    def check_return_date(row):
        o_id = row["order_id"]
        r_date_str = str(row["return_date"])
        if o_id not in order_dates:
            return False
        o_date_str = str(order_dates[o_id])
        try:
            r_dt = datetime.strptime(r_date_str, "%Y-%m-%d")
            o_dt = datetime.strptime(o_date_str, "%Y-%m-%d")
            return r_dt >= o_dt
        except ValueError:
            return False

    valid_date_mask = df.apply(check_return_date, axis=1)
    invalid_date_count = (~valid_date_mask).sum()

    if invalid_date_count > 0:
        df_invalid_dates = df[~valid_date_mask].copy()
        df_invalid_dates["quarantine_reason"] = "Return date precedes order date or malformed"
        quarantine_records.append(df_invalid_dates)
        
        df = df[valid_date_mask].reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "returns", "field_name": "return_date",
                "issue_type": "invalid_date_logic", "action_taken": "quarantine_isolation",
                "records_affected": invalid_date_count, "notes": "Quarantined returns where return_date < order_date."
            })

    # 4. Quantity Bound Check (quantity_returned > 0)
    invalid_qty_mask = df["quantity_returned"] <= 0
    invalid_qty_count = invalid_qty_mask.sum()

    if invalid_qty_count > 0:
        df_invalid_qty = df[invalid_qty_mask].copy()
        df_invalid_qty["quarantine_reason"] = "Non-positive returned quantity (<= 0)"
        quarantine_records.append(df_invalid_qty)
        
        df = df[~invalid_qty_mask].reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "returns", "field_name": "quantity_returned",
                "issue_type": "invalid_quantity", "action_taken": "quarantine_isolation",
                "records_affected": invalid_qty_count, "notes": "Quarantined returns with non-positive returned quantities."
            })

    if len(quarantine_records) > 0:
        df_quarantine = pd.concat(quarantine_records, ignore_index=True)
    else:
        df_quarantine = pd.DataFrame(columns=list(df.columns) + ["quarantine_reason"])

    total_quarantined = len(df_quarantine)
    print(f"Cleaned returns: {raw_count} raw -> {len(df)} processed | {total_quarantined} quarantined")
    
    return df, df_quarantine
