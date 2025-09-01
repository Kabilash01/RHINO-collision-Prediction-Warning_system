class CollisionDetector:
    def __init__(self, threshold=0.3):
        self.threshold = threshold

    def detect_collision(self, box1, box2):
        xA = max(box1[0], box2[0])
        yA = max(box1[1], box2[1])
        xB = min(box1[2], box2[2])
        yB = min(box1[3], box2[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (box1[2] - box1[0]) * (box1[3] - box1[1])
        boxBArea = (box2[2] - box2[0]) * (box2[3] - box2[1])

        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-3)
        return iou > self.threshold

    def check_collisions(self, vehicle_boxes):
        collisions = []
        for i in range(len(vehicle_boxes)):
            for j in range(i + 1, len(vehicle_boxes)):
                if self.detect_collision(vehicle_boxes[i], vehicle_boxes[j]):
                    collisions.append((i, j))
        return collisions