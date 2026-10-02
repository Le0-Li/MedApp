"""Tests for GET /api/slots.

These tests run against the same database the app uses for real seeded
data (see the note in conftest.py), so assertions here check for OUR
specific test slot within the response rather than assuming the list is
empty or contains only what we created - the response also includes
whatever seed/demo data already exists. Using far-future dates (2099)
keeps our fixtures from ever colliding with that seed data, which is
only generated within about two weeks of "now" (see db/init/001_schema.sql).
"""

from datetime import datetime, timezone

from app.models import Booking, Doctor

FUTURE = datetime(2099, 6, 1, 10, 0, tzinfo=timezone.utc)
PAST = datetime(2020, 1, 1, 10, 0, tzinfo=timezone.utc)


def _slot_at(slots: list[dict], starts_at: datetime) -> dict | None:
    """Find the slot matching starts_at in a /api/slots response body,
    ignoring any other (e.g. seeded) slots also present."""
    for slot in slots:
        parsed = datetime.fromisoformat(slot["starts_at"].replace("Z", "+00:00"))
        if parsed == starts_at:
            return slot
    return None


def test_a_newly_created_availability_appears_in_the_list(client, doctor, make_availability):
    make_availability(doctor, FUTURE)

    response = client.get("/api/slots")
    assert response.status_code == 200

    slot = _slot_at(response.json(), FUTURE)
    assert slot is not None
    assert slot["available_doctors"] == 1


def test_two_doctors_at_the_same_time_collapse_into_one_slot(
    client, doctor, make_availability, db_session
):
    """The core aggregation rule: several doctors free at the same start
    time must appear as ONE slot, not one per doctor."""
    second_doctor = Doctor(full_name="Dr. Second", specialty="General Medicine")
    db_session.add(second_doctor)
    db_session.commit()
    db_session.refresh(second_doctor)

    make_availability(doctor, FUTURE)
    make_availability(second_doctor, FUTURE)

    response = client.get("/api/slots")
    matches = [s for s in response.json() if _slot_at([s], FUTURE)]

    assert len(matches) == 1
    assert matches[0]["available_doctors"] == 2


def test_excludes_slots_in_the_past(client, doctor, make_availability):
    make_availability(doctor, PAST)

    response = client.get("/api/slots")

    assert _slot_at(response.json(), PAST) is None


def test_a_booked_doctor_is_removed_but_the_slot_remains_available(
    client, doctor, make_availability, db_session
):
    second_doctor = Doctor(
        full_name="Dr. Second",
        specialty="General Medicine",
    )
    db_session.add(second_doctor)
    db_session.commit()
    db_session.refresh(second_doctor)

    first_availability = make_availability(doctor, FUTURE)
    make_availability(second_doctor, FUTURE)

    db_session.add(
        Booking(
            availability_id=first_availability.id,
            session_id="test-session",
            starts_at=FUTURE
        )
    )
    db_session.commit()

    response = client.get("/api/slots")
    assert response.status_code == 200
    slot = _slot_at(response.json(), FUTURE)
    assert slot is not None
    assert slot["available_doctors"] == 1


def test_slots_are_ordered_by_start_time(client, doctor, make_availability):
    later = datetime(2099, 6, 1, 14, 0, tzinfo=timezone.utc)
    earlier = datetime(2099, 6, 1, 9, 0, tzinfo=timezone.utc)

    make_availability(doctor, later)
    make_availability(doctor, earlier)

    response = client.get("/api/slots")
    starts_at_values = [slot["starts_at"] for slot in response.json()]

    assert starts_at_values == sorted(starts_at_values)

def test_slot_disappears_when_all_doctors_are_booked(
    client, doctor, make_availability, db_session
):
    second_doctor = Doctor(
        full_name="Dr. Second",
        specialty="General Medicine",
    )
    db_session.add(second_doctor)
    db_session.commit()
    db_session.refresh(second_doctor)

    first_availability = make_availability(doctor, FUTURE)
    second_availability = make_availability(second_doctor, FUTURE)

    db_session.add_all(
        [
            Booking(
                availability_id=first_availability.id,
                session_id="session-one",
                starts_at=FUTURE
            ),
            Booking(
                availability_id=second_availability.id,
                session_id="session-two",
                starts_at=FUTURE
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/slots")

    assert response.status_code == 200
    assert _slot_at(response.json(), FUTURE) is None
