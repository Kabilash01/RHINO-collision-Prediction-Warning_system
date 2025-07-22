# llm_handler.py (Enhanced LLM with Gemini + Ollama Support)
import os
import speech_recognition as sr
import pyttsx3
import ollama
import google.generativeai as genai
from dotenv import load_dotenv
import threading
import time
from datetime import datetime

load_dotenv()

# === LLM Configuration ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro')

# Voice interaction state
voice_active = False
continuous_listening = False

# === LLM: Local Ollama ===
def call_llm_local(prompt):
    try:
        response = ollama.chat(
            model='phi3',  # You can also use 'mistral' or 'llama3'
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"[OLLAMA ERROR] {e}"

# === LLM: Google Gemini ===
def call_llm_gemini(prompt):
    try:
        if not GEMINI_API_KEY:
            return call_llm_local(prompt)  # Fallback to local
        
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[GEMINI ERROR] {e}")
        return call_llm_local(prompt)  # Fallback to local

# === ALERT GENERATION ===
def generate_collision_explanation(vsv, vlv, headway, risk_score):
    prompt = f"""Explain this situation in simple terms:
- Subject Vehicle Speed (VSV): {vsv:.1f} km/h
- Lead Vehicle Speed (VLV): {vlv:.1f} km/h
- Headway Distance: {headway:.1f} m
- Predicted Risk Score: {risk_score:.2f}
"""
    return call_llm_local(prompt)

def generate_alert_message(vsv, vlv, headway, risk_score):
    prompt = f"""Generate a short urgent alert for the driver:
- Speed: {vsv} km/h
- Lead speed: {vlv} km/h
- Headway: {headway:.1f} meters
- Risk Score: {risk_score:.2f}
"""
    return call_llm_local(prompt)

# === TTS: Speak Output ===
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    engine.say(text)
    engine.runAndWait()

# === STT: Voice Input ===
def get_voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[🎙️] Listening for driver command...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print("[🗣️] You said:", text)
            return text
        except sr.UnknownValueError:
            return "[STT ERROR] Could not understand audio"
        except sr.RequestError as e:
            return f"[STT ERROR] {e}"

# === ROUTE SIMULATION (Offline Prompt-based) ===
def get_route(destination, origin="Coimbatore, India"):
    prompt = f"Generate a simple voice-friendly driving route summary from {origin} to {destination}."
    return call_llm_local(prompt)

# === ENHANCED VOICE ASSISTANT FEATURES ===

def process_voice_command(command, vehicle_data=None):
    """Process various voice commands with context awareness"""
    command = command.lower()
    
    # Safety commands
    if any(word in command for word in ["help", "emergency", "accident", "crash"]):
        return handle_emergency_command(command, vehicle_data)
    
    # Navigation commands  
    elif any(word in command for word in ["route", "direction", "navigate", "go to"]):
        return handle_navigation_command(command)
    
    # Vehicle status commands
    elif any(word in command for word in ["status", "speed", "distance", "weather"]):
        return handle_status_command(command, vehicle_data)
    
    # Settings commands
    elif any(word in command for word in ["settings", "volume", "voice", "alert"]):
        return handle_settings_command(command)
    
    # General assistant
    else:
        return handle_general_command(command, vehicle_data)

def handle_emergency_command(command, vehicle_data):
    """Handle emergency-related commands"""
    if vehicle_data:
        context = f"Vehicle status: Speed {vehicle_data.get('vsv', 0):.1f} km/h, Lead vehicle {vehicle_data.get('vlv', 0):.1f} km/h, Distance {vehicle_data.get('headway', 0):.1f}m, Visibility {vehicle_data.get('visibility', 'unknown')}"
    else:
        context = "No current vehicle data available"
    
    prompt = f"""You are RHINO emergency assistant. The driver said: '{command}'. 
Current situation: {context}
Provide immediate helpful emergency guidance. Be concise and actionable."""
    
    return call_llm_gemini(prompt)

def handle_navigation_command(command):
    """Handle navigation-related commands"""
    speak_text("Where would you like to go?")
    destination = get_voice_command()
    if destination and not destination.startswith("[STT ERROR]"):
        route_summary = get_route(destination)
        return f"Route to {destination}: {route_summary}"
    return "I couldn't understand the destination. Please try again."

def handle_status_command(command, vehicle_data):
    """Handle vehicle status inquiries"""
    if not vehicle_data:
        return "Vehicle data is not currently available."
    
    status_info = f"""Current vehicle status:
- Your speed: {vehicle_data.get('vsv', 0):.1f} km/h
- Lead vehicle speed: {vehicle_data.get('vlv', 0):.1f} km/h  
- Following distance: {vehicle_data.get('headway', 0):.1f} meters
- Weather visibility: {vehicle_data.get('visibility', 'unknown')}
- Risk level: {vehicle_data.get('risk_level', 'normal')}"""
    
    return status_info

def handle_settings_command(command):
    """Handle settings-related commands"""
    if "volume" in command:
        if "up" in command or "increase" in command:
            return "Volume increased"
        elif "down" in command or "decrease" in command:
            return "Volume decreased"
    
    return "Settings command recognized. What would you like to adjust?"

def handle_general_command(command, vehicle_data):
    """Handle general conversation and questions"""
    context = ""
    if vehicle_data:
        context = f"Current driving context: Speed {vehicle_data.get('vsv', 0):.1f} km/h, visibility {vehicle_data.get('visibility', 'normal')}"
    
    prompt = f"""You are RHINO, an intelligent vehicle assistant. The driver says: '{command}'
{context}
Respond helpfully and conversationally. Keep responses under 50 words for safety while driving."""
    
    return call_llm_gemini(prompt)

# === CONTINUOUS VOICE INTERACTION ===
def start_continuous_listening(vehicle_data_callback=None):
    """Start background voice listening for wake word 'Hey Rhino'"""
    global continuous_listening, voice_active
    continuous_listening = True
    
    def listen_loop():
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        
        # Adjust for ambient noise
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
        
        print("[🎙️] Continuous listening started. Say 'Hey Rhino' to activate...")
        
        while continuous_listening:
            try:
                with mic as source:
                    # Listen for wake word with shorter timeout
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                # Use offline recognition for wake word detection
                try:
                    text = recognizer.recognize_google(audio).lower()
                    if "hey rhino" in text or "rhino" in text:
                        voice_active = True
                        speak_text("Yes, how can I help you?")
                        
                        # Listen for actual command
                        command = get_voice_command()
                        if command and not command.startswith("[STT ERROR]"):
                            # Get current vehicle data if callback provided
                            current_data = vehicle_data_callback() if vehicle_data_callback else None
                            response = process_voice_command(command, current_data)
                            speak_text(response)
                        
                        voice_active = False
                        
                except sr.UnknownValueError:
                    pass  # No speech detected, continue listening
                    
            except sr.WaitTimeoutError:
                pass  # Timeout, continue listening
            except Exception as e:
                print(f"[VOICE ERROR] {e}")
                time.sleep(1)
    
    # Start listening in background thread
    listen_thread = threading.Thread(target=listen_loop, daemon=True)
    listen_thread.start()
    return listen_thread

def stop_continuous_listening():
    """Stop continuous voice listening"""
    global continuous_listening
    continuous_listening = False
    print("[🎙️] Continuous listening stopped.")
