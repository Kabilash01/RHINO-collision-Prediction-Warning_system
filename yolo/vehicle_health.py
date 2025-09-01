# RHINO-CAR Vehicle Health Monitoring System
"""
Comprehensive vehicle diagnostics, predictive maintenance, and health analytics
"""
import json
import time
import sqlite3
import threading
from datetime import datetime, timedelta
from collections import deque
import requests

class VehicleHealthMonitor:
    """Advanced vehicle health monitoring and predictive maintenance"""
    
    def __init__(self, vehicle_id="RHINO_001"):
        self.vehicle_id = vehicle_id
        self.health_db = "vehicle_health.db"
        
        # Health monitoring data
        self.engine_metrics = deque(maxlen=1000)
        self.brake_metrics = deque(maxlen=1000)
        self.tire_metrics = deque(maxlen=500)
        self.battery_metrics = deque(maxlen=500)
        
        # Monitoring status
        self.monitoring_active = False
        self.health_score = 100.0
        self.maintenance_alerts = []
        
        # OBD-II parameters (if available)
        self.obd_parameters = {
            'engine_rpm': 0,
            'vehicle_speed': 0,
            'engine_temp': 0,
            'fuel_level': 100,
            'battery_voltage': 12.0,
            'oil_pressure': 50,
            'brake_fluid_level': 100,
            'tire_pressure': [32, 32, 32, 32]  # FL, FR, RL, RR
        }
        
        # Initialize database
        self.init_health_database()
        
        # Load vehicle profile
        self.vehicle_profile = self.load_vehicle_profile()
    
    def init_health_database(self):
        """Initialize vehicle health database"""
        conn = sqlite3.connect(self.health_db)
        cursor = conn.cursor()
        
        # Vehicle metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT,
                metric_type TEXT,
                metric_value REAL,
                unit TEXT,
                status TEXT,
                timestamp DATETIME
            )
        ''')
        
        # Maintenance records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT,
                service_type TEXT,
                description TEXT,
                cost REAL,
                mileage INTEGER,
                service_date DATETIME,
                next_service_date DATETIME
            )
        ''')
        
        # Health alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT,
                alert_type TEXT,
                severity TEXT,
                description TEXT,
                recommended_action TEXT,
                created_date DATETIME,
                resolved_date DATETIME
            )
        ''')
        
        # Vehicle profile table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_profile (
                vehicle_id TEXT PRIMARY KEY,
                make TEXT,
                model TEXT,
                year INTEGER,
                mileage INTEGER,
                last_service_date DATETIME,
                service_interval_km INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_vehicle_profile(self):
        """Load or create vehicle profile"""
        conn = sqlite3.connect(self.health_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM vehicle_profile WHERE vehicle_id = ?', (self.vehicle_id,))
        profile = cursor.fetchone()
        
        if not profile:
            # Create default profile
            default_profile = {
                'vehicle_id': self.vehicle_id,
                'make': 'Unknown',
                'model': 'RHINO Vehicle', 
                'year': 2024,
                'mileage': 0,
                'last_service_date': datetime.now(),
                'service_interval_km': 10000
            }
            
            cursor.execute('''
                INSERT INTO vehicle_profile 
                (vehicle_id, make, model, year, mileage, last_service_date, service_interval_km)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', tuple(default_profile.values()))
            
            conn.commit()
            conn.close()
            return default_profile
        else:
            conn.close()
            return {
                'vehicle_id': profile[0],
                'make': profile[1],
                'model': profile[2],
                'year': profile[3],
                'mileage': profile[4],
                'last_service_date': profile[5],
                'service_interval_km': profile[6]
            }
    
    def simulate_obd_data(self):
        """Simulate OBD-II data (replace with actual OBD reader)"""
        import random
        
        # Simulate realistic vehicle data
        base_rpm = 800 + random.randint(-100, 500)
        base_temp = 85 + random.randint(-5, 15)
        base_voltage = 12.0 + random.uniform(-0.5, 0.5)
        
        self.obd_parameters.update({
            'engine_rpm': base_rpm,
            'engine_temp': base_temp,
            'battery_voltage': base_voltage,
            'fuel_level': max(0, self.obd_parameters['fuel_level'] - random.uniform(0, 0.1)),
            'oil_pressure': 45 + random.randint(-5, 10),
            'tire_pressure': [
                32 + random.uniform(-1, 1) for _ in range(4)
            ]
        })
    
    def analyze_engine_health(self):
        """Analyze engine health metrics"""
        rpm = self.obd_parameters['engine_rpm']
        temp = self.obd_parameters['engine_temp']
        oil_pressure = self.obd_parameters['oil_pressure']
        
        engine_health = {
            'overall_score': 100.0,
            'rpm_status': 'normal',
            'temperature_status': 'normal',
            'oil_pressure_status': 'normal',
            'alerts': []
        }
        
        # RPM analysis
        if rpm > 6000:
            engine_health['rpm_status'] = 'high'
            engine_health['overall_score'] -= 15
            engine_health['alerts'].append('High RPM detected - reduce engine load')
        elif rpm < 500:
            engine_health['rpm_status'] = 'low'
            engine_health['overall_score'] -= 10
            engine_health['alerts'].append('Engine RPM unusually low')
        
        # Temperature analysis
        if temp > 105:
            engine_health['temperature_status'] = 'overheating'
            engine_health['overall_score'] -= 25
            engine_health['alerts'].append('ENGINE OVERHEATING - Pull over immediately')
        elif temp > 95:
            engine_health['temperature_status'] = 'hot'
            engine_health['overall_score'] -= 10
            engine_health['alerts'].append('Engine running hot - check cooling system')
        elif temp < 70:
            engine_health['temperature_status'] = 'cold'
            engine_health['overall_score'] -= 5
        
        # Oil pressure analysis
        if oil_pressure < 20:
            engine_health['oil_pressure_status'] = 'low'
            engine_health['overall_score'] -= 20
            engine_health['alerts'].append('LOW OIL PRESSURE - Stop engine immediately')
        elif oil_pressure < 30:
            engine_health['oil_pressure_status'] = 'marginal'
            engine_health['overall_score'] -= 10
            engine_health['alerts'].append('Oil pressure low - check oil level')
        
        return engine_health
    
    def analyze_brake_system(self):
        """Analyze brake system health"""
        brake_health = {
            'overall_score': 100.0,
            'brake_fluid_status': 'normal',
            'pad_wear_estimate': 75,  # Percentage remaining
            'alerts': []
        }
        
        fluid_level = self.obd_parameters['brake_fluid_level']
        
        if fluid_level < 20:
            brake_health['brake_fluid_status'] = 'critical'
            brake_health['overall_score'] -= 30
            brake_health['alerts'].append('CRITICAL: Low brake fluid - Service immediately')
        elif fluid_level < 40:
            brake_health['brake_fluid_status'] = 'low'
            brake_health['overall_score'] -= 15
            brake_health['alerts'].append('Brake fluid low - Schedule service')
        
        # Simulate brake pad wear based on mileage
        mileage = self.vehicle_profile['mileage']
        estimated_pad_life = 60000  # km
        pad_wear = max(0, 100 - (mileage % estimated_pad_life) / estimated_pad_life * 100)
        brake_health['pad_wear_estimate'] = pad_wear
        
        if pad_wear < 20:
            brake_health['overall_score'] -= 25
            brake_health['alerts'].append('Brake pads worn - Replace soon')
        elif pad_wear < 40:
            brake_health['overall_score'] -= 10
            brake_health['alerts'].append('Brake pads showing wear - Monitor closely')
        
        return brake_health
    
    def analyze_tire_health(self):
        """Analyze tire condition and pressure"""
        tire_pressures = self.obd_parameters['tire_pressure']
        optimal_pressure = 32.0  # PSI
        
        tire_health = {
            'overall_score': 100.0,
            'pressure_status': 'normal',
            'individual_pressures': tire_pressures,
            'alerts': []
        }
        
        for i, pressure in enumerate(tire_pressures):
            tire_names = ['Front Left', 'Front Right', 'Rear Left', 'Rear Right']
            
            if pressure < 25:
                tire_health['pressure_status'] = 'critical'
                tire_health['overall_score'] -= 20
                tire_health['alerts'].append(f'CRITICAL: {tire_names[i]} tire severely underinflated')
            elif pressure < 28:
                tire_health['pressure_status'] = 'low'
                tire_health['overall_score'] -= 10
                tire_health['alerts'].append(f'{tire_names[i]} tire underinflated')
            elif pressure > 38:
                tire_health['overall_score'] -= 5
                tire_health['alerts'].append(f'{tire_names[i]} tire overinflated')
        
        return tire_health
    
    def analyze_battery_health(self):
        """Analyze battery and electrical system"""
        voltage = self.obd_parameters['battery_voltage']
        
        battery_health = {
            'overall_score': 100.0,
            'voltage_status': 'normal',
            'voltage': voltage,
            'alerts': []
        }
        
        if voltage < 11.5:
            battery_health['voltage_status'] = 'critical'
            battery_health['overall_score'] -= 30
            battery_health['alerts'].append('CRITICAL: Battery voltage low - May not start')
        elif voltage < 12.0:
            battery_health['voltage_status'] = 'low'
            battery_health['overall_score'] -= 15
            battery_health['alerts'].append('Battery voltage low - Check charging system')
        elif voltage > 14.5:
            battery_health['voltage_status'] = 'high'
            battery_health['overall_score'] -= 10
            battery_health['alerts'].append('High voltage - Check alternator')
        
        return battery_health
    
    def calculate_overall_health_score(self):
        """Calculate overall vehicle health score"""
        engine_health = self.analyze_engine_health()
        brake_health = self.analyze_brake_system()
        tire_health = self.analyze_tire_health()
        battery_health = self.analyze_battery_health()
        
        # Weighted average of all systems
        weights = {
            'engine': 0.4,
            'brakes': 0.3,
            'tires': 0.2,
            'battery': 0.1
        }
        
        overall_score = (
            engine_health['overall_score'] * weights['engine'] +
            brake_health['overall_score'] * weights['brakes'] +
            tire_health['overall_score'] * weights['tires'] +
            battery_health['overall_score'] * weights['battery']
        )
        
        # Collect all alerts
        all_alerts = (
            engine_health['alerts'] +
            brake_health['alerts'] +
            tire_health['alerts'] +
            battery_health['alerts']
        )
        
        return {
            'overall_score': overall_score,
            'engine': engine_health,
            'brakes': brake_health,
            'tires': tire_health,
            'battery': battery_health,
            'alerts': all_alerts,
            'health_grade': self.get_health_grade(overall_score)
        }
    
    def get_health_grade(self, score):
        """Convert health score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def predict_maintenance_needs(self):
        """Predict upcoming maintenance needs"""
        mileage = self.vehicle_profile['mileage']
        last_service = self.vehicle_profile['last_service_date']
        service_interval = self.vehicle_profile['service_interval_km']
        
        predictions = []
        
        # Oil change prediction
        oil_change_interval = 5000
        km_since_oil = mileage % oil_change_interval
        km_to_oil_change = oil_change_interval - km_since_oil
        
        if km_to_oil_change <= 500:
            predictions.append({
                'service': 'Oil Change',
                'urgency': 'high' if km_to_oil_change <= 100 else 'medium',
                'estimated_km': km_to_oil_change,
                'estimated_cost': 80,
                'description': 'Engine oil and filter replacement'
            })
        
        # Brake service prediction
        brake_service_interval = 30000
        km_since_brakes = mileage % brake_service_interval
        km_to_brakes = brake_service_interval - km_since_brakes
        
        if km_to_brakes <= 2000:
            predictions.append({
                'service': 'Brake Service',
                'urgency': 'medium',
                'estimated_km': km_to_brakes,
                'estimated_cost': 300,
                'description': 'Brake inspection and possible pad replacement'
            })
        
        # Tire rotation
        tire_rotation_interval = 8000
        km_since_rotation = mileage % tire_rotation_interval
        km_to_rotation = tire_rotation_interval - km_since_rotation
        
        if km_to_rotation <= 1000:
            predictions.append({
                'service': 'Tire Rotation',
                'urgency': 'low',
                'estimated_km': km_to_rotation,
                'estimated_cost': 50,
                'description': 'Tire rotation and pressure check'
            })
        
        return predictions
    
    def generate_health_report(self):
        """Generate comprehensive vehicle health report"""
        health_data = self.calculate_overall_health_score()
        maintenance_predictions = self.predict_maintenance_needs()
        
        report = {
            'vehicle_id': self.vehicle_id,
            'report_date': datetime.now().isoformat(),
            'overall_health': {
                'score': health_data['overall_score'],
                'grade': health_data['health_grade'],
                'status': 'excellent' if health_data['overall_score'] >= 90 else
                         'good' if health_data['overall_score'] >= 80 else
                         'fair' if health_data['overall_score'] >= 70 else
                         'poor'
            },
            'system_health': {
                'engine': health_data['engine'],
                'brakes': health_data['brakes'],
                'tires': health_data['tires'],
                'battery': health_data['battery']
            },
            'active_alerts': health_data['alerts'],
            'maintenance_predictions': maintenance_predictions,
            'vehicle_profile': self.vehicle_profile
        }
        
        return report
    
    def start_health_monitoring(self):
        """Start continuous health monitoring"""
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    # Simulate OBD data collection
                    self.simulate_obd_data()
                    
                    # Store metrics in database
                    self.store_health_metrics()
                    
                    # Check for critical alerts
                    health_data = self.calculate_overall_health_score()
                    self.process_health_alerts(health_data['alerts'])
                    
                    time.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    time.sleep(60)
        
        threading.Thread(target=monitoring_loop, daemon=True).start()
    
    def store_health_metrics(self):
        """Store current health metrics in database"""
        conn = sqlite3.connect(self.health_db)
        cursor = conn.cursor()
        
        timestamp = datetime.now()
        
        # Store key metrics
        metrics = [
            ('engine_rpm', self.obd_parameters['engine_rpm'], 'rpm', 'normal'),
            ('engine_temp', self.obd_parameters['engine_temp'], 'celsius', 'normal'),
            ('battery_voltage', self.obd_parameters['battery_voltage'], 'volts', 'normal'),
            ('fuel_level', self.obd_parameters['fuel_level'], 'percent', 'normal'),
        ]
        
        for metric_type, value, unit, status in metrics:
            cursor.execute('''
                INSERT INTO vehicle_metrics 
                (vehicle_id, metric_type, metric_value, unit, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.vehicle_id, metric_type, value, unit, status, timestamp))
        
        conn.commit()
        conn.close()
    
    def process_health_alerts(self, alerts):
        """Process and potentially voice-announce health alerts"""
        critical_alerts = [alert for alert in alerts if 'CRITICAL' in alert]
        
        if critical_alerts:
            try:
                from llm_handler import speak_text
                speak_text(f"Vehicle health alert: {critical_alerts[0]}")
            except ImportError:
                pass
    
    def voice_health_commands(self, command):
        """Handle voice commands for vehicle health"""
        command_lower = command.lower()
        
        if 'health report' in command_lower or 'vehicle status' in command_lower:
            health_data = self.calculate_overall_health_score()
            score = health_data['overall_score']
            grade = health_data['health_grade']
            
            if health_data['alerts']:
                alert_count = len(health_data['alerts'])
                return f"Vehicle health grade {grade}, score {score:.0f} out of 100. {alert_count} alerts require attention."
            else:
                return f"Vehicle health excellent. Grade {grade} with {score:.0f} out of 100."
        
        elif 'maintenance' in command_lower or 'service' in command_lower:
            predictions = self.predict_maintenance_needs()
            if predictions:
                next_service = predictions[0]
                return f"Next service: {next_service['service']} in {next_service['estimated_km']} kilometers. Estimated cost ${next_service['estimated_cost']}."
            else:
                return "No immediate maintenance required. All systems operating normally."
        
        elif 'fuel level' in command_lower:
            fuel = self.obd_parameters['fuel_level']
            if fuel < 10:
                return f"Fuel level critically low at {fuel:.0f}%. Find gas station immediately."
            elif fuel < 25:
                return f"Fuel level at {fuel:.0f}%. Consider refueling soon."
            else:
                return f"Fuel level at {fuel:.0f}%. No immediate refueling needed."
        
        elif 'tire pressure' in command_lower:
            tire_health = self.analyze_tire_health()
            if tire_health['alerts']:
                return f"Tire pressure issues detected: {tire_health['alerts'][0]}"
            else:
                return "All tire pressures normal. No action required."
        
        else:
            return "Health commands: health report, maintenance schedule, fuel level, tire pressure."

# Usage example
def demo_vehicle_health():
    """Demo vehicle health monitoring"""
    monitor = VehicleHealthMonitor("DEMO_VEHICLE")
    monitor.start_health_monitoring()
    
    # Generate sample report
    report = monitor.generate_health_report()
    
    # Demo voice commands
    commands = [
        "health report",
        "maintenance schedule", 
        "fuel level",
        "tire pressure"
    ]
    
    for command in commands:
        response = monitor.voice_health_commands(command)
        print(f"Command: {command}")
        print(f"Response: {response}\n")

if __name__ == "__main__":
    demo_vehicle_health()
