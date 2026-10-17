"""
NovaCart Data Warehouse Validation & Reconciliation Suite
Validates primary keys, foreign key integrity (0 orphans), grain adherence,
and performs 100% financial metric reconciliation against processed CSV files.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(dotenv_path)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.database.load_dw import get_db_connection


def validate_data_warehouse():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    proc_dir = os.path.join(base_dir, "data", "processed")
    
    # Load processed CSVs for reconciliation
    df_proc_ord = pd.read_csv(os.path.join(proc_dir, "orders_processed.csv"))
    df_proc_cust = pd.read_csv(os.path.join(proc_dir, "customers_processed.csv"))
    df_proc_prod = pd.read_csv(os.path.join(proc_dir, "products_processed.csv"))
    
    print("=" * 80)
    print("NOVACART PHASE 3: DATA WAREHOUSE RECONCILIATION & INTEGRITY CHECKS")
    print("=" * 80)
    
    conn, engine_type = get_db_connection()
    
    def query_val(sql):
        if engine_type == "postgresql":
            cur = conn.cursor()
            cur.execute(sql)
            res = cur.fetchone()[0]
            cur.close()
            return res
        else:
            return conn.execute(sql).fetchone()[0]
    
    errors = []

    
    # 1. Row Count Checks
    fs_count = query_val("SELECT COUNT(*) FROM fact_sales;")
    fr_count = query_val("SELECT COUNT(*) FROM fact_returns;")
    fp_count = query_val("SELECT COUNT(*) FROM fact_payments;")
    
    dc_count = query_val("SELECT COUNT(*) FROM dim_customer;")
    dp_count = query_val("SELECT COUNT(*) FROM dim_product;")
    dl_count = query_val("SELECT COUNT(*) FROM dim_location;")
    dd_count = query_val("SELECT COUNT(*) FROM dim_date;")
    
    print(f"Fact Sales Grain Count    : {fs_count:,} rows (Expected: {len(df_proc_ord):,})")
    print(f"Fact Returns Count        : {fr_count:,} rows")
    print(f"Fact Payments Count       : {fp_count:,} rows")
    print(f"Dim Customer Count        : {dc_count:,} rows (Expected: {len(df_proc_cust):,})")
    print(f"Dim Product Count         : {dp_count:,} rows (Expected: {len(df_proc_prod):,})")
    print(f"Dim Location Count        : {dl_count:,} rows")
    print(f"Dim Date Count            : {dd_count:,} rows (2022-2026 Full Calendar)")
    
    if fs_count != len(df_proc_ord):
        errors.append(f"Row Count Mismatch: fact_sales has {fs_count} rows, CSV has {len(df_proc_ord)}.")
        
    # 2. PK Uniqueness Checks
    pk_checks = [
        ("dim_customer", "customer_key"),
        ("dim_product", "product_key"),
        ("dim_location", "location_key"),
        ("dim_payment", "payment_key"),
        ("dim_date", "date_key"),
        ("fact_sales", "sales_key"),
        ("fact_returns", "return_key"),
        ("fact_payments", "payment_trans_key")
    ]
    
    for tbl, pk_col in pk_checks:
        dupes = query_val(f"SELECT COUNT(*) - COUNT(DISTINCT {pk_col}) FROM {tbl};")
        if dupes > 0:
            errors.append(f"PK Uniqueness Violation: {tbl}.{pk_col} has {dupes} duplicate keys.")
            
    # 3. Foreign Key Integrity (0 Orphans)
    orphan_cust = query_val("SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_customer c ON f.customer_key = c.customer_key WHERE c.customer_key IS NULL;")
    orphan_prod = query_val("SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_product p ON f.product_key = p.product_key WHERE p.product_key IS NULL;")
    orphan_date = query_val("SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_date d ON f.date_key = d.date_key WHERE d.date_key IS NULL;")
    orphan_loc  = query_val("SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_location l ON f.location_key = l.location_key WHERE l.location_key IS NULL;")
    
    print(f"\nFK Integrity - Customer Orphans: {orphan_cust}")
    print(f"FK Integrity - Product Orphans : {orphan_prod}")
    print(f"FK Integrity - Date Orphans    : {orphan_date}")
    print(f"FK Integrity - Location Orphans: {orphan_loc}")
    
    if orphan_cust + orphan_prod + orphan_date + orphan_loc > 0:
        errors.append("FK Integrity Violation: Orphan fact records detected!")

    # 4. Financial Metric Reconciliation
    dw_revenue = float(query_val("SELECT ROUND(SUM(net_revenue), 2) FROM fact_sales;"))
    csv_revenue = round(df_proc_ord["net_revenue"].sum(), 2)
    
    dw_profit = float(query_val("SELECT ROUND(SUM(profit), 2) FROM fact_sales;"))
    csv_profit = round(df_proc_ord["profit"].sum(), 2)
    
    dw_qty = int(query_val("SELECT SUM(quantity) FROM fact_sales;"))
    csv_qty = df_proc_ord["quantity"].sum()


    print("\n--- FINANCIAL RECONCILIATION ---")
    print(f"Net Revenue -> DW: INR {dw_revenue:,.2f} | CSV: INR {csv_revenue:,.2f} | Diff: INR {abs(dw_revenue - csv_revenue):.2f}")
    print(f"Profit      -> DW: INR {dw_profit:,.2f} | CSV: INR {csv_profit:,.2f} | Diff: INR {abs(dw_profit - csv_profit):.2f}")
    print(f"Quantity    -> DW: {dw_qty:,} | CSV: {csv_qty:,} | Diff: {abs(dw_qty - csv_qty)}")
    
    if abs(dw_revenue - csv_revenue) > 0.05:
        errors.append(f"Revenue Reconciliation Failure: DW {dw_revenue} vs CSV {csv_revenue}")
    if abs(dw_profit - csv_profit) > 0.05:
        errors.append(f"Profit Reconciliation Failure: DW {dw_profit} vs CSV {csv_profit}")

    if len(errors) > 0:
        print("\nERRORS DETECTED DURING DW VALIDATION:")
        for e in errors:
            print(f"  - [FAIL] {e}")
        raise ValueError("Data Warehouse validation failed!")
    else:
        print("\n" + "=" * 80)
        print("ALL DATA WAREHOUSE INTEGRITY & RECONCILIATION CHECKS PASSED CLEANLY")
        print("=" * 80)
        return True

if __name__ == "__main__":
    validate_data_warehouse()
