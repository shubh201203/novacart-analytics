"""
Pytest Suite for Feature Engineering & Financial Formulas
"""

import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "data_processing"))

from feature_engineering import generate_features

def test_financial_feature_formulas():
    orders = pd.DataFrame([
        {"order_id": "O1", "order_date": "2024-05-15", "product_id": "P101", "quantity": 2, "unit_price": 1000.0, "discount": 0.10, "shipping_cost": 50.0}
    ])
    products = pd.DataFrame([
        {"product_id": "P101", "cost_price": 600.0}
    ])
    
    df_feat = generate_features(orders, products)
    
    row = df_feat.iloc[0]
    assert row["gross_sales"] == 2000.0        # 2 * 1000
    assert row["discount_amount"] == 200.0     # 2000 * 0.10
    assert row["net_revenue"] == 1800.0        # 2000 - 200
    assert row["product_cost"] == 1200.0       # 2 * 600
    assert row["profit"] == 550.0              # 1800 - 1200 - 50
    assert abs(row["profit_margin"] - 0.3056) < 0.001  # 550 / 1800
    assert row["order_year"] == 2024
    assert row["order_month_name"] == "May"
    assert row["day_of_week"] == "Wednesday"
