# RHINO-CAR Predictive Traffic Intelligence System
"""
Advanced traffic pattern analysis, route optimization, and predictive navigation
"""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import requests
import json
from datetime import datetime, timedelta
from collections import deque, defaultdict
import sqlite3
import threading
import time

class TrafficIntelligenceSystem:
    """AI-powered traffic analysis and route optimization"""
    
    def __init__(self, mapbox_token):
        self.mapbox_token = mapbox_token
        self.traffic_db = "traffic_intelligence.db"
        self.traffic_history = deque(maxlen=10000)
        self.route_analytics = defaultdict(list)
        
        # Traffic prediction model
        self.traffic_model = self.create_traffic_predictor()
        
        # Real-time traffic monitoring
        self.monitoring_active = False
        self.current_location = None
        self.destination = None
        
        # Initialize database
        self.init_traffic_database()
        
    def init_traffic_database(self):
        """Initialize traffic intelligence database"""
        conn = sqlite3.connect(self.traffic_db)
        cursor = conn.cursor()
        
        # Traffic patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_hash TEXT,
                day_of_week INTEGER,
                hour INTEGER,
                traffic_level REAL,
                avg_speed REAL,
                estimated_time REAL,
                timestamp DATETIME
            )
        ''')
        
        # Route analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS route_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT,
                destination TEXT,
                route_data TEXT,
                distance_km REAL,
                estimated_time_min REAL,
                actual_time_min REAL,
                traffic_conditions TEXT,
                weather_conditions TEXT,
                timestamp DATETIME
            )
        ''')
        
        # Traffic incidents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT,
                location TEXT,
                severity TEXT,
                description TEXT,
                start_time DATETIME,
                end_time DATETIME,
                impact_radius_km REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_traffic_predictor(self):
        """Create neural network for traffic prediction"""
        model = nn.Sequential(
            nn.Linear(15, 128),  # Input: time, location, weather, historical data
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3)  # Output: travel_time, traffic_level, best_route_index
        )
        return model
    
    def fetch_real_time_traffic(self, origin, destination):
        """Fetch real-time traffic data from multiple sources"""
        routes_data = []
        
        # Primary: Mapbox Directions API with traffic
        mapbox_url = f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
        mapbox_params = {
            'access_token': self.mapbox_token,
            'alternatives': 'true',
            'steps': 'true',
            'annotations': 'duration,distance,speed',
            'overview': 'full'
        }
        
        try:
            response = requests.get(mapbox_url, params=mapbox_params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for route in data.get('routes', []):
                    route_info = {
                        'source': 'mapbox',
                        'duration_min': route['duration'] / 60,
                        'distance_km': route['distance'] / 1000,
                        'traffic_level': self.calculate_traffic_level(route),
                        'route_geometry': route['geometry'],
                        'traffic_annotations': route.get('legs', [{}])[0].get('annotation', {}),
                        'confidence': 0.9
                    }
                    routes_data.append(route_info)
        except Exception as e:
            print(f"Mapbox traffic fetch error: {e}")
        
        # Secondary: Historical pattern prediction
        historical_prediction = self.predict_from_historical_data(origin, destination)
        if historical_prediction:
            routes_data.append(historical_prediction)
        
        return routes_data
    
    def calculate_traffic_level(self, route_data):
        """Calculate traffic congestion level from route data"""
        if 'legs' not in route_data or not route_data['legs']:
            return 0.5  # Medium traffic
        
        leg = route_data['legs'][0]
        distance = leg.get('distance', 1000)  # meters
        duration = leg.get('duration', 60)    # seconds
        
        # Calculate average speed
        avg_speed_ms = distance / duration if duration > 0 else 15
        avg_speed_kmh = avg_speed_ms * 3.6
        
        # Traffic level based on speed (assuming 50 km/h is free flow)
        if avg_speed_kmh >= 45:
            return 0.1  # Light traffic
        elif avg_speed_kmh >= 30:
            return 0.4  # Moderate traffic
        elif avg_speed_kmh >= 15:
            return 0.7  # Heavy traffic
        else:
            return 0.9  # Severe congestion
    
    def predict_from_historical_data(self, origin, destination):
        """Predict traffic based on historical patterns"""
        now = datetime.now()
        day_of_week = now.weekday()
        hour = now.hour
        
        # Query historical data
        conn = sqlite3.connect(self.traffic_db)
        cursor = conn.cursor()
        
        # Get similar time patterns
        cursor.execute('''
            SELECT AVG(traffic_level), AVG(avg_speed), AVG(estimated_time)
            FROM traffic_patterns 
            WHERE day_of_week = ? AND hour BETWEEN ? AND ?
            AND timestamp > datetime('now', '-30 days')
        ''', (day_of_week, hour-1, hour+1))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] is not None:
            avg_traffic, avg_speed, avg_time = result
            return {
                'source': 'historical',
                'duration_min': avg_time,
                'distance_km': 0,  # Will be updated
                'traffic_level': avg_traffic,
                'avg_speed_kmh': avg_speed,
                'confidence': 0.7
            }
        
        return None
    
    def analyze_route_efficiency(self, routes_data, current_vehicle_data):
        """Analyze and rank routes based on multiple factors"""
        scored_routes = []
        
        for i, route in enumerate(routes_data):
            score = 0
            factors = {}
            
            # Time efficiency (40% weight)
            time_score = 1.0 / (1.0 + route['duration_min'] / 30.0)
            score += time_score * 0.4
            factors['time_efficiency'] = time_score
            
            # Traffic conditions (30% weight)
            traffic_score = 1.0 - route['traffic_level']
            score += traffic_score * 0.3
            factors['traffic_conditions'] = traffic_score
            
            # Safety factor (20% weight) - based on current driving conditions
            safety_score = self.calculate_safety_score(route, current_vehicle_data)
            score += safety_score * 0.2
            factors['safety'] = safety_score
            
            # Fuel efficiency (10% weight)
            fuel_score = self.calculate_fuel_efficiency(route)
            score += fuel_score * 0.1
            factors['fuel_efficiency'] = fuel_score
            
            scored_routes.append({
                'route_index': i,
                'overall_score': score,
                'factors': factors,
                'route_data': route,
                'recommendation': self.generate_route_recommendation(score, factors)
            })
        
        # Sort by overall score
        scored_routes.sort(key=lambda x: x['overall_score'], reverse=True)
        return scored_routes
    
    def calculate_safety_score(self, route, vehicle_data):
        """Calculate safety score based on current conditions"""
        base_score = 0.8
        
        # Adjust for weather
        visibility = vehicle_data.get('visibility', 'clear')
        if visibility in ['foggy', 'rainy']:
            base_score -= 0.2
        elif visibility in ['cloudy']:
            base_score -= 0.1
        
        # Adjust for traffic level
        traffic_level = route.get('traffic_level', 0.5)
        if traffic_level > 0.7:  # Heavy traffic
            base_score -= 0.15
        elif traffic_level < 0.3:  # Light traffic
            base_score += 0.1
        
        # Adjust for time of day
        hour = datetime.now().hour
        if 22 <= hour or hour <= 6:  # Night driving
            base_score -= 0.1
        elif 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            base_score -= 0.05
        
        return max(0.0, min(1.0, base_score))
    
    def calculate_fuel_efficiency(self, route):
        """Calculate fuel efficiency score"""
        # Basic calculation based on traffic level and distance
        traffic_level = route.get('traffic_level', 0.5)
        
        # Stop-and-go traffic is less fuel efficient
        if traffic_level > 0.6:
            return 0.3
        elif traffic_level > 0.4:
            return 0.6
        else:
            return 0.9
    
    def generate_route_recommendation(self, score, factors):
        """Generate human-readable route recommendation"""
        if score >= 0.8:
            return "Excellent route - optimal time and conditions"
        elif score >= 0.7:
            return "Good route - recommended for current conditions"
        elif score >= 0.6:
            if factors['traffic_conditions'] < 0.5:
                return "Moderate traffic expected - consider alternate timing"
            else:
                return "Acceptable route with some delays"
        else:
            return "Not recommended - heavy traffic or poor conditions"
    
    def monitor_traffic_patterns(self):
        """Continuously monitor traffic patterns"""
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                if self.current_location and self.destination:
                    # Fetch current traffic data
                    traffic_data = self.fetch_real_time_traffic(
                        self.current_location, self.destination
                    )
                    
                    # Store in database
                    self.store_traffic_pattern(traffic_data)
                    
                    # Update route recommendations
                    self.update_route_recommendations(traffic_data)
                
                time.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                print(f"Traffic monitoring error: {e}")
                time.sleep(60)
    
    def store_traffic_pattern(self, traffic_data):
        """Store traffic pattern in database"""
        if not traffic_data:
            return
        
        conn = sqlite3.connect(self.traffic_db)
        cursor = conn.cursor()
        
        now = datetime.now()
        for route in traffic_data:
            cursor.execute('''
                INSERT INTO traffic_patterns 
                (route_hash, day_of_week, hour, traffic_level, avg_speed, estimated_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"{self.current_location}_{self.destination}",
                now.weekday(),
                now.hour,
                route.get('traffic_level', 0.5),
                route.get('avg_speed_kmh', 30),
                route.get('duration_min', 30),
                now
            ))
        
        conn.commit()
        conn.close()
    
    def update_route_recommendations(self, traffic_data):
        """Update real-time route recommendations"""
        if not traffic_data:
            return
        
        current_vehicle_data = self.get_current_vehicle_data()
        scored_routes = self.analyze_route_efficiency(traffic_data, current_vehicle_data)
        
        # Store updated recommendations
        self.route_analytics['current'] = scored_routes
        
        # Generate voice alert if significant change
        if len(scored_routes) > 1:
            best_route = scored_routes[0]
            if best_route['overall_score'] < 0.6:
                self.generate_traffic_alert(best_route)
    
    def generate_traffic_alert(self, route_analysis):
        """Generate traffic alert for voice assistant"""
        try:
            from llm_handler import speak_text
            
            score = route_analysis['overall_score']
            factors = route_analysis['factors']
            
            if score < 0.4:
                message = "Heavy traffic ahead. Consider alternate route or delayed departure."
            elif factors['traffic_conditions'] < 0.3:
                message = "Significant traffic congestion detected on current route."
            elif factors['safety'] < 0.5:
                message = "Poor driving conditions ahead. Reduced visibility or heavy traffic."
            else:
                message = "Traffic conditions have changed. Route optimization available."
            
            speak_text(message)
            
        except ImportError:
            print(f"Traffic Alert: {route_analysis['recommendation']}")
    
    def get_current_vehicle_data(self):
        """Get current vehicle data (integration point)"""
        # This would integrate with the main RHINO system
        return {
            'visibility': 'clear',
            'speed': 45,
            'risk_level': 'low'
        }
    
    def voice_traffic_commands(self, command, current_location=None, destination=None):
        """Handle voice commands related to traffic"""
        command_lower = command.lower()
        
        if 'traffic update' in command_lower or 'traffic status' in command_lower:
            if self.route_analytics.get('current'):
                best_route = self.route_analytics['current'][0]
                duration = best_route['route_data']['duration_min']
                traffic_level = best_route['route_data']['traffic_level'] * 100
                return f"Current route: {duration:.0f} minutes with {traffic_level:.0f}% traffic congestion."
            else:
                return "No active route. Please set a destination first."
        
        elif 'best route' in command_lower or 'fastest route' in command_lower:
            if current_location and destination:
                traffic_data = self.fetch_real_time_traffic(current_location, destination)
                vehicle_data = self.get_current_vehicle_data()
                scored_routes = self.analyze_route_efficiency(traffic_data, vehicle_data)
                
                if scored_routes:
                    best = scored_routes[0]
                    return f"Best route: {best['route_data']['duration_min']:.0f} minutes. {best['recommendation']}"
                else:
                    return "Unable to calculate optimal route at this time."
            else:
                return "Please provide current location and destination for route optimization."
        
        elif 'traffic alert' in command_lower:
            self.monitoring_active = True
            threading.Thread(target=self.monitor_traffic_patterns, daemon=True).start()
            return "Traffic monitoring activated. You'll receive alerts for significant changes."
        
        elif 'stop traffic' in command_lower:
            self.monitoring_active = False
            return "Traffic monitoring stopped."
        
        else:
            return "Traffic commands: traffic update, best route, traffic alert, stop traffic monitoring."
    
    def start_intelligent_navigation(self, origin, destination):
        """Start intelligent navigation with continuous optimization"""
        self.current_location = origin
        self.destination = destination
        
        # Initial route calculation
        traffic_data = self.fetch_real_time_traffic(origin, destination)
        vehicle_data = self.get_current_vehicle_data()
        scored_routes = self.analyze_route_efficiency(traffic_data, vehicle_data)
        
        if scored_routes:
            best_route = scored_routes[0]
            print(f"🗺️ Intelligent Navigation Started")
            print(f"Best Route: {best_route['route_data']['duration_min']:.0f} min")
            print(f"Traffic Level: {best_route['route_data']['traffic_level']*100:.0f}%")
            print(f"Recommendation: {best_route['recommendation']}")
        
        # Start continuous monitoring
        self.monitoring_active = True
        threading.Thread(target=self.monitor_traffic_patterns, daemon=True).start()
        
        return scored_routes

# Integration functions
def create_traffic_intelligence_system(mapbox_token):
    """Create and initialize traffic intelligence system"""
    return TrafficIntelligenceSystem(mapbox_token)

def demo_traffic_intelligence():
    """Demo function for traffic intelligence"""
    # This would use your actual Mapbox token
    traffic_system = TrafficIntelligenceSystem("your_mapbox_token_here")
    
    # Example coordinates (San Francisco to San Jose)
    origin = [37.7749, -122.4194]
    destination = [37.3382, -121.8863]
    
    print("🚗 RHINO Traffic Intelligence Demo")
    routes = traffic_system.start_intelligent_navigation(origin, destination)
    
    # Demo voice commands
    commands = [
        "traffic update",
        "best route", 
        "traffic alert"
    ]
    
    for command in commands:
        response = traffic_system.voice_traffic_commands(command, origin, destination)
        print(f"Command: {command}")
        print(f"Response: {response}\n")

if __name__ == "__main__":
    demo_traffic_intelligence()
