# RHINO-CAR Emergency Response System
"""
Advanced emergency detection, response coordination, and automatic assistance
"""
import json
import time
import requests
from datetime import datetime
import threading

class EmergencyResponseSystem:
    """Comprehensive emergency detection and response system"""
    
    def __init__(self, vehicle_id="RHINO_001"):
        self.vehicle_id = vehicle_id
        self.emergency_active = False
        self.emergency_contacts = []
        self.emergency_services = {
            'police': '911',
            'fire': '911', 
            'ambulance': '911',
            'roadside': '1-800-AAA-HELP'
        }
        
        # Emergency detection parameters
        self.crash_threshold = 0.8
        self.emergency_scenarios = []
        
        # Location and vehicle data
        self.current_location = None
        self.vehicle_data = {}
        
        # Load emergency configuration
        self.load_emergency_config()
    
    def load_emergency_config(self):
        """Load emergency configuration and contacts"""
        try:
            with open('emergency_config.json', 'r') as f:
                config = json.load(f)
                self.emergency_contacts = config.get('contacts', [])
                self.emergency_services.update(config.get('services', {}))
        except FileNotFoundError:
            # Create default emergency config
            default_config = {
                'contacts': [
                    {
                        'name': 'Emergency Contact 1',
                        'phone': '+1-555-0100',
                        'relationship': 'Family',
                        'priority': 1
                    }
                ],
                'services': {
                    'roadside': '1-800-AAA-HELP',
                    'insurance': '1-800-GEICO'
                },
                'medical_info': {
                    'blood_type': 'Unknown',
                    'allergies': 'None known',
                    'medications': 'None',
                    'medical_conditions': 'None'
                }
            }
            
            with open('emergency_config.json', 'w') as f:
                json.dump(default_config, f, indent=2)
            
            self.emergency_contacts = default_config['contacts']
    
    def detect_emergency_scenario(self, vehicle_data, collision_detected=False):
        """Detect various emergency scenarios"""
        emergency_type = None
        severity = 'low'
        
        # Collision detection
        if collision_detected or vehicle_data.get('risk_level') == 'critical':
            emergency_type = 'collision'
            severity = 'critical'
        
        # Vehicle malfunction detection
        elif self.detect_vehicle_malfunction(vehicle_data):
            emergency_type = 'breakdown'
            severity = 'medium'
        
        # Driver health emergency
        elif self.detect_driver_emergency(vehicle_data):
            emergency_type = 'medical'
            severity = 'high'
        
        # Environmental hazards
        elif self.detect_environmental_hazard(vehicle_data):
            emergency_type = 'environmental'
            severity = 'medium'
        
        if emergency_type:
            return {
                'type': emergency_type,
                'severity': severity,
                'timestamp': datetime.now(),
                'location': vehicle_data.get('location', {}),
                'vehicle_data': vehicle_data,
                'automatic_response': True
            }
        
        return None
    
    def detect_vehicle_malfunction(self, vehicle_data):
        """Detect vehicle malfunction scenarios"""
        # Engine overheating
        if vehicle_data.get('engine_temp', 85) > 110:
            return True
        
        # Low oil pressure
        if vehicle_data.get('oil_pressure', 50) < 15:
            return True
        
        # Battery failure
        if vehicle_data.get('battery_voltage', 12.0) < 10.0:
            return True
        
        # Tire failure (extreme pressure loss)
        tire_pressures = vehicle_data.get('tire_pressure', [32, 32, 32, 32])
        if any(pressure < 15 for pressure in tire_pressures):
            return True
        
        return False
    
    def detect_driver_emergency(self, vehicle_data):
        """Detect driver health emergency scenarios"""
        # Driver monitoring data
        driver_status = vehicle_data.get('driver_status', {})
        
        # Prolonged unconsciousness
        if driver_status.get('status') == 'unconscious':
            return True
        
        # Severe drowsiness combined with erratic driving
        if (driver_status.get('drowsiness_level', 0) > 0.9 and 
            vehicle_data.get('risk_level') in ['high', 'critical']):
            return True
        
        # No driver response to alerts
        if driver_status.get('no_response_time', 0) > 30:  # 30 seconds
            return True
        
        return False
    
    def detect_environmental_hazard(self, vehicle_data):
        """Detect environmental hazard scenarios"""
        # Severe weather
        visibility = vehicle_data.get('visibility', 'clear')
        if visibility in ['fog_severe', 'rain_heavy', 'snow_blizzard']:
            return True
        
        # Extreme temperature
        ambient_temp = vehicle_data.get('ambient_temp', 20)
        if ambient_temp > 50 or ambient_temp < -30:
            return True
        
        return False
    
    def initiate_emergency_response(self, emergency_scenario):
        """Initiate comprehensive emergency response"""
        self.emergency_active = True
        self.current_emergency = emergency_scenario
        
        print(f"🚨 EMERGENCY DETECTED: {emergency_scenario['type'].upper()}")
        print(f"Severity: {emergency_scenario['severity']}")
        
        # Immediate voice response
        self.emergency_voice_response(emergency_scenario)
        
        # Start emergency protocols
        if emergency_scenario['severity'] == 'critical':
            self.critical_emergency_protocol(emergency_scenario)
        elif emergency_scenario['severity'] == 'high':
            self.high_emergency_protocol(emergency_scenario)
        else:
            self.standard_emergency_protocol(emergency_scenario)
        
        # Start emergency monitoring
        threading.Thread(target=self.monitor_emergency_response, daemon=True).start()
    
    def emergency_voice_response(self, emergency_scenario):
        """Immediate voice response to emergency"""
        try:
            from llm_handler import speak_text
            
            emergency_type = emergency_scenario['type']
            severity = emergency_scenario['severity']
            
            if emergency_type == 'collision':
                speak_text("Collision detected! Emergency services are being contacted. Stay calm and check for injuries.")
            elif emergency_type == 'medical':
                speak_text("Medical emergency detected. Help is being summoned. Try to stay conscious and calm.")
            elif emergency_type == 'breakdown':
                speak_text("Vehicle malfunction detected. Activating hazard lights. Moving to safe location if possible.")
            else:
                speak_text(f"{emergency_type} emergency detected. Emergency response activated.")
                
        except ImportError:
            print(f"Emergency voice response: {emergency_scenario['type']} emergency")
    
    def critical_emergency_protocol(self, emergency_scenario):
        """Protocol for critical emergencies (collision, severe medical)"""
        print("🚨 CRITICAL EMERGENCY PROTOCOL ACTIVATED")
        
        # 1. Immediately contact emergency services
        self.contact_emergency_services(emergency_scenario)
        
        # 2. Notify emergency contacts
        self.notify_emergency_contacts(emergency_scenario, urgent=True)
        
        # 3. Activate vehicle safety systems
        self.activate_safety_systems()
        
        # 4. Continuous location broadcasting
        self.start_location_broadcasting()
        
        # 5. Prepare for first responders
        self.prepare_for_first_responders(emergency_scenario)
    
    def high_emergency_protocol(self, emergency_scenario):
        """Protocol for high-priority emergencies"""
        print("⚠️ HIGH EMERGENCY PROTOCOL ACTIVATED")
        
        # 1. Assess if 911 needed
        needs_911 = self.assess_911_requirement(emergency_scenario)
        if needs_911:
            self.contact_emergency_services(emergency_scenario)
        
        # 2. Notify emergency contacts
        self.notify_emergency_contacts(emergency_scenario)
        
        # 3. Activate safety systems
        self.activate_safety_systems()
        
        # 4. Provide emergency guidance
        self.provide_emergency_guidance(emergency_scenario)
    
    def standard_emergency_protocol(self, emergency_scenario):
        """Protocol for standard emergencies (breakdown, minor issues)"""
        print("🔧 STANDARD EMERGENCY PROTOCOL ACTIVATED")
        
        # 1. Activate hazard systems
        self.activate_hazard_systems()
        
        # 2. Contact roadside assistance
        self.contact_roadside_assistance(emergency_scenario)
        
        # 3. Notify emergency contacts
        self.notify_emergency_contacts(emergency_scenario, urgent=False)
        
        # 4. Provide self-help guidance
        self.provide_self_help_guidance(emergency_scenario)
    
    def contact_emergency_services(self, emergency_scenario):
        """Contact appropriate emergency services"""
        emergency_type = emergency_scenario['type']
        location = emergency_scenario.get('location', {})
        
        # Simulate emergency service contact
        emergency_call_data = {
            'caller_id': self.vehicle_id,
            'emergency_type': emergency_type,
            'location': location,
            'timestamp': emergency_scenario['timestamp'].isoformat(),
            'severity': emergency_scenario['severity'],
            'vehicle_occupants': 1,  # Would be detected
            'medical_info': self.get_medical_info()
        }
        
        print(f"📞 Contacting Emergency Services: {emergency_call_data}")
        
        # In real implementation, this would integrate with emergency service APIs
        # or use cellular emergency calling capabilities
        
        try:
            from llm_handler import speak_text
            speak_text("Emergency services have been contacted with your location and situation details.")
        except ImportError:
            pass
    
    def notify_emergency_contacts(self, emergency_scenario, urgent=False):
        """Notify emergency contacts"""
        for contact in self.emergency_contacts:
            notification_data = {
                'contact': contact,
                'emergency_type': emergency_scenario['type'],
                'location': emergency_scenario.get('location', {}),
                'timestamp': emergency_scenario['timestamp'],
                'vehicle_id': self.vehicle_id,
                'urgent': urgent
            }
            
            # Simulate SMS/call notification
            self.send_emergency_notification(notification_data)
    
    def send_emergency_notification(self, notification_data):
        """Send emergency notification to contact"""
        contact = notification_data['contact']
        emergency_type = notification_data['emergency_type']
        urgent = notification_data['urgent']
        
        message = f"🚨 RHINO Emergency Alert: {emergency_type} detected for vehicle {self.vehicle_id}. "
        message += f"Location: {notification_data['location'].get('address', 'Unknown')}. "
        
        if urgent:
            message += "URGENT - Emergency services contacted. "
        
        message += f"Time: {notification_data['timestamp'].strftime('%H:%M:%S')}"
        
        print(f"📱 Notifying {contact['name']} ({contact['phone']}): {message}")
        
        # In real implementation, integrate with Twilio or similar SMS service
    
    def activate_safety_systems(self):
        """Activate vehicle safety systems"""
        safety_actions = []
        
        # Hazard lights
        safety_actions.append("Hazard lights activated")
        
        # Emergency flashers
        safety_actions.append("Emergency flashers activated")
        
        # Door unlocking (for first responders)
        safety_actions.append("Doors unlocked for emergency access")
        
        # Engine safety shutdown (if applicable)
        safety_actions.append("Engine safety protocols engaged")
        
        print(f"🔒 Safety systems activated: {', '.join(safety_actions)}")
    
    def activate_hazard_systems(self):
        """Activate hazard warning systems for non-critical emergencies"""
        print("⚠️ Hazard systems activated:")
        print("- Hazard lights ON")
        print("- Emergency triangle recommendation")
        print("- Safe location guidance active")
    
    def provide_emergency_guidance(self, emergency_scenario):
        """Provide voice guidance during emergency"""
        try:
            from llm_handler import speak_text, get_voice_command
            
            emergency_type = emergency_scenario['type']
            
            if emergency_type == 'medical':
                speak_text("Medical emergency guidance: Stay calm, breathe slowly. Help is coming. Can you respond?")
                
                # Listen for response
                response = get_voice_command()
                if response and "yes" in response.lower():
                    speak_text("Good. Try to stay conscious and describe your symptoms.")
                else:
                    speak_text("If you can hear me, emergency services are en route to your location.")
                    
            elif emergency_type == 'breakdown':
                speak_text("Vehicle breakdown detected. If safe, pull over to the right shoulder and activate hazard lights.")
                
            elif emergency_type == 'environmental':
                speak_text("Hazardous conditions detected. Reduce speed and find safe shelter if possible.")
                
        except ImportError:
            print(f"Emergency guidance for {emergency_scenario['type']}")
    
    def monitor_emergency_response(self):
        """Monitor ongoing emergency response"""
        start_time = time.time()
        
        while self.emergency_active:
            elapsed_time = time.time() - start_time
            
            # Check if emergency is resolved
            if elapsed_time > 300:  # 5 minutes
                self.check_emergency_resolution()
            
            # Periodic status updates
            if elapsed_time % 60 == 0:  # Every minute
                self.broadcast_emergency_status()
            
            time.sleep(10)
    
    def check_emergency_resolution(self):
        """Check if emergency situation is resolved"""
        try:
            from llm_handler import speak_text, get_voice_command
            
            speak_text("Emergency monitoring active. Are you safe? Say 'emergency resolved' if situation is under control.")
            
            response = get_voice_command()
            if response and "resolved" in response.lower():
                self.resolve_emergency()
            
        except ImportError:
            # Auto-resolve after extended time in demo mode
            print("Auto-resolving emergency after extended monitoring period")
            self.resolve_emergency()
    
    def resolve_emergency(self):
        """Mark emergency as resolved"""
        self.emergency_active = False
        
        try:
            from llm_handler import speak_text
            speak_text("Emergency response concluded. All safety systems remain active. Drive safely.")
        except ImportError:
            print("Emergency response concluded")
        
        # Log emergency resolution
        resolution_data = {
            'vehicle_id': self.vehicle_id,
            'resolution_time': datetime.now(),
            'duration_minutes': time.time(),
            'status': 'resolved'
        }
        
        print(f"✅ Emergency resolved: {resolution_data}")
    
    def get_medical_info(self):
        """Get medical information for emergency services"""
        try:
            with open('emergency_config.json', 'r') as f:
                config = json.load(f)
                return config.get('medical_info', {})
        except:
            return {
                'blood_type': 'Unknown',
                'allergies': 'Unknown',
                'medications': 'Unknown'
            }
    
    def voice_emergency_commands(self, command):
        """Handle voice commands during emergency"""
        command_lower = command.lower()
        
        if 'emergency help' in command_lower or 'call 911' in command_lower:
            emergency_scenario = {
                'type': 'manual',
                'severity': 'high',
                'timestamp': datetime.now(),
                'location': self.current_location or {},
                'vehicle_data': self.vehicle_data,
                'automatic_response': False
            }
            self.initiate_emergency_response(emergency_scenario)
            return "Emergency response activated. Help is being summoned."
        
        elif 'emergency resolved' in command_lower or 'cancel emergency' in command_lower:
            if self.emergency_active:
                self.resolve_emergency()
                return "Emergency response cancelled. All safety systems deactivated."
            else:
                return "No active emergency to resolve."
        
        elif 'emergency status' in command_lower:
            if self.emergency_active:
                return f"Emergency active: {self.current_emergency['type']} emergency. Emergency services contacted."
            else:
                return "No active emergency. All systems normal."
        
        elif 'roadside assistance' in command_lower:
            self.contact_roadside_assistance({'type': 'breakdown', 'severity': 'low'})
            return "Contacting roadside assistance. Help is on the way."
        
        else:
            return "Emergency commands: emergency help, emergency resolved, emergency status, roadside assistance."
    
    def contact_roadside_assistance(self, emergency_scenario):
        """Contact roadside assistance services"""
        print(f"🚗 Contacting roadside assistance for {emergency_scenario['type']}")
        
        # Mock roadside assistance contact
        assistance_data = {
            'service': 'AAA Roadside',
            'eta': '30-45 minutes',
            'service_type': emergency_scenario['type'],
            'location': self.current_location or 'GPS coordinates provided'
        }
        
        print(f"Roadside assistance dispatched: {assistance_data}")
        
        try:
            from llm_handler import speak_text
            speak_text(f"Roadside assistance contacted. Estimated arrival: {assistance_data['eta']}")
        except ImportError:
            pass
    
    def provide_self_help_guidance(self, emergency_scenario):
        """Provide self-help guidance for minor emergencies"""
        emergency_type = emergency_scenario['type']
        
        guidance = {
            'breakdown': "Move to safe location, activate hazards, exit vehicle safely if possible, wait for assistance",
            'tire': "Pull over safely, check tire pressure, use spare tire if trained, or wait for assistance",
            'overheating': "Pull over immediately, turn off engine, do not open hood until cool, add coolant if available",
            'battery': "Try jump start if cables available, ensure all lights/accessories off, call for assistance"
        }
        
        message = guidance.get(emergency_type, "Stay safe, help is coming")
        
        try:
            from llm_handler import speak_text
            speak_text(f"Self-help guidance: {message}")
        except ImportError:
            print(f"Self-help guidance: {message}")

# Integration function
def create_emergency_response_system(vehicle_id="RHINO_001"):
    """Create emergency response system"""
    return EmergencyResponseSystem(vehicle_id)

# Demo function
def demo_emergency_response():
    """Demo emergency response system"""
    ers = EmergencyResponseSystem("DEMO_VEHICLE")
    
    # Simulate different emergency scenarios
    scenarios = [
        {
            'risk_level': 'critical',
            'engine_temp': 85,
            'location': {'lat': 40.7128, 'lon': -74.0060, 'address': 'NYC, NY'}
        },
        {
            'engine_temp': 120,
            'battery_voltage': 8.0,
            'location': {'lat': 34.0522, 'lon': -118.2437, 'address': 'LA, CA'}
        }
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\n--- Emergency Scenario {i+1} ---")
        emergency = ers.detect_emergency_scenario(scenario, collision_detected=(i==0))
        if emergency:
            ers.initiate_emergency_response(emergency)
            time.sleep(3)  # Simulate response time
            ers.resolve_emergency()

if __name__ == "__main__":
    demo_emergency_response()
