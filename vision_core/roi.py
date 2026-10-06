import cv2
import numpy as np

class ROIManager:
    def __init__(self, roi_config, frame_width, frame_height):
        self.enabled = roi_config.get("enabled", False)
        self.width = frame_width
        self.height = frame_height
        self.polygon = []

        if self.enabled and "polygon" in roi_config:

            raw_poly = roi_config["polygon"]
            self.polygon = np.array([
                [int(p[0] * self.width), int(p[1] * self.height)]
                for p in raw_poly
            ], np.int32)

    def is_point_inside(self, point):
        if not self.enabled or len(self.polygon) == 0:
            return True
        
        result = cv2.pointPolygonTest(self.polygon, (float(point[0]), float(point[1])), False)
        return result >= 0

    def draw_roi(self, frame):

        # Draw the ROI polygon on the frame for debugging or visualization.
        
        if self.enabled and len(self.polygon) > 0:
            cv2.polylines(frame, [self.polygon], isClosed=True, color=(0, 255, 0), thickness=2)
        return frame