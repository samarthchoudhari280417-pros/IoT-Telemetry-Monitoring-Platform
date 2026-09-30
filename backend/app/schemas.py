"""Pydantic request/response schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------- Incoming MQTT / ingestion payload ----------

class ReadingIngest(BaseModel):
    """Shape published by ESP32 firmware / simulator over MQTT."""
    device_id: str
    timestamp: int = Field(..., description="Unix epoch seconds")
    voltage: float = Field(..., ge=0, le=400)
    current: float = Field(..., ge=0, le=200)
    power: float = Field(..., ge=0)
    energy_wh: float = Field(..., ge=0)


class StatusIngest(BaseModel):
    device_id: str
    status: str  # "online" | "offline"


# ---------- Device ----------

class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    name: Optional[str] = None
    location: Optional[str] = None
    last_seen: Optional[datetime] = None
    status: str


# ---------- Readings ----------

class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    timestamp: datetime
    voltage: float
    current: float
    power: float
    energy_wh: float


class LatestReadingOut(ReadingOut):
    device_status: str


# ---------- Analytics ----------

class DailyEnergyPoint(BaseModel):
    date: str
    energy_wh: float


class MonthlyEnergyPoint(BaseModel):
    month: str
    energy_wh: float


class AnalyticsOut(BaseModel):
    device_id: str
    current_power_w: float
    today_energy_wh: float
    month_energy_wh: float
    average_power_w: float
    peak_power_w: float


# ---------- Alerts ----------

class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    timestamp: datetime
    power: float
    threshold: float
    message: str
