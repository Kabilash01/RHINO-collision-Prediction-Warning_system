# routing.py
import requests
import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_route(origin, destination):
    url = f"https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving",
        "avoid": "ferries",
        "key": GOOGLE_MAPS_API_KEY
    }
    res = requests.get(url, params=params).json()
    if res["status"] != "OK":
        print("[❌] Google Maps API error:", res["status"])
        return []
    
    steps = res["routes"][0]["legs"][0]["steps"]
    directions = [step["html_instructions"].replace("<b>", "").replace("</b>", "") for step in steps]
    return directions
