-- A given start time may only be booked ONCE overall, no matter how many
-- doctors were originally free at that time - the user picks a time, not
-- a doctor. This column plus its UNIQUE constraint enforce that rule at
-- the database level, which is what actually prevents it under race
-- conditions (application code alone can't guarantee this).

alter table bookings add column starts_at timestamptz;

-- Backfill from the existing availability row, in case any bookings
-- already exist from before this migration.
update bookings b
set starts_at = da.starts_at
from doctor_availabilities da
where da.id = b.availability_id;

alter table bookings alter column starts_at set not null;

alter table bookings add constraint bookings_starts_at_key unique (starts_at);
