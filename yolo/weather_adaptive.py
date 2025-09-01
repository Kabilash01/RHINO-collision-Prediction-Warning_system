# RHINO-CAR Real-time Weather Integration & Adaptive Driving
"""
Advanced weather monitoring, road condition analysis, and adaptive driving recommendations
"""
import requests
import json
from datetime import datetime, timedelta

class WeatherAdaptiveSystem:
    """Real-time weather integration with adaptive driving recommendations"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or "demo_weather_api_key"
        self.current_weather = {}
        self.weather_alerts = []
        self.driving_adaptations = {}
        
        # Weather-based driving parameters
        self.weather_adjustments = {
            'clear': {'speed_factor': 1.0, 'following_distance': 1.0, 'visibility': 'excellent'},
            'cloudy': {'speed_factor': 0.95, 'following_distance': 1.1, 'visibility': 'good'},
            'light_rain': {'speed_factor': 0.85, 'following_distance': 1.5, 'visibility': 'reduced'},
            'heavy_rain': {'speed_factor': 0.7, 'following_distance': 2.0, 'visibility': 'poor'},
            'fog': {'speed_factor': 0.6, 'following_distance': 2.5, 'visibility': 'very_poor'},
            'snow': {'speed_factor': 0.5, 'following_distance': 3.0, 'visibility': 'poor'},
            'ice': {'speed_factor': 0.4, 'following_distance': 4.0, 'visibility': 'hazardous'}
        }
    
    def get_weather_data(self, latitude, longitude):
        """Fetch real-time weather data"""
        # Mock weather data for demo - replace with actual weather API
        mock_weather = {
            'current': {
                'temperature': 22,
                'humidity': 65,
                'conditions': 'partly_cloudy',
                'visibility': 10,  # km
                'wind_speed': 15,  # km/h
                'precipitation': 0,  # mm/h
                'road_temperature': 25
            },
            'forecast': [
                {
                    'time': datetime.now() + timedelta(hours=1),
                    'conditions': 'light_rain',
                    'precipitation_chance': 60,
                    'intensity': 'light'
                },
                {
                    'time': datetime.now() + timedelta(hours=2),
                    'conditions': 'heavy_rain',
                    'precipitation_chance': 80,
                    'intensity': 'moderate'
                }
            ],
            'alerts': [
                {
                    'type': 'rain_warning',
                    'severity': 'moderate',
                    'message': 'Rain expected in next 30 minutes',
                    'start_time': datetime.now() + timedelta(minutes=30),
                    'duration': 120  # minutes
                }
            ]
        }
        
        # In real implementation, use actual weather API:
        # url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={self.api_key}"
        # response = requests.get(url)
        # weather_data = response.json()
        
        self.current_weather = mock_weather
        return mock_weather
    
    def analyze_road_conditions(self, weather_data):
        """Analyze road conditions based on weather"""
        current = weather_data['current']
        
        road_conditions = {
            'surface': 'dry',
            'traction': 'normal',
            'hazard_level': 'low',
            'recommended_speed': 'normal',
            'special_precautions': []
        }
        
        # Temperature-based analysis
        temp = current['temperature']
        road_temp = current['road_temperature']
        
        if road_temp <= 0:
            road_conditions['surface'] = 'icy'
            road_conditions['traction'] = 'extremely_poor'
            road_conditions['hazard_level'] = 'critical'
            road_conditions['special_precautions'].append('black_ice_possible')
        elif temp <= 2 and current['precipitation'] > 0:
            road_conditions['surface'] = 'slippery'
            road_conditions['traction'] = 'poor'
            road_conditions['hazard_level'] = 'high'
        
        # Precipitation analysis
        precipitation = current['precipitation']
        if precipitation > 10:  # Heavy rain
            road_conditions['surface'] = 'flooded'
            road_conditions['traction'] = 'very_poor'
            road_conditions['hazard_level'] = 'high'
            road_conditions['special_precautions'].append('hydroplaning_risk')
        elif precipitation > 2:  # Light rain
            road_conditions['surface'] = 'wet'
            road_conditions['traction'] = 'reduced'
            road_conditions['hazard_level'] = 'medium'
        
        # Visibility analysis
        visibility = current['visibility']
        if visibility < 1:  # Very poor visibility
            road_conditions['hazard_level'] = 'critical'
            road_conditions['special_precautions'].append('extremely_low_visibility')
        elif visibility < 5:  # Poor visibility
            road_conditions['hazard_level'] = 'high'
            road_conditions['special_precautions'].append('reduced_visibility')
        
        # Wind analysis
        wind_speed = current['wind_speed']
        if wind_speed > 60:  # Strong winds
            road_conditions['special_precautions'].append('strong_crosswinds')
            road_conditions['hazard_level'] = 'high'
        
        return road_conditions
    
    def generate_adaptive_recommendations(self, weather_data, road_conditions, current_speed):
        """Generate adaptive driving recommendations"""
        conditions = weather_data['current']['conditions']
        adjustments = self.weather_adjustments.get(conditions, self.weather_adjustments['clear'])
        
        recommendations = {
            'speed_adjustment': {
                'factor': adjustments['speed_factor'],
                'recommended_max': current_speed * adjustments['speed_factor'],
                'reason': f"Weather conditions: {conditions}"
            },
            'following_distance': {
                'factor': adjustments['following_distance'],
                'recommended_seconds': 3 * adjustments['following_distance'],
                'reason': f"Reduced traction: {road_conditions['traction']}"
            },
            'visibility_adjustments': {
                'headlights': 'on' if adjustments['visibility'] in ['reduced', 'poor', 'very_poor'] else 'auto',
                'fog_lights': 'on' if adjustments['visibility'] == 'very_poor' else 'off',
                'hazards': 'on' if road_conditions['hazard_level'] == 'critical' else 'off'
            },
            'special_actions': self.get_special_actions(road_conditions, weather_data),
            'comfort_settings': self.get_comfort_recommendations(weather_data)
        }
        
        return recommendations
    
    def get_special_actions(self, road_conditions, weather_data):
        """Get special actions based on conditions"""
        actions = []
        
        # Critical conditions
        if road_conditions['hazard_level'] == 'critical':
            actions.append('Consider stopping at safe location')
            actions.append('Use extreme caution')
        
        # Ice conditions
        if 'black_ice_possible' in road_conditions['special_precautions']:
            actions.append('Avoid sudden movements')
            actions.append('Test braking gently')
            actions.append('Use winter driving mode if available')
        
        # Flooding risk
        if 'hydroplaning_risk' in road_conditions['special_precautions']:
            actions.append('Avoid standing water')
            actions.append('Reduce speed significantly in turns')
            actions.append('Maintain steady throttle')
        
        # Visibility issues
        if 'extremely_low_visibility' in road_conditions['special_precautions']:
            actions.append('Use fog lights and hazards')
            actions.append('Follow road lines closely')
            actions.append('Consider pulling over safely')
        
        # Wind conditions
        if 'strong_crosswinds' in road_conditions['special_precautions']:
            actions.append('Grip steering wheel firmly')
            actions.append('Anticipate wind gusts on bridges')
        
        # Upcoming weather changes
        for alert in weather_data.get('alerts', []):
            if alert['severity'] in ['high', 'critical']:
                actions.append(f"Weather alert: {alert['message']}")
        
        return actions
    
    def get_comfort_recommendations(self, weather_data):
        """Get comfort and efficiency recommendations"""
        current = weather_data['current']
        
        comfort = {
            'climate_control': {},
            'efficiency_tips': [],
            'maintenance_reminders': []
        }
        
        # Temperature-based comfort
        temp = current['temperature']
        if temp > 30:  # Hot weather
            comfort['climate_control']['ac'] = 'auto'
            comfort['climate_control']['circulation'] = 'recirculate'
            comfort['efficiency_tips'].append('Use A/C efficiently - close windows at highway speeds')
        elif temp < 5:  # Cold weather
            comfort['climate_control']['heater'] = 'auto'
            comfort['climate_control']['defrost'] = 'auto'
            comfort['efficiency_tips'].append('Allow engine to warm up briefly')
            comfort['maintenance_reminders'].append('Check antifreeze levels')
        
        # Humidity considerations
        humidity = current['humidity']
        if humidity > 80:
            comfort['climate_control']['dehumidify'] = 'on'
            comfort['efficiency_tips'].append('Use A/C to reduce window fogging')
        
        # Rain preparations
        if current['precipitation'] > 0:
            comfort['maintenance_reminders'].append('Check wiper blade condition')
            comfort['maintenance_reminders'].append('Ensure headlights are clean')
        
        return comfort
    
    def monitor_weather_changes(self, location, vehicle_data):
        """Continuously monitor weather changes"""
        current_conditions = vehicle_data.get('weather_conditions', 'unknown')
        weather_data = self.get_weather_data(location['lat'], location['lon'])
        new_conditions = weather_data['current']['conditions']
        
        # Check for significant weather changes
        if current_conditions != new_conditions:
            change_notification = self.analyze_weather_change(current_conditions, new_conditions)
            if change_notification:
                return change_notification
        
        # Check for upcoming weather alerts
        upcoming_alerts = self.check_upcoming_alerts(weather_data)
        if upcoming_alerts:
            return upcoming_alerts
        
        return None
    
    def analyze_weather_change(self, old_conditions, new_conditions):
        """Analyze significance of weather change"""
        # Define severity levels
        severity_levels = {
            'clear': 1, 'cloudy': 2, 'light_rain': 3, 
            'heavy_rain': 4, 'fog': 4, 'snow': 5, 'ice': 6
        }
        
        old_severity = severity_levels.get(old_conditions, 0)
        new_severity = severity_levels.get(new_conditions, 0)
        
        # Significant change threshold
        if abs(new_severity - old_severity) >= 2:
            return {
                'type': 'weather_change',
                'message': f"Weather changing from {old_conditions} to {new_conditions}",
                'severity': 'high' if new_severity > old_severity else 'medium',
                'recommendations': self.get_transition_recommendations(old_conditions, new_conditions)
            }
        
        return None
    
    def get_transition_recommendations(self, old_conditions, new_conditions):
        """Get recommendations for weather transitions"""
        recommendations = []
        
        # Getting worse
        if new_conditions in ['heavy_rain', 'fog', 'snow', 'ice']:
            recommendations.append('Reduce speed gradually')
            recommendations.append('Increase following distance')
            recommendations.append('Turn on appropriate lights')
        
        # Getting better
        elif old_conditions in ['heavy_rain', 'fog', 'snow'] and new_conditions in ['clear', 'cloudy']:
            recommendations.append('Gradually return to normal speed')
            recommendations.append('Road surfaces may still be wet')
        
        return recommendations
    
    def check_upcoming_alerts(self, weather_data):
        """Check for upcoming weather alerts"""
        for alert in weather_data.get('alerts', []):
            time_to_alert = (alert['start_time'] - datetime.now()).total_seconds() / 60
            
            if 0 <= time_to_alert <= 30:  # Alert within 30 minutes
                return {
                    'type': 'weather_alert',
                    'message': alert['message'],
                    'severity': alert['severity'],
                    'time_to_event': time_to_alert,
                    'recommendations': self.get_alert_recommendations(alert)
                }
        
        return None
    
    def get_alert_recommendations(self, alert):
        """Get recommendations for weather alerts"""
        recommendations = []
        
        if alert['type'] == 'rain_warning':
            recommendations.append('Find safe location if heavy rain expected')
            recommendations.append('Check wiper operation')
            recommendations.append('Reduce speed when rain begins')
        elif alert['type'] == 'fog_warning':
            recommendations.append('Prepare for reduced visibility')
            recommendations.append('Use fog lights when appropriate')
            recommendations.append('Consider delaying travel if severe')
        
        return recommendations
    
    def voice_weather_commands(self, command, location=None):
        """Handle voice commands for weather information"""
        command_lower = command.lower()
        
        if 'weather report' in command_lower or 'current weather' in command_lower:
            if location:
                weather_data = self.get_weather_data(location['lat'], location['lon'])
                current = weather_data['current']
                return f"Current weather: {current['temperature']}°C, {current['conditions']}, visibility {current['visibility']} kilometers. Humidity {current['humidity']}%."
            else:
                return "Location required for weather report."
        
        elif 'road conditions' in command_lower:
            if location:
                weather_data = self.get_weather_data(location['lat'], location['lon'])
                road_conditions = self.analyze_road_conditions(weather_data)
                return f"Road conditions: {road_conditions['surface']} surface, {road_conditions['traction']} traction, {road_conditions['hazard_level']} hazard level."
            else:
                return "Location required for road conditions."
        
        elif 'weather alerts' in command_lower:
            if self.current_weather and 'alerts' in self.current_weather:
                alerts = self.current_weather['alerts']
                if alerts:
                    alert = alerts[0]
                    return f"Weather alert: {alert['message']}. Severity: {alert['severity']}."
                else:
                    return "No current weather alerts."
            else:
                return "No weather alert data available."
        
        elif 'driving recommendations' in command_lower:
            if location:
                weather_data = self.get_weather_data(location['lat'], location['lon'])
                road_conditions = self.analyze_road_conditions(weather_data)
                recommendations = self.generate_adaptive_recommendations(weather_data, road_conditions, 60)
                
                speed_rec = recommendations['speed_adjustment']
                return f"Driving recommendations: Maximum speed {speed_rec['recommended_max']:.0f} km/h, increase following distance by {recommendations['following_distance']['factor']:.1f}x."
            else:
                return "Location required for driving recommendations."
        
        else:
            return "Weather commands: weather report, road conditions, weather alerts, driving recommendations."
    
    def integrate_with_rhino_system(self, vehicle_data, location):
        """Integration point with main RHINO system"""
        # Get weather data
        weather_data = self.get_weather_data(location['lat'], location['lon'])
        
        # Analyze road conditions
        road_conditions = self.analyze_road_conditions(weather_data)
        
        # Generate recommendations
        current_speed = vehicle_data.get('vsv', 50)
        recommendations = self.generate_adaptive_recommendations(weather_data, road_conditions, current_speed)
        
        # Check for weather changes
        weather_change = self.monitor_weather_changes(location, vehicle_data)
        
        # Compile weather intelligence
        weather_intelligence = {
            'current_weather': weather_data['current'],
            'road_conditions': road_conditions,
            'recommendations': recommendations,
            'weather_change': weather_change,
            'adaptive_parameters': {
                'speed_factor': recommendations['speed_adjustment']['factor'],
                'following_distance_factor': recommendations['following_distance']['factor'],
                'visibility_level': self.weather_adjustments.get(weather_data['current']['conditions'], {}).get('visibility', 'good')
            }
        }
        
        return weather_intelligence

# Integration function
def create_weather_adaptive_system(api_key=None):
    """Create weather adaptive system"""
    return WeatherAdaptiveSystem(api_key)

# Demo function
def demo_weather_system():
    """Demo weather adaptive system"""
    weather_system = WeatherAdaptiveSystem()
    
    # Mock location (New York City)
    location = {'lat': 40.7128, 'lon': -74.0060}
    
    # Mock vehicle data
    vehicle_data = {
        'vsv': 60,
        'visibility': 'clear',
        'weather_conditions': 'clear'
    }
    
    print("🌤️ RHINO Weather Adaptive System Demo")
    
    # Get weather intelligence
    weather_intel = weather_system.integrate_with_rhino_system(vehicle_data, location)
    
    print(f"Current Weather: {weather_intel['current_weather']['conditions']}")
    print(f"Road Conditions: {weather_intel['road_conditions']['surface']}")
    print(f"Speed Recommendation: {weather_intel['recommendations']['speed_adjustment']['recommended_max']:.0f} km/h")
    
    # Demo voice commands
    commands = [
        "weather report",
        "road conditions", 
        "driving recommendations",
        "weather alerts"
    ]
    
    for command in commands:
        response = weather_system.voice_weather_commands(command, location)
        print(f"Command: {command}")
        print(f"Response: {response}\n")

if __name__ == "__main__":
    demo_weather_system()
