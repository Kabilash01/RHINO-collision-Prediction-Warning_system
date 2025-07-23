# RHINO-CAR Enhanced Integration Hub
"""
Enhanced RHINO-CAR system with all new features integrated
Run this to enable all advanced features at once
"""

import sys
import threading
import time
from datetime import datetime

# Import all the new systems
try:
    from advanced_voice_triggers import AdvancedVoiceTrigger
    from smart_voice_commands import SmartVoiceCommands, activate_smart_voice
    from fleet_manager import FleetRhinoManager, RhinoFleetIntegration
    from performance_optimizer import start_performance_optimization, rhino_optimizer
    from llm_handler import speak_text, get_voice_command
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("Some advanced features may not be available")

class RhinoEnhancedSystem:
    """Main integration hub for all RHINO-CAR enhancements"""
    
    def __init__(self, vehicle_id="RHINO_MAIN_001"):
        self.vehicle_id = vehicle_id
        self.system_active = False
        
        # Initialize subsystems
        self.advanced_triggers = None
        self.smart_voice = None
        self.fleet_integration = None
        self.performance_optimizer = None
        
        # System status
        self.features_enabled = {
            'advanced_triggers': False,
            'smart_voice': False,
            'fleet_management': False,
            'performance_optimization': False
        }
        
        print(f"🚗 RHINO Enhanced System initialized for vehicle {vehicle_id}")
    
    def start_all_systems(self):
        """Start all enhanced systems"""
        print("🚀 Starting RHINO Enhanced Systems...")
        
        # 1. Start Performance Optimization
        try:
            self.performance_optimizer = start_performance_optimization()
            self.features_enabled['performance_optimization'] = True
            print("✅ Performance optimization enabled")
        except Exception as e:
            print(f"❌ Performance optimization failed: {e}")
        
        # 2. Initialize Smart Voice Commands
        try:
            self.smart_voice = SmartVoiceCommands()
            self.features_enabled['smart_voice'] = True
            print("✅ Smart voice commands enabled")
        except Exception as e:
            print(f"❌ Smart voice failed: {e}")
        
        # 3. Initialize Fleet Management
        try:
            self.fleet_integration = RhinoFleetIntegration(self.vehicle_id)
            self.features_enabled['fleet_management'] = True
            print("✅ Fleet management enabled")
        except Exception as e:
            print(f"❌ Fleet management failed: {e}")
        
        # 4. Initialize Advanced Triggers
        try:
            self.advanced_triggers = AdvancedVoiceTrigger(
                voice_callback=self.enhanced_voice_activation
            )
            self.advanced_triggers.start_all_triggers()
            self.features_enabled['advanced_triggers'] = True
            print("✅ Advanced triggers enabled")
        except Exception as e:
            print(f"❌ Advanced triggers failed: {e}")
        
        self.system_active = True
        
        # Start main system loop
        self.system_thread = threading.Thread(target=self.system_loop)
        self.system_thread.daemon = True
        self.system_thread.start()
        
        print("🎯 All RHINO Enhanced Systems are active!")
        self.speak_system_status()
    
    def enhanced_voice_activation(self, vehicle_data=None):
        """Enhanced voice activation with all features"""
        if not vehicle_data:
            vehicle_data = self.get_current_vehicle_data()
        
        print(f"🎤 Enhanced voice activation at {datetime.now().strftime('%H:%M:%S')}")
        
        # Use smart voice commands if available
        if self.smart_voice and self.features_enabled['smart_voice']:
            self.smart_voice.smart_voice_activation(vehicle_data)
        else:
            # Fallback to basic voice activation
            speak_text("Voice assistant activated. How can I help?")
            command = get_voice_command()
            if command and not command.startswith("[STT ERROR]"):
                response = self.process_enhanced_command(command, vehicle_data)
                speak_text(response)
    
    def process_enhanced_command(self, command, vehicle_data):
        """Process voice commands with all enhanced features"""
        command_lower = command.lower()
        
        # System status commands
        if 'system status' in command_lower:
            return self.get_system_status_voice()
        
        # Performance commands
        elif any(word in command_lower for word in ['performance', 'optimize', 'speed up']):
            if self.performance_optimizer:
                return rhino_optimizer.voice_performance_command(command)
            else:
                return "Performance optimization not available"
        
        # Fleet commands
        elif any(word in command_lower for word in ['fleet', 'nearby vehicles', 'incident']):
            if self.fleet_integration:
                return self.fleet_integration.process_fleet_voice_command(command, vehicle_data)
            else:
                return "Fleet management not available"
        
        # Feature control commands
        elif 'restart systems' in command_lower:
            return self.restart_all_systems()
        
        elif 'help' in command_lower or 'what can you do' in command_lower:
            return self.get_help_message()
        
        # Default processing
        else:
            # Use smart voice if available, otherwise basic processing
            if self.smart_voice:
                return self.smart_voice.process_smart_command(command, vehicle_data, [])
            else:
                from llm_handler import process_voice_command
                return process_voice_command(command, vehicle_data)
    
    def get_current_vehicle_data(self):
        """Get current vehicle data (placeholder - integrate with main RHINO system)"""
        # This would be integrated with the main RHINO detection system
        import random
        return {
            'vsv': random.randint(40, 90),  # Vehicle speed
            'vlv': random.randint(35, 85),  # Lead vehicle speed  
            'headway': random.randint(15, 50),  # Following distance
            'risk_level': random.choice(['low', 'moderate', 'high']),
            'visibility': random.choice(['sunny', 'cloudy', 'rainy']),
            'location': {'lat': 40.7128, 'lon': -74.0060},  # NYC coordinates
            'vehicle_id': self.vehicle_id
        }
    
    def system_loop(self):
        """Main system monitoring loop"""
        while self.system_active:
            try:
                # Get current vehicle data
                vehicle_data = self.get_current_vehicle_data()
                
                # Update fleet with current data
                if self.fleet_integration and self.features_enabled['fleet_management']:
                    self.fleet_integration.update_fleet_with_vehicle_data(vehicle_data)
                
                # Monitor for critical situations
                if vehicle_data.get('risk_level') == 'critical':
                    self.handle_critical_situation(vehicle_data)
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"System loop error: {e}")
                time.sleep(10)
    
    def handle_critical_situation(self, vehicle_data):
        """Handle critical driving situations"""
        print("🚨 CRITICAL SITUATION DETECTED!")
        
        # Voice alert
        speak_text(f"Critical risk detected! Speed {vehicle_data['vsv']}, distance {vehicle_data.get('headway', 0)} meters. Reduce speed immediately!")
        
        # Fleet notification
        if self.fleet_integration:
            self.fleet_integration.fleet_manager.report_incident(
                self.vehicle_id,
                'critical',
                f"Critical risk: Speed {vehicle_data['vsv']}, headway {vehicle_data.get('headway', 0)}m",
                vehicle_data.get('location', {})
            )
    
    def get_system_status_voice(self):
        """Get system status for voice response"""
        active_features = [name for name, status in self.features_enabled.items() if status]
        active_count = len(active_features)
        
        if active_count == 4:
            return "All RHINO enhanced systems operational. Advanced triggers, smart voice, fleet management, and performance optimization active."
        elif active_count >= 2:
            return f"{active_count} enhanced systems active: {', '.join(active_features[:2])} and others."
        elif active_count >= 1:
            return f"Basic enhanced systems active: {active_features[0]}."
        else:
            return "Running basic RHINO system only. Enhanced features not available."
    
    def speak_system_status(self):
        """Announce system status via voice"""
        active_count = sum(self.features_enabled.values())
        speak_text(f"RHINO Enhanced System ready. {active_count} of 4 advanced features active.")
    
    def get_help_message(self):
        """Get help message for voice commands"""
        return """Available commands: System status, performance report, fleet status, nearby vehicles, 
               report incident, optimize system, restart systems. Say 'voice help' for more options."""
    
    def restart_all_systems(self):
        """Restart all enhanced systems"""
        print("🔄 Restarting RHINO Enhanced Systems...")
        
        # Stop current systems
        if self.advanced_triggers:
            self.advanced_triggers.stop_all_triggers()
        
        if self.performance_optimizer:
            rhino_optimizer.stop_performance_monitoring()
        
        # Small delay
        time.sleep(2)
        
        # Restart systems
        self.start_all_systems()
        
        return "All RHINO enhanced systems have been restarted successfully."
    
    def stop_all_systems(self):
        """Stop all enhanced systems"""
        print("⏹️ Stopping RHINO Enhanced Systems...")
        
        self.system_active = False
        
        if self.advanced_triggers:
            self.advanced_triggers.stop_all_triggers()
        
        if self.performance_optimizer:
            rhino_optimizer.stop_performance_monitoring()
        
        print("All systems stopped")

