"""Concurrency test for the double-booking guarantee.

Uses concurrency_client and raw_session_factory (see conftest.py) rather
than the shared db_session/client fixtures - those wrap everything in one
transaction, but concurrent requests need genuinely independent DB
connections and committed data to actually exercise FOR UPDATE SKIP
LOCKED and the UNIQUE constraint the way concurrent real users would.
Cleanup is done explicitly at the end instead of relying on a rollback.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.models import Booking, Doctor, DoctorAvailability

STARTS_AT = datetime(2099, 3, 1, 10, 0, tzinfo=timezone.utc)


def test_only_one_booking_succeeds_among_concurrent_requests_for_the_same_slot(
    concurrency_client, raw_session_factory
):
    """Two doctors are free at the same time. Four simultaneous booking
    requests for that time should produce exactly one success and three
    409s - never more than one committed booking for that start time,
    matching the "one booking per time slot" business rule even under
    real concurrency."""
    session = raw_session_factory()
    doctor_a = Doctor(full_name="Dr. Concurrency A", specialty="General Medicine")
    doctor_b = Doctor(full_name="Dr. Concurrency B", specialty="General Medicine")
    try:
        session.add_all([doctor_a, doctor_b])
        session.commit()
        session.refresh(doctor_a)
        session.refresh(doctor_b)
        # Capture plain ints now: doctor_a/doctor_b become detached once
        # the session below closes, and reading .id after that re-triggers
        # a DB load with no session attached, raising DetachedInstanceError.
        doctor_a_id = doctor_a.id
        doctor_b_id = doctor_b.id

        session.add_all(
            [
                DoctorAvailability(
                    doctor_id=doctor_a_id,
                    starts_at=STARTS_AT,
                    ends_at=STARTS_AT + timedelta(minutes=30),
                ),
                DoctorAvailability(
                    doctor_id=doctor_b_id,
                    starts_at=STARTS_AT,
                    ends_at=STARTS_AT + timedelta(minutes=30),
                ),
            ]
        )
        session.commit()
    finally:
        session.close()

    def attempt_booking(_index: int):
        return concurrency_client.post("/api/book", json={"starts_at": STARTS_AT.isoformat()})

    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            responses = list(executor.map(attempt_booking, range(4)))

        status_codes = sorted(response.status_code for response in responses)
        assert status_codes == [201, 409, 409, 409]
    finally:
        cleanup = raw_session_factory()
        try:
            cleanup.execute(delete(Booking).where(Booking.starts_at == STARTS_AT))
            cleanup.execute(
                delete(DoctorAvailability).where(DoctorAvailability.starts_at == STARTS_AT)
            )
            cleanup.execute(delete(Doctor).where(Doctor.id.in_([doctor_a_id, doctor_b_id])))
            cleanup.commit()
        finally:
            cleanup.close()
