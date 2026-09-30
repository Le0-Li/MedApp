"""Shared pytest fixtures for the backend test suite.

Tests run against a DEDICATED test database (backend_exercise_test) -
never the dev database the running app uses - so seeded/demo data can
never leak into test assertions. It's created and schema-migrated
automatically the first time the Postgres container initializes (see
db/init/000_test_db.sql for how).

It's still real Postgres, though - not SQLite or a mock - so the
Postgres-specific behaviour this project actually relies on (the UNIQUE
constraints and FOR UPDATE SKIP LOCKED that guarantee no double-booking)
is genuinely exercised, not assumed. Most tests additionally run inside
their own transaction (a SAVEPOINT nested in an outer transaction) that's
always rolled back afterwards, for isolation between tests too - the
exception is concurrency-style tests, which need real independent
connections and commits (see raw_session_factory / concurrency_client).
"""

import os
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import get_db
from app.main import app
from app.models import Doctor, DoctorAvailability

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://app:app@localhost:5432/backend_exercise_test",
)
test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)


@pytest.fixture()
def db_session():
    """A DB session scoped to a single test, bound to the TEST database.

    join_transaction_mode="create_savepoint" means any session.commit()
    made by the code under test only releases a SAVEPOINT, not the outer
    transaction - so the final transaction.rollback() below always undoes
    everything, however many times the app itself "commits".
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """A FastAPI TestClient wired to use db_session for every request,
    so setup done directly via db_session and assertions made through
    HTTP requests both see the same (eventually rolled-back) data."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def raw_session_factory():
    """A callable that returns a brand-new, independent session bound to
    the test database - NOT wrapped in the rollback used by db_session.

    For tests that need real, separately-committed data across multiple
    genuinely independent connections (e.g. concurrency tests), which
    must therefore clean up after themselves explicitly instead of
    relying on a rollback.
    """
    return sessionmaker(bind=test_engine)


@pytest.fixture()
def concurrency_client(raw_session_factory):
    """A TestClient where each request gets its own fresh DB session
    (bound to the test database), mirroring how the real app behaves in
    production - unlike `client`, requests here are NOT pinned to one
    shared, rolled-back transaction, which is what makes it possible to
    genuinely race concurrent requests against each other."""

    def override_get_db():
        session = raw_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def doctor(db_session):
    """A single doctor to attach availabilities to in tests."""
    new_doctor = Doctor(full_name="Dr. Test Subject", specialty="General Medicine")
    db_session.add(new_doctor)
    db_session.commit()
    db_session.refresh(new_doctor)
    return new_doctor


@pytest.fixture()
def make_availability(db_session):
    """Factory fixture: make_availability(doctor, starts_at) creates and
    returns a 30-minute DoctorAvailability row for that doctor."""

    def _make(for_doctor: Doctor, starts_at):
        availability = DoctorAvailability(
            doctor_id=for_doctor.id,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=30),
        )
        db_session.add(availability)
        db_session.commit()
        db_session.refresh(availability)
        return availability

    return _make
