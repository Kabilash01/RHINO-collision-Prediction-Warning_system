import cv2
import torch
import numpy as np
import json
from collections import deque
from ultralytics import YOLO
import torch.nn as nn
import sys
import os
sys.path.append(os.path.abspath("../utils"))
sys.path.append(os.path.abspath("../alerts"))
from velocity_model import VelocityPredictor
from visibility_classifier import predict_visibility_from_frame
from hybrid_headway import estimate_headway
from prediction_horizon import map_visibility_to_prt
from vlv_tracker import get_vlv
from sms_alert import SmsAlert
from email_alert import EmailAlert
from llm_handler import generate_collision_explanation, get_voice_command, speak_text, get_route

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

# === Load Models ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

# === Video Source ===
VIDEO_PATH = "C:/RHINO-CAR/test_videos/test (6).mp4"
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("[ERROR] Could not open video.")
    exit()

# === Initialize State ===
RISK_THRESHOLDS = [0.7, 0.4, 0.2]
last_speeds = [40.0, 42.0, 41.0]
history = deque(maxlen=5)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = yolo(frame)[0]
    boxes = results.boxes
    vehicle_boxes = [b for b in boxes if int(b.cls) in vehicle_ids]

    _, y1, _, y2 = vehicle_boxes[0].xyxy[0] if vehicle_boxes else (0, 0, 0, 0)
    box_height = y2 - y1
    sensor_value = 250.0  # Simulated
    headway = estimate_headway(sensor_value, box_height)
    visibility = predict_visibility_from_frame(frame)

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

    # === Draw Risk Bars ===
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

    # === Alert Triggering ===
    if forecast[0] > 0.3 and headway < 20.0 and ttc < prt + 1:
        cv2.putText(frame, "🔥 CRASH DETECTED!", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        SmsAlert(location="Video Test Mode").run()
        EmailAlert(location="Video Test Mode").run()
        explanation = generate_collision_explanation(vsv, vlv, headway, forecast[0])
        speak_text(explanation)

        driver_command = get_voice_command().lower()
        if "route" in driver_command or "direction" in driver_command:
            speak_text("Where would you like to go?")
            destination = get_voice_command()
            route_summary = get_route(destination)
            speak_text(route_summary)

    else:
        cv2.putText(frame, "✓ SAFE", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # === Display Stats ===
    cv2.putText(frame, f"VSV: {vsv:.1f} VLV: {vlv:.1f} Headway: {headway:.1f}", (30, 105),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"Weather: {visibility}", (30, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 255), 1)

    cv2.imshow("RHINO-X Video Test", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
