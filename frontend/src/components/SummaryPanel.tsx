import { CheckCircle2, Clock3 } from "lucide-react";

import type { AppointmentSlot, BookingResponse } from "../types";

/** Formats an ISO timestamp's date portion, e.g. "Monday, August 3". */
function formatDay(value: string) {
  return new Intl.DateTimeFormat("en", {
    weekday: "long",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(value));
}

/** Formats an ISO timestamp as a UTC clock time, e.g. "10:00 AM". */
function formatTime(value: string) {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  }).format(new Date(value));
}

type SummaryPanelProps = {
  selectedSlot: AppointmentSlot | null;
  isBooking: boolean;
  confirmedBooking: BookingResponse | null;
  onConfirm: () => void;
};

/**
 * Right-hand panel: shows the currently selected slot, the confirm
 * button, and the confirmation message once a booking has succeeded.
 */
export function SummaryPanel({
  selectedSlot,
  isBooking,
  confirmedBooking,
  onConfirm,
}: SummaryPanelProps) {
  return (
    <aside className="summary-panel" aria-labelledby="summary-title">
      <h2 id="summary-title">Summary</h2>

      {selectedSlot ? (
        <p className="summary-detail">
          <strong>{formatDay(selectedSlot.startsAt)}</strong>
          {formatTime(selectedSlot.startsAt)}
        </p>
      ) : (
        <p className="summary-empty">Select a slot to continue.</p>
      )}

      <button
        className="confirm-button"
        disabled={!selectedSlot || isBooking}
        onClick={onConfirm}
        type="button"
      >
        <Clock3 size={18} aria-hidden="true" />
        {isBooking ? "Booking…" : "Confirm appointment"}
      </button>

      {confirmedBooking && (
        <div className="status-message" role="status">
          <CheckCircle2 size={18} aria-hidden="true" />
          Appointment confirmed with {confirmedBooking.doctor_name} on{" "}
          {formatDay(confirmedBooking.starts_at)} at {formatTime(confirmedBooking.starts_at)}.
        </div>
      )}
    </aside>
  );
}
