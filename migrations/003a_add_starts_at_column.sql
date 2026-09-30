-- STAGE 1 of 4 for the "one booking per time slot" fix, staged for a
-- live production table with real data and real traffic.
--
-- Adds the column only - nullable, no default. This is a metadata-only
-- change in Postgres: it doesn't rewrite existing rows or scan the
-- table, so it's safe and effectively instant even on a huge table.
--
-- DO run this alone, as its own deploy.
-- DO NOT combine it with 003b/003c/003d - see the README in this folder
-- for why each stage needs real time (and an app deploy) between them.

alter table bookings add column starts_at timestamptz;
