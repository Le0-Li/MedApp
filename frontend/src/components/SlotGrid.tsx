import type { AppointmentSlot } from "../types";
import { SlotButton } from "./SlotButton";

/** Formats an ISO timestamp's date portion, e.g. "Monday, August 3". */
function formatDay(value: string) {
  return new Intl.DateTimeFormat("en", {
    weekday: "long",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(value));
}

/** Groups a flat list of slots into buckets keyed by their calendar day (UTC). */
function groupSlotsByDay(slots: AppointmentSlot[]) {
  return slots.reduce<Record<string, AppointmentSlot[]>>((groups, slot) => {
    const key = slot.startsAt.slice(0, 10); // "YYYY-MM-DD" prefix of the ISO string
    groups[key] = groups[key] ?? [];
    groups[key].push(slot);
    return groups;
  }, {});
}

type SlotGridProps = {
  slots: AppointmentSlot[];
  selectedSlot: AppointmentSlot | null;
  onSelect: (slot: AppointmentSlot) => void;
};

/** Renders every available slot, grouped and labelled by day. */
export function SlotGrid({ slots, selectedSlot, onSelect }: SlotGridProps) {
  const slotsByDay = groupSlotsByDay(slots);

  return (
    <>
      {Object.entries(slotsByDay).map(([day, daySlots]) => (
        <div className="day-group" key={day}>
          <div className="day-title">{formatDay(day)}</div>
          <div className="slot-grid">
            {daySlots.map((slot) => (
              <SlotButton
                key={slot.startsAt}
                slot={slot}
                isSelected={selectedSlot?.startsAt === slot.startsAt}
                onSelect={onSelect}
              />
            ))}
          </div>
        </div>
      ))}
    </>
  );
}
