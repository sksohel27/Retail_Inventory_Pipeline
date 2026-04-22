import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from transform import extract, validate_raw, transform
from load import get_engine, create_schema, load
import logging

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/pipeline.log',
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s'
)

def run_pipeline():
    print("\n🚀 Starting Inventory ETL Pipeline...\n")
    logging.info("========== PIPELINE RUN STARTED ==========")

    try:
        print("📥 Step 1: Extracting raw data...")
        suppliers, products, stock, sales = extract()

        print("🔍 Step 2: Validating raw data...")
        validate_raw(suppliers, products, stock, sales)

        print("⚙️  Step 3: Transforming data...")
        suppliers, products, stock, sales = transform(suppliers, products, stock, sales)

        print("📤 Step 4: Loading into PostgreSQL...")
        engine = get_engine()
        create_schema(engine)
        load(suppliers, products, stock, sales, engine)

        print("\n✅ Pipeline completed successfully!")
        logging.info("========== PIPELINE RUN COMPLETED ==========")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        logging.error(f"PIPELINE FAILED: {e}")

if __name__ == "__main__":
    run_pipeline()