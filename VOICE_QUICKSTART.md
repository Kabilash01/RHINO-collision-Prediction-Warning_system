# RHINO Voice Assistant Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd RHINO-CAR
pip install -r requirements.txt
pip install pyaudio  # For microphone support
```

### Step 2: Install Ollama (Local LLM)
1. Download from: https://ollama.ai/
2. Install and run: `ollama pull phi3`

### Step 3: Configure API Keys (Optional)
```bash
# Copy configuration template
cp .env.example .env

# Edit .env and add your keys:
GEMINI_API_KEY=your_key_here  # For better responses
GOOGLE_MAPS_API_KEY=your_key  # For navigation
```

### Step 4: Test Voice Assistant
```bash
cd yolo
python voice_demo.py
```

## 🎙️ Voice Commands Cheat Sheet

### Wake Word
- **"Hey Rhino"** - Activate voice assistant

### Emergency Commands
- "Help! Emergency assistance needed"
- "Accident detected, what should I do?"
- "I need immediate help"

### Status Commands  
- "What's my current speed?"
- "How's my following distance?"
- "What's the weather visibility?"
- "What's my risk level?"

### Navigation Commands
- "Navigate to [destination]"
- "Get directions to the hospital"
- "How do I get to [place]?"

### Safety Commands
- "Is it safe to overtake?"
- "Should I change lanes?"
- "How should I drive in fog?"
- "What's the safe following distance?"

### General Commands
- "How are you today?"
- "Tell me about road safety"
- "What should I do in heavy traffic?"

## 🔧 Manual Controls

### Keyboard Shortcuts (in main app)
- **'v' key** - Activate single voice command
- **'q' key** - Quit application

### Demo Modes
1. **Interactive Demo** - Live voice interaction
2. **Automated Demo** - Predefined command testing  
3. **Feature Testing** - Comprehensive system test
4. **Scenario Simulation** - Different driving conditions

## ⚡ Performance Tips

### For Better Voice Recognition:
- Speak clearly and at normal pace
- Use a good quality microphone
- Minimize background noise
- Ensure stable internet connection

### For Better LLM Responses:
- Configure Gemini API key for advanced responses
- Keep Ollama running in background
- Use specific, clear commands

### For System Performance:
- Use GPU for faster video processing
- Close unnecessary applications
- Ensure adequate RAM (8GB+ recommended)

## 🚨 Troubleshooting

### Voice Not Working?
```bash
# Test microphone
python -c "import speech_recognition as sr; print('Mic test:', sr.Microphone.list_microphone_names())"

# Test TTS
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Test'); engine.runAndWait()"
```

### LLM Not Responding?
```bash
# Test Ollama
ollama run phi3 "Hello, are you working?"

# Check Gemini API
python -c "import os; print('Gemini key:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

### Audio Issues?
- Check Windows audio drivers
- Try: `pip uninstall pyaudio && pip install pyaudio`
- Use external USB microphone if built-in fails

## 📱 Integration with Main System

### In rhinomain.py:
- Voice assistant runs automatically in background
- Say "Hey Rhino" anytime during driving
- Emergency commands trigger during crash detection
- Manual 'v' key for on-demand interaction

### Real-time Data Integration:
- Current vehicle speed (VSV)
- Lead vehicle speed (VLV)  
- Following distance (headway)
- Weather visibility
- Risk assessment level
- Temperature and humidity

## 🎯 Best Practices

1. **Keep commands natural** - "What's my speed?" vs "speed query"
2. **Use context** - Assistant knows your current driving situation
3. **Emergency priority** - Emergency commands get immediate response
4. **Safety first** - Voice interaction designed for hands-free operation
5. **Regular updates** - Keep models and dependencies updated

## 🔄 Next Steps

1. **Customize voice commands** - Edit `llm_handler.py` for new commands
2. **Train custom models** - Use your own driving data
3. **Integrate hardware** - Add more sensors for enhanced detection
4. **Cloud deployment** - Scale system for fleet management

---

**Need help?** Check the full README.md or open an issue on GitHub!
