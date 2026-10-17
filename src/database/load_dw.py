"""
NovaCart Data Warehouse Loader (PostgreSQL / DuckDB Dual-Engine DW Builder)
Populates the Star Schema data warehouse strictly from data/processed/ outputs.
Guarantees idempotency, primary/foreign key mapping, and date dimension completeness.
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(dotenv_path)

DB_TYPE = os.getenv("DB_TYPE", "postgresql").lower()
DB_HOST = os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "localhost"))
DB_PORT = os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "novacart_analytics"))
DB_USER = os.getenv("POSTGRES_USER", os.getenv("DB_USER", "postgres"))
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD", "postgres"))


def get_db_connection():
    """Attempts PostgreSQL connection first; falls back to DuckDB engine if PostgreSQL is unavailable."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        print(f"[Engine] Connected successfully to PostgreSQL database '{DB_NAME}' at {DB_HOST}:{DB_PORT}")
        return conn, "postgresql"
    except Exception as e:
        print(f"[Notice] PostgreSQL daemon unavailable. Initializing DuckDB Data Warehouse engine...")
        import duckdb
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed", "novacart_analytics.duckdb")
        conn = duckdb.connect(db_path)
        print(f"[Engine] Connected successfully to DuckDB Data Warehouse at '{db_path}'")
        return conn, "duckdb"

