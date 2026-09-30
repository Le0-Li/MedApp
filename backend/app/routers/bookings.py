"""Routes for confirming an appointment booking."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Booking, Doctor, DoctorAvailability
from app.schemas import BookingOut, BookingRequest

router = APIRouter(prefix="/api", tags=["bookings"])


@router.post("/book", response_model=BookingOut, status_code=201)
def book_slot(payload: BookingRequest, db: Session = Depends(get_db)) -> BookingOut:
    """Book one available doctor for the requested start time.

    A time slot can only be booked ONCE overall, even if several doctors
    were free at that time - the user picks a time, not a doctor, so once
    any doctor has been assigned to a given start time, that slot is
    considered taken and any further attempt must fail with 409.

    Safety layers, from cheapest to strongest:
    1. An early existence check on Booking.starts_at gives a fast, clear
       409 for the common case (someone already booked this time).
    2. FOR UPDATE SKIP LOCKED reserves one specific doctor's availability
       row, so two concurrent requests don't fight over the SAME doctor.
    3. The UNIQUE constraint on bookings.starts_at is the real guarantee:
       even if two different doctors get reserved concurrently for the
       same requested time (step 2 alone wouldn't stop that, since they'd
       be reserving two different availability rows), only one INSERT can
       ever commit for a given starts_at. The loser's transaction rolls
       back cleanly - its reserved doctor becomes free again - and the
       client gets a 409.
    """
    # Step 1: fast path - is this time already booked by anyone at all?
    already_booked = db.execute(
        select(Booking.id).where(Booking.starts_at == payload.starts_at)
    ).scalar_one_or_none()
    if already_booked is not None:
        raise HTTPException(status_code=409, detail="This slot is no longer available.")

    # Step 2: reserve one free doctor for this time, locking that row so
    # no other transaction can grab the SAME doctor concurrently.
    availability = db.execute(
        select(DoctorAvailability)
        .outerjoin(Booking, Booking.availability_id == DoctorAvailability.id)
        .where(
            DoctorAvailability.starts_at == payload.starts_at,
            Booking.id.is_(None),
        )
        .with_for_update(of=DoctorAvailability, skip_locked=True)
        .limit(1)
    ).scalar_one_or_none()

    if availability is None:
        db.rollback()
        raise HTTPException(status_code=409, detail="This slot is no longer available.")

    # Step 3: record the booking. The UNIQUE constraint on starts_at is
    # what actually enforces "one booking per time slot, however many
    # doctors are free" - it rejects this insert if another request won
    # the race for the same time in between steps 1 and now.
    booking = Booking(availability_id=availability.id, starts_at=availability.starts_at)
    db.add(booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This slot is no longer available.")

    db.refresh(booking)
    doctor = db.get(Doctor, availability.doctor_id)

    """
    Left this in comment, because it was the option I thought about first. The first line allows to remove the LOCK/SKIP and the try expect
    But going a bit further, having a try/expect would be a safe gard if someone ever change the code and remove the first line
    db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"), {"key": payload.starts_at.isoformat()})

    # Now authoritative - nothing else can be checking/booking this same
    # starts_at concurrently, so this check can't go stale before we commit.
    already_booked = db.execute(
        select(Booking.id).where(Booking.starts_at == payload.starts_at)
    ).scalar_one_or_none()
    if already_booked is not None:
        raise HTTPException(status_code=409, detail="This slot is no longer available.")

    availability = db.execute(
        select(DoctorAvailability)
        .outerjoin(Booking, Booking.availability_id == DoctorAvailability.id)
        .where(
            DoctorAvailability.starts_at == payload.starts_at,
            Booking.id.is_(None),
        )
        .limit(1)   # no FOR UPDATE / SKIP LOCKED needed - nothing else is contending
    ).scalar_one_or_none()

    if availability is None:
        raise HTTPException(status_code=409, detail="This slot is no longer available.")

    booking = Booking(availability_id=availability.id, starts_at=availability.starts_at)
    db.add(booking)
    db.commit()   # no try/except needed - the UNIQUE constraint can't actually fire
    """

    return BookingOut(
        id=booking.id,
        starts_at=availability.starts_at,
        ends_at=availability.ends_at,
        doctor_name=doctor.full_name,
    )