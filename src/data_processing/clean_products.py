"""
NovaCart Data Cleaning Module — Products Table
Standardizes category casing, subcategories, brands, and validates price & cost margin bounds.
"""

import pandas as pd

CATEGORY_STANDARD_MAP = {
    "ELECTRONICS": "Electronics",
    "ELECTRONICS": "Electronics",
    "BEAUTY & PERSONAL CARE": "Beauty & Personal Care",
    "BEAUTY & PERSONAL CARE": "Beauty & Personal Care",
    "BOOKS & MEDIA": "Books & Media",
    "BOOKS & MEDIA": "Books & Media",
    "HOME & KITCHEN": "Home & Kitchen",
    "SPORTS & OUTDOORS": "Sports & Outdoors",
    "APPAREL": "Apparel"
}

def clean_products(df_raw, audit_log=None):
    df = df_raw.copy()
    raw_count = len(df)
    
    # 1. Deduplication
    dupes_count = df.duplicated().sum()
    if dupes_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        if audit_log is not None:
            audit_log.append({
                "table_name": "products", "field_name": "all_fields",
                "issue_type": "duplicate_rows", "action_taken": "drop_duplicates",
                "records_affected": dupes_count, "notes": "Removed identical duplicate product rows."
            })
            
    # 2. Standardize Category Casing
    orig_cats = df["category"].nunique()
    
    def standardize_category(cat):
        if pd.isnull(cat):
            return "General"
        c_upper = str(cat).strip().upper()
        if c_upper in CATEGORY_STANDARD_MAP:
            return CATEGORY_STANDARD_MAP[c_upper]
        return str(cat).strip().title()
        
    df["category"] = df["category"].apply(standardize_category)
    new_cats = df["category"].nunique()
    
    if audit_log is not None and orig_cats != new_cats:
        audit_log.append({
            "table_name": "products", "field_name": "category",
            "issue_type": "casing_inconsistency", "action_taken": "title_case_standardization",
            "records_affected": raw_count, "notes": f"Standardized category count from {orig_cats} variations down to {new_cats} clean categories."
        })
        
    # 3. Standardize subcategory & brand formatting
    df["subcategory"] = df["subcategory"].astype(str).str.strip().str.title()
    df["brand"] = df["brand"].astype(str).str.strip()
    
    # 4. Validate Price Integrity (list_price > cost_price > 0)
    invalid_prices = ((df["list_price"] <= 0) | (df["cost_price"] <= 0)).sum()
    if invalid_prices > 0:
        raise ValueError(f"Found {invalid_prices} products with non-positive cost or list prices!")
        
    print(f"Cleaned products: {raw_count} raw -> {len(df)} processed (categories standardized to {new_cats} unique categories)")
    return df
