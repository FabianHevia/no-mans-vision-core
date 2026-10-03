import time
import logging
import requests

class AlertManager:
    def __init__(self, config):
        self.config = config.get("alerts", {})
        self.cooldown = self.config.get("cooldown_seconds", 10)
        self.last_alert_time = 0

    def trigger(self, event_type: str, details: dict):
        if not self.config.get("enabled", True):
            return

        current_time = time.time()
        if current_time - self.last_alert_time < self.cooldown:
            return

        message = f"🚨 [ALERT - {event_type.upper()}] {details}"
        
        if self.config.get("channels", {}).get("console", True):
            logging.info(message)

        webhook_cfg = self.config.get("channels", {}).get("webhook", {})
        if webhook_cfg.get("enabled") and webhook_cfg.get("url"):
            try:
                requests.post(webhook_cfg["url"], json={"event": event_type, "details": details}, timeout=3)
            except Exception as e:
                logging.error(f"Error enviando Webhook: {e}")

        telegram_cfg = self.config.get("channels", {}).get("telegram", {})
        if telegram_cfg.get("enabled") and telegram_cfg.get("bot_token"):
            try:
                url = f"https://api.telegram.org/bot{telegram_cfg['bot_token']}/sendMessage"
                requests.post(url, json={"chat_id": telegram_cfg["chat_id"], "text": message}, timeout=3)
            except Exception as e:
                logging.error(f"Error enviando Telegram: {e}")

        self.last_alert_time = current_time