#!/usr/bin/env python3
"""
RHINO-CAR Emergency Voice Test
Test the emergency voice assistant without waiting for actual crash detection
"""

import sys
import os

# Add project paths
sys.path.append(os.path.abspath("../utils"))
sys.path.append(os.path.abspath("../alerts"))

from llm_handler import speak_text, get_voice_command, call_llm_gemini, process_voice_command

def simulate_crash_scenario():
    """Simulate crash detection and test emergency voice response"""
    
    print("🚨 SIMULATING CRASH SCENARIO...")
    
    # Mock vehicle data during crash
    crash_vehicle_data = {
        'vsv': 45.0,  # Vehicle was going 45 km/h
        'vlv': 20.0,  # Lead vehicle suddenly slowed to 20 km/h  
        'headway': 5.0,  # Very close following distance
        'visibility': 'clear',
        'risk_level': 'critical',
        'temperature': 22.0,
        'humidity': 60.0
    }
    
    print("Mock crash data:", crash_vehicle_data)
    
    # Activate emergency voice assistant
    speak_text("CRASH DETECTED! Emergency voice assistant activated. How can I help you?")
    
    try:
        # Listen for emergency command
        print("[🎙️ ] Listening for emergency command...")
        
        print(1)
        user_input = get_voice_command()
        print(2)
        
        if user_input and not user_input.startswith("[STT ERROR]"):
            print(f"[DRIVER SAID] {user_input}")
            
            # Generate emergency response
            emergency_context = f"""EMERGENCY SITUATION: Crash detected. 
Vehicle data - Speed: {crash_vehicle_data['vsv']:.1f} km/h, 
Lead vehicle: {crash_vehicle_data['vlv']:.1f} km/h, 
Distance: {crash_vehicle_data['headway']:.1f}m, 
Visibility: {crash_vehicle_data['visibility']}, 
Risk: {crash_vehicle_data['risk_level']}. 
Driver says: '{user_input}'"""
            
            print("[🤖] Generating emergency response...")
            reply = call_llm_gemini(f"You are an emergency vehicle safety assistant. {emergency_context}. Provide immediate, helpful emergency guidance. Be concise and actionable.")
            
            print(f"[ASSISTANT RESPONSE] {reply}")
            speak_text(reply)
            
            # Check for navigation assistance
            if any(word in user_input.lower() for word in ["hospital", "help", "emergency", "directions", "navigate"]):
                speak_text("Would you like directions to the nearest hospital?")
                
                hospital_response = get_voice_command()
                if hospital_response and any(word in hospital_response.lower() for word in ["yes", "okay", "sure", "hospital"]):
                    # Simulate route response
                    route_info = "Route to nearest hospital: Head north on Main Street for 2 kilometers, turn right on Hospital Avenue. Estimated time: 8 minutes."
                    speak_text(route_info)
                    print(f"[NAVIGATION] {route_info}")
        else:
            speak_text("I couldn't understand. Emergency services have been notified. Stay calm and follow standard emergency procedures.")
            print("[WARNING] Could not understand voice input")
            
    except Exception as e:
        print(f"[ERROR] Emergency voice assistant failed: {e}")
        speak_text("Emergency services have been notified. Please stay safe.")

def test_manual_voice_commands():
    """Test regular voice commands without crash"""
    
    print("\n🎙️ TESTING MANUAL VOICE COMMANDS...")
    
    # Mock normal driving data
    normal_vehicle_data = {
        'vsv': 60.0,
        'vlv': 65.0,
        'headway': 25.0,
        'visibility': 'sunny',
        'risk_level': 'low',
        'temperature': 25.0,
        'humidity': 45.0
    }
    
    speak_text("Voice assistant activated. What can I help you with?")
    
    try:
        command = get_voice_command()
        if command and not command.startswith("[STT ERROR]"):
            print(f"[COMMAND] {command}")
            response = process_voice_command(command, normal_vehicle_data)
            print(f"[RESPONSE] {response}")
            speak_text(response)
        else:
            speak_text("I couldn't understand. Please try again.")
            
    except Exception as e:
        print(f"[ERROR] Voice command failed: {e}")

def main():
    """Main test function"""
    print("🚗 RHINO-CAR Emergency Voice Assistant Test")
    print("=" * 50)
    
    print("\nChoose test mode:")
    print("1. Simulate crash scenario (emergency voice)")
    print("2. Test manual voice commands") 
    print("3. Both tests")
    
    try:
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == "1":
            simulate_crash_scenario()
        elif choice == "2":
            test_manual_voice_commands()
        elif choice == "3":
            simulate_crash_scenario()
            print("\n" + "="*30)
            test_manual_voice_commands()
        else:
            print("Invalid choice. Running crash simulation...")
            simulate_crash_scenario()
            
        print("\n✅ Test completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()
