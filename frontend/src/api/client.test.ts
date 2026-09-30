import { afterEach, describe, expect, it, vi } from "vitest";

import { bookSlot, fetchSlots, SlotUnavailableError } from "./client";

describe("fetchSlots", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it("returns the parsed slot list on success", async () => {
    const mockSlots = [{ starts_at: "2099-01-01T10:00:00Z", available_doctors: 2 }];
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify(mockSlots), { status: 200 })
    );

    await expect(fetchSlots()).resolves.toEqual(mockSlots);
  });

  it("throws when the server responds with an error status", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(new Response("", { status: 500 }));

    await expect(fetchSlots()).rejects.toThrow("Could not load available slots.");
  });

  it("throws a timeout-specific message if the request takes too long", async () => {
    vi.useFakeTimers();

    try {
      vi.spyOn(global, "fetch").mockImplementation(
        (_input, init) =>
          new Promise((_resolve, reject) => {
            (init as RequestInit)?.signal?.addEventListener("abort", () => {
              reject(new DOMException("Aborted", "AbortError"));
            });
          })
      );

      const pending = fetchSlots();

      const assertion = expect(pending).rejects.toThrow("took too long");

      await vi.advanceTimersByTimeAsync(8000);

      await assertion;
    } finally {
      vi.useRealTimers();
      vi.restoreAllMocks();
    }
  });
});

describe("bookSlot", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("returns the booking confirmation on success", async () => {
    const booking = {
      id: 1,
      starts_at: "2099-01-01T10:00:00Z",
      ends_at: "2099-01-01T10:30:00Z",
      doctor_name: "Dr. Test",
    };
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify(booking), { status: 201 })
    );

    await expect(bookSlot("2099-01-01T10:00:00Z")).resolves.toEqual(booking);
  });

  it("throws SlotUnavailableError specifically on a 409", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(new Response("", { status: 409 }));

    await expect(bookSlot("2099-01-01T10:00:00Z")).rejects.toBeInstanceOf(
      SlotUnavailableError
    );
  });

  it("throws a generic error on any other failure status", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(new Response("", { status: 500 }));

    await expect(bookSlot("2099-01-01T10:00:00Z")).rejects.toThrow("Booking failed.");
  });
});
