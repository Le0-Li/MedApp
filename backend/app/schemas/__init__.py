"""Pydantic schemas package.

Kept separate from the SQLAlchemy models in app/models/: those describe
database rows, these describe what the HTTP API accepts and returns.

Re-exports every schema so routers can do
`from app.schemas import SlotOut, BookingRequest, BookingOut`
without needing to know which file each one lives in.
"""

from .bookings import BookingOut, BookingRequest
from .slots import SlotOut

__all__ = ["SlotOut", "BookingRequest", "BookingOut"]