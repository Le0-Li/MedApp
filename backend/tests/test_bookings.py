"""Tests for POST /api/book."""

from datetime import datetime, timezone

from app.models import Doctor

FUTURE = datetime(2099, 6, 1, 14, 0, tzinfo=timezone.utc)


def test_books_the_available_doctor(client, doctor, make_availability):
    make_availability(doctor, FUTURE)

    response = client.post("/api/book", json={"starts_at": FUTURE.isoformat()})

    assert response.status_code == 201
    body = response.json()
    assert body["doctor_name"] == doctor.full_name
    assert datetime.fromisoformat(body["starts_at"]) == FUTURE


def test_client_cannot_choose_a_doctor(client, doctor, make_availability):
    """The request schema only accepts starts_at - passing a doctor_id
    (or anything else) has no effect; the backend still picks the doctor."""
    make_availability(doctor, FUTURE)

    response = client.post(
        "/api/book", json={"starts_at": FUTURE.isoformat(), "doctor_id": 999}
    )

    assert response.status_code == 201
    assert response.json()["doctor_name"] == doctor.full_name


def test_returns_409_when_no_doctor_was_ever_available(client):
    response = client.post("/api/book", json={"starts_at": FUTURE.isoformat()})

    assert response.status_code == 409
    assert "no longer available" in response.json()["detail"]


def test_missing_starts_at_is_rejected_with_422(client):
    response = client.post("/api/book", json={})

    assert response.status_code == 422


def test_second_booking_for_the_same_time_is_rejected_even_with_another_doctor_free(
    client, doctor, make_availability, db_session
):
    """The key business rule: a time slot can only be booked ONCE overall,
    even if more than one doctor was free for it."""
    second_doctor = Doctor(full_name="Dr. Second", specialty="General Medicine")
    db_session.add(second_doctor)
    db_session.commit()
    db_session.refresh(second_doctor)

    make_availability(doctor, FUTURE)
    make_availability(second_doctor, FUTURE)

    first = client.post("/api/book", json={"starts_at": FUTURE.isoformat()})
    second = client.post("/api/book", json={"starts_at": FUTURE.isoformat()})

    assert first.status_code == 201
    assert second.status_code == 409
    assert "no longer available" in second.json()["detail"]


def test_booking_a_different_time_still_works_after_one_is_taken(
    client, doctor, make_availability
):
    other_time = datetime(2099, 6, 1, 16, 0, tzinfo=timezone.utc)
    make_availability(doctor, FUTURE)
    make_availability(doctor, other_time)

    client.post("/api/book", json={"starts_at": FUTURE.isoformat()})
    response = client.post("/api/book", json={"starts_at": other_time.isoformat()})

    assert response.status_code == 201
