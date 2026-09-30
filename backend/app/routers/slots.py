"""Routes for browsing available appointment slots."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Booking, DoctorAvailability
from app.schemas import SlotOut

router = APIRouter(prefix="/api", tags=["slots"])


@router.get("/slots", response_model=list[SlotOut])
def list_slots(db: Session = Depends(get_db)) -> list[SlotOut]:
    """Return open slots, aggregated by start time.

    Several doctors free at the same start time collapse into a single
    slot; `available_doctors` tells the frontend how many doctors were
    originally free for it. A time is excluded entirely as soon as ANY
    doctor has been booked for it - a slot can only ever be booked once
    overall, so once that happens it's no longer offered at all, not just
    reduced by one. Past slots are excluded too.
    """
    rows = db.execute(
        select(
            DoctorAvailability.starts_at,
            func.count(DoctorAvailability.id).label("available_doctors"),
        )
        # Join on starts_at (not availability_id): once ANY doctor is
        # booked for a given time, the whole slot must disappear from the
        # list, not just that one doctor's row.
        .outerjoin(Booking, Booking.starts_at == DoctorAvailability.starts_at)
        .where(
            Booking.id.is_(None),  # exclude times that already have a booking
            DoctorAvailability.starts_at >= datetime.now(timezone.utc),
        )
        .group_by(DoctorAvailability.starts_at)
        .order_by(DoctorAvailability.starts_at)
    ).all()

    return [
        SlotOut(starts_at=row.starts_at, available_doctors=row.available_doctors)
        for row in rows
    ]