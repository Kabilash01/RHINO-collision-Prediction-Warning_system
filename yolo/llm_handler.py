# llm_handler.py (Offline Local LLM with Ollama)
import os
import speech_recognition as sr
import pyttsx3
import ollama

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
