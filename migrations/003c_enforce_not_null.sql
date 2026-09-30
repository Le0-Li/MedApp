-- STAGE 3 of 4 for the "one booking per time slot" fix.
--
-- Only run this AFTER 003b's backfill script has finished completely
-- (printed "Backfill complete"). If any row still has starts_at = NULL,
-- the VALIDATE CONSTRAINT step below will fail loudly - which is
-- correct behaviour, not a bug: it means the backfill wasn't finished.
--
-- Two-step approach instead of a plain
--   ALTER TABLE bookings ALTER COLUMN starts_at SET NOT NULL;
-- which would require a full-table scan while holding an
-- ACCESS EXCLUSIVE lock (blocks all reads AND writes) for however long
-- that scan takes - real downtime on a huge table.
--
-- Step 1: add the check WITHOUT validating existing rows yet - this
-- only takes a brief lock to register the constraint.
alter table bookings add constraint starts_at_not_null check (starts_at is not null) not valid;

-- Step 2: validate separately - this scans the table, but only takes a
-- SHARE UPDATE EXCLUSIVE lock, which still allows concurrent reads AND
-- writes to continue while it runs.
alter table bookings validate constraint starts_at_not_null;

-- Step 3: now that the check is validated, Postgres (12+) can add the
-- real NOT NULL constraint essentially for free, trusting the already-
-- validated check instead of re-scanning the table.
alter table bookings alter column starts_at set not null;

-- Step 4: the CHECK constraint is now redundant (NOT NULL covers it) -
-- drop it to keep the schema clean.
alter table bookings drop constraint starts_at_not_null;
