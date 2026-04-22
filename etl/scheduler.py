import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from apscheduler.schedulers.blocking import BlockingScheduler
from pipeline import run_pipeline
import logging

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/scheduler.log',
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s'
)

scheduler = BlockingScheduler()

# Run every day at 8:00 AM
scheduler.add_job(
    run_pipeline,
    trigger='cron',
    hour=8,
    minute=0,
    id='inventory_etl_job'
)

print("✅ Scheduler started — pipeline will run every day at 8:00 AM")
print("   Press Ctrl+C to stop\n")
logging.info("Scheduler started")

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("\n🛑 Scheduler stopped.")
    logging.info("Scheduler stopped")