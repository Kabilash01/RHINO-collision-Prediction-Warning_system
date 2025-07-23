# Smart Contextual Voice Commands for RHINO-CAR
from llm_handler import process_voice_command, speak_text, get_voice_command

class SmartVoiceCommands:
    """Enhanced voice command system with context awareness and proactive suggestions"""
    
    def __init__(self):
        self.command_history = []
        self.context_patterns = {
            'high_risk_driving': ['slow down', 'increase distance', 'be careful'],
            'navigation_needed': ['hospital', 'gas station', 'restaurant', 'directions'],
            'weather_concerns': ['visibility', 'rain', 'fog', 'weather'],
            'speed_questions': ['speed', 'fast', 'slow', 'velocity']
        }
        
    def analyze_driving_context(self, vehicle_data):
        """Analyze current driving situation for proactive suggestions"""
        suggestions = []
        
        # High risk situation
        if vehicle_data.get('risk_level') in ['high', 'critical']:
            suggestions.append("Consider reducing speed for safety")
            
        # Close following
        if vehicle_data.get('headway', 100) < 15:
            suggestions.append("Following distance is quite close")
            
        # Poor visibility
        if vehicle_data.get('visibility') in ['foggy', 'rainy']:
            suggestions.append("Reduced visibility detected - drive carefully")
            
        # High speed in risk situation
        if vehicle_data.get('vsv', 0) > 80 and vehicle_data.get('risk_level') != 'low':
            suggestions.append("High speed with elevated risk detected")
            
        return suggestions
    
    def smart_voice_activation(self, vehicle_data):
        """Smart voice activation with contextual prompts"""
        
        # Analyze current situation
        suggestions = self.analyze_driving_context(vehicle_data)
        
        # Provide contextual greeting
        if suggestions:
            speak_text(f"Voice assistant activated. I notice {suggestions[0]}. How can I help?")
        else:
            speak_text("Voice assistant activated. All systems look good. What can I help you with?")
        
        # Listen for command
        command = get_voice_command()
        
        if command and not command.startswith("[STT ERROR]"):
            # Enhanced command processing
            response = self.process_smart_command(command, vehicle_data, suggestions)
            speak_text(response)
            
            # Remember this interaction
            self.command_history.append({
                'command': command,
                'context': vehicle_data.copy(),
                'suggestions': suggestions
            })
        else:
            speak_text("I couldn't understand. Please try again or press V for another attempt.")
    
    def process_smart_command(self, command, vehicle_data, current_suggestions):
        """Process command with enhanced context and smart responses"""
        
        # Quick status commands
        if any(word in command.lower() for word in ['status', 'how am i', "how's it going"]):
            return self.generate_driving_status_report(vehicle_data)
        
        # Proactive safety suggestions
        elif any(word in command.lower() for word in ['advice', 'suggest', 'recommend']):
            return self.generate_safety_recommendations(vehicle_data)
        
        # Smart navigation
        elif any(word in command.lower() for word in ['where', 'find', 'locate', 'nearest']):
            return self.handle_smart_navigation(command, vehicle_data)
        
        # Enhanced emergency handling
        elif any(word in command.lower() for word in ['emergency', 'help', 'urgent', 'problem']):
            return self.handle_emergency_smart(command, vehicle_data)
        
        # Default to enhanced processing
        else:
            # Add current suggestions to the response context
            enhanced_prompt = f"Current driving context: {current_suggestions[0] if current_suggestions else 'Normal conditions'}. Driver command: {command}"
            return process_voice_command(enhanced_prompt, vehicle_data)
    
    def generate_driving_status_report(self, vehicle_data):
        """Generate comprehensive driving status report"""
        vsv = vehicle_data.get('vsv', 0)
        vlv = vehicle_data.get('vlv', 0)
        headway = vehicle_data.get('headway', 0)
        risk = vehicle_data.get('risk_level', 'unknown')
        visibility = vehicle_data.get('visibility', 'unknown')
        
        # Smart status based on conditions
        if risk == 'critical':
            return f"ALERT: Critical risk situation. Your speed {vsv:.0f}, lead vehicle {vlv:.0f}, distance {headway:.0f} meters. Immediate attention needed!"
        elif risk == 'high':
            return f"Caution advised. Speed {vsv:.0f} km/h, following distance {headway:.0f} meters, visibility {visibility}. Consider reducing speed."
        elif risk == 'moderate':
            return f"Moderate risk detected. Speed {vsv:.0f} km/h, distance {headway:.0f} meters. Stay alert."
        else:
            return f"Driving conditions good. Speed {vsv:.0f} km/h, safe distance {headway:.0f} meters, {visibility} visibility."
    
    def generate_safety_recommendations(self, vehicle_data):
        """Generate personalized safety recommendations"""
        recommendations = []
        
        vsv = vehicle_data.get('vsv', 0)
        headway = vehicle_data.get('headway', 100)
        risk = vehicle_data.get('risk_level', 'low')
        
        # Speed recommendations
        if vsv > 100:
            recommendations.append("Consider reducing speed for better control")
        
        # Distance recommendations  
        if headway < 20:
            safe_distance = max(20, vsv * 0.5)  # Speed-based safe distance
            recommendations.append(f"Increase following distance to at least {safe_distance:.0f} meters")
        
        # Risk-based recommendations
        if risk != 'low':
            recommendations.append("Current conditions require extra attention")
        
        # Weather-based recommendations
        visibility = vehicle_data.get('visibility', 'sunny')
        if visibility in ['foggy', 'rainy']:
            recommendations.append("Reduced visibility - use headlights and reduce speed")
        
        if recommendations:
            return "Here are my recommendations: " + ". ".join(recommendations[:3])
        else:
            return "Your driving looks safe. Keep maintaining good speed and distance."
    
    def handle_smart_navigation(self, command, vehicle_data):
        """Handle navigation with emergency priority"""
        
        # Emergency locations get priority
        if any(word in command.lower() for word in ['hospital', 'emergency', 'police', 'fire']):
            return "For emergency services, I'll find the nearest location immediately. Getting directions now..."
        
        # Gas stations for low fuel emergencies
        elif 'gas' in command.lower() or 'fuel' in command.lower():
            return "Locating nearest gas stations along your route. This is important for safety."
        
        # Regular navigation
        else:
            return f"I'll help you navigate. Current location conditions: {vehicle_data.get('visibility', 'good')} visibility. What's your destination?"
    
    def handle_emergency_smart(self, command, vehicle_data):
        """Smart emergency handling with context"""
        
        # Analyze severity from vehicle data
        risk = vehicle_data.get('risk_level', 'low')
        vsv = vehicle_data.get('vsv', 0)
        
        if risk == 'critical' or vsv > 120:
            return "URGENT: High-risk situation detected. Reduce speed immediately. Pull over safely if possible. What specific help do you need?"
        
        elif 'medical' in command.lower() or 'hurt' in command.lower():
            return "Medical emergency detected. Stay calm. If serious, call emergency services immediately. Do you need hospital directions?"
        
        elif 'breakdown' in command.lower() or 'car' in command.lower():
            return "Vehicle emergency. Turn on hazard lights, pull over safely. Do you need roadside assistance or nearest service station?"
        
        else:
            return f"Emergency assistance activated. Current situation: {risk} risk level. What specific help do you need?"

# Quick integration example
def activate_smart_voice(vehicle_data):
    """Simple function to activate enhanced voice system"""
    smart_commands = SmartVoiceCommands()
    smart_commands.smart_voice_activation(vehicle_data)
