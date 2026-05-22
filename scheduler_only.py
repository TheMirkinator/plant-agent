from scheduler import start_scheduler
from telegram_handler import handle_telegram_messages
from logging_setup import setup_logging
from database import init_db
import time

setup_logging()
init_db()

print("🌿 Plant Bot Scheduler + Telegram Handler Running...")
scheduler = start_scheduler()

# Keep the process alive and handle Telegram messages
try:
    while True:
        handle_telegram_messages()  # Check for new messages every 2 seconds
        time.sleep(2)
except KeyboardInterrupt:
    scheduler.shutdown()
    print("Scheduler stopped.")