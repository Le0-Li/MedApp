-- A booking claims exactly one doctor_availabilities row.
-- The UNIQUE constraint is what actually prevents the same underlying
-- doctor/time slot from being booked twice, even under concurrent requests.
create table bookings (
  id bigserial primary key,
  availability_id bigint not null references doctor_availabilities(id) on delete cascade,
  created_at timestamp with time zone not null default now(),
  constraint bookings_availability_id_key unique (availability_id)
);
