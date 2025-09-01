import os
import sys
import cv2
import json
import torch
import numpy as np
import torch.nn as nn
from collections import deque
from ultralytics import YOLO
import serial

# Add RHINO-X utils and alerts
sys.path.append(os.path.abspath("../utils"))
sys.path.append(os.path.abspath("../alerts"))

from velocity_model import VelocityPredictor
from visibility_classifier import predict_visibility_from_frame
from hybrid_headway import estimate_headway
from prediction_horizon import map_visibility_to_prt
from vlv_tracker import get_vlv
from sms_alert import SmsAlert
from email_alert import EmailAlert

# === Risk Sequence Model ===
class RiskSequenceModel(nn.Module):
    def __init__(self, input_dim=3, hidden_dim=64, num_layers=2, output_dim=3):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return self.sigmoid(out)

# === Device Setup ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# === Load Models ===
risk_seq_model = RiskSequenceModel().to(device)
risk_seq_model.load_state_dict(torch.load("../models/risk_seq_model.pth", map_location=device))
risk_seq_model.eval()

vsv_model = VelocityPredictor().to(device)
vsv_model.load_state_dict(torch.load("../models/velocity_model.pth", map_location=device))
vsv_model.eval()

yolo = YOLO("yolov8n.pt")
with open("../label_mapping.json", 'r') as f:
    label_map = json.load(f)
vehicle_ids = [int(k) for k, v in label_map.items() if v in ["car", "truck", "bus", "motorcycle", "bicycle"]]

# === Serial Port ===
try:
    ser = serial.Serial('COM3', 115200, timeout=1)
    print("[INFO] Serial COM3 connected.")
except:
    ser = None
    print("[WARNING] Serial port not connected. Using defaults.")

def read_sensor_data():
    if ser and ser.in_waiting:
        try:
            line = ser.readline().decode(errors='ignore').strip()
            if not line.startswith("{") or not line.endswith("}"):
                print("[SKIPPED] Invalid serial:", line)
                return 250.0, 0.0, 0.0, "sunny"

            data = json.loads(line)
            distance = float(data.get("distance", 9999))
            temperature = float(data.get("temperature", 0.0))
            humidity = float(data.get("humidity", 0.0))
            visibility = "foggy" if distance >= 2000 else "sunny"
            return distance, temperature, humidity, visibility
        except Exception as e:
            print(f"[ERROR] Failed to parse serial: {e}")
    return 250.0, 0.0, 0.0, "sunny"

# === Runtime Parameters ===
RISK_THRESHOLDS = [0.7, 0.4, 0.2]
last_speeds = [40.0, 42.0, 41.0]
history = deque(maxlen=5)

# === IP Webcam Video Stream ===
VIDEO_URL = "http://192.168.82.137:8080/video"
cap = cv2.VideoCapture(VIDEO_URL)
if not cap.isOpened():
    print("[ERROR] Video stream not opened.")
    exit()

print("[INFO] RHINO-X live stream started...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = yolo(frame)[0]
    boxes = results.boxes
    vehicle_boxes = [b for b in boxes if int(b.cls) in vehicle_ids]

    sensor_value, temperature, humidity, visibility = read_sensor_data()
    if sensor_value == 9999:
        visibility = predict_visibility_from_frame(frame)

    _, y1, _, y2 = vehicle_boxes[0].xyxy[0] if vehicle_boxes else (0, 0, 0, 0)
    box_height = y2 - y1
    headway = estimate_headway(sensor_value, box_height)

    vsv_tensor = torch.tensor([last_speeds], dtype=torch.float32).to(device)
    vsv = vsv_model(vsv_tensor).item()
    last_speeds = [last_speeds[1], last_speeds[2], vsv]

    vlv = get_vlv()
    history.append([vsv, vlv, headway])

    forecast = [0.0, 0.0, 0.0]
    if len(history) == 5:
        seq_input = torch.tensor(np.array(history), dtype=torch.float32).unsqueeze(0).to(device)
        with torch.no_grad():
            forecast = risk_seq_model(seq_input).squeeze(0).tolist()

    prt = map_visibility_to_prt(visibility)
    ttc = headway / (vsv - vlv + 1e-3)

    # === Risk bars ===
    for i, risk in enumerate(forecast):
        color = (0, 255, 0)
        if risk > RISK_THRESHOLDS[0]:
            color = (0, 0, 255)
        elif risk > RISK_THRESHOLDS[1]:
            color = (0, 255, 255)
        elif risk > RISK_THRESHOLDS[2]:
            color = (0, 165, 255)
        x = 30 + i * 50
        cv2.rectangle(frame, (x, 40), (x + 30, 70), color, -1)
        cv2.putText(frame, f"{risk:.2f}", (x, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # === Fallback Crash Detection ===
    crash_flag = False
    if len(vehicle_boxes) >= 2:
        box1 = vehicle_boxes[0].xyxy[0].cpu().numpy()
        box2 = vehicle_boxes[1].xyxy[0].cpu().numpy()
        xA = max(box1[0], box2[0])
        yA = max(box1[1], box2[1])
        xB = min(box1[2], box2[2])
        yB = min(box1[3], box2[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (box1[2] - box1[0]) * (box1[3] - box1[1])
        boxBArea = (box2[2] - box2[0]) * (box2[3] - box2[1])
        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-3)
        if iou > 0.3:
            crash_flag = True
            print(f"[💥] Overlap CRASH DETECTED! IoU = {iou:.2f}")

    # === Alert System ===
    if (forecast[0] > 0.3 and headway < 20.0 and ttc < prt + 1) or crash_flag:
        cv2.putText(frame, "🔥 CRASH DETECTED!", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        SmsAlert(location="⚠ Crash Detected").run()
        EmailAlert(location="⚠ Crash Detected").run()
    else:
        cv2.putText(frame, "✓ SAFE", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # === Sensor + System Info ===
    cv2.putText(frame, f"VSV: {vsv:.1f} VLV: {vlv:.1f} Headway: {headway:.1f}", (30, 105),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"Weather: {visibility}", (30, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 255), 1)
    cv2.putText(frame, f"Temp: {temperature:.1f}C  Humidity: {humidity:.1f}%", (30, 190),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
    cv2.putText(frame, f"Distance: {sensor_value:.1f} mm", (30, 220),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("RHINO-X Live", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
