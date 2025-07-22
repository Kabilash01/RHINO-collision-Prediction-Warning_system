# Enhanced Multi-Provider Routing System
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

class MultiMapRouter:
    """Unified routing interface supporting multiple map providers"""
    
    def __init__(self):
        self.provider = os.getenv("MAP_SERVICE_PROVIDER", "openroute").lower()
        self.setup_credentials()
    
    def setup_credentials(self):
        """Setup API credentials for different providers"""
        self.credentials = {
            'google': os.getenv("GOOGLE_MAPS_API_KEY"),
            'openroute': os.getenv("OPENROUTESERVICE_API_KEY"),
            'mapbox': os.getenv("MAPBOX_ACCESS_TOKEN"),
            'here': os.getenv("HERE_API_KEY"),
            'mapquest': os.getenv("MAPQUEST_API_KEY"),
            'bing': os.getenv("BING_MAPS_API_KEY")
        }
    
    def get_route(self, origin, destination, mode="driving"):
        """Get route from specified provider or fallback to available ones"""
        
        # Try primary provider first
        try:
            return self._get_route_by_provider(self.provider, origin, destination, mode)
        except Exception as e:
            print(f"[WARNING] Primary provider '{self.provider}' failed: {e}")
        
        # Fallback to other available providers
        fallback_order = ['openroute', 'mapbox', 'google', 'here', 'mapquest', 'bing']
        
        for provider in fallback_order:
            if provider != self.provider and self.credentials.get(provider):
                try:
                    print(f"[INFO] Trying fallback provider: {provider}")
                    return self._get_route_by_provider(provider, origin, destination, mode)
                except Exception as e:
                    print(f"[WARNING] Provider '{provider}' failed: {e}")
                    continue
        
        # Final fallback to offline/simple directions
        return self._get_offline_route(origin, destination)
    
    def _get_route_by_provider(self, provider, origin, destination, mode):
        """Route using specific provider"""
        
        if provider == 'google':
            return self._google_route(origin, destination, mode)
        elif provider == 'openroute':
            return self._openroute_route(origin, destination, mode)
        elif provider == 'mapbox':
            return self._mapbox_route(origin, destination, mode)
        elif provider == 'here':
            return self._here_route(origin, destination, mode)
        elif provider == 'mapquest':
            return self._mapquest_route(origin, destination, mode)
        elif provider == 'bing':
            return self._bing_route(origin, destination, mode)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _google_route(self, origin, destination, mode):
        """Google Maps Directions API"""
        api_key = self.credentials['google']
        if not api_key:
            raise ValueError("Google Maps API key not configured")
        
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] != "OK":
            raise Exception(f"Google Maps API error: {data['status']}")
        
        route = data["routes"][0]["legs"][0]
        return {
            "provider": "Google Maps",
            "distance": route["distance"]["text"],
            "duration": route["duration"]["text"],
            "steps": [step["html_instructions"].replace("<b>", "").replace("</b>", "") 
                     for step in route["steps"]]
        }
    
    def _openroute_route(self, origin, destination, mode):
        """OpenRouteService API (FREE alternative)"""
        api_key = self.credentials['openroute']
        if not api_key:
            # Try without API key (limited requests)
            api_key = "5b3ce3597851110001cf6248YOUR_API_KEY_HERE"
        
        # Convert locations to coordinates (simplified - you may want to use geocoding)
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        
        # For demo, using approximate coordinates
        # In production, you'd geocode the addresses first
        body = {
            "coordinates": [[77.5946, 12.9716], [77.6412, 13.0827]],  # Bangalore coordinates
            "format": "json",
            "instructions": True
        }
        
        response = requests.post(url, json=body, headers=headers)
        data = response.json()
        
        if 'routes' not in data:
            raise Exception("OpenRouteService error")
        
        route = data["routes"][0]
        return {
            "provider": "OpenRouteService",
            "distance": f"{route['summary']['distance']/1000:.1f} km",
            "duration": f"{route['summary']['duration']/60:.0f} minutes",
            "steps": [step["instruction"] for step in route["segments"][0]["steps"]]
        }
    
    def _mapbox_route(self, origin, destination, mode):
        """Mapbox Directions API - RECOMMENDED for RHINO-CAR"""
        access_token = self.credentials['mapbox']
        if not access_token:
            raise ValueError("Mapbox access token not configured")
        
        # Mapbox requires coordinates, so we'll use their geocoding first
        # For demo, using text-based geocoding endpoint
        
        # Convert mode for Mapbox
        mapbox_profile = {
            "driving": "driving-traffic",  # Real-time traffic data!
            "walking": "walking",
            "cycling": "cycling"
        }.get(mode, "driving-traffic")
        
        # Use Mapbox Directions API with geocoding
        url = f"https://api.mapbox.com/directions/v5/mapbox/{mapbox_profile}/{origin};{destination}"
        params = {
            "access_token": access_token,
            "steps": "true",
            "geometries": "geojson",
            "overview": "full",
            "annotations": "speed,duration,distance",
            "banner_instructions": "true",
            "voice_instructions": "true",  # Perfect for RHINO voice assistant!
            "alternatives": "true"  # Get multiple route options
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'routes' not in data or not data['routes']:
            # Try with geocoding if direct coordinates failed
            return self._mapbox_route_with_geocoding(origin, destination, mode)
        
        route = data["routes"][0]  # Primary route
        
        # Extract detailed route information
        steps = []
        for leg in route["legs"]:
            for step in leg["steps"]:
                instruction = step["maneuver"]["instruction"]
                if "voice_instructions" in step and step["voice_instructions"]:
                    # Use voice-optimized instructions for RHINO
                    voice_text = step["voice_instructions"][0]["announcement"]
                    steps.append(voice_text)
                else:
                    steps.append(instruction)
        
        return {
            "provider": "Mapbox (Traffic-Optimized)",
            "distance": f"{route['distance']/1000:.1f} km",
            "duration": f"{route['duration']/60:.0f} minutes",
            "steps": steps,
            "traffic_aware": True,
            "alternatives": len(data['routes']) > 1,
            "voice_optimized": True
        }
    
    def _mapbox_route_with_geocoding(self, origin, destination, mode):
        """Fallback Mapbox routing with geocoding"""
        access_token = self.credentials['mapbox']
        
        try:
            # Geocode origin and destination
            origin_coords = self._mapbox_geocode(origin, access_token)
            dest_coords = self._mapbox_geocode(destination, access_token)
            
            if not origin_coords or not dest_coords:
                raise ValueError("Could not geocode locations")
            
            # Now route with coordinates
            mapbox_profile = "driving-traffic" if mode == "driving" else mode
            coord_string = f"{origin_coords[0]},{origin_coords[1]};{dest_coords[0]},{dest_coords[1]}"
            
            url = f"https://api.mapbox.com/directions/v5/mapbox/{mapbox_profile}/{coord_string}"
            params = {
                "access_token": access_token,
                "steps": "true",
                "voice_instructions": "true",
                "banner_instructions": "true"
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'routes' not in data:
                raise Exception("Mapbox routing failed after geocoding")
            
            route = data["routes"][0]
            steps = []
            for leg in route["legs"]:
                for step in leg["steps"]:
                    steps.append(step["maneuver"]["instruction"])
            
            return {
                "provider": "Mapbox (Geocoded)",
                "distance": f"{route['distance']/1000:.1f} km", 
                "duration": f"{route['duration']/60:.0f} minutes",
                "steps": steps,
                "traffic_aware": True
            }
            
        except Exception as e:
            raise Exception(f"Mapbox geocoding fallback failed: {e}")
    
    def _mapbox_geocode(self, location, access_token):
        """Geocode location using Mapbox"""
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json"
        params = {
            "access_token": access_token,
            "limit": 1
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'features' not in data or not data['features']:
            return None
        
        # Return [longitude, latitude] as required by Mapbox
        return data['features'][0]['center']
    
    def _here_route(self, origin, destination, mode):
        """HERE Maps API"""
        api_key = self.credentials['here']
        if not api_key:
            raise ValueError("HERE API key not configured")
        
        url = "https://router.hereapi.com/v8/routes"
        params = {
            "transportMode": mode,
            "origin": origin,
            "destination": destination,
            "return": "summary,actions,instructions",
            "apikey": api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'routes' not in data:
            raise Exception("HERE Maps API error")
        
        route = data["routes"][0]
        return {
            "provider": "HERE Maps",
            "distance": f"{route['sections'][0]['summary']['length']/1000:.1f} km",
            "duration": f"{route['sections'][0]['summary']['duration']/60:.0f} minutes",
            "steps": [action["instruction"] for action in route["sections"][0]["actions"]]
        }
    
    def _mapquest_route(self, origin, destination, mode):
        """MapQuest Directions API"""
        api_key = self.credentials['mapquest']
        if not api_key:
            raise ValueError("MapQuest API key not configured")
        
        url = "http://www.mapquestapi.com/directions/v2/route"
        params = {
            "key": api_key,
            "from": origin,
            "to": destination,
            "routeType": "fastest"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["info"]["statuscode"] != 0:
            raise Exception("MapQuest API error")
        
        route = data["route"]
        return {
            "provider": "MapQuest",
            "distance": f"{route['distance']:.1f} km",
            "duration": route["formattedTime"],
            "steps": [maneuver["narrative"] for leg in route["legs"] 
                     for maneuver in leg["maneuvers"]]
        }
    
    def _bing_route(self, origin, destination, mode):
        """Bing Maps API"""
        api_key = self.credentials['bing']
        if not api_key:
            raise ValueError("Bing Maps API key not configured")
        
        url = "http://dev.virtualearth.net/REST/v1/Routes/Driving"
        params = {
            "wp.0": origin,
            "wp.1": destination,
            "key": api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data["resourceSets"] or not data["resourceSets"][0]["resources"]:
            raise Exception("Bing Maps API error")
        
        route = data["resourceSets"][0]["resources"][0]
        return {
            "provider": "Bing Maps",
            "distance": f"{route['travelDistance']:.1f} km",
            "duration": f"{route['travelDuration']/60:.0f} minutes",
            "steps": [step["instruction"]["text"] for leg in route["routeLegs"] 
                     for step in leg["itineraryItems"]]
        }
    
    def _get_offline_route(self, origin, destination):
        """Fallback offline routing (basic directions)"""
        return {
            "provider": "Offline/Emergency",
            "distance": "Unknown",
            "duration": "Unknown", 
            "steps": [
                f"Head towards {destination} from {origin}",
                "Follow main roads and highway signs",
                "Use local traffic signs for guidance",
                "Consider using offline GPS navigation app",
                f"Destination: {destination}"
            ]
        }

# Convenience function for voice assistant
def get_route_multi_provider(origin, destination="Current Location"):
    """Get route using multi-provider system"""
    router = MultiMapRouter()
    try:
        route_data = router.get_route(origin, destination)
        
        # Format for voice output
        summary = f"Route via {route_data['provider']}: "
        summary += f"Distance {route_data['distance']}, "
        summary += f"Duration {route_data['duration']}. "
        
        # Add first few steps
        if route_data['steps']:
            summary += "Directions: " + ". ".join(route_data['steps'][:3])
            if len(route_data['steps']) > 3:
                summary += f" and {len(route_data['steps'])-3} more steps."
        
        return summary
        
    except Exception as e:
        return f"Unable to get route directions: {e}. Please use your preferred navigation app."

# Test function
if __name__ == "__main__":
    # Test the multi-provider system
    router = MultiMapRouter()
    result = router.get_route("Coimbatore, India", "Chennai, India")
    print(json.dumps(result, indent=2))
