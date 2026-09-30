"""Application configuration loaded from environment variables."""
import os
from functools import lru_cache
from typing import List, Optional


class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./energy_monitor.db")

    # MQTT broker
    MQTT_HOST: str = os.getenv("MQTT_HOST", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USERNAME: Optional[str] = os.getenv("MQTT_USERNAME") or None
    MQTT_PASSWORD: Optional[str] = os.getenv("MQTT_PASSWORD") or None
    MQTT_READINGS_TOPIC: str = "energy/+/readings"
    MQTT_STATUS_TOPIC: str = "energy/+/status"
    MQTT_CLIENT_ID: str = os.getenv("MQTT_CLIENT_ID", "energy-backend")

    # Alerts
    POWER_THRESHOLD_W: float = float(os.getenv("POWER_THRESHOLD_W", "2000"))

    # Device offline detection
    DEVICE_OFFLINE_AFTER_SECONDS: int = int(os.getenv("DEVICE_OFFLINE_AFTER_SECONDS", "30"))

    # CORS - dashboard origin(s)
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
