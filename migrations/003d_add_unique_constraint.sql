-- STAGE 4 of 4 for the "one booking per time slot" fix - the final
-- step, which actually enforces "one booking per time slot" at the
-- database level.
--
-- A plain
--   ALTER TABLE bookings ADD CONSTRAINT bookings_starts_at_key UNIQUE (starts_at);
-- builds its backing index while holding a lock that blocks writes for
-- the entire build - real downtime on a huge table.
--
-- CREATE INDEX CONCURRENTLY avoids that: it builds the index without
-- blocking reads or writes. Trade-offs: it takes longer, cannot run
-- inside a transaction block (most migration tools have a specific
-- flag/marker for this - e.g. Alembic's autocommit_block()), and it
-- waits for any currently-running long transactions on this table to
-- finish before it can start. Worth checking pg_stat_activity for
-- long-running transactions on `bookings` before running this.
create unique index concurrently bookings_starts_at_idx on bookings (starts_at);

-- Attach the constraint to the already-built index - cheap, since the
-- index already exists; this step just registers it as a constraint.
alter table bookings add constraint bookings_starts_at_key unique using index bookings_starts_at_idx;
