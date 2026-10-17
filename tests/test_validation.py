"""
Pytest Suite for Post-Cleaning Validation & Referential Integrity
"""

import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "data_processing"))

from validate_data import validate_processed_data

def test_validation_suite_pass():
    cust = pd.DataFrame([{"customer_id": "C1"}])
    prod = pd.DataFrame([{"product_id": "P1"}])
    ord_df = pd.DataFrame([{
        "order_id": "O1", "customer_id": "C1", "product_id": "P1",
        "quantity": 1, "unit_price": 100.0, "discount": 0.0, "shipping_cost": 10.0,
        "gross_sales": 100.0, "discount_amount": 0.0, "net_revenue": 100.0,
        "product_cost": 50.0, "profit": 40.0
    }])
    ret = pd.DataFrame([{"order_id": "O1", "quantity_returned": 1}])
    pay = pd.DataFrame([{"order_id": "O1", "payment_status": "Completed"}])
    
    assert validate_processed_data(cust, prod, ord_df, ret, pay) is True

def test_validation_orphan_referential_failure():
    cust = pd.DataFrame([{"customer_id": "C1"}])
    prod = pd.DataFrame([{"product_id": "P1"}])
    ord_df = pd.DataFrame([{
        "order_id": "O1", "customer_id": "C999", "product_id": "P1",  # Invalid C999
        "quantity": 1, "unit_price": 100.0, "discount": 0.0, "shipping_cost": 10.0,
        "gross_sales": 100.0, "discount_amount": 0.0, "net_revenue": 100.0,
        "product_cost": 50.0, "profit": 40.0
    }])
    ret = pd.DataFrame([{"order_id": "O1", "quantity_returned": 1}])
    pay = pd.DataFrame([{"order_id": "O1", "payment_status": "Completed"}])
    
    with pytest.raises(ValueError):
        validate_processed_data(cust, prod, ord_df, ret, pay)
