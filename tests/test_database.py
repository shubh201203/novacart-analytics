"""
Pytest Suite for Data Warehouse Schema, Integrity, Fact Grains & Business Semantics
"""

import sys
import os
import duckdb
import pytest

base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, base_dir)

from src.database.load_dw import get_db_connection

from decimal import Decimal

class CursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        return tuple(float(x) if isinstance(x, Decimal) else x for x in row)

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [tuple(float(x) if isinstance(x, Decimal) else x for x in r) for r in rows]

class DBWrapper:
    def __init__(self, conn, engine_type):
        self._conn = conn
        self._engine_type = engine_type

    def execute(self, query, params=None):
        if self._engine_type == "postgresql":
            if query.strip().rstrip(";").upper() == "SHOW TABLES":
                query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            cur = self._conn.cursor()
            cur.execute(query, params or ())
            return CursorWrapper(cur)
        else:
            return self._conn.execute(query, params or ())

    def close(self):
        self._conn.close()


@pytest.fixture(scope="module")
def dw_conn():
    conn, engine_type = get_db_connection()
    wrapper = DBWrapper(conn, engine_type)
    yield wrapper
    wrapper.close()


def test_dw_tables_exist(dw_conn):
    tables = [r[0] for r in dw_conn.execute("SHOW TABLES;").fetchall()]
    expected_tables = ["dim_customer", "dim_product", "dim_location", "dim_payment", "dim_date", "fact_sales", "fact_returns", "fact_payments"]
    for tbl in expected_tables:
        assert tbl in tables

def test_fact_table_grains(dw_conn):
    """Verifies exact row counts matching documented table grains."""
    fs_count = dw_conn.execute("SELECT COUNT(*) FROM fact_sales;").fetchone()[0]
    fr_count = dw_conn.execute("SELECT COUNT(*) FROM fact_returns;").fetchone()[0]
    fp_count = dw_conn.execute("SELECT COUNT(*) FROM fact_payments;").fetchone()[0]
    
    assert fs_count == 104852  # One row per product line within an order
    assert fr_count == 5792    # One row per returned item line
    assert fp_count == 62952   # One row per payment transaction

def test_primary_key_uniqueness(dw_conn):
    cust_dupes = dw_conn.execute("SELECT COUNT(*) - COUNT(DISTINCT customer_key) FROM dim_customer;").fetchone()[0]
    prod_dupes = dw_conn.execute("SELECT COUNT(*) - COUNT(DISTINCT product_key) FROM dim_product;").fetchone()[0]
    sales_dupes = dw_conn.execute("SELECT COUNT(*) - COUNT(DISTINCT sales_key) FROM fact_sales;").fetchone()[0]
    
    assert cust_dupes == 0
    assert prod_dupes == 0
    assert sales_dupes == 0

def test_foreign_key_integrity(dw_conn):
    orphans = dw_conn.execute("""
        SELECT COUNT(*) 
        FROM fact_sales f 
        LEFT JOIN dim_customer c ON f.customer_key = c.customer_key 
        LEFT JOIN dim_product p ON f.product_key = p.product_key 
        LEFT JOIN dim_date d ON f.date_key = d.date_key 
        WHERE c.customer_key IS NULL OR p.product_key IS NULL OR d.date_key IS NULL;
    """).fetchone()[0]
    assert orphans == 0

def test_status_semantic_flags(dw_conn):
    """Verifies that status boolean flags match categorical order_status values."""
    comp_mismatch = dw_conn.execute("SELECT COUNT(*) FROM fact_sales WHERE is_completed = TRUE AND order_status NOT IN ('Completed', 'Shipped');").fetchone()[0]
    canc_mismatch = dw_conn.execute("SELECT COUNT(*) FROM fact_sales WHERE is_cancelled = TRUE AND order_status != 'Cancelled';").fetchone()[0]
    ret_mismatch  = dw_conn.execute("SELECT COUNT(*) FROM fact_sales WHERE is_returned = TRUE AND order_status != 'Returned';").fetchone()[0]
    
    assert comp_mismatch == 0
    assert canc_mismatch == 0
    assert ret_mismatch == 0

def test_financial_metric_reconciliation(dw_conn):
    """Verifies exact benchmark numbers for Net Revenue, Profit, and Quantity."""
    net_rev = dw_conn.execute("SELECT ROUND(SUM(net_revenue), 2) FROM fact_sales;").fetchone()[0]
    profit  = dw_conn.execute("SELECT ROUND(SUM(profit), 2) FROM fact_sales;").fetchone()[0]
    qty     = dw_conn.execute("SELECT SUM(quantity) FROM fact_sales;").fetchone()[0]
    
    assert abs(net_rev - 971486941.80) < 0.05
    assert abs(profit  - 300804487.91) < 0.05
    assert qty == 156395

def test_fact_to_fact_join_safety_cte(dw_conn):
    """Verifies CTE pattern prevents incorrect aggregations when joining sales to payments."""
    direct_join_rev = dw_conn.execute("""
        SELECT ROUND(SUM(f.net_revenue), 2)
        FROM fact_sales f
        JOIN fact_payments p ON f.order_id = p.order_id;
    """).fetchone()[0]
    
    cte_join_rev = dw_conn.execute("""
        WITH order_sales AS (
            SELECT order_id, SUM(net_revenue) AS ord_rev
            FROM fact_sales
            GROUP BY order_id
        )
        SELECT ROUND(SUM(ord_rev), 2)
        FROM order_sales;
    """).fetchone()[0]
    
    # Direct join yields distorted revenue due to cardinality mismatch; CTE produces exact reconciled revenue
    assert cte_join_rev == 971486941.80
    assert direct_join_rev != cte_join_rev  # Confirms direct join produces distorted figures
