"""Pydantic schemas for the bookings resource (POST /api/book)."""

from datetime import datetime

from pydantic import BaseModel


class BookingRequest(BaseModel):
    """Body for POST /api/book.

    The client only sends a time, never a doctor - the backend is
    responsible for picking which doctor to assign.
    """

    starts_at: datetime


class BookingOut(BaseModel):
    """Confirmation returned after a successful booking."""

    id: int
    starts_at: datetime
    ends_at: datetime
    doctor_name: str