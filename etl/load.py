import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import logging

load_dotenv()

def get_engine():
    user     = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host     = os.getenv('DB_HOST')
    port     = os.getenv('DB_PORT')
    dbname   = os.getenv('DB_NAME')
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(url)

def create_schema(engine):
    schema_sql = """
    CREATE TABLE IF NOT EXISTS dim_supplier (
        supplier_id   VARCHAR(10) PRIMARY KEY,
        supplier_name VARCHAR(100),
        contact_email VARCHAR(100),
        city          VARCHAR(50)
    );

    CREATE TABLE IF NOT EXISTS dim_product (
        product_id    VARCHAR(10) PRIMARY KEY,
        product_name  VARCHAR(100),
        category      VARCHAR(50),
        unit_price    NUMERIC(10,2),
        reorder_level INT,
        supplier_id   VARCHAR(10) REFERENCES dim_supplier(supplier_id)
    );

    CREATE TABLE IF NOT EXISTS dim_date (
        date_id    DATE PRIMARY KEY,
        year       INT,
        month      INT,
        quarter    INT,
        month_name VARCHAR(20)
    );

    CREATE TABLE IF NOT EXISTS fact_sales (
        sale_id       VARCHAR(10) PRIMARY KEY,
        product_id    VARCHAR(10) REFERENCES dim_product(product_id),
        quantity_sold INT,
        sale_date     DATE,
        customer_city VARCHAR(50),
        revenue       NUMERIC(10,2),
        year          INT,
        month         INT,
        quarter       INT
    );

    CREATE TABLE IF NOT EXISTS fact_stock (
        product_id        VARCHAR(10) REFERENCES dim_product(product_id),
        quantity_in_stock INT,
        reorder_level     INT,
        is_low_stock      BOOLEAN,
        last_updated      DATE
    );
    """
    with engine.connect() as conn:
        conn.execute(text(schema_sql))
        conn.commit()
    logging.info("Schema created/verified")

def load(suppliers, products, stock, sales, engine):
    dates = sales[['sale_date','year','month','quarter']].drop_duplicates().copy()
    dates = dates.rename(columns={'sale_date': 'date_id'})
    dates['month_name'] = dates['date_id'].dt.strftime('%B')

    # Drop tables in correct order first (child tables before parent tables)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fact_stock CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS fact_sales CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS dim_date CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS dim_product CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS dim_supplier CASCADE"))
        conn.commit()

    # Recreate schema fresh
    create_schema(engine)

    # Load in correct order (parent tables before child tables)
    tables = {
        'dim_supplier' : suppliers,
        'dim_product'  : products[['product_id','product_name','category','unit_price','reorder_level','supplier_id']],
        'dim_date'     : dates,
        'fact_sales'   : sales[['sale_id','product_id','quantity_sold','sale_date','customer_city','revenue','year','month','quarter']],
        'fact_stock'   : stock[['product_id','quantity_in_stock','reorder_level','is_low_stock','last_updated']]
    }

    for table_name, df in tables.items():
        df.to_sql(table_name, engine, if_exists='append', index=False)
        logging.info(f"Loaded {len(df)} rows into {table_name}")
        print(f"✅ Loaded {len(df)} rows → {table_name}")