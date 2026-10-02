"""Routes for confirming an appointment booking."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Booking, Doctor, DoctorAvailability
from app.schemas import BookingOut, BookingRequest
from app.dependencies import get_session_id


router = APIRouter(prefix="/api", tags=["bookings"])


@router.post("/book", response_model=BookingOut, status_code=201)
def book_slot(payload: BookingRequest, db: Session = Depends(get_db), session_id: str = Depends(get_session_id)) -> BookingOut:
    # Step 1: this session can only have one booking.
    existing_booking = db.execute(
        select(Booking.id)
        .join(
            DoctorAvailability,
            DoctorAvailability.id == Booking.availability_id,
        )
        .where(
            Booking.session_id == session_id,
            DoctorAvailability.starts_at == payload.starts_at,
        )
    ).scalar_one_or_none()

    if existing_booking is not None:
        raise HTTPException(
            status_code=409,
            detail="You already have a booking.",
        )

    # Step 2: find and lock one free doctor availability.
    availability = db.execute(
        select(DoctorAvailability)
        .outerjoin(
            Booking,
            Booking.availability_id == DoctorAvailability.id,
        )
        .where(
            DoctorAvailability.starts_at == payload.starts_at,
            Booking.id.is_(None),
        )
        .with_for_update(
            of=DoctorAvailability,
            skip_locked=True,
        )
        .limit(1)
    ).scalar_one_or_none()


    if availability is None:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This slot is no longer available.",
        )

    # Step 3: create the booking.
    booking = Booking(
        availability_id=availability.id,
        session_id=session_id,
        starts_at=availability.starts_at,
    )

    db.add(booking)


    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This slot is no longer available.",
        )

    db.refresh(booking)

    doctor = db.get(Doctor, availability.doctor_id)

    return BookingOut(
        id=booking.id,
        starts_at=availability.starts_at,
        ends_at=availability.ends_at,
        doctor_name=doctor.full_name,
    )
