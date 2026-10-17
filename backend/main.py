"""
NovaCart FastAPI Backend Application
Provides RESTful endpoints delivering analytical metrics directly from PostgreSQL 18.
"""

import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from backend.database import get_db_connection
from backend.queries import (
    get_filter_options,
    get_overview_data,
    get_sales_data,
    get_customers_data,
    get_products_data,
    get_regional_data,
    get_retention_data
)

app = FastAPI(
    title="NovaCart Analytics API",
    description="Enterprise Analytics API serving PostgreSQL 18 Star Schema data for NovaCart React Dashboard.",
    version="1.0.0"
)

# CORS Configuration: allow origin specification via ALLOWED_ORIGINS env
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    """Health check endpoint confirming PostgreSQL warehouse connectivity."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"status": "healthy", "database": "postgresql_18", "connected": True}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="Database connectivity failure. Check server connection and credentials."
        )

@app.get("/api/filters")
def filter_options():
    """Returns available slicer/filter options for the frontend."""
    conn = get_db_connection()
    try:
        data = get_filter_options(conn)
        return data
    finally:
        conn.close()

@app.get("/api/overview")
def overview_analytics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Page 1: Executive Sales & Profitability Overview."""
    conn = get_db_connection()
    try:
        return get_overview_data(conn, year, month, region, category)
    finally:
        conn.close()

@app.get("/api/sales")
def sales_analytics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Page 2: Sales & Profitability Analysis."""
    conn = get_db_connection()
    try:
        return get_sales_data(conn, year, month, region, category)
    finally:
        conn.close()

@app.get("/api/customers")
def customer_analytics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Page 3: Customer Intelligence & Loyalty."""
    conn = get_db_connection()
    try:
        return get_customers_data(conn, year, month, region, category)
    finally:
        conn.close()

@app.get("/api/products")
def product_analytics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Page 4: Product Performance & Profitability."""
    conn = get_db_connection()
    try:
        return get_products_data(conn, year, month, region, category)
    finally:
        conn.close()

@app.get("/api/regional")
def regional_analytics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Page 5: Regional Operations & Geographic Demand."""
    conn = get_db_connection()
    try:
        return get_regional_data(conn, year, month, region, category)
    finally:
        conn.close()

@app.get("/api/retention")
def retention_analytics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Page 6: Customer Retention & Cohort Heatmap."""
    conn = get_db_connection()
    try:
        return get_retention_data(conn, year, month, region, category)
    finally:
        conn.close()
