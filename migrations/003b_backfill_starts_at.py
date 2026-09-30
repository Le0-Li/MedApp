"""STAGE 2 of 4 for the "one booking per time slot" fix.

Backfills bookings.starts_at in small batches, safe to run against a
live table with real traffic. A single giant UPDATE would hold locks
across the whole table for however long it takes to finish, and generate
a huge amount of write-ahead log all at once - this script avoids both
by committing after each small batch and pausing briefly in between.

Idempotent and resumable: every batch only touches rows that still have
starts_at = NULL, so it's safe to stop this at any point (Ctrl+C, a
deploy, a crash) and simply re-run it later - it will pick up exactly
where it left off.

IMPORTANT PRECONDITION: before running this, the application must
already be deployed writing starts_at on every NEW booking (see 003a's
deploy notes) - otherwise this backfill would be chasing new NULL rows
forever and never catch up.

Run manually, e.g.:
    python migrations/003b_backfill_starts_at.py
or wire it into a one-off deploy/ops task depending on your platform.
"""

import time

from sqlalchemy import text

from app.db import SessionLocal

BATCH_SIZE = 1000
PAUSE_BETWEEN_BATCHES_SECONDS = 0.5

BACKFILL_QUERY = text(
    """
    update bookings
    set starts_at = da.starts_at
    from doctor_availabilities da
    where da.id = bookings.availability_id
      and bookings.starts_at is null
      and bookings.id in (
        select id from bookings where starts_at is null limit :batch_size
      )
    """
)


def run_backfill() -> None:
    total_updated = 0

    while True:
        session = SessionLocal()
        try:
            result = session.execute(BACKFILL_QUERY, {"batch_size": BATCH_SIZE})
            session.commit()
        finally:
            session.close()

        rows_updated = result.rowcount
        total_updated += rows_updated
        print(f"Backfilled {rows_updated} rows (total so far: {total_updated})")

        if rows_updated == 0:
            print("Backfill complete - no rows left with a NULL starts_at.")
            break

        # Brief pause so this doesn't hog I/O from real production traffic.
        time.sleep(PAUSE_BETWEEN_BATCHES_SECONDS)


if __name__ == "__main__":
    run_backfill()
