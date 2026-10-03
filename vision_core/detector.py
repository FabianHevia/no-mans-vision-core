import cv2
import numpy as np
from ultralytics import YOLO

class VisionDetector:
    def __init__(self, config):
        self.cfg = config
        self.model = YOLO(self.cfg["detector"]["model_path"])
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

    def detect_motion(self, frame):
        fg_mask = self.bg_subtractor.apply(frame)
        _, thresh = cv2.threshold(fg_mask, 244, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > self.cfg["motion"]["min_area"]:
                motion_detected = True
                break
        return motion_detected

    def process_frame(self, frame):
        motion_present = self.detect_motion(frame)
        
        persons_count = 0
        non_persons_count = 0

        results = self.model(frame, verbose=False, conf=self.cfg["detector"]["confidence_threshold"])[0]
        
        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id in self.cfg["detector"]["target_classes"]["human"]:
                persons_count += 1
            elif cls_id in self.cfg["detector"]["target_classes"]["non_human"]:
                non_persons_count += 1

        return {
            "motion_detected": motion_present,
            "persons_count": persons_count,
            "non_persons_count": non_persons_count,
            "has_human": persons_count > 0
        }