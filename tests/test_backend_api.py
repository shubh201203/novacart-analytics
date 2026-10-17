"""
Automated Integration Tests for NovaCart FastAPI Endpoints
Verifies that the backend API matches the exact PostgreSQL canonical benchmarks.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["connected"] is True

def test_filter_options():
    response = client.get("/api/filters")
    assert response.status_code == 200
    data = response.json()
    assert "years" in data
    assert "regions" in data
    assert "categories" in data
    assert 2024 in data["years"]
    assert "South" in data["regions"]
    assert "Electronics" in data["categories"]

def test_overview_canonical_reconciliation():
    response = client.get("/api/overview")
    assert response.status_code == 200
    kpis = response.json()["kpis"]
    
    # Assert exact canonical benchmarks
    assert abs(kpis["placed_net_revenue"] - 971486941.80) < 0.05
    assert abs(kpis["realized_net_revenue"] - 847624781.93) < 0.05
    assert abs(kpis["returned_revenue"] - 50871926.16) < 0.05
    assert abs(kpis["post_return_revenue"] - 796752855.77) < 0.05
    assert abs(kpis["realized_profit"] - 262159342.82) < 0.05
    assert abs(kpis["realized_margin"] - 30.93) < 0.05
    assert kpis["active_customers"] == 3970
    assert kpis["realized_orders"] == 54854
    assert abs(kpis["average_order_value"] - 15452.38) < 0.05
    assert abs(kpis["return_rate"] - 5.57) < 0.05

def test_customer_canonical_reconciliation():
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    kpis = data["kpis"]
    assert kpis["active_customers"] == 3970
    assert kpis["repeat_customers"] == 3260
    assert kpis["onetime_customers"] == 710
    assert abs(kpis["repeat_customer_share"] - 82.12) < 0.05
    assert len(data["top_customers"]) == 10

def test_products_canonical_reconciliation():
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data["category_performance"]) == 6
    # Verify Electronics is highest volume
    elec = next(c for c in data["category_performance"] if c["category"] == "Electronics")
    assert abs(elec["realized_revenue"] - 494248007.71) < 0.05
    assert abs(elec["realized_profit"] - 91800413.59) < 0.05

def test_regional_canonical_reconciliation():
    response = client.get("/api/regional")
    assert response.status_code == 200
    data = response.json()
    assert len(data["regional_summary"]) == 6
    south = next(r for r in data["regional_summary"] if r["region"] == "South")
    assert abs(south["realized_revenue"] - 250276869.15) < 0.05

def test_retention_canonical_reconciliation():
    response = client.get("/api/retention")
    assert response.status_code == 200
    data = response.json()
    assert len(data["cohort_matrix"]) > 0
    # Month 0 retention should be 100%
    month_0_records = [c for c in data["cohort_matrix"] if c["month_offset"] == 0]
    for r in month_0_records:
        assert r["retention_rate"] == 100.0

def test_dynamic_filter_slicing():
    # Slicing by Year = 2024
    resp_2024 = client.get("/api/overview?year=2024")
    assert resp_2024.status_code == 200
    kpis_2024 = resp_2024.json()["kpis"]
    assert kpis_2024["realized_net_revenue"] < 847624781.93
    assert kpis_2024["realized_orders"] < 54854

def test_customer_purchase_frequency_ranking():
    """Verify customer purchase frequency is computed using distinct realized orders, not sales rows or revenue."""
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert "top_customers_by_frequency" in data
    freq_list = data["top_customers_by_frequency"]
    assert len(freq_list) == 10
    
    # Verify top ranked customer by distinct completed orders matches PostgreSQL source of truth
    assert freq_list[0]["customer_name"] == "Anushka Mehta"
    assert freq_list[0]["customer_id"] == "CUST-14343"
    assert freq_list[0]["realized_orders"] == 2918
    
    assert freq_list[1]["customer_name"] == "Ishita Iyer"
    assert freq_list[1]["realized_orders"] == 1545
    
    assert freq_list[2]["customer_name"] == "Swati Choudhury"
    assert freq_list[2]["realized_orders"] == 810
    
    # Assert monotonic ordering by realized orders
    for i in range(len(freq_list) - 1):
        assert freq_list[i]["realized_orders"] >= freq_list[i+1]["realized_orders"]
