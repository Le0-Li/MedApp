import { CalendarDays } from "lucide-react";
import { useState } from "react";

import "./App.css";
import { AlreadyBookedError, bookSlot, SlotUnavailableError } from "./api/client";
import { SlotGrid } from "./components/SlotGrid";
import { SummaryPanel } from "./components/SummaryPanel";
import { useSlots } from "./hooks/useSlots";
import type { AppointmentSlot, BookingResponse } from "./types";

/**
 * Top-level screen: loads slots via useSlots, lets the user pick one, and
 * confirms the booking through the API. Data-fetching detail lives in the
 * hook/api layer - this component just wires state to the UI pieces.
 */
export default function App() {
  const { slots, isLoading, error, setError, refetch } = useSlots();
  const [selectedSlot, setSelectedSlot] = useState<AppointmentSlot | null>(null);
  const [confirmedBooking, setConfirmedBooking] = useState<BookingResponse | null>(null);
  const [isBooking, setIsBooking] = useState(false);

  /** Attempt to confirm the currently selected slot with the backend. */
  async function handleConfirm() {
    if (!selectedSlot) {
      return;
    }

    setIsBooking(true);
    setError(null);

    try {
      const booking = await bookSlot(selectedSlot.startsAt);

      setConfirmedBooking(booking);
      setSelectedSlot(null);

      await refetch();
    } catch (err) {
      if (err instanceof AlreadyBookedError) {
        setSelectedSlot(null);

        setError(
          "You already have an appointment in this session."
        );
      } else if (err instanceof SlotUnavailableError) {
        // The slot was taken between page load and clicking "confirm" -
        // clear the stale selection and refresh so the user sees reality.
        setSelectedSlot(null);

        // Refresh first, because refetch may clear the existing error.
        await refetch();

        // Set the conflict message after the refresh.
        setError(
          "That slot was just booked by someone else. Please pick another time."
        );
      } else {
        setError("Something went wrong while booking. Please try again.");
      }
    } finally {
      setIsBooking(false);
    }
  }


  return (
    <main className="app-shell">
      <section className="appointment-layout">
        <header className="page-header">
          <div>
            <p className="eyebrow">Medical appointment</p>
            <h1>Choose a time slot</h1>
          </div>
          <div className="header-meta">
            <CalendarDays size={18} aria-hidden="true" />
            UTC schedule
          </div>
        </header>

        <section className="slot-panel" aria-labelledby="available-slots-title">
          <h2 id="available-slots-title">Available slots</h2>

          {isLoading && <p className="summary-empty">Loading available slots…</p>}
          {error && (
            <p className="status-message" role="alert">
              {error}
            </p>
          )}

          {!isLoading && (
            <SlotGrid slots={slots} selectedSlot={selectedSlot} onSelect={setSelectedSlot} />
          )}
        </section>

        <SummaryPanel
          selectedSlot={selectedSlot}
          isBooking={isBooking}
          confirmedBooking={confirmedBooking}
          onConfirm={handleConfirm}
        />
      </section>
    </main>
  );
}
