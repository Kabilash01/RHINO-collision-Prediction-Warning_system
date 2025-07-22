# routing.py - Enhanced Multi-Provider Routing
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Import the new multi-provider router
try:
    from multi_map_router import MultiMapRouter, get_route_multi_provider
    USE_MULTI_PROVIDER = True
except ImportError:
    USE_MULTI_PROVIDER = False
    print("[WARNING] Multi-provider router not available, using Google Maps only")

# Legacy Google Maps implementation (kept for compatibility)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_route(origin, destination):
    """Enhanced routing with multi-provider support"""
    
    if USE_MULTI_PROVIDER:
        # Use new multi-provider system
        try:
            router = MultiMapRouter()
            route_data = router.get_route(origin, destination)
            
            # Convert to legacy format for compatibility
            directions = route_data['steps'] if route_data['steps'] else [
                f"Navigate from {origin} to {destination}",
                f"Distance: {route_data['distance']}",
                f"Duration: {route_data['duration']}"
            ]
            
            print(f"[INFO] Route via {route_data['provider']}")
            return directions
            
        except Exception as e:
            print(f"[WARNING] Multi-provider routing failed: {e}")
            # Fall back to Google Maps
    
    # Legacy Google Maps implementation
    return get_route_google_legacy(origin, destination)

def get_route_google_legacy(origin, destination):
    """Legacy Google Maps routing (fallback)"""
    if not GOOGLE_MAPS_API_KEY:
        return [
            "Navigation API not configured.",
            f"Please navigate from {origin} to {destination} using your preferred map app.",
            "Consider configuring alternative map providers in .env file."
        ]
    
    url = f"https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving",
        "avoid": "ferries",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    try:
        res = requests.get(url, params=params).json()
        if res["status"] != "OK":
            print("[❌] Google Maps API error:", res["status"])
            return [f"Unable to get directions from {origin} to {destination}"]
        
        steps = res["routes"][0]["legs"][0]["steps"]
        directions = [step["html_instructions"].replace("<b>", "").replace("</b>", "") for step in steps]
        print("[INFO] Route via Google Maps")
        return directions
        
    except Exception as e:
        print(f"[ERROR] Google Maps routing failed: {e}")
        return [f"Navigation error. Please use alternative navigation app."]

def get_route_voice_friendly(origin, destination):
    """Get route formatted for voice output"""
    if USE_MULTI_PROVIDER:
        return get_route_multi_provider(origin, destination)
    else:
        directions = get_route(origin, destination)
        if len(directions) > 3:
            # Summarize for voice
            return f"Route from {origin} to {destination}: {'. '.join(directions[:3])} and {len(directions)-3} more steps."
        else:
            return f"Route from {origin} to {destination}: {'. '.join(directions)}"
