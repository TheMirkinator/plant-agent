from scheduler import start_scheduler
from logging_setup import setup_logging
from database import init_db
import time

setup_logging()
init_db()

print("🌿 Plant Bot Scheduler Running...")
scheduler = start_scheduler()

# Keep the process alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()
    print("Scheduler stopped.")