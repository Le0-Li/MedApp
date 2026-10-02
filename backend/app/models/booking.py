"""Booking model: records that a specific availability row was claimed."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .availability import DoctorAvailability
from .base import Base


class Booking(Base):

    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("session_id", "starts_at", name="uq_booking_session_starts_at"),
    )


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    availability_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("doctor_availabilities.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    availability: Mapped[DoctorAvailability] = relationship(back_populates="booking")