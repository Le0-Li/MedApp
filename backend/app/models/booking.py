"""Booking model: records that a specific availability row was claimed."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .availability import DoctorAvailability
from .base import Base


class Booking(Base):
    """A confirmed appointment booking.

    Each booking claims exactly one `DoctorAvailability` row (one doctor).
    But the actual product rule is stricter than that: a given START TIME
    can only be booked ONCE overall, even if several doctors were free at
    that time - the user picks a time, not a doctor, so once any doctor is
    assigned to a time, that whole slot is closed to further bookings.

    Both UNIQUE constraints below are enforced in the database (see
    db/init/002_bookings.sql and 003_single_booking_per_slot.sql):
    - `availability_id` UNIQUE: the same doctor/slot row can't be double-booked.
    - `starts_at` UNIQUE: the same TIME can't be booked twice, period.
    """

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    availability_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("doctor_availabilities.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        unique=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    availability: Mapped[DoctorAvailability] = relationship(back_populates="booking")