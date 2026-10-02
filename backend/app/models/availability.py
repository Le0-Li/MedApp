"""DoctorAvailability model: a single doctor's open appointment window."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .doctor import Doctor


class DoctorAvailability(Base):
    """One doctor's availability window (typically 30 minutes).

    Several doctors can have a row with the same `starts_at`. The API
    aggregates rows sharing a start time into a single slot shown to the
    end user, who never picks a specific doctor or availability row - the
    backend does that when a booking is made.

    Attributes:
        doctor_id: The doctor this availability belongs to.
        starts_at / ends_at: The UTC window during which the doctor is free.
        booking: The Booking that claimed this row, if any. `None` means
            the slot is still available.
    """

    __tablename__ = "doctor_availabilities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    "Relationship, when doctor is accessed, fetch full Doctor with doctor_id"
    doctor: Mapped[Doctor] = relationship(back_populates="availabilities")
    booking: Mapped["Booking | None"] = relationship(back_populates="availability", uselist=False)

