import serial
import json

ser = serial.Serial('COM14', 115200, timeout=1)

while True:
    if ser.in_waiting:
        try:
            line = ser.readline().decode(errors='ignore').strip()
            if line.startswith("{") and line.endswith("}"):
                data = json.loads(line)
                temp = data.get("temperature")
                hum = data.get("humidity")
                dist = data.get("distance")
                buzz = data.get("buzzer")
                print(f"🌡 Temp: {temp}°C | 💧 Hum: {hum}% | 📏 Distance: {dist} mm | 🔔 Buzzer: {buzz}")
            else:
                print("[SKIPPED] Incomplete or malformed line:", line)
        except Exception as e:
            print("⚠️ JSON Parse Error:", e)
