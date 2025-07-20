# voice_input.py
import speech_recognition as sr

def listen_command(timeout=5):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[🎤] Listening for driver command...")
        audio = recognizer.listen(source, timeout=timeout)
        try:
            text = recognizer.recognize_google(audio)
            print("[🗣️] You said:", text)
            return text
        except sr.UnknownValueError:
            print("[❌] Could not understand audio.")
        except sr.RequestError as e:
            print("[🚫] STT service error:", e)
    return ""
