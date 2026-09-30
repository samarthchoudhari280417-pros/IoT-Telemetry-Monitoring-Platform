"""Tests for REST API endpoints."""
from datetime import datetime, timezone


def _post_reading(client, device_id="esp32-energy-01", power=460.0):
    """Helper: simulate an MQTT-ingested reading by calling the service directly
    via the same DB session the test client uses would require app internals,
    so instead we exercise ingestion through the service layer using the
    client's overridden session."""
    from app.database import get_db
    from app.main import app
    from app.schemas import ReadingIngest
    from app.services import energy_service

    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)
    payload = ReadingIngest(
        device_id=device_id,
        timestamp=int(datetime.now(timezone.utc).timestamp()),
        voltage=230.0,
        current=power / 230.0,
        power=power,
        energy_wh=1.0,
    )
    return energy_service.ingest_reading(db, payload)


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_devices_empty(client):
    resp = client.get("/api/v1/devices")
    assert resp.status_code == 200
    assert resp.json() == []


def test_device_appears_after_reading(client):
    _post_reading(client)
    resp = client.get("/api/v1/devices")
    assert resp.status_code == 200
    devices = resp.json()
    assert len(devices) == 1
    assert devices[0]["device_id"] == "esp32-energy-01"
    assert devices[0]["status"] == "online"


def test_get_single_device_not_found(client):
    resp = client.get("/api/v1/devices/does-not-exist")
    assert resp.status_code == 404


def test_readings_latest(client):
    _post_reading(client, power=531.76)
    resp = client.get("/api/v1/readings/latest?device_id=esp32-energy-01")
    assert resp.status_code == 200
    body = resp.json()
    assert body["power"] == 531.76
    assert body["device_status"] == "online"


def test_readings_latest_404_when_empty(client):
    resp = client.get("/api/v1/readings/latest")
    assert resp.status_code == 404


def test_analytics_endpoint(client):
    _post_reading(client, power=400.0)
    _post_reading(client, power=800.0)
    resp = client.get("/api/v1/analytics?device_id=esp32-energy-01")
    assert resp.status_code == 200
    body = resp.json()
    assert body["peak_power_w"] == 800.0
    assert body["current_power_w"] == 800.0


def test_alert_created_and_listed(client, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "POWER_THRESHOLD_W", 2000.0)

    _post_reading(client, power=2500.0)
    resp = client.get("/api/v1/alerts")
    assert resp.status_code == 200
    alerts = resp.json()
    assert len(alerts) == 1
    assert alerts[0]["power"] == 2500.0


def test_readings_list_respects_limit(client):
    for i in range(5):
        _post_reading(client, power=100.0 + i)
    resp = client.get("/api/v1/readings?limit=3")
    assert resp.status_code == 200
    assert len(resp.json()) == 3
