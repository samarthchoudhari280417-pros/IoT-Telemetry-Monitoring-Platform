"""Reading / analytics / alert endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, EnergyReading
from app.schemas import AlertOut, AnalyticsOut, LatestReadingOut, ReadingOut
from app.services import energy_service

router = APIRouter(prefix="/api/v1", tags=["readings"])


@router.get("/readings", response_model=List[ReadingOut])
def list_readings(
    device_id: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
):
    q = db.query(EnergyReading)
    if device_id:
        q = q.filter(EnergyReading.device_id == device_id)
    return q.order_by(EnergyReading.timestamp.desc()).limit(limit).all()


@router.get("/readings/latest", response_model=LatestReadingOut)
def get_latest_reading(device_id: Optional[str] = None, db: Session = Depends(get_db)):
    reading = energy_service.latest_reading(db, device_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="No readings found")
    device_status = reading.device.status if reading.device else "offline"
    return LatestReadingOut(
        id=reading.id,
        device_id=reading.device_id,
        timestamp=reading.timestamp,
        voltage=reading.voltage,
        current=reading.current,
        power=reading.power,
        energy_wh=reading.energy_wh,
        device_status=device_status,
    )


@router.get("/readings/daily")
def get_daily_readings(device_id: str, days: int = 30, db: Session = Depends(get_db)):
    return energy_service.daily_energy(db, device_id, days)


@router.get("/readings/monthly")
def get_monthly_readings(device_id: str, months: int = 12, db: Session = Depends(get_db)):
    return energy_service.monthly_energy(db, device_id, months)


@router.get("/analytics", response_model=AnalyticsOut)
def get_analytics(device_id: str, db: Session = Depends(get_db)):
    return energy_service.compute_analytics(db, device_id)


@router.get("/alerts", response_model=List[AlertOut])
def list_alerts(
    device_id: Optional[str] = None,
    limit: int = Query(default=50, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Alert)
    if device_id:
        q = q.filter(Alert.device_id == device_id)
    return q.order_by(Alert.timestamp.desc()).limit(limit).all()
