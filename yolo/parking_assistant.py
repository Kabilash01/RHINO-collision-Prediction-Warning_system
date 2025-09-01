# RHINO-CAR Intelligent Parking Assistant
"""
AI-powered parking detection, guidance, and smart parking management
"""
import cv2
import numpy as np
import torch
import torch.nn as nn
import json
import time
from datetime import datetime
from ultralytics import YOLO
import requests

class IntelligentParkingAssistant:
    """Advanced parking detection and guidance system"""
    
    def __init__(self):
        # Initialize YOLO for object detection
        self.yolo_model = YOLO('yolov8n.pt')
        
        # Parking detection parameters
        self.parking_spaces = []
        self.occupied_spaces = []
        self.available_spaces = []
        
        # Distance estimation
        self.focal_length = 800  # Camera focal length (pixels)
        self.real_car_width = 1.8  # Average car width in meters
        
        # Parking guidance
        self.guidance_active = False
        self.target_space = None
        self.parking_history = []
        
        # Smart parking features
        self.parking_database = {}
        self.favorite_locations = []
        
    def detect_parking_spaces(self, frame):
        """Detect available parking spaces using computer vision"""
        # Run YOLO detection
        results = self.yolo_model(frame)
        
        # Extract vehicles
        vehicles = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = self.yolo_model.names[class_id]
                    
                    # Check if it's a vehicle
                    if class_name in ['car', 'truck', 'bus', 'motorcycle']:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0])
                        
                        vehicles.append({
                            'bbox': [x1, y1, x2, y2],
                            'confidence': confidence,
                            'type': class_name,
                            'distance': self.estimate_distance(x1, y1, x2, y2)
                        })
        
        # Analyze parking spaces
        parking_analysis = self.analyze_parking_layout(frame, vehicles)
        
        return parking_analysis
    
    def estimate_distance(self, x1, y1, x2, y2):
        """Estimate distance to detected vehicle"""
        vehicle_width_pixels = x2 - x1
        if vehicle_width_pixels > 0:
            distance = (self.real_car_width * self.focal_length) / vehicle_width_pixels
            return max(1.0, min(50.0, distance))  # Clamp between 1-50 meters
        return 10.0  # Default distance
    
    def analyze_parking_layout(self, frame, vehicles):
        """Analyze parking layout and identify available spaces"""
        h, w = frame.shape[:2]
        
        # Simple grid-based parking space detection
        grid_size = 80  # pixels
        spaces = []
        
        for y in range(0, h - grid_size, grid_size):
            for x in range(0, w - grid_size, grid_size):
                space_region = [x, y, x + grid_size, y + grid_size]
                
                # Check if space is occupied
                occupied = False
                for vehicle in vehicles:
                    if self.rectangles_overlap(space_region, vehicle['bbox']):
                        occupied = True
                        break
                
                # Analyze space quality
                space_quality = self.assess_space_quality(frame, space_region, vehicles)
                
                spaces.append({
                    'region': space_region,
                    'occupied': occupied,
                    'quality': space_quality,
                    'distance_from_vehicles': self.min_distance_to_vehicles(space_region, vehicles),
                    'accessibility': self.assess_accessibility(space_region, vehicles)
                })
        
        # Filter and rank available spaces
        available_spaces = [s for s in spaces if not s['occupied'] and s['quality'] > 0.5]
        available_spaces.sort(key=lambda x: x['quality'], reverse=True)
        
        return {
            'total_spaces': len(spaces),
            'available_spaces': available_spaces[:5],  # Top 5 spaces
            'occupied_count': len([s for s in spaces if s['occupied']]),
            'vehicles_detected': vehicles,
            'parking_difficulty': self.calculate_parking_difficulty(spaces, vehicles)
        }
    
    def rectangles_overlap(self, rect1, rect2):
        """Check if two rectangles overlap"""
        x1, y1, x2, y2 = rect1
        a1, b1, a2, b2 = rect2
        return not (x2 < a1 or a2 < x1 or y2 < b1 or b2 < y1)
    
    def assess_space_quality(self, frame, space_region, vehicles):
        """Assess the quality of a parking space"""
        x1, y1, x2, y2 = space_region
        
        # Extract space region
        space_roi = frame[y1:y2, x1:x2]
        
        # Basic quality metrics
        quality_score = 0.7  # Base score
        
        # Check for obstacles or markings
        gray_roi = cv2.cvtColor(space_roi, cv2.COLOR_BGR2GRAY)
        
        # Edge detection to find parking lines
        edges = cv2.Canny(gray_roi, 50, 150)
        line_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        if line_density > 0.1:  # Good parking line markings
            quality_score += 0.2
        
        # Check proximity to other vehicles (prefer some distance)
        min_distance = self.min_distance_to_vehicles(space_region, vehicles)
        if min_distance > 3.0:
            quality_score += 0.1
        elif min_distance < 1.5:
            quality_score -= 0.3
        
        return max(0.0, min(1.0, quality_score))
    
    def min_distance_to_vehicles(self, space_region, vehicles):
        """Calculate minimum distance from space to nearest vehicle"""
        if not vehicles:
            return 10.0
        
        space_center_x = (space_region[0] + space_region[2]) / 2
        space_center_y = (space_region[1] + space_region[3]) / 2
        
        min_dist = float('inf')
        for vehicle in vehicles:
            veh_center_x = (vehicle['bbox'][0] + vehicle['bbox'][2]) / 2
            veh_center_y = (vehicle['bbox'][1] + vehicle['bbox'][3]) / 2
            
            dist = np.sqrt((space_center_x - veh_center_x)**2 + (space_center_y - veh_center_y)**2)
            min_dist = min(min_dist, dist)
        
        # Convert pixel distance to rough meter estimate
        return min_dist / 100.0
    
    def assess_accessibility(self, space_region, vehicles):
        """Assess how accessible a parking space is"""
        # Simple accessibility check based on surrounding vehicles
        x1, y1, x2, y2 = space_region
        expanded_region = [x1-50, y1-50, x2+50, y2+50]
        
        blocking_vehicles = 0
        for vehicle in vehicles:
            if self.rectangles_overlap(expanded_region, vehicle['bbox']):
                blocking_vehicles += 1
        
        if blocking_vehicles == 0:
            return 1.0  # Excellent accessibility
        elif blocking_vehicles <= 2:
            return 0.7  # Good accessibility
        else:
            return 0.3  # Poor accessibility
    
    def calculate_parking_difficulty(self, spaces, vehicles):
        """Calculate overall parking difficulty"""
        total_spaces = len(spaces)
        available_spaces = len([s for s in spaces if not s['occupied']])
        
        if total_spaces == 0:
            return 1.0  # Maximum difficulty
        
        availability_ratio = available_spaces / total_spaces
        vehicle_density = len(vehicles) / max(1, total_spaces)
        
        difficulty = 1.0 - (availability_ratio * 0.7) + (vehicle_density * 0.3)
        return max(0.0, min(1.0, difficulty))
    
    def provide_parking_guidance(self, frame, parking_analysis, target_preference='closest'):
        """Provide visual and voice guidance for parking"""
        if not parking_analysis['available_spaces']:
            return frame, "No parking spaces available"
        
        # Select best space based on preference
        if target_preference == 'closest':
            best_space = min(parking_analysis['available_spaces'], 
                           key=lambda x: x['distance_from_vehicles'])
        elif target_preference == 'easiest':
            best_space = max(parking_analysis['available_spaces'], 
                           key=lambda x: x['accessibility'])
        else:  # best quality
            best_space = max(parking_analysis['available_spaces'], 
                           key=lambda x: x['quality'])
        
        # Draw guidance on frame
        annotated_frame = self.draw_parking_guidance(frame, best_space, parking_analysis)
        
        # Generate guidance message
        guidance_msg = self.generate_guidance_message(best_space, parking_analysis)
        
        return annotated_frame, guidance_msg
    
    def draw_parking_guidance(self, frame, best_space, parking_analysis):
        """Draw visual parking guidance on frame"""
        annotated_frame = frame.copy()
        
        # Draw all available spaces in green
        for space in parking_analysis['available_spaces']:
            x1, y1, x2, y2 = [int(coord) for coord in space['region']]
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add quality score
            quality_text = f"{space['quality']:.1f}"
            cv2.putText(annotated_frame, quality_text, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Highlight best space
        x1, y1, x2, y2 = [int(coord) for coord in best_space['region']]
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 255), 4)
        cv2.putText(annotated_frame, "BEST SPACE", (x1, y1-30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Draw occupied spaces in red
        for vehicle in parking_analysis['vehicles_detected']:
            x1, y1, x2, y2 = [int(coord) for coord in vehicle['bbox']]
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(annotated_frame, f"{vehicle['type']}", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Add parking statistics
        stats_text = [
            f"Available: {len(parking_analysis['available_spaces'])}",
            f"Occupied: {parking_analysis['occupied_count']}",
            f"Difficulty: {parking_analysis['parking_difficulty']:.1f}"
        ]
        
        for i, text in enumerate(stats_text):
            cv2.putText(annotated_frame, text, (10, 30 + i*25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return annotated_frame
    
    def generate_guidance_message(self, best_space, parking_analysis):
        """Generate voice guidance message"""
        quality = best_space['quality']
        accessibility = best_space['accessibility']
        difficulty = parking_analysis['parking_difficulty']
        
        if difficulty > 0.8:
            difficulty_desc = "very challenging"
        elif difficulty > 0.6:
            difficulty_desc = "moderately difficult"
        elif difficulty > 0.4:
            difficulty_desc = "moderate"
        else:
            difficulty_desc = "easy"
        
        if quality > 0.8 and accessibility > 0.8:
            return f"Excellent parking space identified. {difficulty_desc} parking conditions."
        elif quality > 0.6:
            return f"Good parking space available. {difficulty_desc} parking conditions."
        else:
            return f"Parking space found but requires careful maneuvering. {difficulty_desc} conditions."
    
    def smart_parking_search(self, location, radius_km=1.0):
        """Search for parking using external APIs and local knowledge"""
        # This would integrate with parking APIs like ParkWhiz, SpotHero, etc.
        mock_parking_data = {
            'nearby_lots': [
                {
                    'name': 'City Center Garage',
                    'distance_km': 0.3,
                    'hourly_rate': 5.0,
                    'availability': 'High',
                    'spaces_available': 45,
                    'max_height': '2.1m',
                    'payment_methods': ['Credit Card', 'Mobile Pay'],
                    'security': 'Camera Monitored'
                },
                {
                    'name': 'Street Parking Zone A',
                    'distance_km': 0.1,
                    'hourly_rate': 2.0,
                    'availability': 'Medium',
                    'spaces_available': 8,
                    'time_limit': '2 hours',
                    'payment_methods': ['Meter', 'Mobile App']
                }
            ],
            'street_parking': {
                'estimated_spots': 12,
                'difficulty': 'Medium',
                'cost': 'Free after 6PM'
            }
        }
        
        return mock_parking_data
    
    def voice_parking_commands(self, command, current_location=None):
        """Handle voice commands for parking assistance"""
        command_lower = command.lower()
        
        if 'find parking' in command_lower or 'parking nearby' in command_lower:
            if current_location:
                parking_data = self.smart_parking_search(current_location)
                if parking_data['nearby_lots']:
                    best_lot = parking_data['nearby_lots'][0]
                    return f"Best parking: {best_lot['name']}, {best_lot['distance_km']} km away, ${best_lot['hourly_rate']}/hour, {best_lot['availability'].lower()} availability."
                else:
                    return "No parking information available for current location."
            else:
                return "Location required for parking search. Please provide destination."
        
        elif 'parking guidance' in command_lower or 'help me park' in command_lower:
            self.guidance_active = True
            return "Parking guidance activated. I'll help you find and navigate to the best available space."
        
        elif 'parking cost' in command_lower or 'parking price' in command_lower:
            # Mock pricing information
            return "Typical parking: Street parking $2-4/hour, Garage parking $5-8/hour, Airport parking $15-25/day."
        
        elif 'stop parking' in command_lower:
            self.guidance_active = False
            return "Parking assistance stopped."
        
        else:
            return "Parking commands: find parking, parking guidance, parking cost, stop parking assistance."
    
    def demo_parking_assistant(self):
        """Demo function for parking assistant"""
        cap = cv2.VideoCapture(0)
        
        print("🅿️ RHINO Intelligent Parking Assistant Demo")
        print("Press 'g' to toggle guidance, 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect parking spaces
            parking_analysis = self.detect_parking_spaces(frame)
            
            # Provide guidance if active
            if self.guidance_active and parking_analysis['available_spaces']:
                annotated_frame, guidance_msg = self.provide_parking_guidance(frame, parking_analysis)
                print(f"Guidance: {guidance_msg}")
            else:
                annotated_frame = self.draw_parking_guidance(frame, 
                    parking_analysis['available_spaces'][0] if parking_analysis['available_spaces'] else None, 
                    parking_analysis)
            
            cv2.imshow('RHINO Parking Assistant', annotated_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('g'):
                self.guidance_active = not self.guidance_active
                print(f"Guidance: {'ON' if self.guidance_active else 'OFF'}")
        
        cap.release()
        cv2.destroyAllWindows()

# Integration with main RHINO system
def integrate_parking_assistant():
    """Integration function for parking assistant"""
    return IntelligentParkingAssistant()

if __name__ == "__main__":
    assistant = IntelligentParkingAssistant()
    assistant.demo_parking_assistant()
