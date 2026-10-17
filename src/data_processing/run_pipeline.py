"""
NovaCart Master Data Processing Pipeline
Orchestrates Phase 2 raw ingestion, cleaning, deterministic recovery, quarantine isolation,
feature engineering, post-cleaning validation, data reconciliation, and audit reporting.
"""

import os
import pandas as pd
from clean_customers import clean_customers
from clean_products import clean_products
from clean_orders import clean_orders
from clean_returns import clean_returns
from clean_payments import clean_payments
from feature_engineering import generate_features
from validate_data import validate_processed_data
from data_quality_report import generate_quality_report

def run_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    quarantine_dir = os.path.join(processed_dir, "quarantine")
    reports_dir = os.path.join(base_dir, "reports")
    
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(quarantine_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    audit_log = []
    summary_stats = []
    
    print("=" * 80)
    print("STARTING NOVACART DATA CLEANING & FEATURE ENGINEERING PIPELINE")
    print("=" * 80)
    
    # 1. Load Raw Tables
    df_raw_cust = pd.read_csv(os.path.join(raw_dir, "customers_raw.csv"))
    df_raw_prod = pd.read_csv(os.path.join(raw_dir, "products_raw.csv"))
    df_raw_ord = pd.read_csv(os.path.join(raw_dir, "orders_raw.csv"))
    df_raw_ret = pd.read_csv(os.path.join(raw_dir, "returns_raw.csv"))
    df_raw_pay = pd.read_csv(os.path.join(raw_dir, "payments_raw.csv"))
    
    # 2. Clean Customers
    df_cust = clean_customers(df_raw_cust, audit_log)
    summary_stats.append({
        "Table": "Customers",
        "Raw Rows": len(df_raw_cust),
        "Processed Rows": len(df_cust),
        "Quarantined Rows": 0,
        "Duplicates Removed": len(df_raw_cust) - len(df_cust),
        "Missing Resolved": df_raw_cust["customer_name"].isnull().sum() + df_raw_cust["city"].isnull().sum()
    })
    
    # 3. Clean Products
    df_prod = clean_products(df_raw_prod, audit_log)
    summary_stats.append({
        "Table": "Products",
        "Raw Rows": len(df_raw_prod),
        "Processed Rows": len(df_prod),
        "Quarantined Rows": 0,
        "Duplicates Removed": len(df_raw_prod) - len(df_prod),
        "Missing Resolved": 0
    })
    
    # 4. Clean Orders (Recovery + Quarantine Engine)
    df_ord, df_ord_quarantine = clean_orders(df_raw_ord, audit_log)
    summary_stats.append({
        "Table": "Orders",
        "Raw Rows": len(df_raw_ord),
        "Processed Rows": len(df_ord),
        "Quarantined Rows": len(df_ord_quarantine),
        "Duplicates Removed": df_raw_ord.duplicated().sum(),
        "Missing Resolved": df_raw_ord["payment_method"].isnull().sum()
    })
    
    # 5. Clean Returns
    df_ret, df_ret_quarantine = clean_returns(df_raw_ret, df_ord, audit_log)
    summary_stats.append({
        "Table": "Returns",
        "Raw Rows": len(df_raw_ret),
        "Processed Rows": len(df_ret),
        "Quarantined Rows": len(df_ret_quarantine),
        "Duplicates Removed": df_raw_ret.duplicated().sum(),
        "Missing Resolved": 0
    })
    
    # 6. Clean Payments
    df_pay = clean_payments(df_raw_pay, df_ord, audit_log)
    summary_stats.append({
        "Table": "Payments",
        "Raw Rows": len(df_raw_pay),
        "Processed Rows": len(df_pay),
        "Quarantined Rows": 0,
        "Duplicates Removed": df_raw_pay.duplicated().sum(),
        "Missing Resolved": df_raw_pay["payment_status"].isnull().sum()
    })
    
    # 7. Feature Engineering
    df_ord_engineered = generate_features(df_ord, df_prod)
    
    # 8. Post-Cleaning Validation & Reconciliation
    validate_processed_data(df_cust, df_prod, df_ord_engineered, df_ret, df_pay)
    
    # 9. Save Processed Datasets
    df_cust.to_csv(os.path.join(processed_dir, "customers_processed.csv"), index=False)
    df_prod.to_csv(os.path.join(processed_dir, "products_processed.csv"), index=False)
    df_ord_engineered.to_csv(os.path.join(processed_dir, "orders_processed.csv"), index=False)
    df_ret.to_csv(os.path.join(processed_dir, "returns_processed.csv"), index=False)
    df_pay.to_csv(os.path.join(processed_dir, "payments_processed.csv"), index=False)
    
    # Save Quarantined Datasets
    df_ord_quarantine.to_csv(os.path.join(quarantine_dir, "orders_quarantine.csv"), index=False)
    df_ret_quarantine.to_csv(os.path.join(quarantine_dir, "returns_quarantine.csv"), index=False)
    
    # 10. Generate Quality & Audit Report
    generate_quality_report(summary_stats, audit_log, reports_dir)
    
    print("\n" + "=" * 80)
    print("PHASE 2 PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    run_pipeline()
