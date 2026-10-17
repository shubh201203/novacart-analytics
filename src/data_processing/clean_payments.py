"""
NovaCart Data Cleaning Module — Payments Table
Implements deduplication, referential integrity validation against processed orders,
and deterministic payment_status imputation based on order lifecycle states.
"""

import pandas as pd

def clean_payments(df_raw_payments, df_processed_orders, audit_log=None):
    df = df_raw_payments.copy()
    raw_count = len(df)

    # 1. Deduplication
    dupes_count = df.duplicated().sum()
    if dupes_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "payments", "field_name": "all_fields",
                "issue_type": "duplicate_payments", "action_taken": "drop_duplicates",
                "records_affected": dupes_count, "notes": "Removed duplicate payment records."
            })

    # 2. Referential Integrity Check
    valid_order_ids = set(df_processed_orders["order_id"].dropna().unique())
    orphan_mask = ~df["order_id"].isin(valid_order_ids)
    orphan_count = orphan_mask.sum()

    if orphan_count > 0:
        df = df[~orphan_mask].reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "payments", "field_name": "order_id",
                "issue_type": "orphan_foreign_key", "action_taken": "remove_orphans",
                "records_affected": orphan_count, "notes": "Removed payment records referencing quarantined orders."
            })

    # 3. Deterministic Payment Status Imputation
    missing_status_mask = df["payment_status"].isnull()
    missing_status_count = missing_status_mask.sum()

    if missing_status_count > 0:
        order_status_map = df_processed_orders.groupby("order_id")["order_status"].first().to_dict()
        
        def impute_payment_status(row):
            if pd.notnull(row["payment_status"]):
                return row["payment_status"]
            o_id = row["order_id"]
            o_stat = order_status_map.get(o_id, "Completed")
            if o_stat == "Cancelled":
                return "Failed"
            elif o_stat == "Returned":
                return "Refunded"
            else:
                return "Completed"

        df["payment_status"] = df.apply(impute_payment_status, axis=1)
        if audit_log is not None:
            audit_log.append({
                "table_name": "payments", "field_name": "payment_status",
                "issue_type": "missing_payment_status", "action_taken": "order_lifecycle_imputation",
                "records_affected": missing_status_count, "notes": "Deterministically imputed missing payment_status based on order_status."
            })

    print(f"Cleaned payments: {raw_count} raw -> {len(df)} processed (imputed missing statuses: {missing_status_count})")
    return df
