# NovaCart Power Query (M Language) Data Ingestion Scripts

This document details the Power Query M code for connecting to PostgreSQL or DuckDB tables, validating data types, establishing staging structures, and loading star schema tables into Power BI.

---

## 1. M Script: `dim_customer`

```powerquery
let
    Source = PostgreSQL.Database("localhost", "novacart_analytics"),
    dim_customer_Table = Source{[Schema="public",Item="dim_customer"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(dim_customer_Table,{
        {"customer_key", Int64.Type},
        {"customer_id", type text},
        {"customer_name", type text},
        {"gender", type text},
        {"age", Int64.Type},
        {"signup_date", type date},
        {"city", type text},
        {"state", type text},
        {"state_code", type text},
        {"region", type text},
        {"customer_segment", type text}
    })
in
    #"Changed Type"
```

---

## 2. M Script: `dim_product`

```powerquery
let
    Source = PostgreSQL.Database("localhost", "novacart_analytics"),
    dim_product_Table = Source{[Schema="public",Item="dim_product"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(dim_product_Table,{
        {"product_key", Int64.Type},
        {"product_id", type text},
        {"product_name", type text},
        {"category", type text},
        {"subcategory", type text},
        {"brand", type text},
        {"cost_price", Currency.Type},
        {"list_price", Currency.Type}
    })
in
    #"Changed Type"
```

---

## 3. M Script: `dim_date`

```powerquery
let
    Source = PostgreSQL.Database("localhost", "novacart_analytics"),
    dim_date_Table = Source{[Schema="public",Item="dim_date"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(dim_date_Table,{
        {"date_key", Int64.Type},
        {"full_date", type date},
        {"day_of_month", Int64.Type},
        {"day_name", type text},
        {"day_of_week", Int64.Type},
        {"week_of_year", Int64.Type},
        {"month_num", Int64.Type},
        {"month_name", type text},
        {"quarter", Int64.Type},
        {"year", Int64.Type},
        {"is_weekend", type logical},
        {"is_holiday_season", type logical}
    })
in
    #"Changed Type"
```

---

## 4. M Script: `fact_sales`

```powerquery
let
    Source = PostgreSQL.Database("localhost", "novacart_analytics"),
    fact_sales_Table = Source{[Schema="public",Item="fact_sales"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(fact_sales_Table,{
        {"sales_key", Int64.Type},
        {"order_id", type text},
        {"date_key", Int64.Type},
        {"customer_key", Int64.Type},
        {"product_key", Int64.Type},
        {"location_key", Int64.Type},
        {"payment_key", Int64.Type},
        {"quantity", Int64.Type},
        {"gross_sales", Currency.Type},
        {"discount_amount", Currency.Type},
        {"net_revenue", Currency.Type},
        {"product_cost", Currency.Type},
        {"shipping_cost", Currency.Type},
        {"profit", Currency.Type},
        {"profit_margin", Percentage.Type},
        {"order_status", type text},
        {"is_completed", type logical},
        {"is_cancelled", type logical},
        {"is_returned", type logical}
    })
in
    #"Changed Type"
```

---

## 5. M Script: `fact_returns`

```powerquery
let
    Source = PostgreSQL.Database("localhost", "novacart_analytics"),
    fact_returns_Table = Source{[Schema="public",Item="fact_returns"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(fact_returns_Table,{
        {"return_key", Int64.Type},
        {"return_id", type text},
        {"order_id", type text},
        {"return_date_key", Int64.Type},
        {"customer_key", Int64.Type},
        {"product_key", Int64.Type},
        {"quantity_returned", Int64.Type},
        {"return_reason", type text}
    })
in
    #"Changed Type"
```
