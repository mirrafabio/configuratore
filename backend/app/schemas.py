from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models import VehicleStatus, AlertType


class VehicleBase(BaseModel):
    name: str
    plate: str
    model: Optional[str] = None
    driver: Optional[str] = None
    imei: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    name: Optional[str] = None
    plate: Optional[str] = None
    model: Optional[str] = None
    driver: Optional[str] = None
    imei: Optional[str] = None


class VehicleOut(VehicleBase):
    id: int
    status: VehicleStatus
    last_seen: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class VehicleWithPosition(VehicleOut):
    last_position: Optional["PositionOut"] = None


class PositionOut(BaseModel):
    id: int
    vehicle_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: float
    angle: int
    speed: int
    satellites: int
    ignition: bool
    movement: bool
    battery_voltage: Optional[float] = None
    gsm_signal: Optional[int] = None
    odometer: Optional[float] = None

    model_config = {"from_attributes": True}


class TripOut(BaseModel):
    id: int
    vehicle_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    start_lat: float
    start_lng: float
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    start_address: Optional[str] = None
    end_address: Optional[str] = None
    distance_km: float
    max_speed: int
    avg_speed: float
    duration_sec: int

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: int
    vehicle_id: int
    type: AlertType
    message: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed: Optional[int] = None
    acknowledged: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertAck(BaseModel):
    acknowledged: bool = True


class DashboardStats(BaseModel):
    total_vehicles: int
    online_vehicles: int
    moving_vehicles: int
    idle_vehicles: int
    offline_vehicles: int
    active_trips: int
    unacknowledged_alerts: int
    total_distance_today_km: float
