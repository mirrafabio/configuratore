from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class VehicleStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    moving = "moving"
    idle = "idle"


class AlertType(str, enum.Enum):
    speeding = "speeding"
    geofence_exit = "geofence_exit"
    geofence_enter = "geofence_enter"
    ignition_on = "ignition_on"
    ignition_off = "ignition_off"
    low_battery = "low_battery"
    harsh_braking = "harsh_braking"
    harsh_acceleration = "harsh_acceleration"
    device_offline = "device_offline"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    plate: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    model: Mapped[str] = mapped_column(String(100), nullable=True)
    driver: Mapped[str] = mapped_column(String(100), nullable=True)
    imei: Mapped[str] = mapped_column(String(20), nullable=True, unique=True, index=True)
    status: Mapped[VehicleStatus] = mapped_column(
        Enum(VehicleStatus), default=VehicleStatus.offline
    )
    last_seen: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    positions: Mapped[list["Position"]] = relationship(back_populates="vehicle", lazy="select")
    trips: Mapped[list["Trip"]] = relationship(back_populates="vehicle", lazy="select")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="vehicle", lazy="select")


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude: Mapped[float] = mapped_column(Float, default=0.0)
    angle: Mapped[int] = mapped_column(Integer, default=0)
    speed: Mapped[int] = mapped_column(Integer, default=0)
    satellites: Mapped[int] = mapped_column(Integer, default=0)
    ignition: Mapped[bool] = mapped_column(Boolean, default=False)
    movement: Mapped[bool] = mapped_column(Boolean, default=False)
    battery_voltage: Mapped[float] = mapped_column(Float, nullable=True)
    gsm_signal: Mapped[int] = mapped_column(Integer, nullable=True)
    odometer: Mapped[float] = mapped_column(Float, nullable=True)
    raw_io: Mapped[str] = mapped_column(Text, nullable=True)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="positions")


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    start_lat: Mapped[float] = mapped_column(Float, nullable=False)
    start_lng: Mapped[float] = mapped_column(Float, nullable=False)
    end_lat: Mapped[float] = mapped_column(Float, nullable=True)
    end_lng: Mapped[float] = mapped_column(Float, nullable=True)
    start_address: Mapped[str] = mapped_column(String(255), nullable=True)
    end_address: Mapped[str] = mapped_column(String(255), nullable=True)
    distance_km: Mapped[float] = mapped_column(Float, default=0.0)
    max_speed: Mapped[int] = mapped_column(Integer, default=0)
    avg_speed: Mapped[float] = mapped_column(Float, default=0.0)
    duration_sec: Mapped[int] = mapped_column(Integer, default=0)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="trips")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False, index=True)
    type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    speed: Mapped[int] = mapped_column(Integer, nullable=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="alerts")