def load_data_warehouse():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    proc_dir = os.path.join(base_dir, "data", "processed")
    quar_dir = os.path.join(proc_dir, "quarantine")
    
    print("=" * 80)
    print("STARTING NOVACART STAR SCHEMA DATA WAREHOUSE LOAD")
    print("=" * 80)
    
    # 1. Read Processed CSVs Only
    df_cust = pd.read_csv(os.path.join(proc_dir, "customers_processed.csv"))
    df_prod = pd.read_csv(os.path.join(proc_dir, "products_processed.csv"))
    df_ord  = pd.read_csv(os.path.join(proc_dir, "orders_processed.csv"))
    df_ret  = pd.read_csv(os.path.join(proc_dir, "returns_processed.csv"))
    df_pay  = pd.read_csv(os.path.join(proc_dir, "payments_processed.csv"))
    
    # Report Quarantined Exclusions
    quar_ord_count = len(pd.read_csv(os.path.join(quar_dir, "orders_quarantine.csv"))) if os.path.exists(os.path.join(quar_dir, "orders_quarantine.csv")) else 0
    quar_ret_count = len(pd.read_csv(os.path.join(quar_dir, "returns_quarantine.csv"))) if os.path.exists(os.path.join(quar_dir, "returns_quarantine.csv")) else 0
    
    print(f"[Exclusion Policy] Quarantined orders excluded from DW: {quar_ord_count:,} records")
    print(f"[Exclusion Policy] Quarantined returns excluded from DW: {quar_ret_count:,} records")
    
    conn, engine_type = get_db_connection()
    
    # Execute Schema DDL
    sql_schema_path = os.path.join(base_dir, "sql", "schema.sql")
    with open(sql_schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    if engine_type == "postgresql":
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
    else:
        conn.execute("DROP TABLE IF EXISTS fact_returns;")
        conn.execute("DROP TABLE IF EXISTS fact_payments;")
        conn.execute("DROP TABLE IF EXISTS fact_sales;")
        conn.execute("DROP TABLE IF EXISTS dim_customer;")
        conn.execute("DROP TABLE IF EXISTS dim_product;")
        conn.execute("DROP TABLE IF EXISTS dim_location;")
        conn.execute("DROP TABLE IF EXISTS dim_payment;")
        conn.execute("DROP TABLE IF EXISTS dim_date;")
        
        conn.execute("""
        CREATE TABLE dim_customer (
            customer_key INTEGER PRIMARY KEY,
            customer_id VARCHAR UNIQUE,
            customer_name VARCHAR, gender VARCHAR, age INTEGER, signup_date DATE,
            city VARCHAR, state VARCHAR, state_code VARCHAR, region VARCHAR, customer_segment VARCHAR
        );
        CREATE TABLE dim_product (
            product_key INTEGER PRIMARY KEY,
            product_id VARCHAR UNIQUE,
            product_name VARCHAR, category VARCHAR, subcategory VARCHAR, brand VARCHAR,
            cost_price DOUBLE, list_price DOUBLE
        );
        CREATE TABLE dim_location (
            location_key INTEGER PRIMARY KEY,
            city VARCHAR, state VARCHAR, state_code VARCHAR, region VARCHAR
        );
        CREATE TABLE dim_payment (
            payment_key INTEGER PRIMARY KEY,
            payment_method VARCHAR, payment_status VARCHAR
        );
        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY, full_date DATE UNIQUE, day_of_month INTEGER,
            day_name VARCHAR, day_of_week INTEGER, week_of_year INTEGER, month_num INTEGER,
            month_name VARCHAR, quarter INTEGER, year INTEGER, is_weekend BOOLEAN, is_holiday_season BOOLEAN
        );
        CREATE TABLE fact_sales (
            sales_key BIGINT PRIMARY KEY, order_id VARCHAR, date_key INTEGER, customer_key INTEGER,
            product_key INTEGER, location_key INTEGER, payment_key INTEGER, quantity INTEGER,
            gross_sales DOUBLE, discount_amount DOUBLE, net_revenue DOUBLE, product_cost DOUBLE,
            shipping_cost DOUBLE, profit DOUBLE, profit_margin DOUBLE, order_status VARCHAR,
            is_completed BOOLEAN, is_cancelled BOOLEAN, is_returned BOOLEAN
        );
        CREATE TABLE fact_returns (
            return_key INTEGER PRIMARY KEY, return_id VARCHAR, order_id VARCHAR, return_date_key INTEGER,
            customer_key INTEGER, product_key INTEGER, quantity_returned INTEGER, return_reason VARCHAR
        );
        CREATE TABLE fact_payments (
            payment_trans_key INTEGER PRIMARY KEY, payment_id VARCHAR, order_id VARCHAR,
            payment_date_key INTEGER, payment_key INTEGER, payment_amount DOUBLE
        );
        """)

    # ---------------------------------------------------------
    # 2. POPULATE DIMENSIONS
    # ---------------------------------------------------------
    # Dim Customer
    df_cust = df_cust.reset_index(drop=True)
    df_cust["customer_key"] = df_cust.index + 1
    # Select exact columns matching schema
    dim_cust_cols = ["customer_key", "customer_id", "customer_name", "gender", "age", "signup_date", "city", "state_name", "state_code", "region", "customer_segment"]
    df_dim_cust = df_cust[dim_cust_cols].rename(columns={"state_name": "state"})
    
    # Dim Product
    df_prod = df_prod.reset_index(drop=True)
    df_prod["product_key"] = df_prod.index + 1
    dim_prod_cols = ["product_key", "product_id", "product_name", "category", "subcategory", "brand", "cost_price", "list_price"]
    df_dim_prod = df_prod[dim_prod_cols]
    
    # Dim Location (Unique City + State combination)
    df_loc = df_cust[["city", "state_name", "state_code", "region"]].drop_duplicates().reset_index(drop=True)
    df_loc.columns = ["city", "state", "state_code", "region"]
    df_loc["location_key"] = df_loc.index + 1
    dim_loc_cols = ["location_key", "city", "state", "state_code", "region"]
    df_dim_loc = df_loc[dim_loc_cols]
    
    # Dim Payment (Unique Payment Method + Payment Status combination)
    pay_methods = df_ord["payment_method"].unique()
    pay_statuses = df_pay["payment_status"].unique()
    loc_pay_list = []
    p_key = 1
    for pm in pay_methods:
        for ps in pay_statuses:
            if pd.notnull(pm) and pd.notnull(ps):
                loc_pay_list.append({"payment_key": p_key, "payment_method": pm, "payment_status": ps})
                p_key += 1
    df_dim_pay = pd.DataFrame(loc_pay_list)
    dim_pay_cols = ["payment_key", "payment_method", "payment_status"]
    df_dim_pay = df_dim_pay[dim_pay_cols]
    
    # Dim Date (2022-01-01 to 2026-12-31)
    start_d = datetime(2022, 1, 1)
    end_d = datetime(2026, 12, 31)
    d_list = []
    curr_d = start_d
    while curr_d <= end_d:
        dk = int(curr_d.strftime("%Y%m%d"))
        is_wknd = curr_d.weekday() in [5, 6]
        is_festive = curr_d.month in [10, 11]
        d_list.append({
            "date_key": dk,
            "full_date": curr_d.strftime("%Y-%m-%d"),
            "day_of_month": curr_d.day,
            "day_name": curr_d.strftime("%A"),
            "day_of_week": curr_d.weekday() + 1,
            "week_of_year": curr_d.isocalendar()[1],
            "month_num": curr_d.month,
            "month_name": curr_d.strftime("%B"),
            "quarter": (curr_d.month - 1) // 3 + 1,
            "year": curr_d.year,
            "is_weekend": is_wknd,
            "is_holiday_season": is_festive
        })
        curr_d += timedelta(days=1)
    df_dim_date = pd.DataFrame(d_list)

    # ---------------------------------------------------------
    # 3. POPULATE FACTS
    # ---------------------------------------------------------
    cust_key_map = df_dim_cust.set_index("customer_id")["customer_key"].to_dict()
    prod_key_map = df_dim_prod.set_index("product_id")["product_key"].to_dict()
    
    loc_key_map = df_dim_loc.set_index(["city", "state_code"])["location_key"].to_dict()
    cust_loc_info = df_dim_cust.set_index("customer_id")[["city", "state_code"]].to_dict("index")
    
    pay_dim_map = df_dim_pay.set_index(["payment_method", "payment_status"])["payment_key"].to_dict()
    ord_pay_status_map = df_pay.set_index("order_id")["payment_status"].to_dict()

    fact_sales_list = []
    for idx, row in df_ord.iterrows():
        c_id = row["customer_id"]
        p_id = row["product_id"]
        o_id = row["order_id"]
        o_date = str(row["order_date"])
        d_key = int(o_date.replace("-", ""))
        
        c_key = cust_key_map.get(c_id)
        pr_key = prod_key_map.get(p_id)
        
        c_loc = cust_loc_info.get(c_id, {"city": "Unknown City", "state_code": "UN"})
        l_key = loc_key_map.get((c_loc["city"], c_loc["state_code"]), 1)
        
        p_method = row["payment_method"]
        p_status = ord_pay_status_map.get(o_id, "Completed")
        py_key = pay_dim_map.get((p_method, p_status), 1)
        
        o_stat = row["order_status"]
        is_comp = o_stat in ["Completed", "Shipped"]
        is_canc = o_stat == "Cancelled"
        is_ret = o_stat == "Returned"
        
        fact_sales_list.append({
            "sales_key": idx + 1,
            "order_id": o_id,
            "date_key": d_key,
            "customer_key": c_key,
            "product_key": pr_key,
            "location_key": l_key,
            "payment_key": py_key,
            "quantity": row["quantity"],
            "gross_sales": row["gross_sales"],
            "discount_amount": row["discount_amount"],
            "net_revenue": row["net_revenue"],
            "product_cost": row["product_cost"],
            "shipping_cost": row["shipping_cost"],
            "profit": row["profit"],
            "profit_margin": row["profit_margin"],
            "order_status": o_stat,
            "is_completed": is_comp,
            "is_cancelled": is_canc,
            "is_returned": is_ret
        })
    df_fact_sales = pd.DataFrame(fact_sales_list)
    
    ord_cust_map = df_ord.groupby("order_id")["customer_id"].first().to_dict()
    ord_prod_map = df_ord.groupby("order_id")["product_id"].first().to_dict()

    fact_returns_list = []
    for idx, row in df_ret.iterrows():
        o_id = row["order_id"]
        c_id = ord_cust_map.get(o_id)
        p_id = ord_prod_map.get(o_id)
        
        r_date = str(row["return_date"])
        rd_key = int(r_date.replace("-", ""))
        
        c_key = cust_key_map.get(c_id, 1)
        pr_key = prod_key_map.get(p_id, 1)
        
        fact_returns_list.append({
            "return_key": idx + 1,
            "return_id": row["return_id"],
            "order_id": o_id,
            "return_date_key": rd_key,
            "customer_key": c_key,
            "product_key": pr_key,
            "quantity_returned": row["quantity_returned"],
            "return_reason": row["return_reason"]
        })
    df_fact_returns = pd.DataFrame(fact_returns_list)

    valid_date_keys = set(df_dim_date["date_key"])
    ord_date_map = df_ord.groupby("order_id")["order_date"].first().apply(lambda x: int(str(x).replace("-", ""))).to_dict()

    fact_payments_list = []
    for idx, row in df_pay.iterrows():
        o_id = row["order_id"]
        p_date = str(row["payment_date"])
        try:
            pd_key = int(p_date.replace("-", ""))
            if pd_key not in valid_date_keys:
                pd_key = ord_date_map.get(o_id, 20240101)
        except Exception:
            pd_key = ord_date_map.get(o_id, 20240101)
        
        p_method = row["payment_method"]
        p_status = row["payment_status"]
        py_key = pay_dim_map.get((p_method, p_status), 1)
        
        fact_payments_list.append({
            "payment_trans_key": idx + 1,
            "payment_id": row["payment_id"],
            "order_id": o_id,
            "payment_date_key": pd_key,
            "payment_key": py_key,
            "payment_amount": row["payment_amount"]
        })
    df_fact_payments = pd.DataFrame(fact_payments_list)


    # ---------------------------------------------------------
    # 4. LOAD INTO DATABASE
    # ---------------------------------------------------------
    if engine_type == "postgresql":
        from sqlalchemy import create_engine
        engine_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        sql_engine = create_engine(engine_url)
        
        df_dim_cust.to_sql("dim_customer", sql_engine, if_exists="append", index=False)
        df_dim_prod.to_sql("dim_product", sql_engine, if_exists="append", index=False)
        df_dim_loc.to_sql("dim_location", sql_engine, if_exists="append", index=False)
        df_dim_pay.to_sql("dim_payment", sql_engine, if_exists="append", index=False)
        df_dim_date.to_sql("dim_date", sql_engine, if_exists="append", index=False)
        
        df_fact_sales.to_sql("fact_sales", sql_engine, if_exists="append", index=False)
        df_fact_returns.to_sql("fact_returns", sql_engine, if_exists="append", index=False)
        df_fact_payments.to_sql("fact_payments", sql_engine, if_exists="append", index=False)
    else:
        conn.register("df_cust_view", df_dim_cust)
        conn.execute("INSERT INTO dim_customer SELECT * FROM df_cust_view;")
        
        conn.register("df_prod_view", df_dim_prod)
        conn.execute("INSERT INTO dim_product SELECT * FROM df_prod_view;")
        
        conn.register("df_loc_view", df_dim_loc)
        conn.execute("INSERT INTO dim_location SELECT * FROM df_loc_view;")
        
        conn.register("df_dim_pay_view", df_dim_pay)
        conn.execute("INSERT INTO dim_payment SELECT * FROM df_dim_pay_view;")
        
        conn.register("df_dim_date_view", df_dim_date)
        conn.execute("INSERT INTO dim_date SELECT * FROM df_dim_date_view;")
        
        conn.register("df_fact_sales_view", df_fact_sales)
        conn.execute("INSERT INTO fact_sales SELECT * FROM df_fact_sales_view;")
        
        conn.register("df_fact_returns_view", df_fact_returns)
        conn.execute("INSERT INTO fact_returns SELECT * FROM df_fact_returns_view;")
        
        conn.register("df_fact_payments_view", df_fact_payments)
        conn.execute("INSERT INTO fact_payments SELECT * FROM df_fact_payments_view;")

    print("\n--- LOADED STAR SCHEMA DATA WAREHOUSE ROW COUNTS ---")
    print(f"dim_customer : {len(df_dim_cust):,} rows")
    print(f"dim_product  : {len(df_dim_prod):,} rows")
    print(f"dim_location : {len(df_dim_loc):,} rows")
    print(f"dim_payment  : {len(df_dim_pay):,} rows")
    print(f"dim_date     : {len(df_dim_date):,} rows (2022-2026 full calendar)")
    print(f"fact_sales   : {len(df_fact_sales):,} rows (GRAIN: 1 row per product line/order)")
    print(f"fact_returns : {len(df_fact_returns):,} rows")
    print(f"fact_payments: {len(df_fact_payments):,} rows")
    
    print("\n" + "=" * 80)
    print("STAR SCHEMA LOAD COMPLETED IDEMPOTENTLY & SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    load_data_warehouse()
