import cv2
import torch
import numpy as np
from ultralytics import YOLO

class YoloDetector:
    def __init__(self, model_path='models/yolov8n.pt', device='cuda'):
        self.device = device
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame)
        boxes = results[0].boxes
        detections = []

        for box in boxes:
            detection = {
                'xyxy': box.xyxy[0].cpu().numpy(),
                'confidence': box.conf[0].item(),
                'class_id': int(box.cls[0].item())
            }
            detections.append(detection)

        return detections

    def draw_detections(self, frame, detections):
        for detection in detections:
            x1, y1, x2, y2 = detection['xyxy']
            confidence = detection['confidence']
            class_id = detection['class_id']
            label = f'ID: {class_id} Conf: {confidence:.2f}'

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame