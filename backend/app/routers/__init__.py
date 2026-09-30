# app/routers/__init__.py
"""Combines every resource router into one for main.py to mount."""
from fastapi import APIRouter

from . import bookings, slots

api_router = APIRouter()
api_router.include_router(slots.router)
api_router.include_router(bookings.router)