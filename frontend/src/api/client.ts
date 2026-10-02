import type { BookingResponse, SlotResponse } from "../types";

/**
 * Base URL of the backend API. Falls back to the local dev default if
 * VITE_API_BASE_URL isn't set (e.g. running outside docker compose).
 */
const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

/** Thrown by bookSlot when the backend rejects a booking (HTTP 409)
 * because the slot was taken before the request was processed. */
export class SlotUnavailableError extends Error {}

/**
 * Thrown when the current session already has a booking.
 */
export class AlreadyBookedError extends Error {
  constructor(message = "You already have a booking.") {
    super(message);
    this.name = "AlreadyBookedError";
  }
}

/**
 * Fetch the current list of aggregated, bookable slots from the backend.
 * Throws a generic Error if the request fails.
 */
export async function fetchSlots(): Promise<SlotResponse[]> {
  const controller = new AbortController();

  const timeout = setTimeout(() => {
    controller.abort();
  }, 8000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/slots`, {
      signal: controller.signal,
      // Allows the browser to send the session_id cookie.
      credentials: "include"
    });

    if (!response.ok) {
      throw new Error("Could not load available slots.");
    }

    return response.json();
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Request took too long.");
    }

    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * Ask the backend to book one available doctor for the given start time.
 * The caller never chooses a doctor - the backend is responsible for that.
 *
 * @throws SlotUnavailableError if the slot was taken before this request
 *   reached the server (HTTP 409).
 * @throws Error for any other failure.
 */
export async function bookSlot(startsAt: string): Promise<BookingResponse> {
  const response = await fetch(`${API_BASE_URL}/api/book`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ starts_at: startsAt }),
  });

  if (response.status === 409) {
    let detail: string | undefined;

    try {
      const body = await response.json();
      detail = body.detail;
    } catch {
      // Empty or invalid response body.
    }

    if (detail === "You already have a booking.") {
      throw new AlreadyBookedError(detail);
    }

    throw new SlotUnavailableError(
      detail ?? "This slot is no longer available."
    );
  }
  if (!response.ok) {
    throw new Error("Booking failed.");
  }

  return response.json();
}
