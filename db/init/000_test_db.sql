-- Creates a second, dedicated database for the automated test suite, and
-- applies the same schema/migrations to it as the main database - but
-- deliberately NOT 001_seed.sql's demo data - so tests run against real
-- Postgres (its constraints, locking, etc. are all genuinely exercised)
-- without ever seeing dev/demo data mixed into their results.
--
-- Runs first alphabetically (000 < 001), but that only matters for when
-- THIS script runs relative to the others on the main database - the
-- \i includes below read each file's content directly from disk, so it
-- doesn't matter whether Postgres has "gotten to" 001/002/003 yet in its
-- own loop over the main database.

create database backend_exercise_test;

\connect backend_exercise_test

\i /docker-entrypoint-initdb.d/001_schema.sql
\i /docker-entrypoint-initdb.d/002_bookings.sql
\i /docker-entrypoint-initdb.d/003_single_booking_per_slot.sql
