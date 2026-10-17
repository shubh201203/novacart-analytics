"""
NovaCart Synthetic Raw Data Generator (India E-Commerce Edition)
Generates realistic e-commerce order-line records across customers, products, orders,
returns, and payments with Indian geography, payment methods (UPI, COD, NetBanking, etc.),
festive seasonality (Diwali/Navratri/Independence Sale surges), realistic pricing/margins,
customer purchasing behavior, and controlled raw data-quality flaws.
"""

import os
import random
import argparse
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="NovaCart Raw Data Generator")
    parser.add_argument("--rows", type=int, default=105000, help="Target number of order line records")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output_dir", type=str, default=None, help="Directory to save raw CSV files")
    return parser.parse_args()

def generate_raw_data(num_rows=105000, seed=42, output_dir=None):
    random.seed(seed)
    np.random.seed(seed)

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Starting NovaCart Raw Data Generation (India Market, seed={seed}, target_rows={num_rows})...")

    # ---------------------------------------------------------
    # 1. GENERATE CUSTOMERS (~5,000)
    # ---------------------------------------------------------
    NUM_CUSTOMERS = 5000

    FIRST_NAMES = [
        "Aarav", "Ananya", "Rohan", "Priya", "Aditya", "Sneha", "Rahul", "Pooja",
        "Vikram", "Neha", "Arjun", "Kavya", "Siddharth", "Riya", "Varun", "Anushka",
        "Karan", "Shreya", "Amit", "Meera", "Rajesh", "Sunita", "Sanjay", "Deepika",
        "Vivek", "Swati", "Nikhil", "Ishita", "Gaurav", "Divya", "Manish", "Tanvi",
        "Abhishek", "Preeti", "Alok", "Nisha", "Tarun", "Simran", "Prashant", "Bhavna"
    ]

    LAST_NAMES = [
        "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Shah", "Joshi",
        "Rao", "Nair", "Reddy", "Iyer", "Kulkarni", "Deshmukh", "Banerjee", "Chatterjee",
        "Mehta", "Agarwal", "Bhasin", "Malhotra", "Chawla", "Dutta", "Das", "Roy",
        "Mishra", "Pandey", "Thakur", "Choudhury", "Bhattacharya", "Jain"
    ]

    CITIES_STATES_REGIONS = [
        # South
        ("Bengaluru", "Karnataka", "KA", "South"),
        ("Mysuru", "Karnataka", "KA", "South"),
        ("Mangaluru", "Karnataka", "KA", "South"),
        ("Hyderabad", "Telangana", "TG", "South"),
        ("Warangal", "Telangana", "TG", "South"),
        ("Chennai", "Tamil Nadu", "TN", "South"),
        ("Coimbatore", "Tamil Nadu", "TN", "South"),
        ("Madurai", "Tamil Nadu", "TN", "South"),
        ("Kochi", "Kerala", "KL", "South"),
        ("Thiruvananthapuram", "Kerala", "KL", "South"),
        ("Visakhapatnam", "Andhra Pradesh", "AP", "South"),
        ("Vijayawada", "Andhra Pradesh", "AP", "South"),
        
        # West
        ("Mumbai", "Maharashtra", "MH", "West"),
        ("Pune", "Maharashtra", "MH", "West"),
        ("Nagpur", "Maharashtra", "MH", "West"),
        ("Ahmedabad", "Gujarat", "GJ", "West"),
        ("Surat", "Gujarat", "GJ", "West"),
        ("Vadodara", "Gujarat", "GJ", "West"),
        ("Jaipur", "Rajasthan", "RJ", "West"),
        ("Jodhpur", "Rajasthan", "RJ", "West"),
        ("Udaipur", "Rajasthan", "RJ", "West"),
        
        # North
        ("New Delhi", "Delhi", "DL", "North"),
        ("Gurugram", "Haryana", "HR", "North"),
        ("Faridabad", "Haryana", "HR", "North"),
        ("Noida", "Uttar Pradesh", "UP", "North"),
        ("Lucknow", "Uttar Pradesh", "UP", "North"),
        ("Kanpur", "Uttar Pradesh", "UP", "North"),
        ("Varanasi", "Uttar Pradesh", "UP", "North"),
        ("Ludhiana", "Punjab", "PB", "North"),
        ("Amritsar", "Punjab", "PB", "North"),
        ("Chandigarh", "Punjab", "PB", "North"),
        
        # East
        ("Kolkata", "West Bengal", "WB", "East"),
        ("Siliguri", "West Bengal", "WB", "East"),
        ("Bhubaneswar", "Odisha", "OD", "East"),
        ("Cuttack", "Odisha", "OD", "East"),
        ("Patna", "Bihar", "BR", "East"),
        ("Gaya", "Bihar", "BR", "East"),
        ("Ranchi", "Jharkhand", "JH", "East"),
        ("Jamshedpur", "Jharkhand", "JH", "East"),
        
        # Central
        ("Bhopal", "Madhya Pradesh", "MP", "Central"),
        ("Indore", "Madhya Pradesh", "MP", "Central"),
        
        # Northeast
        ("Guwahati", "Assam", "AS", "Northeast"),
        ("Silchar", "Assam", "AS", "Northeast")
    ]

    SEGMENTS = ["Consumer", "Corporate", "Small Business"]
    SEGMENT_WEIGHTS = [0.72, 0.18, 0.10]

    customer_list = []
    start_signup = datetime(2022, 1, 1)
    end_signup = datetime(2025, 9, 30)

    for i in range(1, NUM_CUSTOMERS + 1):
        cust_id = f"CUST-{10000 + i}"
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        
        # Introduce inconsistent casing for ~3% of names
        r_name = random.random()
        if r_name < 0.015:
            name = f"{fn.lower()} {ln.lower()}"
        elif r_name < 0.03:
            name = f"{fn.upper()} {ln.upper()}"
        else:
            name = f"{fn} {ln}"
            
        gender = random.choice(["Male", "Female", "Non-binary"])
        # Inconsistent gender encoding for ~2%
        r_gen = random.random()
        if r_gen < 0.01:
            gender = "M" if gender == "Male" else "F"
        elif r_gen < 0.02:
            gender = gender.lower()
            
        age = int(np.random.normal(34, 10))
        age = max(18, min(75, age))
        # ~0.1% outlier age values
        if random.random() < 0.001:
            age = random.choice([-5, 150, 999])
            
        # Signup date
        delta_days = (end_signup - start_signup).days
        signup_dt = start_signup + timedelta(days=random.randint(0, delta_days))
        signup_str = signup_dt.strftime("%Y-%m-%d")
        
        city, state_full, state_abbr, region = random.choice(CITIES_STATES_REGIONS)
        
        # State naming inconsistency (e.g. KA vs Karnataka)
        state = state_abbr if random.random() < 0.4 else state_full
        if random.random() < 0.02:
            state = state.lower()
            
        segment = np.random.choice(SEGMENTS, p=SEGMENT_WEIGHTS)
        
        # ~0.5% missing customer names or cities
        if random.random() < 0.005:
            name = None
        if random.random() < 0.005:
            city = None
            
        customer_list.append({
            "customer_id": cust_id,
            "customer_name": name,
            "gender": gender,
            "age": age,
            "signup_date": signup_str,
            "city": city,
            "state": state,
            "region": region,
            "customer_segment": segment
        })

    df_customers = pd.DataFrame(customer_list)

    # Duplicate customer records (~0.3%)
    num_dupes = int(len(df_customers) * 0.003)
    dupe_custs = df_customers.sample(n=num_dupes, random_state=seed)
    df_customers = pd.concat([df_customers, dupe_custs], ignore_index=True)

    df_customers.to_csv(os.path.join(output_dir, "customers_raw.csv"), index=False)
    print(f"Generated customers_raw.csv: {len(df_customers)} records")

    # ---------------------------------------------------------
    # 2. GENERATE PRODUCTS (~180 SKUs across 6 categories)
    # ---------------------------------------------------------
    CATEGORIES_DATA = {
        "Electronics": {
            "subcategories": ["Smartphones", "Laptops & Accessories", "Audio & Wearables", "Smart Home", "Cameras"],
            "brands": ["BoatWave", "NoiseFit", "RealmeTech", "MiSmart", "SamsungOptima"],
            "price_range_inr": (999.00, 79999.00),
            "margin_range": (0.18, 0.32)
        },
        "Apparel": {
            "subcategories": ["Ethnic Wear", "Men's Casuals", "Women's Western", "Footwear", "Activewear"],
            "brands": ["FabEthnic", "UrbanBanyan", "ManyavarLike", "AllenCasual", "MetroSteps"],
            "price_range_inr": (499.00, 4999.00),
            "margin_range": (0.50, 0.70)
        },
        "Home & Kitchen": {
            "subcategories": ["Kitchenware", "Mixer Grinders", "Home Furnishings", "Decor & Lighting", "Water Purifiers"],
            "brands": ["PrestigeLike", "MiltonCraft", "BajajHome", "HavellsSmart", "SolimoNest"],
            "price_range_inr": (799.00, 14999.00),
            "margin_range": (0.38, 0.58)
        },
        "Beauty & Personal Care": {
            "subcategories": ["Skincare", "Haircare", "Grooming & Shavers", "Fragrance", "Ayurvedic Care"],
            "brands": ["MamaearthLike", "NykaaStyle", "PlumClean", "ForestEssentials", "BombayGrooming"],
            "price_range_inr": (249.00, 2499.00),
            "margin_range": (0.55, 0.75)
        },
        "Books & Media": {
            "subcategories": ["Indian Fiction", "Competitive Exam Prep", "Business & Finance", "Self-Help", "Children's Books"],
            "brands": ["PenguinIndia", "HarperCollinsIN", "ArihantPub", "RupaBooks", "JaicoPress"],
            "price_range_inr": (199.00, 1499.00),
            "margin_range": (0.35, 0.50)
        },
        "Sports & Outdoors": {
            "subcategories": ["Cricket Gear", "Fitness & Gym Equipment", "Yoga Mats", "Badminton & Tennis", "Outdoor Camping"],
            "brands": ["SGPro", "NiviaSports", "BoldFit", "DecathlonLike", "YonexPro"],
            "price_range_inr": (499.00, 9999.00),
            "margin_range": (0.40, 0.60)
        }
    }

    product_list = []
    prod_counter = 1001

    for cat_name, cat_info in CATEGORIES_DATA.items():
        for subcat in cat_info["subcategories"]:
            for k in range(6):  # 6 * 5 * 6 = 180 items
                prod_id = f"PROD-{prod_counter}"
                brand = random.choice(cat_info["brands"])
                p_name = f"{brand} {subcat} {chr(65 + k)}{k+1}"
                
                min_p, max_p = cat_info["price_range_inr"]
                list_price = round(random.uniform(min_p, max_p), 2)
                
                min_m, max_m = cat_info["margin_range"]
                margin = random.uniform(min_m, max_m)
                cost_price = round(list_price * (1.0 - margin), 2)
                
                # Inconsistent category capitalization (~4%)
                c_cat = cat_name
                r_cat = random.random()
                if r_cat < 0.02:
                    c_cat = cat_name.lower()
                elif r_cat < 0.04:
                    c_cat = cat_name.upper()
                    
                product_list.append({
                    "product_id": prod_id,
                    "product_name": p_name,
                    "category": c_cat,
                    "subcategory": subcat,
                    "brand": brand,
                    "cost_price": cost_price,
                    "list_price": list_price
                })
                prod_counter += 1

    df_products = pd.DataFrame(product_list)
    df_products.to_csv(os.path.join(output_dir, "products_raw.csv"), index=False)
    print(f"Generated products_raw.csv: {len(df_products)} records")

    # ---------------------------------------------------------
    # 3. GENERATE ORDERS (~105,000 order line records)
    # ---------------------------------------------------------
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days + 1

    # Festive Indian Seasonality (Diwali/Navratri surge in Oct/Nov, Freedom Sale in Aug, New Year in Dec)
    day_dates = [start_date + timedelta(days=d) for d in range(total_days)]
    day_weights = []

    for dt in day_dates:
        w = 1.0
        # Oct-Nov Festive Surge (Diwali / Great Indian Sale)
        if dt.month == 10:
            w *= 2.1
            if 15 <= dt.day <= 31:
                w *= 1.4
        elif dt.month == 11:
            w *= 1.8
            if 1 <= dt.day <= 15:
                w *= 1.5
        elif dt.month == 8:  # Independence Day Freedom Sale
            w *= 1.5
            if 10 <= dt.day <= 18:
                w *= 1.6
        elif dt.month == 12:  # Year-End Shopping
            w *= 1.4
        elif dt.month in [1, 2]:  # Post-festive dip
            w *= 0.8
            
        # YoY Growth
        if dt.year == 2024:
            w *= 1.25
        elif dt.year == 2025:
            w *= 1.52
            
        # Weekend boost
        if dt.weekday() in [5, 6]:
            w *= 1.12
            
        day_weights.append(w)

    day_weights = np.array(day_weights) / sum(day_weights)

    cust_ids = df_customers["customer_id"].unique()
    num_unique_cust = len(cust_ids)
    cust_p = np.random.pareto(a=1.5, size=num_unique_cust)
    cust_p /= sum(cust_p)

    # Indian Payment Methods
    PAYMENT_METHODS = ["UPI", "Cash on Delivery", "Credit Card", "Debit Card", "Net Banking", "Digital Wallet"]
    PAYMENT_WEIGHTS = [0.52, 0.22, 0.12, 0.08, 0.04, 0.02]

    # Order Statuses
    STATUSES = ["Completed", "Shipped", "Processing", "Cancelled", "Returned"]
    STATUS_WEIGHTS = [0.75, 0.12, 0.04, 0.04, 0.05]

    # Discounts (0%, 5%, 10%, 15%, 20%, 25%, 30%, 40%)
    DISCOUNT_CHOICES = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
    DISCOUNT_WEIGHTS = [0.42, 0.20, 0.16, 0.10, 0.06, 0.03, 0.02, 0.01]

    orders_list = []
    order_id_counter = 100001
    lines_generated = 0

    products_records = df_products.to_dict("records")
    prod_weights = np.random.pareto(a=1.8, size=len(products_records))
    prod_weights /= sum(prod_weights)

    while lines_generated < num_rows:
        order_id = f"ORD-{order_id_counter}"
        
        chosen_day_idx = np.random.choice(total_days, p=day_weights)
        order_date_dt = day_dates[chosen_day_idx]
        order_date_str = order_date_dt.strftime("%Y-%m-%d")
        
        cust_id = np.random.choice(cust_ids, p=cust_p)
        pay_method = np.random.choice(PAYMENT_METHODS, p=PAYMENT_WEIGHTS)
        status = np.random.choice(STATUSES, p=STATUS_WEIGHTS)
        
        items_in_order = random.choices([1, 2, 3, 4], weights=[0.55, 0.28, 0.12, 0.05])[0]
        chosen_prods_idx = np.random.choice(len(products_records), size=items_in_order, replace=False, p=prod_weights)
        
        for p_idx in chosen_prods_idx:
            p = products_records[p_idx]
            qty = random.choices([1, 2, 3, 4, 5], weights=[0.70, 0.18, 0.07, 0.03, 0.02])[0]
            
            u_price = p["list_price"]
            
            # Festive season higher discount probability
            if order_date_dt.month in [10, 11]:
                disc = random.choices(DISCOUNT_CHOICES, weights=[0.28, 0.22, 0.20, 0.14, 0.08, 0.05, 0.02, 0.01])[0]
            else:
                disc = random.choices(DISCOUNT_CHOICES, weights=DISCOUNT_WEIGHTS)[0]
                
            ship_cost = round(random.choice([0.0, 49.0, 79.0, 99.0, 149.0]), 2)
            
            # Intentional Data Quality Flaws
            c_id_final = cust_id
            if random.random() < 0.002:
                c_id_final = None
                
            pay_method_final = pay_method
            if random.random() < 0.002:
                pay_method_final = None
                
            if random.random() < 0.0005:
                qty = random.choice([-1, 0])
                
            o_date_final = order_date_str
            if random.random() < 0.0005:
                o_date_final = "2024-02-30"
                
            orders_list.append({
                "order_id": order_id,
                "order_date": o_date_final,
                "customer_id": c_id_final,
                "product_id": p["product_id"],
                "quantity": qty,
                "unit_price": u_price,
                "discount": disc,
                "shipping_cost": ship_cost,
                "payment_method": pay_method_final,
                "order_status": status
            })
            
            lines_generated += 1
            if lines_generated >= num_rows:
                break
                
        order_id_counter += 1

    df_orders = pd.DataFrame(orders_list)

    # Intentional duplicate order lines (~0.4%)
    num_order_dupes = int(len(df_orders) * 0.004)
    dupe_orders = df_orders.sample(n=num_order_dupes, random_state=seed)
    df_orders = pd.concat([df_orders, dupe_orders], ignore_index=True)

    df_orders.to_csv(os.path.join(output_dir, "orders_raw.csv"), index=False)
    print(f"Generated orders_raw.csv: {len(df_orders)} records")

    # ---------------------------------------------------------
    # 4. GENERATE RETURNS (~6,000)
    # ---------------------------------------------------------
    returned_orders = df_orders[df_orders["order_status"] == "Returned"].copy()

    additional_needed = int(len(df_orders) * 0.055) - len(returned_orders)
    if additional_needed > 0:
        eligible = df_orders[df_orders["order_status"].isin(["Completed", "Shipped"])].sample(n=additional_needed, random_state=seed)
        returned_orders = pd.concat([returned_orders, eligible], ignore_index=True)

    return_reasons = ["Defective Product", "Wrong Size/Color", "Item Not as Described", "Changed Mind", "Late Delivery"]
    return_weights = [0.28, 0.32, 0.18, 0.14, 0.08]

    returns_list = []
    return_counter = 300001

    for idx, row in returned_orders.iterrows():
        ret_id = f"RET-{return_counter}"
        o_id = row["order_id"]
        
        try:
            o_dt = datetime.strptime(str(row["order_date"]), "%Y-%m-%d")
        except ValueError:
            o_dt = datetime(2024, 6, 15)
            
        ret_dt = o_dt + timedelta(days=random.randint(2, 18))
        ret_dt_str = ret_dt.strftime("%Y-%m-%d")
        
        ret_qty = max(1, row["quantity"])
        reason = np.random.choice(return_reasons, p=return_weights)
        
        returns_list.append({
            "return_id": ret_id,
            "order_id": o_id,
            "return_date": ret_dt_str,
            "quantity_returned": ret_qty,
            "return_reason": reason
        })
        return_counter += 1

    df_returns = pd.DataFrame(returns_list)
    df_returns.to_csv(os.path.join(output_dir, "returns_raw.csv"), index=False)
    print(f"Generated returns_raw.csv: {len(df_returns)} records")

    # ---------------------------------------------------------
    # 5. GENERATE PAYMENTS (~60,000+ unique order payments)
    # ---------------------------------------------------------
    valid_orders = df_orders[df_orders["quantity"] > 0].copy()
    valid_orders["line_revenue"] = valid_orders["quantity"] * valid_orders["unit_price"] * (1.0 - valid_orders["discount"]) + valid_orders["shipping_cost"]

    order_totals = valid_orders.groupby(["order_id", "order_date", "payment_method", "order_status"])["line_revenue"].sum().reset_index()

    payments_list = []
    pay_counter = 400001

    for idx, row in order_totals.iterrows():
        pay_id = f"PAY-{pay_counter}"
        o_id = row["order_id"]
        o_date = row["order_date"]
        p_method = row["payment_method"]
        status = row["order_status"]
        amt = round(row["line_revenue"], 2)
        
        if status == "Cancelled":
            p_status = "Failed"
        elif status == "Returned":
            p_status = "Refunded"
        else:
            p_status = "Completed"
            
        if random.random() < 0.003:
            p_status = None
            
        payments_list.append({
            "payment_id": pay_id,
            "order_id": o_id,
            "payment_date": o_date,
            "payment_method": p_method,
            "payment_status": p_status,
            "payment_amount": amt
        })
        pay_counter += 1

    df_payments = pd.DataFrame(payments_list)
    df_payments.to_csv(os.path.join(output_dir, "payments_raw.csv"), index=False)
    print(f"Generated payments_raw.csv: {len(df_payments)} records")

    print("\n--- RAW DATA GENERATION COMPLETED SUCCESSFULLY ---")

if __name__ == "__main__":
    args = parse_args()
    generate_raw_data(num_rows=args.rows, seed=args.seed, output_dir=args.output_dir)
