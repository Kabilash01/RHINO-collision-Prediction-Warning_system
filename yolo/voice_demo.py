#!/usr/bin/env python3
"""
RHINO Voice Assistant Demo
Enhanced integrated LLM voice interaction system

Features:
- Continuous listening with "Hey Rhino" wake word
- Context-aware responses using vehicle data
- Emergency assistance commands
- Navigation and routing support  
- Vehicle status inquiries
- General conversation capabilities
"""

import sys
import os
import time
import json
from datetime import datetime

# Add project paths
sys.path.append(os.path.abspath("../utils"))
sys.path.append(os.path.abspath("../alerts"))

from llm_handler import (
    start_continuous_listening, 
    stop_continuous_listening,
    process_voice_command,
    speak_text,
    get_voice_command
)

# Mock vehicle data for demo
mock_vehicle_data = {
    'vsv': 65.0,  # Subject vehicle speed
    'vlv': 50.0,  # Lead vehicle speed
    'headway': 25.5,  # Following distance in meters
    'visibility': 'sunny',
    'risk_level': 'low',
    'temperature': 22.5,
    'humidity': 45.0,
    'ttc': 5.2  # Time to collision
}

def get_mock_vehicle_data():
    """Mock callback to simulate live vehicle data"""
    # Simulate some variation in data
    import random
    data = mock_vehicle_data.copy()
    data['vsv'] += random.uniform(-2, 2)
    data['vlv'] += random.uniform(-1, 1) 
    data['headway'] += random.uniform(-1, 1)
    return data

def demo_voice_commands():
    """Demo different voice command categories"""
    
    print("\n🎙️ RHINO Voice Assistant Demo")
    print("="*50)
    
    test_commands = [
        # Emergency commands
        ("Help! I need emergency assistance", "emergency"),
        ("Accident detected, what should I do?", "emergency"),
        
        # Status commands  
        ("What's my current speed?", "status"),
        ("How's the weather visibility?", "status"),
        ("What's my following distance?", "status"),
        
        # Navigation commands
        ("Navigate to the nearest hospital", "navigation"),
        ("Get directions to the gas station", "navigation"),
        
        # General conversation
        ("How are you today?", "general"),
        ("Tell me about road safety", "general")
    ]
    
    print("Testing voice command categories:")
    for command, category in test_commands:
        print(f"\n[{category.upper()}] Testing: '{command}'")
        response = process_voice_command(command, get_mock_vehicle_data())
        print(f"Response: {response}")
        
        # Speak the response
        if len(response) < 200:  # Only speak shorter responses in demo
            speak_text(response)
        
        time.sleep(2)  # Pause between tests
    
    commands_to_test = [
        ("Hey Rhino, what's my current speed?", "status_inquiry"),
        ("Hey Rhino, help me with emergency", "emergency_command"),
        ("Hey Rhino, navigate to the hospital", "navigation_command"),
        ("Hey Rhino, how's the weather looking?", "general_question"),
        ("Hey Rhino, is it safe to overtake?", "safety_question")
    ]
    
    for command, category in commands_to_test:
        print(f"\n📝 Testing {category}:")
        print(f"Command: '{command}'")
        
        # Simulate the command processing
        response = process_voice_command(command.replace("Hey Rhino, ", ""), get_mock_vehicle_data())
        print(f"Response: {response}")
        
        # Optional: Actually speak the response
        # speak_text(response)
        
        time.sleep(1)

def interactive_demo():
    """Interactive demo with live voice input"""
    
    print("\n🎙️ Starting Interactive Voice Demo")
    print("="*50)
    print("Available commands:")
    print("- 'Hey Rhino' + your question (continuous listening)")
    print("- Press 'v' + Enter for manual voice input")
    print("- Type 'quit' to exit")
    print("- Type 'demo' to run automated demo")
    
    speak_text("RHINO voice assistant demo started. Say 'Hey Rhino' or press 'v' for voice input.")
    
    # Start continuous listening
    voice_thread = start_continuous_listening(get_mock_vehicle_data)
    
    try:
        while True:
            user_input = input("\nEnter command (v/demo/quit): ").strip().lower()
            
            if user_input == 'quit':
                break
            elif user_input == 'demo':
                demo_voice_commands()
            elif user_input == 'v':
                print("🎙️ Listening for voice command...")
                command = get_voice_command()
                if command and not command.startswith("[STT ERROR]"):
                    response = process_voice_command(command, get_mock_vehicle_data())
                    print(f"Response: {response}")
                    speak_text(response)
                else:
                    print("❌ Could not understand voice command")
            else:
                # Process text command directly
                if user_input:
                    response = process_voice_command(user_input, get_mock_vehicle_data())
                    print(f"Response: {response}")
                    speak_text(response)
    
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    
    finally:
        stop_continuous_listening()
        speak_text("RHINO voice assistant demo ended.")
