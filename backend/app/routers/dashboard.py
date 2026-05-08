from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Vehicle, Trip, Alert, VehicleStatus
from app.schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count()).select_from(Vehicle))).scalar() or 0
    online = (
        await db.execute(
            select(func.count()).select_from(Vehicle).where(
                Vehicle.status.in_([VehicleStatus.online, VehicleStatus.moving, VehicleStatus.idle])
            )
        )
    ).scalar() or 0
    moving = (
        await db.execute(
            select(func.count()).select_from(Vehicle).where(Vehicle.status == VehicleStatus.moving)
        )
    ).scalar() or 0
    idle = (
        await db.execute(
            select(func.count()).select_from(Vehicle).where(Vehicle.status == VehicleStatus.idle)
        )
    ).scalar() or 0
    offline = (
        await db.execute(
            select(func.count()).select_from(Vehicle).where(Vehicle.status == VehicleStatus.offline)
        )
    ).scalar() or 0

    active_trips = (
        await db.execute(
            select(func.count()).select_from(Trip).where(Trip.end_time.is_(None))
        )
    ).scalar() or 0

    unack_alerts = (
        await db.execute(
            select(func.count()).select_from(Alert).where(Alert.acknowledged.is_(False))
        )
    ).scalar() or 0

    today_start = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    dist_today = (
        await db.execute(
            select(func.coalesce(func.sum(Trip.distance_km), 0.0))
            .where(Trip.start_time >= today_start)
        )
    ).scalar() or 0.0

    return DashboardStats(
        total_vehicles=total,
        online_vehicles=online,
        moving_vehicles=moving,
        idle_vehicles=idle,
        offline_vehicles=offline,
        active_trips=active_trips,
        unacknowledged_alerts=unack_alerts,
        total_distance_today_km=round(float(dist_today), 1),
    )
