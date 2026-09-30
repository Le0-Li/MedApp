import { useCallback, useEffect, useState } from "react";

import { fetchSlots } from "../api/client";
import type { AppointmentSlot } from "../types";

/**
 * Loads the current available slots from the backend on mount, and
 * exposes loading/error state plus a `refetch` you can call again later
 * (e.g. after a booking attempt) to keep the list in sync with the server.
 */
export function useSlots() {
  const [slots, setSlots] = useState<AppointmentSlot[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /** Re-fetch slots from the API and update state accordingly. */
  const refetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchSlots();
      // Convert the API's snake_case shape into the frontend's camelCase type.
      setSlots(
        data.map((slot) => ({
          startsAt: slot.starts_at,
          availableDoctors: slot.available_doctors,
        }))
      );
    } catch (err) {
      // Surface the specific message from api/client.ts (e.g. "timed out"
      // vs. "could not reach the server") rather than a generic fallback,
      // so the user gets an honest, actionable explanation.
      setError(err instanceof Error ? err.message : "Could not load available slots.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load slots once when this hook is first used.
  useEffect(() => {
    refetch();
  }, [refetch]);

  return { slots, isLoading, error, setError, refetch };
}
