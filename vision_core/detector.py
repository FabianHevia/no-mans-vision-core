import cv2
import numpy as np
from ultralytics import YOLO

class VisionDetector:
    def __init__(self, config, frame_shape):
        self.cfg = config
        self.model = YOLO(self.cfg["detector"]["model_path"])
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)
        
        height, width = frame_shape[:2]
        self.roi_mgr = ROIManager(self.cfg.get("roi", {}), width, height)

    def detect_motion(self, frame):
        fg_mask = self.bg_subtractor.apply(frame)
        _, thresh = cv2.threshold(fg_mask, 244, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_in_roi = False
        for contour in contours:
            if cv2.contourArea(contour) > self.cfg["motion"]["min_area"]:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    if self.roi_mgr.is_point_inside((cx, cy)):
                        motion_in_roi = True
                        break
        return motion_in_roi

    def process_frame(self, frame):
        motion_present = self.detect_motion(frame)
        
        persons_count = 0
        non_persons_count = 0

        results = self.model(frame, verbose=False, conf=self.cfg["detector"]["confidence_threshold"])[0]
        
        for box in results.boxes:
            cls_id = int(box.cls[0])
            xyxy = box.xyxy[0].cpu().numpy()
            center_x = int((xyxy[0] + xyxy[2]) / 2)
            center_y = int((xyxy[1] + xyxy[3]) / 2)

            if self.roi_mgr.is_point_inside((center_x, center_y)):
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