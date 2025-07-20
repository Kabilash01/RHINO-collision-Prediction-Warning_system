# voice_output.py
import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 165)  # words per minute

def speak(text):
    print("[🔊] Speaking:", text)
    engine.say(text)
    engine.runAndWait()
