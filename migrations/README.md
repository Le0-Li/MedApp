# Staged migration: one booking per time slot

Production-style, zero-downtime version of `db/init/003_single_booking_per_slot.sql`.
For local dev/test, keep using the simpler all-at-once file in `db/init/` -
these staged files are only needed against a live database with real data
and real concurrent traffic.

## Why these can't just run back-to-back

1. **003b must fully finish before 003c runs.** 003c's validation will
   correctly fail if any row is still missing `starts_at`. On a large
   table this backfill can take hours - it cannot be chained into the
   same deploy as the others.
2. **App code must be deployed between 003a and 003b.** New bookings
   created while the backfill is still running need to already be
   writing `starts_at` themselves, or 003b would be chasing new NULL
   rows forever.

## Order of operations

| Step | What | Blocking? |
|---|---|---|
| 1 | Run `003a_add_starts_at_column.sql` | No - metadata only |
| 2 | Deploy app code that writes `starts_at` on every new booking | N/A |
| 3 | Run `003b_backfill_starts_at.py` (can take hours; safe to pause/resume) | No |
| 4 | Run `003c_enforce_not_null.sql` | No - two-step validate pattern |
| 5 | Run `003d_add_unique_constraint.sql` | No - `CONCURRENTLY` index build |

Each step is applied individually, by an explicit command (a person or a
deploy pipeline step) - never automatically on boot the way `db/init/`
works.
