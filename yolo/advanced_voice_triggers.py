# Enhanced Voice Trigger System for RHINO-CAR
import threading
import time
import pygame
from pynput import keyboard

class AdvancedVoiceTrigger:
    """Enhanced voice activation system with multiple trigger methods"""
    
    def __init__(self, voice_callback):
        self.voice_callback = voice_callback
        self.is_listening = False
        self.trigger_methods = {
            'keyboard': True,    # V key
            'gamepad': False,    # Controller button
            'gesture': False,    # Hand gesture
            'sound': False,      # Clap detection
            'hotword': False     # "Hey Rhino" detection
        }
    
    def setup_gamepad_trigger(self):
        """Setup game controller for voice activation"""
        try:
            pygame.init()
            pygame.joystick.init()
            
            if pygame.joystick.get_count() > 0:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                self.trigger_methods['gamepad'] = True
                print(f"✅ Gamepad trigger enabled: {joystick.get_name()}")
                return True
        except Exception as e:
            print(f"⚠️ Gamepad setup failed: {e}")
        return False
    
    def check_gamepad_trigger(self):
        """Check for gamepad button press"""
        if not self.trigger_methods['gamepad']:
            return False
            
        try:
            pygame.event.pump()
            joystick = pygame.joystick.Joystick(0)
            
            # Check button 0 (usually 'A' or 'X' button)
            if joystick.get_button(0):
                return True
        except:
            pass
        return False
    
    def setup_hotkey_combinations(self):
        """Setup advanced keyboard combinations"""
        def on_press(key):
            try:
                # Ctrl + V for voice
                if key == keyboard.Key.ctrl_l:
                    self.ctrl_pressed = True
                elif hasattr(key, 'char') and key.char == 'v' and getattr(self, 'ctrl_pressed', False):
                    self.voice_callback("hotkey_trigger")
                
                # F1 for emergency voice
                elif key == keyboard.Key.f1:
                    self.voice_callback("emergency_trigger")
                    
            except AttributeError:
                pass
        
        def on_release(key):
            if key == keyboard.Key.ctrl_l:
                self.ctrl_pressed = False
        
        # Start hotkey listener
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        listener.start()
        print("✅ Advanced hotkeys enabled: Ctrl+V (voice), F1 (emergency)")
    
    def setup_sound_trigger(self):
        """Setup clap detection for voice activation"""
        try:
            import pyaudio
            import numpy as np
            
            def detect_clap():
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 44100
                THRESHOLD = 3000  # Clap detection threshold
                
                p = pyaudio.PyAudio()
                stream = p.stream(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK)
                
                print("✅ Clap detection enabled: Double clap to activate voice")
                
                clap_times = []
                while True:
                    try:
                        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
                        volume = np.sqrt(np.mean(data**2))
                        
                        if volume > THRESHOLD:
                            current_time = time.time()
                            clap_times.append(current_time)
                            
                            # Keep only recent claps (within 2 seconds)
                            clap_times = [t for t in clap_times if current_time - t < 2.0]
                            
                            # Check for double clap pattern
                            if len(clap_times) >= 2:
                                if clap_times[-1] - clap_times[-2] < 0.8:  # Double clap within 0.8 seconds
                                    self.voice_callback("clap_trigger")
                                    clap_times.clear()
                                    time.sleep(1)  # Prevent multiple triggers
                    except Exception as e:
                        print(f"Clap detection error: {e}")
                        break
                        
                stream.stop_stream()
                stream.close()
                p.terminate()
            
            # Start clap detection in background
            clap_thread = threading.Thread(target=detect_clap, daemon=True)
            clap_thread.start()
            self.trigger_methods['sound'] = True
            return True
            
        except ImportError:
            print("⚠️ Clap detection requires pyaudio: pip install pyaudio")
        except Exception as e:
            print(f"⚠️ Clap detection setup failed: {e}")
        return False

# Integration example
def enhanced_voice_callback(trigger_type):
    """Handle different types of voice triggers"""
    trigger_messages = {
        'manual': "Manual voice activation",
        'hotkey_trigger': "Hotkey voice activation", 
        'emergency_trigger': "EMERGENCY voice activation",
        'clap_trigger': "Clap-activated voice",
        'gamepad_trigger': "Controller voice activation"
    }
    
    message = trigger_messages.get(trigger_type, "Voice activation")
    print(f"[🎙️] {message}")
    
    # Different behaviors for different triggers
    if trigger_type == 'emergency_trigger':
        speak_text("EMERGENCY voice assistant activated! What's your emergency?")
    else:
        speak_text("Voice assistant activated. How can I help you?")
    
    # Continue with normal voice processing...
