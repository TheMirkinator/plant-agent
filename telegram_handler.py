import requests
from logging_setup import logger
from anthropic import Anthropic
from dotenv import load_dotenv
import os
from database import build_plant_context
from prompts import PLANT_CARE_SYSTEM, USER_CONFIG

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
    system_prompt = PLANT_CARE_SYSTEM.format(
        plant_context=plant_context,
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

def handle_telegram_messages():
    """Poll for messages and process them."""
    global last_update_id
    updates = get_telegram_updates()
    
    for update in updates:
        update_id = update["update_id"]
        if update_id <= last_update_id:
            continue
        last_update_id = update_id
        
        if "message" in update:
            message = update["message"]
            user_message = message.get("text", "")
            if user_message:
                logger.info(f"Telegram message received: {user_message}")
                response = process_telegram_message(user_message)
                send_telegram_response(response)