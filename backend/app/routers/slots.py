"""Routes for browsing available appointment slots."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Booking, DoctorAvailability
from app.schemas import SlotOut
from app.dependencies import get_session_id

router = APIRouter(prefix="/api", tags=["slots"])


@router.get("/slots", response_model=list[SlotOut])
def list_slots(db: Session = Depends(get_db), session_id: str = Depends(get_session_id)) -> list[SlotOut]:
    session_booked_times = select(Booking.starts_at).where(Booking.session_id == session_id)

    rows = db.execute(
        select(
            DoctorAvailability.starts_at,
            func.count(DoctorAvailability.id).label("available_doctors"),
        )
        .outerjoin(
            Booking,
            Booking.availability_id == DoctorAvailability.id,
        )
        .where(
            DoctorAvailability.starts_at >= datetime.now(timezone.utc),
            Booking.id.is_(None),
            ~DoctorAvailability.starts_at.in_(session_booked_times),
        )
        .group_by(DoctorAvailability.starts_at)
        .order_by(DoctorAvailability.starts_at)
    ).all()

    return [
        SlotOut(
            starts_at=row.starts_at,
            available_doctors=row.available_doctors,
        )
        for row in rows
    ]