# Quick start functions
def start_enhanced_rhino(vehicle_id="RHINO_001"):
    """Quick start function for enhanced RHINO system"""
    enhanced_system = RhinoEnhancedSystem(vehicle_id)
    enhanced_system.start_all_systems()
    return enhanced_system

def demo_enhanced_features():
    """Demonstration of all enhanced features"""
    print("""
🌟 RHINO Enhanced Features Demo
================================

1. Advanced Voice Triggers:
   - Gamepad button activation
   - Keyboard hotkeys (Ctrl+V, F1)
   - Clap detection
   - Multiple activation methods

2. Smart Voice Commands:
   - Context-aware responses
   - Driving situation analysis
   - Proactive safety suggestions
   - Enhanced emergency handling

3. Fleet Management:
   - Multi-vehicle coordination
   - Incident reporting
   - Fleet status monitoring
   - Nearby vehicle detection

4. Performance Optimization:
   - Real-time performance monitoring
   - Dynamic quality adjustment
   - Resource usage optimization
   - Performance reporting

5. Integration Features:
   - Unified command processing
   - Multi-system coordination
   - Critical situation handling
   - Voice status reporting

To start: enhanced_rhino = start_enhanced_rhino()
    """)

if __name__ == "__main__":
    # Run demo if called directly
    demo_enhanced_features()
    
    # Start enhanced system
    print("Starting RHINO Enhanced System...")
    enhanced_rhino = start_enhanced_rhino()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        enhanced_rhino.stop_all_systems()
        print("RHINO Enhanced System stopped")
