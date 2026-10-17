"""
Pytest Suite for Data Cleaning & Quarantine Logic
"""

import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "data_processing"))

from clean_customers import clean_customers
from clean_products import clean_products
from clean_orders import clean_orders

def test_customer_deduplication_and_missing_imputation():
    raw_data = pd.DataFrame([
        {"customer_id": "C1", "customer_name": "aarav sharma", "gender": "male", "age": 30, "city": None, "state": "KA"},
        {"customer_id": "C1", "customer_name": "aarav sharma", "gender": "male", "age": 30, "city": None, "state": "KA"},
        {"customer_id": "C2", "customer_name": None, "gender": "F", "age": -5, "city": "mumbai", "state": "Maharashtra"}
    ])
    
    audit_log = []
    cleaned = clean_customers(raw_data, audit_log)
    
    assert len(cleaned) == 2  # Duplicate removed
    assert cleaned.loc[0, "customer_name"] == "Aarav Sharma"
    assert cleaned.loc[1, "customer_name"] == "Unknown Customer"
    assert cleaned.loc[1, "age"] > 0  # Invalid age corrected
    assert cleaned.loc[0, "state_code"] == "KA"
    assert cleaned.loc[1, "state_code"] == "MH"

def test_missing_customer_recovery_and_quarantine():
    raw_orders = pd.DataFrame([
        {"order_id": "O1", "order_date": "2024-01-01", "customer_id": "C100", "product_id": "P1", "quantity": 2, "unit_price": 100, "discount": 0.0, "shipping_cost": 10, "payment_method": "UPI", "order_status": "Completed"},
        {"order_id": "O1", "order_date": "2024-01-01", "customer_id": None, "product_id": "P2", "quantity": 1, "unit_price": 200, "discount": 0.1, "shipping_cost": 10, "payment_method": "UPI", "order_status": "Completed"},
        {"order_id": "O2", "order_date": "2024-01-02", "customer_id": None, "product_id": "P3", "quantity": 1, "unit_price": 300, "discount": 0.0, "shipping_cost": 10, "payment_method": "UPI", "order_status": "Completed"}
    ])
    
    audit_log = []
    df_proc, df_quar = clean_orders(raw_orders, audit_log)
    
    assert len(df_proc) == 2
    # Order line 2 of O1 recovered C100 deterministically
    assert df_proc[df_proc["order_id"] == "O1"]["customer_id"].isnull().sum() == 0
    # O2 was unrecoverable and moved to quarantine
    assert len(df_quar) == 1
    assert df_quar.iloc[0]["order_id"] == "O2"
