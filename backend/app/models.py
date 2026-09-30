"""SQLAlchemy ORM models: Device, EnergyReading, Alert."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="offline", nullable=False)  # "online" | "offline"
    created_at = Column(DateTime(timezone=True), default=utcnow)

    readings = relationship(
        "EnergyReading", back_populates="device", cascade="all, delete-orphan"
    )


class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(
        String, ForeignKey("devices.device_id"), index=True, nullable=False
    )
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    voltage = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    power = Column(Float, nullable=False)      # Watts
    energy_wh = Column(Float, nullable=False)  # cumulative session energy, Wh

    device = relationship("Device", back_populates="readings")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utcnow, index=True)
    power = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    message = Column(Text, nullable=False)
