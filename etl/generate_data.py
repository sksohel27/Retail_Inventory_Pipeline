import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# So we get the same data every time we run
random.seed(42)
np.random.seed(42)

# --- CONFIG ---
NUM_PRODUCTS = 50
NUM_SUPPLIERS = 10
NUM_SALES = 500

# --- CATEGORIES ---
categories = ['Electronics', 'Clothing', 'Groceries', 'Furniture', 'Stationery']

# --- SUPPLIERS ---
suppliers = pd.DataFrame({
    'supplier_id': [f'SUP{str(i).zfill(3)}' for i in range(1, NUM_SUPPLIERS + 1)],
    'supplier_name': [f'Supplier_{i}' for i in range(1, NUM_SUPPLIERS + 1)],
    'contact_email': [f'supplier{i}@email.com' for i in range(1, NUM_SUPPLIERS + 1)],
    'city': random.choices(['Kolkata', 'Mumbai', 'Delhi', 'Chennai', 'Bangalore'], k=NUM_SUPPLIERS)
})

# --- PRODUCTS ---
products = pd.DataFrame({
    'product_id': [f'PRD{str(i).zfill(3)}' for i in range(1, NUM_PRODUCTS + 1)],
    'product_name': [f'Product_{i}' for i in range(1, NUM_PRODUCTS + 1)],
    'category': random.choices(categories, k=NUM_PRODUCTS),
    'unit_price': np.round(np.random.uniform(50, 5000, NUM_PRODUCTS), 2),
    'reorder_level': np.random.randint(5, 20, NUM_PRODUCTS),
    'supplier_id': random.choices(suppliers['supplier_id'].tolist(), k=NUM_PRODUCTS)
})

# --- STOCK ---
stock = pd.DataFrame({
    'product_id': products['product_id'],
    'quantity_in_stock': np.random.randint(0, 100, NUM_PRODUCTS),
    'last_updated': datetime.today().strftime('%Y-%m-%d')
})

# --- SALES ---
start_date = datetime(2024, 1, 1)
sales_dates = [start_date + timedelta(days=random.randint(0, 364)) for _ in range(NUM_SALES)]

sales = pd.DataFrame({
    'sale_id': [f'SAL{str(i).zfill(4)}' for i in range(1, NUM_SALES + 1)],
    'product_id': random.choices(products['product_id'].tolist(), k=NUM_SALES),
    'quantity_sold': np.random.randint(1, 20, NUM_SALES),
    'sale_date': [d.strftime('%Y-%m-%d') for d in sales_dates],
    'customer_city': random.choices(['Kolkata', 'Mumbai', 'Delhi', 'Chennai', 'Bangalore'], k=NUM_SALES)
})

# Introduce some dirty data intentionally (so you have something to clean)
sales.loc[random.sample(range(NUM_SALES), 10), 'quantity_sold'] = None  # nulls
products.loc[random.sample(range(NUM_PRODUCTS), 3), 'unit_price'] = None  # nulls

# --- SAVE ---
os.makedirs('data/raw', exist_ok=True)
suppliers.to_csv('data/raw/suppliers.csv', index=False)
products.to_csv('data/raw/products.csv', index=False)
stock.to_csv('data/raw/stock.csv', index=False)
sales.to_csv('data/raw/sales.csv', index=False)

print("✅ Raw data generated successfully in data/raw/")
print(f"   Suppliers : {len(suppliers)} rows")
print(f"   Products  : {len(products)} rows")
print(f"   Stock     : {len(stock)} rows")
print(f"   Sales     : {len(sales)} rows")