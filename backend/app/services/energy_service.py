"""Core business logic: ingesting readings, computing analytics, raising alerts."""
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Alert, Device, EnergyReading
from app.schemas import ReadingIngest


def _get_or_create_device(db: Session, device_id: str) -> Device:
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if device is None:
        device = Device(device_id=device_id, status="offline")
        db.add(device)
        db.flush()
    return device


def ingest_reading(db: Session, payload: ReadingIngest) -> EnergyReading:
    """Validate + persist a reading, update device status, and raise alerts if needed."""
    device = _get_or_create_device(db, payload.device_id)

    ts = datetime.fromtimestamp(payload.timestamp, tz=timezone.utc)

    reading = EnergyReading(
        device_id=payload.device_id,
        timestamp=ts,
        voltage=payload.voltage,
        current=payload.current,
        power=payload.power,
        energy_wh=payload.energy_wh,
    )
    db.add(reading)

    device.last_seen = ts
    device.status = "online"

    threshold = settings.POWER_THRESHOLD_W
    if payload.power > threshold:
        db.add(
            Alert(
                device_id=payload.device_id,
                timestamp=ts,
                power=payload.power,
                threshold=threshold,
                message=f"Power consumption exceeded {threshold:.0f} W.",
            )
        )

    db.commit()
    db.refresh(reading)
    return reading


def set_device_status(db: Session, device_id: str, status: str) -> Device:
    device = _get_or_create_device(db, device_id)
    device.status = status
    if status == "online":
        device.last_seen = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    return device


def refresh_stale_devices(db: Session) -> None:
    """Mark devices offline if no reading seen within DEVICE_OFFLINE_AFTER_SECONDS."""
    cutoff = datetime.now(timezone.utc) - timedelta(
        seconds=settings.DEVICE_OFFLINE_AFTER_SECONDS
    )
    stale = (
        db.query(Device)
        .filter(Device.status == "online")
        .filter((Device.last_seen == None) | (Device.last_seen < cutoff))  # noqa: E711
        .all()
    )
    for device in stale:
        device.status = "offline"
    if stale:
        db.commit()


def latest_reading(db: Session, device_id: Optional[str] = None) -> Optional[EnergyReading]:
    q = db.query(EnergyReading)
    if device_id:
        q = q.filter(EnergyReading.device_id == device_id)
    # Order by id as a tie-breaker in case two readings share the same
    # (second-resolution) timestamp.
    return q.order_by(EnergyReading.timestamp.desc(), EnergyReading.id.desc()).first()


def compute_analytics(db: Session, device_id: str):
    """Compute current power, today's energy, this month's energy, avg/peak power."""
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    latest = latest_reading(db, device_id)
    current_power = latest.power if latest else 0.0

    today_energy = (
        db.query(func.coalesce(func.sum(EnergyReading.energy_wh), 0.0))
        .filter(EnergyReading.device_id == device_id)
        .filter(EnergyReading.timestamp >= start_of_day)
        .scalar()
    ) or 0.0

    month_energy = (
        db.query(func.coalesce(func.sum(EnergyReading.energy_wh), 0.0))
        .filter(EnergyReading.device_id == device_id)
        .filter(EnergyReading.timestamp >= start_of_month)
        .scalar()
    ) or 0.0

    avg_power = (
        db.query(func.avg(EnergyReading.power))
        .filter(EnergyReading.device_id == device_id)
        .scalar()
    ) or 0.0

    peak_power = (
        db.query(func.max(EnergyReading.power))
        .filter(EnergyReading.device_id == device_id)
        .scalar()
    ) or 0.0

    return {
        "device_id": device_id,
        "current_power_w": round(current_power, 2),
        "today_energy_wh": round(today_energy, 2),
        "month_energy_wh": round(month_energy, 2),
        "average_power_w": round(avg_power, 2),
        "peak_power_w": round(peak_power, 2),
    }


def daily_energy(db: Session, device_id: str, days: int = 30):
    """Energy summed per calendar day, most recent `days` days."""
    rows = (
        db.query(
            func.date(EnergyReading.timestamp).label("day"),
            func.sum(EnergyReading.energy_wh).label("energy_wh"),
        )
        .filter(EnergyReading.device_id == device_id)
        .group_by("day")
        .order_by("day")
        .all()
    )
    return [{"date": str(r.day), "energy_wh": round(r.energy_wh or 0.0, 2)} for r in rows][-days:]


def monthly_energy(db: Session, device_id: str, months: int = 12):
    """Energy summed per calendar month, most recent `months` months."""
    rows = (
        db.query(
            func.strftime("%Y-%m", EnergyReading.timestamp).label("month")
            if _is_sqlite(db)
            else func.to_char(EnergyReading.timestamp, "YYYY-MM").label("month"),
            func.sum(EnergyReading.energy_wh).label("energy_wh"),
        )
        .filter(EnergyReading.device_id == device_id)
        .group_by("month")
        .order_by("month")
        .all()
    )
    return [{"month": r.month, "energy_wh": round(r.energy_wh or 0.0, 2)} for r in rows][-months:]


def _is_sqlite(db: Session) -> bool:
    return db.get_bind().dialect.name == "sqlite"
