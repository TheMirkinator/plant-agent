from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import get_plants_needing_water
from logging_setup import logger
from anthropic import Anthropic
from dotenv import load_dotenv
from telegram_notifications import send_telegram_message
from weather import get_current_weather


load_dotenv()
client = Anthropic()

# Store the last notification so we don't spam
last_notification = {"time": None, "message": None}

def check_plants_daily():
    """Daily task: Check which plants need water and generate a notification."""
    # Force refresh weather at 8 AM
    get_current_weather(force_refresh=True)
    
    plants_needing_water = get_plants_needing_water()
    
    if not plants_needing_water:
        message = "🌿 Good morning! All your plants are well-watered. Keep up the great care!"
        logger.info("Daily check: All plants are fine")
    else:
        # Format the list nicely
        plant_names = ", ".join([p['name'] for p in plants_needing_water])
        
        prompt = f"""The user has these plants that need watering today: {plant_names}. 
        Generate a friendly, motivating morning message reminding them to water these specific plants. 
        Keep it to 2-3 sentences and warm in tone."""
        
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        message = response.content[0].text
        logger.info(f"Daily check: Plants need water: {plant_names}")
    
    # Store the notification
    last_notification["message"] = message
    
    # Send via Telegram
    send_telegram_message(message)
    print(f"\n🌿 Telegram notification sent: {message[:50]}...")

def start_scheduler():
    """Start the background scheduler."""
    scheduler = BackgroundScheduler()
    
    # Run daily at 7:30 AM
    scheduler.add_job(
        check_plants_daily,
        trigger=CronTrigger(hour=7, minute=30, timezone='America/New_York'),
        id='daily_plant_check',
        name='Daily plant water check',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started - will check plants daily at 7:30 AM")
    
    return scheduler

def get_last_notification():
    """Get the last generated notification."""
    return last_notification["message"]