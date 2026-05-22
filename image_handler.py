import requests
import base64
from logging_setup import logger
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def download_telegram_image(file_id):
    """Download image from Telegram and return base64."""
    try:
        # Get file path from Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
        params = {"file_id": file_id}
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data.get("ok"):
            logger.error(f"Failed to get file: {data}")
            return None
        
        file_path = data["result"]["file_path"]
        
        # Download the actual image
        download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        image_response = requests.get(download_url)
        
        if image_response.status_code == 200:
            # Convert to base64
            base64_image = base64.b64encode(image_response.content).decode('utf-8')
            logger.info("Image downloaded and converted to base64")
            return base64_image
        else:
            logger.error(f"Failed to download image: {image_response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None

def analyze_plant_image(base64_image):
    """Send image to Claude for plant analysis."""
    from anthropic import Anthropic
    from prompts import PLANT_CARE_SYSTEM, USER_CONFIG
    from database import build_plant_context
    
    client = Anthropic()
    
    plant_context = build_plant_context()
    
    system_prompt = PLANT_CARE_SYSTEM.format(
        plant_context=plant_context,
        weather_data="",  # Optional weather context
        **USER_CONFIG
    )
    
    # Build the analysis prompt
    analysis_prompt = """You are analyzing a plant photo that the user sent. 

Provide:
1. Plant identification (what type of plant is this?)
2. Health assessment (looks healthy, stressed, diseased?)
3. Issues detected (if any - pests, diseases, nutrient deficiency, etc.)
4. Specific treatment recommendations
5. Urgency level (monitor, treat soon, treat immediately)

Be practical and actionable."""
    
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=500,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": analysis_prompt
                        }
                    ]
                }
            ]
        )
        
        return response.content[0].text
    except Exception as e:
        logger.error(f"Claude vision error: {e}")
        return f"Sorry, I couldn't analyze the image: {e}"