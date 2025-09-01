class VehicleTracker:
    def __init__(self):
        self.tracked_vehicles = {}

    def update(self, detections):
        for detection in detections:
            vehicle_id = detection['id']
            if vehicle_id not in self.tracked_vehicles:
                self.tracked_vehicles[vehicle_id] = detection
            else:
                self.tracked_vehicles[vehicle_id].update(detection)

    def get_tracked_vehicles(self):
        return self.tracked_vehicles

    def clear_tracks(self):
        self.tracked_vehicles.clear()