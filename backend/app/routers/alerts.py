from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Alert
from app.schemas import AlertOut, AlertAck

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertOut])
async def list_alerts(
    vehicle_id: Optional[int] = Query(None),
    unacknowledged_only: bool = Query(False),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
):
    q = select(Alert).order_by(desc(Alert.created_at)).limit(limit)
    if vehicle_id is not None:
        q = q.where(Alert.vehicle_id == vehicle_id)
    if unacknowledged_only:
        q = q.where(Alert.acknowledged.is_(False))
    result = await db.execute(q)
    return result.scalars().all()


@router.patch("/{alert_id}", response_model=AlertOut)
async def acknowledge_alert(
    alert_id: int, payload: AlertAck, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.acknowledged = payload.acknowledged
    await db.commit()
    await db.refresh(alert)
    return alert


@router.post("/acknowledge-all", status_code=204)
async def acknowledge_all(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.acknowledged.is_(False)))
    for alert in result.scalars().all():
        alert.acknowledged = True
    await db.commit()
