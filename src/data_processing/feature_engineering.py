"""
NovaCart Feature Engineering Module
Calculates analytical financial metrics (gross_sales, discount_amount, net_revenue,
product_cost, profit, profit_margin) and extracts temporal dimension features.
"""

import pandas as pd
import numpy as np

def generate_features(df_orders, df_products):
    df = df_orders.copy()
    
    # Merge cost_price from products table
    prod_cost_map = df_products.set_index("product_id")["cost_price"].to_dict()
    df["cost_price"] = df["product_id"].map(prod_cost_map).fillna(0.0)
    
    # 1. Financial Metrics
    df["gross_sales"] = (df["quantity"] * df["unit_price"]).round(2)
    df["discount_amount"] = (df["gross_sales"] * df["discount"]).round(2)
    df["net_revenue"] = (df["gross_sales"] - df["discount_amount"]).round(2)
    df["product_cost"] = (df["quantity"] * df["cost_price"]).round(2)
    df["shipping_cost"] = df["shipping_cost"].fillna(0.0).round(2)
    df["profit"] = (df["net_revenue"] - df["product_cost"] - df["shipping_cost"]).round(2)
    
    # Safe Profit Margin Calculation (Division by zero protection)
    df["profit_margin"] = np.where(
        df["net_revenue"] != 0,
        (df["profit"] / df["net_revenue"]).round(4),
        0.0
    )
    
    # 2. Date & Time Features
    dt_series = pd.to_datetime(df["order_date"])
    df["order_year"] = dt_series.dt.year
    df["order_quarter"] = dt_series.dt.quarter
    df["order_month"] = dt_series.dt.month
    df["order_month_name"] = dt_series.dt.strftime("%b")
    df["order_week"] = dt_series.dt.isocalendar().week.astype(int)
    df["day_of_week"] = dt_series.dt.strftime("%A")
    df["is_weekend"] = dt_series.dt.weekday.isin([5, 6]).astype(int)
    
    print(f"Feature engineering complete: {len(df)} records transformed across financial & temporal features.")
    return df
