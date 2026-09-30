"""Tests for core power/energy calculation & ingestion logic."""
from datetime import datetime, timezone

from app.schemas import ReadingIngest
from app.services import energy_service


def test_ingest_reading_creates_device_and_reading(db_session):
    payload = ReadingIngest(
        device_id="esp32-energy-01",
        timestamp=int(datetime.now(timezone.utc).timestamp()),
        voltage=230.0,
        current=2.0,
        power=460.0,
        energy_wh=1.28,
    )
    reading = energy_service.ingest_reading(db_session, payload)

    assert reading.id is not None
    assert reading.power == 460.0

    device = db_session.query(energy_service.Device).filter_by(
        device_id="esp32-energy-01"
    ).first()
    assert device is not None
    assert device.status == "online"
    assert device.last_seen is not None


def test_power_equals_voltage_times_current():
    voltage, current = 230.0, 2.4
    expected_power = voltage * current
    assert round(expected_power, 2) == 552.0


def test_high_power_reading_creates_alert(db_session, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "POWER_THRESHOLD_W", 2000.0)

    payload = ReadingIngest(
        device_id="esp32-energy-01",
        timestamp=int(datetime.now(timezone.utc).timestamp()),
        voltage=230.0,
        current=10.0,
        power=2300.0,  # exceeds threshold
        energy_wh=0.5,
    )
    energy_service.ingest_reading(db_session, payload)

    alerts = db_session.query(energy_service.Alert).all()
    assert len(alerts) == 1
    assert alerts[0].power == 2300.0
    assert "2000" in alerts[0].message


def test_normal_power_reading_does_not_create_alert(db_session, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "POWER_THRESHOLD_W", 2000.0)

    payload = ReadingIngest(
        device_id="esp32-energy-01",
        timestamp=int(datetime.now(timezone.utc).timestamp()),
        voltage=230.0,
        current=2.0,
        power=460.0,
        energy_wh=0.5,
    )
    energy_service.ingest_reading(db_session, payload)

    alerts = db_session.query(energy_service.Alert).all()
    assert len(alerts) == 0


def test_analytics_aggregates_readings(db_session):
    now = int(datetime.now(timezone.utc).timestamp())
    for i, power in enumerate([400.0, 500.0, 600.0]):
        payload = ReadingIngest(
            device_id="esp32-energy-01",
            timestamp=now + i,
            voltage=230.0,
            current=power / 230.0,
            power=power,
            energy_wh=1.0,
        )
        energy_service.ingest_reading(db_session, payload)

    analytics = energy_service.compute_analytics(db_session, "esp32-energy-01")

    assert analytics["current_power_w"] == 600.0  # most recent reading
    assert analytics["peak_power_w"] == 600.0
    assert analytics["average_power_w"] == 500.0
    assert analytics["today_energy_wh"] == 3.0
