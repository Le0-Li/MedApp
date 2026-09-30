"""Doctor model: the medical staff who hold appointment availability."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class Doctor(Base):
    """A doctor who can be assigned to appointment slots.

    Attributes:
        full_name: Doctor's display name (e.g. "Dr. Amelia Hart").
        specialty: Medical specialty (e.g. "General Medicine").
        availabilities: Every time slot this doctor has opened up, booked
            or not. See DoctorAvailability for the booking relationship.
    """

    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    specialty: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    availabilities: Mapped[list["DoctorAvailability"]] = relationship(
        back_populates="doctor"
    )
