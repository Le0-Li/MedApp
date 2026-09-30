/**
 * Shared types describing appointment data as used by the UI and the API.
 */

/** A single bookable time slot, aggregated across every doctor free then. */
export type AppointmentSlot = {
  startsAt: string;
  availableDoctors: number;
};

/** Raw shape returned by GET /api/slots (snake_case, as sent by FastAPI). */
export type SlotResponse = {
  starts_at: string;
  available_doctors: number;
};

/** Raw shape returned by POST /api/book on success. */
export type BookingResponse = {
  id: number;
  starts_at: string;
  ends_at: string;
  doctor_name: string;
};
