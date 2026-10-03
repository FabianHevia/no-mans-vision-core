import cv2
import threading
import time

class RTSPStreamReader:
    def __init__(self, source, fps_target=15):
        self.source = source
        self.cap = cv2.VideoCapture(self.source)
        self.grabbed, self.frame = self.cap.read()
        self.running = False
        self.thread = None
        self.delay = 1.0 / fps_target

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        return self

    def _update(self):
        while self.running:
            if not self.cap.isOpened():
                time.sleep(1)
                self.cap = cv2.VideoCapture(self.source)
                continue

            grabbed, frame = self.cap.read()
            if grabbed:
                self.grabbed, self.frame = grabbed, frame
            time.sleep(self.delay)

    def read(self):
        return self.grabbed, self.frame

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.cap.release()