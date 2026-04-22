import pandas as pd
import logging
import os

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/pipeline.log',
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s'
)

def extract():
    logging.info("EXTRACT phase started")
    try:
        BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        suppliers = pd.read_csv(os.path.join(BASE_DIR, 'data/raw/suppliers.csv'))
        products  = pd.read_csv(os.path.join(BASE_DIR, 'data/raw/products.csv'))
        stock     = pd.read_csv(os.path.join(BASE_DIR, 'data/raw/stock.csv'))
        sales     = pd.read_csv(os.path.join(BASE_DIR, 'data/raw/sales.csv'))
        logging.info(f"Extracted — suppliers:{len(suppliers)}, products:{len(products)}, stock:{len(stock)}, sales:{len(sales)}")
        return suppliers, products, stock, sales
    except Exception as e:
        logging.error(f"EXTRACT failed: {e}")
        raise

def validate_raw(suppliers, products, stock, sales):
    logging.info("Validation started")
    errors = []

    if len(suppliers) == 0: errors.append("suppliers table is empty")
    if len(products) == 0:  errors.append("products table is empty")
    if len(sales) == 0:     errors.append("sales table is empty")

    if products['product_id'].isnull().any():
        errors.append("product_id has nulls in products table")
    if sales['sale_id'].isnull().any():
        errors.append("sale_id has nulls in sales table")

    if products['product_id'].duplicated().any():
        errors.append("Duplicate product_ids found")
    if sales['sale_id'].duplicated().any():
        errors.append("Duplicate sale_ids found")

    if errors:
        for e in errors:
            logging.error(f"Validation error: {e}")
        raise ValueError(f"Data quality checks failed: {errors}")
    
    logging.info("Validation passed")

def transform(suppliers, products, stock, sales):
    logging.info("TRANSFORM phase started")

    # Clean products
    before = len(products)
    products['unit_price'] = products['unit_price'].fillna(products['unit_price'].median())
    products['product_name'] = products['product_name'].str.strip()
    products['category'] = products['category'].str.strip().str.title()
    logging.info(f"Products cleaned — {before} rows retained")

    # Clean sales
    before = len(sales)
    sales = sales.dropna(subset=['quantity_sold'])
    sales['quantity_sold'] = sales['quantity_sold'].astype(int)
    sales['sale_date'] = pd.to_datetime(sales['sale_date'])
    after = len(sales)
    logging.info(f"Sales cleaned — dropped {before - after} null rows, {after} rows retained")

    # Clean stock
    stock['last_updated'] = pd.to_datetime(stock['last_updated'])

    # Enrich sales
    sales_enriched = sales.merge(
        products[['product_id','product_name','category','unit_price','supplier_id']],
        on='product_id', how='left'
    )
    sales_enriched['revenue'] = sales_enriched['quantity_sold'] * sales_enriched['unit_price']
    sales_enriched['year']    = sales_enriched['sale_date'].dt.year
    sales_enriched['month']   = sales_enriched['sale_date'].dt.month
    sales_enriched['quarter'] = sales_enriched['sale_date'].dt.quarter

    # Flag low stock
    stock_enriched = stock.merge(
        products[['product_id','reorder_level']],
        on='product_id', how='left'
    )
    stock_enriched['is_low_stock'] = stock_enriched['quantity_in_stock'] < stock_enriched['reorder_level']

    logging.info("TRANSFORM phase complete")
    return suppliers, products, stock_enriched, sales_enriched