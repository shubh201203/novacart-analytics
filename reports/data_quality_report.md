# NovaCart Automated Data Quality & Cleaning Report
## Executive Data Health Summary
The table below details row lineage from raw ingestion through cleaning, deduplication, deterministic missing recovery, and quarantine isolation.
| Table | Raw Rows | Processed Rows | Quarantined Rows | Duplicates Removed | Missing Imputed/Recovered |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Customers | 5,015 | 5,000 | 0 | 15 | 43 |
| Products | 180 | 180 | 0 | 0 | 0 |
| Orders | 105,420 | 104,852 | 148 | 420 | 227 |
| Returns | 5,798 | 5,792 | 6 | 0 | 0 |
| Payments | 63,035 | 62,952 | 0 | 0 | 170 |

## Audit Trail Log Highlights
| Table | Field | Issue Type | Action Taken | Records Affected | Notes |
| :--- | :--- | :--- | :--- | ---: | :--- |
| customers | all_fields | duplicate_rows | drop_duplicates | 15 | Removed identical duplicate customer records. |
| customers | customer_name | missing_value | fillna('Unknown Customer') | 19 | Imputed missing customer names. |
| customers | city | missing_value | fillna('Unknown City') | 23 | Imputed missing customer city names. |
| customers | age | outlier_value | replace_with_median(34) | 6 | Replaced invalid age values with median age 34. |
| products | category | casing_inconsistency | title_case_standardization | 180 | Standardized category count from 10 variations down to 6 clean categories. |
| orders | all_fields | duplicate_order_lines | drop_duplicates | 420 | Removed identical duplicate order-line records. |
| orders | order_date | malformed_date_string | quarantine_isolation | 43 | Moved order lines with unparseable date strings into quarantine. |
| orders | quantity | invalid_quantity_value | quarantine_isolation | 37 | Moved order lines with quantity <= 0 into quarantine. |
| orders | customer_id | missing_customer_id | recovered=142, quarantined=68 | 210 | Deterministically recovered 142 customer_ids from order line co-occurrences; quarantined 68 unrecoverable records. |
| orders | payment_method | missing_payment_method | fillna('UPI') | 226 | Imputed missing order payment methods using modal payment method (UPI). |
| returns | order_id | orphan_foreign_key | quarantine_isolation | 4 | Quarantined return records referencing non-existent orders. |
| returns | return_date | invalid_date_logic | quarantine_isolation | 2 | Quarantined returns where return_date < order_date. |
| payments | order_id | orphan_foreign_key | remove_orphans | 83 | Removed payment records referencing quarantined orders. |
| payments | payment_status | missing_payment_status | order_lifecycle_imputation | 169 | Deterministically imputed missing payment_status based on order_status. |

## Data Reconciliation Verification
* **Gross Sales Formula**: `quantity * unit_price` (Reconciled: 100% Match)
* **Net Revenue Formula**: `gross_sales - discount_amount` (Reconciled: 100% Match)
* **Profit Formula**: `net_revenue - product_cost - shipping_cost` (Reconciled: 100% Match)
* **Missing customer_id Policy**: 100% accounted for (Recovered co-occurring customer_ids deterministically; remaining unrecoverable isolated in `data/processed/quarantine/orders_quarantine.csv`).
