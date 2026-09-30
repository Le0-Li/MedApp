import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchSlots } from "../api/client";
import { useSlots } from "./useSlots";

vi.mock("../api/client", () => ({
  fetchSlots: vi.fn(),
}));

const mockedFetchSlots = vi.mocked(fetchSlots);

describe("useSlots", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("loads slots on mount and converts them to the frontend's camelCase shape", async () => {
    mockedFetchSlots.mockResolvedValue([
      { starts_at: "2099-01-01T10:00:00Z", available_doctors: 2 },
    ]);

    const { result } = renderHook(() => useSlots());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.slots).toEqual([
      { startsAt: "2099-01-01T10:00:00Z", availableDoctors: 2 },
    ]);
    expect(result.current.error).toBeNull();
  });

  it("sets an error message when loading fails", async () => {
    mockedFetchSlots.mockRejectedValue(new Error("network down"));

    const { result } = renderHook(() => useSlots());

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe("network down");
    expect(result.current.slots).toEqual([]);
  });

  it("refetch reloads the slot list with fresh data", async () => {
    mockedFetchSlots.mockResolvedValue([]);
    const { result } = renderHook(() => useSlots());
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    mockedFetchSlots.mockResolvedValue([
      { starts_at: "2099-01-01T11:00:00Z", available_doctors: 1 },
    ]);

    await act(async () => {
      await result.current.refetch();
    });

    expect(result.current.slots).toEqual([
      { startsAt: "2099-01-01T11:00:00Z", availableDoctors: 1 },
    ]);
  });
});
