import yaml
import time
import logging
import cv2
from vision_core.stream import RTSPStreamReader
from vision_core.detector import VisionDetector
from vision_core.alerts import AlertManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    stream = RTSPStreamReader(config["stream"]["source"], config["stream"]["fps_target"]).start()
    detector = VisionDetector(config)
    alert_mgr = AlertManager(config)

    logging.info("Core Engine started successfully.")

    try:
        while True:
            grabbed, frame = stream.read()
            if not grabbed or frame is None:
                time.sleep(0.01)
                continue

            analysis = detector.process_frame(frame)

            # Lógica de Disparo de Alertas según reglas de negocio
            if analysis["motion_detected"] and analysis["has_human"]:
                alert_mgr.trigger("human_detected", {
                    "people": analysis["persons_count"],
                    "non_people": analysis["non_persons_count"]
                })
            elif analysis["motion_detected"] and not analysis["has_human"]:
                alert_mgr.trigger("non_human_motion_ignored", {
                    "non_people": analysis["non_persons_count"]
                })

            time.sleep(0.05)

    except KeyboardInterrupt:
        logging.info("Stopping Engine...")
    finally:
        stream.stop()

if __name__ == "__main__":
    main()