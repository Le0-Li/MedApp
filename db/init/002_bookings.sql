-- A booking claims exactly one doctor_availabilities row.
-- The UNIQUE constraint is what actually prevents the same underlying
-- doctor/time slot from being booked twice, even under concurrent requests.
create table bookings (
    id bigserial primary key,
    availability_id bigint not null references doctor_availabilities(id) on delete cascade,
    session_id varchar(64) not null,
    starts_at timestamp NOT NULL,
    created_at timestamp not null default now(),
    constraint uq_booking_session_starts_at unique (session_id, starts_at)

);
