from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Position
from app.schemas import PositionOut

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("/", response_model=list[PositionOut])
async def get_positions(
    vehicle_id: Optional[int] = Query(None),
    limit: int = Query(100, le=1000),
    since: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Position).order_by(desc(Position.timestamp)).limit(limit)
    if vehicle_id is not None:
        q = q.where(Position.vehicle_id == vehicle_id)
    if since is not None:
        q = q.where(Position.timestamp >= since)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/latest", response_model=list[PositionOut])
async def get_latest_positions(db: AsyncSession = Depends(get_db)):
    """Return the most recent position for each vehicle."""
    from sqlalchemy import func
    subq = (
        select(Position.vehicle_id, func.max(Position.id).label("max_id"))
        .group_by(Position.vehicle_id)
        .subquery()
    )
    q = select(Position).join(subq, Position.id == subq.c.max_id)
    result = await db.execute(q)
    return result.scalars().all()
