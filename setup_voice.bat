@echo off
echo RHINO-CAR Enhanced Voice Assistant Setup
echo =======================================

echo.
echo Installing required packages...
pip install -r requirements.txt

echo.
echo Installing additional audio dependencies...
pip install pyaudio==0.2.11

echo.
echo Setting up Ollama (local LLM)...
echo Please install Ollama from: https://ollama.ai/
echo Then run: ollama pull phi3

echo.
echo Configuration:
echo 1. Copy .env.example to .env
echo 2. Add your API keys (Gemini, Google Maps, etc.)
echo 3. Configure serial port and video stream settings

echo.
echo To test voice assistant:
echo python yolo/voice_demo.py

echo.
echo Setup complete! Check README for configuration details.
pause
