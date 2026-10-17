"""
Pytest Suite for Phase 4 & Phase 4.1 Canonical KPI Benchmarks & SQL Analytics
"""

import sys
import os
import pandas as pd
import duckdb
import pytest

base_dir = os.path.dirname(os.path.dirname(__file__))
results_dir = os.path.join(base_dir, "data", "analysis_results")
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


def test_canonical_kpi_benchmarks(dw_conn):
    """Verifies all Phase 4.1 canonical KPI benchmark values exactly."""
    placed_rev = dw_conn.execute("SELECT ROUND(SUM(net_revenue), 2) FROM fact_sales;").fetchone()[0]
    realized_rev = dw_conn.execute("SELECT ROUND(SUM(net_revenue), 2) FROM fact_sales WHERE is_completed = TRUE;").fetchone()[0]
    placed_profit = dw_conn.execute("SELECT ROUND(SUM(profit), 2) FROM fact_sales;").fetchone()[0]
    realized_profit = dw_conn.execute("SELECT ROUND(SUM(profit), 2) FROM fact_sales WHERE is_completed = TRUE;").fetchone()[0]
    ordered_qty = dw_conn.execute("SELECT SUM(quantity) FROM fact_sales;").fetchone()[0]
    returned_qty = dw_conn.execute("SELECT SUM(quantity_returned) FROM fact_returns;").fetchone()[0]
    
    returned_rev = dw_conn.execute("""
        SELECT ROUND(SUM(r.quantity_returned * (s.net_revenue / s.quantity)), 2)
        FROM fact_returns r
        JOIN fact_sales s ON r.order_id = s.order_id AND r.product_key = s.product_key;
    """).fetchone()[0]
    
    post_return_rev = round(realized_rev - returned_rev, 2)
    
    # Assert exact canonical benchmarks
    assert abs(placed_rev - 971486941.80) < 0.05
    assert abs(realized_rev - 847624781.93) < 0.05
    assert abs(post_return_rev - 796752855.77) < 0.05
    assert abs(placed_profit - 300804487.91) < 0.05
    assert abs(realized_profit - 262159342.82) < 0.05
    assert ordered_qty == 156395
    assert returned_qty == 8712

def test_exported_analysis_datasets_exist():
    """Verifies all required analytical result CSV files exist in data/analysis_results/."""
    expected_files = [
        "monthly_sales.csv",
        "customer_value.csv",
        "product_performance.csv",
        "regional_performance.csv",
        "rfm_segments.csv",
        "cohort_retention.csv",
        "return_analysis.csv",
        "payment_analysis.csv",
        "profitability_analysis.csv"
    ]
    for fn in expected_files:
        fp = os.path.join(results_dir, fn)
        assert os.path.exists(fp), f"Expected result file {fn} missing!"
        df = pd.read_csv(fp)
        assert len(df) > 0, f"Result file {fn} is empty!"

def test_rfm_segments_completeness():
    """Verifies RFM segment mapping covers 100% of active completed customers."""
    fp = os.path.join(results_dir, "rfm_segments.csv")
    df = pd.read_csv(fp)
    total_rfm_cust = df["customer_count"].sum()
    assert total_rfm_cust == 3970  # Active completed customer count

def test_cohort_retention_indices():
    """Verifies month_number is within valid bounds and retention rate is <= 100%."""
    fp = os.path.join(results_dir, "cohort_retention.csv")
    df = pd.read_csv(fp)
    assert df["retention_rate_pct"].max() <= 100.0
    assert df["cohort_index_month"].min() >= 0
    assert df["cohort_index_month"].max() <= 12
