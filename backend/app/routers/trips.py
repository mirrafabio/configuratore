from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Trip
from app.schemas import TripOut

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/", response_model=list[TripOut])
async def list_trips(
    vehicle_id: Optional[int] = Query(None),
    limit: int = Query(50, le=500),
    db: AsyncSession = Depends(get_db),
):
    q = select(Trip).order_by(desc(Trip.start_time)).limit(limit)
    if vehicle_id is not None:
        q = q.where(Trip.vehicle_id == vehicle_id)
    result = await db.execute(q)
    return result.scalars().all()
