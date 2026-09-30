import type { AppointmentSlot } from "../types";

/** Formats an ISO timestamp as a UTC clock time, e.g. "10:00 AM". */
function formatTime(value: string) {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  }).format(new Date(value));
}

type SlotButtonProps = {
  slot: AppointmentSlot;
  isSelected: boolean;
  onSelect: (slot: AppointmentSlot) => void;
};

/** A single clickable time slot, showing its time and how many doctors are free. */
export function SlotButton({ slot, isSelected, onSelect }: SlotButtonProps) {
  return (
    <button
      className={isSelected ? "slot-button selected" : "slot-button"}
      onClick={() => onSelect(slot)}
      type="button"
    >
      <span className="slot-time">{formatTime(slot.startsAt)}</span>
      <span className="slot-capacity">
        {slot.availableDoctors} doctor{slot.availableDoctors > 1 ? "s" : ""} available
      </span>
    </button>
  );
}
