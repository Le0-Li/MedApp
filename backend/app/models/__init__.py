"""ORM models package.

Re-exports every model so the rest of the app can do
`from app.models import Doctor, DoctorAvailability, Booking`
without needing to know which file each one lives in.
"""

from .availability import DoctorAvailability
from .base import Base
from .booking import Booking
from .doctor import Doctor

__all__ = ["Base", "Doctor", "DoctorAvailability", "Booking"]
