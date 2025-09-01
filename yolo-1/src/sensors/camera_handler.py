import cv2

class CameraHandler:
    def __init__(self, video_source=0):
        self.video_source = video_source
        self.capture = cv2.VideoCapture(self.video_source)

    def is_opened(self):
        return self.capture.isOpened()

    def read_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            return None
        return frame

    def release(self):
        if self.capture.isOpened():
            self.capture.release()