def check_system_status():
    """Check if all voice assistant components are working"""
    print("\n🔧 System Status Check")
    print("="*30)
    
    # Check LLM availability
    try:
        from llm_handler import call_llm_local, call_llm_gemini
        local_response = call_llm_local("Say 'Local LLM working' if you can respond")
        print(f"✅ Local LLM (Ollama): {local_response[:30]}...")
    except Exception as e:
        print(f"❌ Local LLM Error: {e}")
    
    try:
        gemini_response = call_llm_gemini("Say 'Gemini working' if you can respond")
        print(f"✅ Gemini LLM: {gemini_response[:30]}...")
    except Exception as e:
        print(f"⚠️ Gemini LLM: {e}")
    
    # Check speech recognition
    try:
        import speech_recognition as sr
        print("✅ Speech Recognition: Available")
    except ImportError:
        print("❌ Speech Recognition: Not installed")
    
    # Check text-to-speech
    try:
        import pyttsx3
        print("✅ Text-to-Speech: Available")
    except ImportError:
        print("❌ Text-to-Speech: Not installed")
    
    # Display current vehicle data
    print(f"\n📊 Mock Vehicle Data:")
    data = get_mock_vehicle_data()
    for key, value in data.items():
        print(f"   {key}: {value}")

def simulate_driving_scenarios():
    """Simulate different driving scenarios with voice interaction"""
    scenarios = [
        {
            'name': 'Heavy Traffic',
            'data': {'vsv': 25.0, 'vlv': 20.0, 'headway': 5.0, 'visibility': 'clear', 'risk_level': 'high'},
            'trigger_command': "What should I do in heavy traffic?"
        },
        {
            'name': 'Highway Driving', 
            'data': {'vsv': 110.0, 'vlv': 105.0, 'headway': 50.0, 'visibility': 'clear', 'risk_level': 'low'},
            'trigger_command': "Is it safe to change lanes?"
        },
        {
            'name': 'Foggy Conditions',
            'data': {'vsv': 40.0, 'vlv': 35.0, 'headway': 15.0, 'visibility': 'foggy', 'risk_level': 'moderate'},
            'trigger_command': "How should I drive in fog?"
        }
    ]
    
    print("\n🚗 Driving Scenario Simulation")
    print("="*40)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[SCENARIO {i}] {scenario['name']}")
        print(f"Data: {scenario['data']}")
        
        # Update mock data
        mock_vehicle_data.update(scenario['data'])
        
        # Process the trigger command
        response = process_voice_command(scenario['trigger_command'], get_mock_vehicle_data())
        print(f"Command: '{scenario['trigger_command']}'")
        print(f"Response: {response}")
        
        # Optional: speak the response
        speak_text(f"Scenario {i}: {scenario['name']}. {response[:100]}")
        
        time.sleep(3)  # Pause between scenarios

def test_voice_features():
    """Test specific voice interaction features"""
    
    print("\n🧪 Testing Voice Features")
    print("="*50)
    
    # Test 1: Emergency handling
    print("1. Testing Emergency Response...")
    emergency_response = process_voice_command("help there's been an accident", get_mock_vehicle_data())
    print(f"Emergency Response: {emergency_response}")
    
    # Test 2: Status inquiry  
    print("\n2. Testing Status Inquiry...")
    status_response = process_voice_command("what's my current speed and distance", get_mock_vehicle_data())
    print(f"Status Response: {status_response}")
    
    # Test 3: Navigation
    print("\n3. Testing Navigation...")
    nav_response = process_voice_command("I need directions to the nearest hospital", get_mock_vehicle_data())
    print(f"Navigation Response: {nav_response}")
    
    # Test 4: General conversation
    print("\n4. Testing General Conversation...")
    general_response = process_voice_command("how are you doing today", get_mock_vehicle_data())
    print(f"General Response: {general_response}")

if __name__ == "__main__":
    print("🚗 RHINO Voice Assistant Enhanced Demo")
    print("="*50)
    
    # Check system status first
    check_system_status()
    
    print("\nChoose demo mode:")
    print("1. Interactive Demo (with voice input)")
    print("2. Automated Demo (text-based)")  
    print("3. Feature Testing")
    print("4. Driving Scenario Simulation")
    print("5. System Status Check Only")
    
    try:
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🎙️ Starting Interactive Voice Demo...")
            interactive_demo()
        elif choice == "2":
            print("\n🤖 Running Automated Demo...")
            demo_voice_commands()
        elif choice == "3":
            print("\n🧪 Running Feature Tests...")
            test_voice_features()
        elif choice == "4":
            print("\n🚗 Running Driving Scenarios...")
            simulate_driving_scenarios()
        elif choice == "5":
            print("\n✅ System check completed.")
        else:
            print("Invalid choice. Running automated demo...")
            demo_voice_commands()
            
        print("\n✅ Demo completed successfully!")
            
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("Make sure all dependencies are installed and API keys are configured.")
        print("Run 'pip install -r requirements.txt' and configure .env file")
    finally:
        print("\n👋 Thank you for trying RHINO Voice Assistant!")
