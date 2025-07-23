# RHINO-CAR Fleet Management Integration
import json
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class FleetRhinoManager:
    """Fleet management system for multiple RHINO-CAR vehicles"""
    
    def __init__(self, fleet_id: str = "RHINO_FLEET_001"):
        self.fleet_id = fleet_id
        self.db_path = "fleet_data.db"
        self.init_database()
        
        # Fleet communication settings
        self.fleet_api_endpoint = "http://localhost:8080/fleet"  # Your fleet server
        self.vehicle_registry = {}
        
    def init_database(self):
        """Initialize fleet database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vehicle tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                vehicle_id TEXT PRIMARY KEY,
                status TEXT,
                location TEXT,
                risk_level TEXT,
                speed REAL,
                last_update TIMESTAMP
            )
        ''')
        
        # Incident reporting table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                vehicle_id TEXT,
                severity TEXT,
                description TEXT,
                location TEXT,
                timestamp TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Fleet alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fleet_alerts (
                alert_id TEXT PRIMARY KEY,
                alert_type TEXT,
                message TEXT,
                affected_vehicles TEXT,
                timestamp TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_vehicle(self, vehicle_id: str, vehicle_info: Dict):
        """Register a new vehicle in the fleet"""
        self.vehicle_registry[vehicle_id] = {
            'id': vehicle_id,
            'registration_time': datetime.now(),
            'status': 'active',
            **vehicle_info
        }
        print(f"✅ Vehicle {vehicle_id} registered in fleet {self.fleet_id}")
        
    def update_vehicle_status(self, vehicle_id: str, vehicle_data: Dict):
        """Update individual vehicle status in fleet database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO vehicles 
            (vehicle_id, status, location, risk_level, speed, last_update)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            vehicle_id,
            vehicle_data.get('status', 'active'),
            json.dumps(vehicle_data.get('location', {})),
            vehicle_data.get('risk_level', 'low'),
            vehicle_data.get('vsv', 0),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def report_incident(self, vehicle_id: str, severity: str, description: str, location: Dict):
        """Report an incident from a fleet vehicle"""
        incident_id = f"INC_{vehicle_id}_{int(datetime.now().timestamp())}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO incidents 
            (incident_id, vehicle_id, severity, description, location, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            incident_id,
            vehicle_id,
            severity,
            description,
            json.dumps(location),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        # Broadcast alert to other vehicles if severe
        if severity in ['critical', 'high']:
            self.broadcast_fleet_alert(
                alert_type="incident",
                message=f"High severity incident reported by {vehicle_id}: {description}",
                affected_area=location
            )
        
        print(f"🚨 Incident {incident_id} reported for vehicle {vehicle_id}")
        return incident_id
    
    def broadcast_fleet_alert(self, alert_type: str, message: str, affected_area: Dict = None):
        """Broadcast alert to all fleet vehicles"""
        alert_id = f"ALERT_{int(datetime.now().timestamp())}"
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fleet_alerts 
            (alert_id, alert_type, message, affected_vehicles, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            alert_id,
            alert_type,
            message,
            json.dumps(affected_area) if affected_area else "all",
            datetime.now()
        ))
        conn.commit()
        conn.close()
        
        # Broadcast to vehicles (would be via API/websocket in production)
        print(f"📢 FLEET ALERT [{alert_type.upper()}]: {message}")
        
        # Voice announcement for current vehicle
        from llm_handler import speak_text
        if alert_type == "incident":
            speak_text(f"Fleet alert: Incident reported in area. Exercise caution.")
        elif alert_type == "weather":
            speak_text(f"Fleet weather alert: {message}")
        
        return alert_id
    
    def get_nearby_fleet_vehicles(self, current_location: Dict, radius_km: float = 10) -> List[Dict]:
        """Find nearby fleet vehicles for coordination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT vehicle_id, location, risk_level, speed, last_update 
            FROM vehicles 
            WHERE last_update > ? AND vehicle_id != ?
        ''', (datetime.now() - timedelta(minutes=30), current_location.get('vehicle_id', 'unknown')))
        
        nearby_vehicles = []
        for row in cursor.fetchall():
            vehicle_id, location_json, risk_level, speed, last_update = row
            try:
                vehicle_location = json.loads(location_json)
                # Simple distance check (would use proper geodesic calculation in production)
                if self.calculate_distance(current_location, vehicle_location) <= radius_km:
                    nearby_vehicles.append({
                        'vehicle_id': vehicle_id,
                        'location': vehicle_location,
                        'risk_level': risk_level,
                        'speed': speed,
                        'last_update': last_update
                    })
            except:
                continue
        
        conn.close()
        return nearby_vehicles
    
    def calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two locations (simplified)"""
        # Simplified distance calculation - use proper geodesic in production
        try:
            lat1, lon1 = loc1.get('lat', 0), loc1.get('lon', 0)
            lat2, lon2 = loc2.get('lat', 0), loc2.get('lon', 0)
            
            # Rough approximation for demonstration
            return abs(lat1 - lat2) + abs(lon1 - lon2)
        except:
            return 999  # Far distance if calculation fails
    
    def get_fleet_status_summary(self) -> Dict:
        """Get overall fleet status summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Active vehicles
        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE last_update > ?", 
                      (datetime.now() - timedelta(hours=1),))
        active_vehicles = cursor.fetchone()[0]
        
        # Risk distribution
        cursor.execute('''
            SELECT risk_level, COUNT(*) 
            FROM vehicles 
            WHERE last_update > ? 
            GROUP BY risk_level
        ''', (datetime.now() - timedelta(hours=1),))
        risk_distribution = dict(cursor.fetchall())
        
        # Recent incidents
        cursor.execute('''
            SELECT COUNT(*) 
            FROM incidents 
            WHERE timestamp > ? AND resolved = FALSE
        ''', (datetime.now() - timedelta(hours=24),))
        active_incidents = cursor.fetchone()[0]
        
        # Active alerts
        cursor.execute("SELECT COUNT(*) FROM fleet_alerts WHERE active = TRUE")
        active_alerts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'fleet_id': self.fleet_id,
            'active_vehicles': active_vehicles,
            'risk_distribution': risk_distribution,
            'active_incidents': active_incidents,
            'active_alerts': active_alerts,
            'status': 'operational' if active_incidents == 0 else 'incidents_reported'
        }
    
    def handle_fleet_voice_command(self, command: str, vehicle_id: str, current_location: Dict):
        """Handle fleet-related voice commands"""
        command_lower = command.lower()
        
        if 'fleet status' in command_lower or 'fleet summary' in command_lower:
            status = self.get_fleet_status_summary()
            return f"Fleet status: {status['active_vehicles']} vehicles active, {status['active_incidents']} incidents, {status['active_alerts']} alerts."
        
        elif 'nearby vehicles' in command_lower or 'nearby fleet' in command_lower:
            nearby = self.get_nearby_fleet_vehicles(current_location)
            if nearby:
                return f"Found {len(nearby)} nearby fleet vehicles. Closest vehicle has {nearby[0]['risk_level']} risk level."
            else:
                return "No nearby fleet vehicles detected in your area."
        
        elif 'report incident' in command_lower:
            # This would trigger incident reporting flow
            return "Incident reporting activated. Describe the situation and I'll log it for the fleet."
        
        elif 'fleet alert' in command_lower:
            return "Fleet communication active. What message should I broadcast to nearby vehicles?"
        
        else:
            return "Fleet commands available: fleet status, nearby vehicles, report incident, fleet alert."

# Integration with main RHINO system
class RhinoFleetIntegration:
    """Integration layer between RHINO-CAR and fleet management"""
    
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        self.fleet_manager = FleetRhinoManager()
        self.fleet_manager.register_vehicle(vehicle_id, {
            'vehicle_type': 'RHINO-CAR',
            'capabilities': ['collision_detection', 'risk_prediction', 'voice_assistant']
        })
    
    def update_fleet_with_vehicle_data(self, vehicle_data: Dict):
        """Update fleet with current vehicle data"""
        fleet_data = {
            'status': 'active',
            'location': vehicle_data.get('location', {}),
            'risk_level': vehicle_data.get('risk_level', 'low'),
            'vsv': vehicle_data.get('vsv', 0),
            'vlv': vehicle_data.get('vlv', 0),
            'headway': vehicle_data.get('headway', 0),
            'visibility': vehicle_data.get('visibility', 'good')
        }
        
        self.fleet_manager.update_vehicle_status(self.vehicle_id, fleet_data)
        
        # Auto-report critical situations
        if fleet_data['risk_level'] == 'critical':
            self.fleet_manager.report_incident(
                self.vehicle_id,
                'critical',
                f"Critical risk detected: Speed {fleet_data['vsv']:.0f} km/h, Distance {vehicle_data.get('headway', 0):.0f}m",
                fleet_data['location']
            )
    
    def process_fleet_voice_command(self, command: str, vehicle_data: Dict):
        """Process voice commands related to fleet operations"""
        return self.fleet_manager.handle_fleet_voice_command(
            command, 
            self.vehicle_id, 
            vehicle_data.get('location', {})
        )

# Usage example for integration
def integrate_fleet_management(vehicle_id: str = "RHINO_001"):
    """Quick setup function for fleet integration"""
    return RhinoFleetIntegration(vehicle_id)
