"""FastAPI application entrypoint."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import devices, readings
from app.config import settings
from app.database import init_db
from app.mqtt_client import start_mqtt_client, stop_mqtt_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_mqtt_client()
    yield
    stop_mqtt_client()


app = FastAPI(
    title="Smart Energy Monitor API",
    description="Backend for the ESP32-based smart energy monitoring system.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router)
app.include_router(readings.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
