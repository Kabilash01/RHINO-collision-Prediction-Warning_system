# RHINO-CAR Advanced Driver Monitoring System
"""
Eye tracking, drowsiness detection, and driver behavior analysis
"""
import cv2
import numpy as np
import torch
import torch.nn as nn
import mediapipe as mp
from collections import deque
import time
from datetime import datetime

class DriverMonitoringSystem:
    """Advanced driver state monitoring with eye tracking and behavior analysis"""
    
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye tracking indices (MediaPipe landmarks)
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        # Driver state tracking
        self.blink_counter = 0
        self.drowsiness_counter = 0
        self.distraction_counter = 0
        self.head_pose_history = deque(maxlen=30)
        self.blink_history = deque(maxlen=100)
        
        # Thresholds
        self.EYE_AR_THRESH = 0.25
        self.EYE_AR_CONSEC_FRAMES = 15
        self.DROWSY_TIME_THRESHOLD = 3.0
        self.DISTRACTION_THRESHOLD = 2.0
        
        # Driver behavior model (simple neural network)
        self.behavior_model = self.create_behavior_model()
        
    def create_behavior_model(self):
        """Create neural network for driver behavior classification"""
        model = nn.Sequential(
            nn.Linear(10, 64),  # Input: eye ratio, head pose, blink rate, etc.
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 4),   # Output: alert, drowsy, distracted, normal
            nn.Softmax(dim=1)
        )
        return model
    
    def calculate_eye_aspect_ratio(self, eye_landmarks):
        """Calculate eye aspect ratio for blink detection"""
        if len(eye_landmarks) < 6:
            return 0.0
        
        # Vertical eye landmarks
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal eye landmark
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # Eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear
    
    def extract_eye_landmarks(self, landmarks, eye_indices):
        """Extract eye landmarks from face mesh"""
        eye_points = []
        for idx in eye_indices:
            point = landmarks.landmark[idx]
            eye_points.append([point.x, point.y])
        return np.array(eye_points)
    
    def calculate_head_pose(self, landmarks, frame_shape):
        """Calculate head pose angles"""
        h, w = frame_shape[:2]
        
        # 3D model points
        model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])
        
        # 2D image points
        image_points = np.array([
            (landmarks.landmark[1].x * w, landmarks.landmark[1].y * h),     # Nose tip
            (landmarks.landmark[152].x * w, landmarks.landmark[152].y * h),   # Chin
            (landmarks.landmark[226].x * w, landmarks.landmark[226].y * h),   # Left eye left corner
            (landmarks.landmark[446].x * w, landmarks.landmark[446].y * h),   # Right eye right corner
            (landmarks.landmark[57].x * w, landmarks.landmark[57].y * h),     # Left mouth corner
            (landmarks.landmark[287].x * w, landmarks.landmark[287].y * h)    # Right mouth corner
        ], dtype="double")
        
        # Camera matrix
        focal_length = w
        center = (w/2, h/2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]], dtype="double")
        
        # Distortion coefficients
        dist_coeffs = np.zeros((4,1))
        
        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
        
        if success:
            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            
            # Calculate Euler angles
            angles = cv2.RQDecomp3x3(rotation_matrix)[0]
            return angles[0], angles[1], angles[2]  # pitch, yaw, roll
        
        return 0, 0, 0
    
    def analyze_driver_state(self, frame):
        """Main function to analyze driver state"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        driver_state = {
            'status': 'normal',
            'drowsiness_level': 0.0,
            'distraction_level': 0.0,
            'blink_rate': 0.0,
            'head_pose': (0, 0, 0),
            'alerts': []
        }
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Extract eye landmarks
                left_eye = self.extract_eye_landmarks(face_landmarks, self.LEFT_EYE[:6])
                right_eye = self.extract_eye_landmarks(face_landmarks, self.RIGHT_EYE[:6])
                
                # Calculate eye aspect ratios
                left_ear = self.calculate_eye_aspect_ratio(left_eye)
                right_ear = self.calculate_eye_aspect_ratio(right_eye)
                avg_ear = (left_ear + right_ear) / 2.0
                
                # Blink detection
                if avg_ear < self.EYE_AR_THRESH:
                    self.blink_counter += 1
                else:
                    if self.blink_counter >= self.EYE_AR_CONSEC_FRAMES:
                        self.drowsiness_counter += 1
                    self.blink_counter = 0
                
                # Store blink data
                self.blink_history.append(avg_ear)
                
                # Calculate head pose
                pitch, yaw, roll = self.calculate_head_pose(face_landmarks, frame.shape)
                self.head_pose_history.append((pitch, yaw, roll))
                driver_state['head_pose'] = (pitch, yaw, roll)
                
                # Analyze drowsiness
                if len(self.blink_history) >= 30:
                    recent_blinks = list(self.blink_history)[-30:]
                    closed_eyes_ratio = sum(1 for ear in recent_blinks if ear < self.EYE_AR_THRESH) / len(recent_blinks)
                    driver_state['drowsiness_level'] = closed_eyes_ratio
                    
                    if closed_eyes_ratio > 0.4:  # 40% of time eyes closed
                        driver_state['status'] = 'drowsy'
                        driver_state['alerts'].append('DROWSINESS_DETECTED')
                
                # Analyze distraction (head pose)
                if len(self.head_pose_history) >= 10:
                    recent_poses = list(self.head_pose_history)[-10:]
                    avg_yaw = np.mean([pose[1] for pose in recent_poses])
                    
                    if abs(avg_yaw) > 25:  # Looking away from road
                        driver_state['distraction_level'] = abs(avg_yaw) / 45.0
                        if abs(avg_yaw) > 35:
                            driver_state['status'] = 'distracted'
                            driver_state['alerts'].append('DISTRACTION_DETECTED')
                
                # Calculate blink rate
                if len(self.blink_history) >= 60:  # Last 2 seconds at 30fps
                    recent_blinks = list(self.blink_history)[-60:]
                    blink_transitions = 0
                    for i in range(1, len(recent_blinks)):
                        if recent_blinks[i-1] < self.EYE_AR_THRESH and recent_blinks[i] >= self.EYE_AR_THRESH:
                            blink_transitions += 1
                    driver_state['blink_rate'] = blink_transitions * 30  # Blinks per minute
                
                # Draw landmarks and info on frame
                self.draw_driver_monitoring_overlay(frame, driver_state, left_eye, right_eye)
        
        return driver_state, frame
    
    def draw_driver_monitoring_overlay(self, frame, driver_state, left_eye, right_eye):
        """Draw driver monitoring overlay on frame"""
        h, w = frame.shape[:2]
        
        # Status indicator
        status_color = {
            'normal': (0, 255, 0),
            'drowsy': (0, 165, 255),
            'distracted': (0, 0, 255)
        }
        color = status_color.get(driver_state['status'], (255, 255, 255))
        
        cv2.putText(frame, f"Driver: {driver_state['status'].upper()}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Drowsiness level
        drowsy_level = int(driver_state['drowsiness_level'] * 100)
        cv2.putText(frame, f"Drowsiness: {drowsy_level}%", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Distraction level  
        distract_level = int(driver_state['distraction_level'] * 100)
        cv2.putText(frame, f"Distraction: {distract_level}%", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        
        # Blink rate
        cv2.putText(frame, f"Blink Rate: {driver_state['blink_rate']:.1f}/min", 
                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Head pose
        pitch, yaw, roll = driver_state['head_pose']
        cv2.putText(frame, f"Head: P{pitch:.1f} Y{yaw:.1f} R{roll:.1f}", 
                   (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Draw eye regions
        if len(left_eye) > 0:
            cv2.polylines(frame, [np.int32(left_eye * [w, h])], True, (0, 255, 0), 1)
        if len(right_eye) > 0:
            cv2.polylines(frame, [np.int32(right_eye * [w, h])], True, (0, 255, 0), 1)
        
        # Alert indicators
        if driver_state['alerts']:
            for i, alert in enumerate(driver_state['alerts']):
                cv2.putText(frame, f"⚠️ {alert}", 
                           (w - 300, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    def generate_driver_alert(self, driver_state):
        """Generate appropriate alerts based on driver state"""
        alerts = []
        
        if driver_state['status'] == 'drowsy':
            alerts.append({
                'type': 'drowsiness',
                'severity': 'high',
                'message': f"Driver drowsiness detected: {driver_state['drowsiness_level']*100:.1f}%",
                'recommendation': "Pull over safely and rest, or switch drivers"
            })
        
        if driver_state['status'] == 'distracted':
            alerts.append({
                'type': 'distraction',
                'severity': 'medium',
                'message': f"Driver distraction detected: looking away {driver_state['distraction_level']*100:.1f}%",
                'recommendation': "Focus attention on the road ahead"
            })
        
        if driver_state['blink_rate'] < 10:  # Very low blink rate
            alerts.append({
                'type': 'fatigue',
                'severity': 'medium',
                'message': f"Low blink rate detected: {driver_state['blink_rate']:.1f}/min",
                'recommendation': "Take regular breaks to rest your eyes"
            })
        
        return alerts

# Integration with voice assistant
def driver_monitoring_voice_integration(driver_state):
    """Integrate driver monitoring with voice assistant"""
    from llm_handler import speak_text
    
    if driver_state['status'] == 'drowsy':
        speak_text("Driver drowsiness detected. Please consider pulling over safely to rest.")
    elif driver_state['status'] == 'distracted':
        speak_text("Please focus your attention on the road ahead.")
    elif driver_state['blink_rate'] < 8:
        speak_text("You seem tired. Consider taking a break.")

# Example usage
def demo_driver_monitoring():
    """Demonstration of driver monitoring system"""
    dms = DriverMonitoringSystem()
    cap = cv2.VideoCapture(0)  # Use front-facing camera
    
    print("🚗 Driver Monitoring System Demo")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Analyze driver state
        driver_state, annotated_frame = dms.analyze_driver_state(frame)
        
        # Generate alerts
        alerts = dms.generate_driver_alert(driver_state)
        
        # Voice integration (commented out for demo)
        # if alerts:
        #     driver_monitoring_voice_integration(driver_state)
        
        # Display frame
        cv2.imshow('RHINO Driver Monitoring', annotated_frame)
        
        # Print status
        if driver_state['status'] != 'normal':
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Driver Status: {driver_state['status']}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    demo_driver_monitoring()
