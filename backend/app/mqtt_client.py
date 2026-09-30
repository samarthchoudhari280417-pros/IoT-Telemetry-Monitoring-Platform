"""MQTT client: subscribes to device readings/status topics and persists them."""
import json
import logging

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from app.config import settings
from app.database import SessionLocal
from app.schemas import ReadingIngest, StatusIngest
from app.services import energy_service

logger = logging.getLogger("mqtt_client")

_client: mqtt.Client | None = None


def _on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Connected to MQTT broker %s:%s", settings.MQTT_HOST, settings.MQTT_PORT)
        client.subscribe(settings.MQTT_READINGS_TOPIC)
        client.subscribe(settings.MQTT_STATUS_TOPIC)
    else:
        logger.error("MQTT connection failed with code %s", rc)


def _on_disconnect(client, userdata, rc, properties=None):
    logger.warning("Disconnected from MQTT broker (rc=%s). Client will auto-reconnect.", rc)


def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("Received non-JSON payload on %s, discarding.", msg.topic)
        return

    db = SessionLocal()
    try:
        if msg.topic.endswith("/readings"):
            reading = ReadingIngest(**payload)
            energy_service.ingest_reading(db, reading)
            logger.info(
                "Stored reading device=%s power=%.2fW", reading.device_id, reading.power
            )
        elif msg.topic.endswith("/status"):
            status = StatusIngest(**payload)
            energy_service.set_device_status(db, status.device_id, status.status)
            logger.info("Device %s status -> %s", status.device_id, status.status)
    except ValidationError as e:
        logger.warning("Invalid payload on %s: %s", msg.topic, e)
    except Exception:
        logger.exception("Error processing MQTT message on %s", msg.topic)
    finally:
        db.close()


def start_mqtt_client() -> mqtt.Client:
    """Create, connect, and start the MQTT client loop in a background thread."""
    global _client
    client = mqtt.Client(
        client_id=settings.MQTT_CLIENT_ID,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )
    if settings.MQTT_USERNAME:
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect
    client.on_message = _on_message

    client.reconnect_delay_set(min_delay=1, max_delay=30)

    try:
        client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
        client.loop_start()
    except Exception:
        logger.exception(
            "Could not connect to MQTT broker at startup; will keep retrying in background."
        )
        client.loop_start()  # paho will keep retrying connect on its own loop

    _client = client
    return client


def stop_mqtt_client() -> None:
    global _client
    if _client is not None:
        _client.loop_stop()
        _client.disconnect()
        _client = None
