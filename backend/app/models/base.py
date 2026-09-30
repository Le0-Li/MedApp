"""Shared SQLAlchemy declarative base.

Every ORM model in this package inherits from this Base so they all
register onto the same metadata/registry (needed for relationships between
models defined in different files to resolve correctly).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models in this application."""
