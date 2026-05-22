import requests
from logging_setup import logger
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LATITUDE = 40.8239
LONGITUDE = -74.2113

# Cache variables
weather_cache = None
cache_timestamp = None
CACHE_DURATION_MINUTES = 30

def is_cache_valid():
    """Check if cached weather is still fresh."""
    global cache_timestamp
    if cache_timestamp is None:
        return False
    return datetime.now() - cache_timestamp < timedelta(minutes=CACHE_DURATION_MINUTES)

def get_current_weather(force_refresh=False):
    """Get current weather and 7-day forecast with caching."""
    global weather_cache, cache_timestamp
    
    # Return cache if valid and not forcing refresh
    if not force_refresh and is_cache_valid() and weather_cache:
        logger.info("Using cached weather data")
        return weather_cache
    
    if not OPENWEATHER_API_KEY:
        logger.error("OpenWeather API key not set")
        return weather_cache or "Weather data unavailable"
    
    url = "https://api.openweathermap.org/data/2.5/forecast"
    
    params = {
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            weather_cache = parse_weather_data(data)
            cache_timestamp = datetime.now()
            logger.info("Weather data fetched and cached")
            return weather_cache
        else:
            logger.error(f"OpenWeather error: {data}")
            return weather_cache or "Weather data unavailable"
    except Exception as e:
        logger.error(f"Failed to get weather: {e}")
        return weather_cache or "Weather data unavailable"

def parse_weather_data(data):
    """Parse OpenWeather forecast data into readable format."""
    forecasts = data.get("list", [])
    
    weather_summary = "7-Day Weather Forecast for your garden:\n"
    
    current_date = None
    day_count = 0
    
    for forecast in forecasts:
        dt = datetime.fromtimestamp(forecast["dt"])
        date_str = dt.strftime("%Y-%m-%d")
        
        if current_date != date_str and day_count < 7:
            current_date = date_str
            day_count += 1
            
            temp = forecast["main"]["temp"]
            condition = forecast["weather"][0]["main"]
            humidity = forecast["main"]["humidity"]
            rain_chance = forecast.get("pop", 0) * 100
            
            weather_summary += f"\n{dt.strftime('%A, %B %d')}:\n"
            weather_summary += f"  Temperature: {temp}°F\n"
            weather_summary += f"  Condition: {condition}\n"
            weather_summary += f"  Humidity: {humidity}%\n"
            weather_summary += f"  Rain chance: {rain_chance:.0f}%\n"
    
    return weather_summary

def get_watering_adjustment():
    """Get fresh weather data and return it."""
    return get_current_weather(force_refresh=False)