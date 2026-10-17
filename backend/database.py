"""
NovaCart Backend Database & Configuration Module
Loads environment variables safely and provides pooled connections to PostgreSQL 18.
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables from project root .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "localhost"))
DB_PORT = os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "novacart_analytics"))
DB_USER = os.getenv("POSTGRES_USER", os.getenv("DB_USER", "postgres"))
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD", "postgres"))
DB_SSLMODE = os.getenv("POSTGRES_SSLMODE", os.getenv("DB_SSLMODE", None))

def get_db_connection():
    """Returns a direct psycopg2 connection with dictionary cursor support."""
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        
    conn_kwargs = {
        "host": DB_HOST,
        "port": DB_PORT,
        "dbname": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "cursor_factory": RealDictCursor
    }
    if DB_SSLMODE:
        conn_kwargs["sslmode"] = DB_SSLMODE
        
    return psycopg2.connect(**conn_kwargs)
