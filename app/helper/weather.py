import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.environ['WEATHER_API_KEY']

def get_weather(location: str) -> str:
    data = requests.get(f"http://api.weatherapi.com/v1/current.json?key=7f24db82b3cd4cd5949183322252201&q={location.lower()}&aqi=yes").json()

    return data['current']