#!/usr/bin/env python3
"""
RHINO-CAR API Key Manager
Quick tool to update and test API keys without restarting the system
"""

import os
import sys
from dotenv import load_dotenv, set_key

# Add project paths
sys.path.append(os.path.abspath("../utils"))
sys.path.append(os.path.abspath("../alerts"))

try:
    from llm_handler import update_gemini_api_key, check_llm_status, call_llm_gemini, call_llm_local
except ImportError:
    print("Error: Could not import llm_handler. Make sure you're in the yolo directory.")
    sys.exit(1)

def update_env_file(key_name, key_value):
    """Update .env file with new API key"""
    env_path = "../.env"
    if not os.path.exists(env_path):
        env_path = ".env"
    
    if not os.path.exists(env_path):
        print("Creating new .env file...")
        with open(env_path, 'w') as f:
            f.write(f"{key_name}={key_value}\n")
    else:
        set_key(env_path, key_name, key_value)
    
    print(f"✅ Updated {env_path} with new {key_name}")

def test_new_gemini_key():
    """Test a new Gemini API key"""
    print("\n🔑 Gemini API Key Update")
    print("=" * 40)
    
    current_key = os.getenv("GEMINI_API_KEY", "Not set")
    print(f"Current key: {current_key[:20]}...{current_key[-10:] if len(current_key) > 30 else current_key}")
    
    new_key = input("\nEnter new Gemini API key: ").strip()
    
    if not new_key:
        print("❌ No key provided")
        return
    
    if len(new_key) < 30:
        print("⚠️ Warning: API key seems short. Are you sure it's correct?")
        confirm = input("Continue? (y/N): ").lower()
        if confirm != 'y':
            return
    
    print("\n🧪 Testing new API key...")
    
    # Test the key
    if update_gemini_api_key(new_key):
        # Update .env file
        update_env_file("GEMINI_API_KEY", new_key)
        print("✅ Gemini API key updated successfully!")
        
        # Test with emergency prompt
        try:
            test_prompt = "You are an emergency vehicle assistant. A crash has been detected. The driver says 'I need help'. Respond with immediate helpful guidance in 2 sentences."
            response = call_llm_gemini(test_prompt)
            print(f"\n🚨 Emergency Test Response:\n{response}")
        except Exception as e:
            print(f"⚠️ Emergency test failed: {e}")
    else:
        print("❌ Failed to update API key. Please check the key and try again.")

def check_system_status():
    """Check status of all LLM systems"""
    print("\n🔍 System Status Check")
    print("=" * 30)
    
    status = check_llm_status()
    
    print(f"\nSystem Summary:")
    print(f"Gemini API: {'✅ Working' if status['gemini'] else '❌ Not working'}")
    print(f"Ollama Local: {'✅ Working' if status['ollama'] else '❌ Not working'}")
    
    if not status['gemini'] and not status['ollama']:
        print("\n⚠️ WARNING: No LLM systems are working!")
        print("Emergency voice assistant will not function properly.")
    elif not status['gemini']:
        print("\n💡 INFO: Only Ollama is working. Emergency responses will use local AI.")
    elif not status['ollama']:
        print("\n💡 INFO: Only Gemini is working. No fallback available if Gemini fails.")
    else:
        print("\n✅ GOOD: Both LLM systems are working. Full fallback support available.")

def emergency_voice_test():
    """Test emergency voice response with current setup"""
    print("\n🚨 Emergency Voice Test")
    print("=" * 25)
    
    emergency_scenarios = [
        "I need help, there's been an accident",
        "I'm injured and need directions to hospital", 
        "What should I do after a crash?",
        "Emergency! Call ambulance"
    ]
    
    print("Testing emergency responses...")
    
    for i, scenario in enumerate(emergency_scenarios, 1):
        print(f"\n[Test {i}] Driver says: '{scenario}'")
        
        try:
            emergency_context = f"EMERGENCY SITUATION: Crash detected. Vehicle data - Speed: 45 km/h, Distance: 5m, Risk: critical. Driver says: '{scenario}'"
            response = call_llm_gemini(f"You are an emergency vehicle safety assistant. {emergency_context}. Provide immediate, helpful emergency guidance. Be concise and actionable.")
            print(f"Response: {response}")
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")

def main():
    """Main menu"""
    print("🚗 RHINO-CAR API Key Manager")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Update Gemini API key")
        print("2. Check system status") 
        print("3. Test emergency voice responses")
        print("4. Show current configuration")
        print("5. Exit")
        
        try:
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                test_new_gemini_key()
            elif choice == "2":
                check_system_status()
            elif choice == "3":
                emergency_voice_test()
            elif choice == "4":
                print(f"\nCurrent Configuration:")
                print(f"Gemini API Key: {os.getenv('GEMINI_API_KEY', 'Not set')[:20]}...")
                print(f"Mapbox Token: {os.getenv('MAPBOX_ACCESS_TOKEN', 'Not set')[:20]}...")
                print(f"Serial Port: {os.getenv('SERIAL_PORT', 'COM14')}")
                print(f"Video URL: {os.getenv('VIDEO_URL', 'Not set')}")
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    main()
