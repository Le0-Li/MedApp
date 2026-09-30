"""Pydantic schemas for the slots resource (GET /api/slots)."""

from datetime import datetime

from pydantic import BaseModel


class SlotOut(BaseModel):
    """One aggregated appointment slot, as returned by GET /api/slots."""

    starts_at: datetime
    available_doctors: int