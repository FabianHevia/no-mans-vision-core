import time
import logging

class BusinessStateManager:
    def __init__(self, config):
        self.mode = config.get("mode", "perimeter")
        self.rules = config.get("rules", {})
        
        self.occupancy_start_empty = None
        self.sanitization_alert_sent = False
        
        self.last_perimeter_alert = 0

    def process(self, has_human: bool, has_non_human_motion: bool, alert_manager):
        current_time = time.time()

        if self.mode == "perimeter":
            self._handle_perimeter_mode(has_human, has_non_human_motion, current_time, alert_manager)
        elif self.mode == "occupancy":
            self._handle_occupancy_mode(has_human, current_time, alert_manager)

    def _handle_perimeter_mode(self, has_human, has_non_human_motion, current_time, alert_manager):
        cooldown = self.rules.get("perimeter", {}).get("cooldown_seconds", 15)

        if has_human:
            if current_time - self.last_perimeter_alert >= cooldown:
                alert_manager.trigger("perimeter_intrusion_human", {
                    "level": "CRITICAL",
                    "message": "Intrusión humana confirmada en perímetro."
                })
                self.last_perimeter_alert = current_time
        elif has_non_human_motion:
            logging.debug("Movimiento no humano detectado en perímetro (Filtrado).")

    def _handle_occupancy_mode(self, has_human, current_time, alert_manager):
        required_empty_sec = self.rules.get("occupancy", {}).get("required_empty_minutes", 3) * 60

        if has_human:
            self.occupancy_start_empty = None
            self.sanitization_alert_sent = False
        else:
            if self.occupancy_start_empty is None:
                self.occupancy_start_empty = current_time

            elapsed_empty = current_time - self.occupancy_start_empty

            if elapsed_empty >= required_empty_sec and not self.sanitization_alert_sent:
                alert_manager.trigger("zone_ready_for_cleaning", {
                    "level": "INFO",
                    "empty_duration_minutes": round(elapsed_empty / 60, 1),
                    "message": "Área desocupada. Lista para protocolo de sanitización."
                })
                self.sanitization_alert_sent = True