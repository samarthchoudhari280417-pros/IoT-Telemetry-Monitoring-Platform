"""Device endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Device
from app.schemas import DeviceOut
from app.services import energy_service

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


@router.get("", response_model=List[DeviceOut])
def list_devices(db: Session = Depends(get_db)):
    energy_service.refresh_stale_devices(db)
    return db.query(Device).order_by(Device.device_id).all()


@router.get("/{device_id}", response_model=DeviceOut)
def get_device(device_id: str, db: Session = Depends(get_db)):
    energy_service.refresh_stale_devices(db)
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
