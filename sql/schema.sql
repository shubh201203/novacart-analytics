-- =============================================================================
-- NovaCart Data Warehouse — Star Schema DDL (PostgreSQL Compatible)
-- Database: novacart_analytics
-- =============================================================================

DROP TABLE IF EXISTS fact_returns CASCADE;
DROP TABLE IF EXISTS fact_payments CASCADE;
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_location CASCADE;
DROP TABLE IF EXISTS dim_payment CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- =============================================================================
-- 1. DIMENSION TABLES
-- =============================================================================

-- Dim Customer
CREATE TABLE dim_customer (
    customer_key     SERIAL PRIMARY KEY,
    customer_id      VARCHAR(20) NOT NULL UNIQUE,
    customer_name    VARCHAR(100) NOT NULL,
    gender           VARCHAR(20),
    age              INT,
    signup_date      DATE,
    city             VARCHAR(100),
    state            VARCHAR(50),
    state_code       VARCHAR(10),
    region           VARCHAR(50),
    customer_segment VARCHAR(50)
);

COMMENT ON TABLE dim_customer IS 'Customer dimension storing demographic, segment, and geographical location attributes.';

-- Dim Product
CREATE TABLE dim_product (
    product_key   SERIAL PRIMARY KEY,
    product_id    VARCHAR(20) NOT NULL UNIQUE,
    product_name  VARCHAR(150) NOT NULL,
    category      VARCHAR(100) NOT NULL,
    subcategory   VARCHAR(100) NOT NULL,
    brand         VARCHAR(100) NOT NULL,
    cost_price    NUMERIC(10, 2) NOT NULL,
    list_price    NUMERIC(10, 2) NOT NULL
);

COMMENT ON TABLE dim_product IS 'Product dimension storing product hierarchy, categories, brands, cost and list pricing.';

-- Dim Location
CREATE TABLE dim_location (
    location_key SERIAL PRIMARY KEY,
    city         VARCHAR(100) NOT NULL,
    state        VARCHAR(50) NOT NULL,
    state_code   VARCHAR(10) NOT NULL,
    region       VARCHAR(50) NOT NULL,
    CONSTRAINT idx_location_unique UNIQUE (city, state_code)
);

COMMENT ON TABLE dim_location IS 'Location dimension capturing geographic hierarchy (City, State, Region).';

-- Dim Payment
CREATE TABLE dim_payment (
    payment_key    SERIAL PRIMARY KEY,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    CONSTRAINT idx_payment_unique UNIQUE (payment_method, payment_status)
);

COMMENT ON TABLE dim_payment IS 'Payment method and status dimensional combinations.';

-- Dim Date
CREATE TABLE dim_date (
    date_key           INT PRIMARY KEY, -- Format: YYYYMMDD
    full_date          DATE NOT NULL UNIQUE,
    day_of_month       INT NOT NULL,
    day_name           VARCHAR(20) NOT NULL,
    day_of_week        INT NOT NULL,
    week_of_year       INT NOT NULL,
    month_num          INT NOT NULL,
    month_name         VARCHAR(20) NOT NULL,
    quarter            INT NOT NULL,
    year               INT NOT NULL,
    is_weekend         BOOLEAN NOT NULL,
    is_holiday_season  BOOLEAN NOT NULL
);

COMMENT ON TABLE dim_date IS 'Complete calendar date dimension covering the entire analytical timeline.';

-- =============================================================================
-- 2. FACT TABLES
-- =============================================================================

-- Fact Sales
-- GRAIN: One row per product line within a customer order.
CREATE TABLE fact_sales (
    sales_key       BIGSERIAL PRIMARY KEY,
    order_id        VARCHAR(30) NOT NULL,
    date_key        INT NOT NULL REFERENCES dim_date(date_key),
    customer_key    INT NOT NULL REFERENCES dim_customer(customer_key),
    product_key     INT NOT NULL REFERENCES dim_product(product_key),
    location_key    INT NOT NULL REFERENCES dim_location(location_key),
    payment_key     INT NOT NULL REFERENCES dim_payment(payment_key),
    quantity        INT NOT NULL CHECK (quantity > 0),
    gross_sales     NUMERIC(12, 2) NOT NULL,
    discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    net_revenue     NUMERIC(12, 2) NOT NULL,
    product_cost    NUMERIC(12, 2) NOT NULL,
    shipping_cost   NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    profit          NUMERIC(12, 2) NOT NULL,
    profit_margin   NUMERIC(6, 4) NOT NULL,
    order_status    VARCHAR(30) NOT NULL,
    is_completed    BOOLEAN NOT NULL,
    is_cancelled    BOOLEAN NOT NULL,
    is_returned     BOOLEAN NOT NULL
);

COMMENT ON TABLE fact_sales IS 'Sales fact table. GRAIN: One row per product line item within an order.';

-- Fact Returns
-- GRAIN: One row per returned product line item / return transaction.
CREATE TABLE fact_returns (
    return_key        SERIAL PRIMARY KEY,
    return_id         VARCHAR(30) NOT NULL,
    order_id          VARCHAR(30) NOT NULL,
    return_date_key   INT NOT NULL REFERENCES dim_date(date_key),
    customer_key      INT NOT NULL REFERENCES dim_customer(customer_key),
    product_key       INT NOT NULL REFERENCES dim_product(product_key),
    quantity_returned INT NOT NULL CHECK (quantity_returned > 0),
    return_reason     VARCHAR(150) NOT NULL
);

COMMENT ON TABLE fact_returns IS 'Returns fact table. GRAIN: One row per returned item line.';

-- Fact Payments
-- GRAIN: One row per payment transaction.
CREATE TABLE fact_payments (
    payment_trans_key SERIAL PRIMARY KEY,
    payment_id        VARCHAR(30) NOT NULL,
    order_id          VARCHAR(30) NOT NULL,
    payment_date_key  INT NOT NULL REFERENCES dim_date(date_key),
    payment_key       INT NOT NULL REFERENCES dim_payment(payment_key),
    payment_amount    NUMERIC(12, 2) NOT NULL
);

COMMENT ON TABLE fact_payments IS 'Payments fact table. GRAIN: One row per order payment transaction.';

-- =============================================================================
-- 3. INDEXES FOR HIGH-PERFORMANCE ANALYTICAL QUERIES
-- =============================================================================

CREATE INDEX idx_fact_sales_order_id ON fact_sales(order_id);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product  ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_date     ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_location ON fact_sales(location_key);
CREATE INDEX idx_fact_sales_payment  ON fact_sales(payment_key);
CREATE INDEX idx_fact_sales_status   ON fact_sales(order_status);

CREATE INDEX idx_fact_returns_order ON fact_returns(order_id);
CREATE INDEX idx_fact_returns_date  ON fact_returns(return_date_key);
CREATE INDEX idx_fact_returns_prod  ON fact_returns(product_key);

CREATE INDEX idx_fact_payments_order ON fact_payments(order_id);
CREATE INDEX idx_fact_payments_date  ON fact_payments(payment_date_key);
