import requests
import time
from collections import defaultdict
from threading import Timer
from logging_setup import logger
from anthropic import Anthropic
from dotenv import load_dotenv
import os
from database import build_plant_context
from prompts import PLANT_CARE_SYSTEM, USER_CONFIG
from weather import get_watering_adjustment
from image_handler import download_telegram_image, analyze_plant_image

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
client = Anthropic()

last_update_id = 0

def get_telegram_updates():
    """Fetch new messages from Telegram."""
    global last_update_id
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 30}
    try:
        response = requests.get(url, params=params, timeout=35)
        data = response.json()
        if data.get("ok"):
            return data.get("result", [])
        else:
            logger.error(f"Telegram error: {data}")
            return []
    except Exception as e:
        logger.error(f"Failed to get Telegram updates: {e}")
        return []

def send_telegram_response(message):
    """Send a message back to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info("Telegram response sent")
            return True
        else:
            logger.error(f"Failed to send response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending Telegram response: {e}")
        return False

def process_telegram_message(user_message):
    """Process a Telegram message with Claude."""
    
    plant_context = build_plant_context()
    weather_data = get_watering_adjustment()  # Gets cached or fresh if old
    
    system_prompt = PLANT_CARE_SYSTEM.format(
        plant_context=plant_context,
        weather_data=weather_data,
        **USER_CONFIG
    )
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Claude error: {e}")
        return f"Sorry, I had an error: {e}"

# Store messages by chat, with timestamps
message_buffer = defaultdict(list)
pending_timers = {}

def send_batched_response(chat_id):
    """Send response after collecting messages."""
    global message_buffer, pending_timers
    
    if chat_id not in message_buffer or not message_buffer[chat_id]:
        return
    
    # Combine all messages
    messages = message_buffer[chat_id]
    combined_message = "\n".join(messages)
    
    logger.info(f"Sending batched response for {len(messages)} message(s)")
    
    response = process_telegram_message(combined_message)
    send_telegram_response(response)
    
    # Clear buffer
    message_buffer[chat_id] = []
    if chat_id in pending_timers:
        del pending_timers[chat_id]

def handle_telegram_messages():
    """Poll for messages and batch them."""
    global last_update_id, message_buffer, pending_timers
    
    updates = get_telegram_updates()
    processed_ids = set()
    
    for update in updates:
        update_id = update["update_id"]
        
        if update_id <= last_update_id or update_id in processed_ids:
            continue
        
        processed_ids.add(update_id)
        last_update_id = update_id
        
        if "message" in update:
            message = update["message"]
            chat_id = message.get("chat", {}).get("id")
            
            # Handle text messages
            user_message = message.get("text", "")
            if user_message:
                logger.info(f"Telegram message received: {user_message}")
                
                # Add to buffer
                message_buffer[chat_id].append(user_message)
                
                # Cancel previous timer if exists
                if chat_id in pending_timers:
                    pending_timers[chat_id].cancel()
                
                # Set new timer (wait 3 seconds for more messages)
                timer = Timer(3.0, send_batched_response, args=[chat_id])
                timer.daemon = True
                timer.start()
                pending_timers[chat_id] = timer
            
            # Handle image messages (process immediately, don't batch)
            elif "photo" in message:
                logger.info("Plant image received")
                photos = message["photo"]
                file_id = photos[-1]["file_id"]
                base64_image = download_telegram_image(file_id)
                
                if base64_image:
                    analysis = analyze_plant_image(base64_image)
                    send_telegram_response(f"🌿 Plant Analysis:\n\n{analysis}")
                else:
                    send_telegram_response("Sorry, I couldn't download the image. Try again!")