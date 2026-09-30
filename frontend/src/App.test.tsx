import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { bookSlot, fetchSlots, SlotUnavailableError } from "./api/client";

vi.mock("./api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api/client")>();

  return {
    ...actual,
    fetchSlots: vi.fn(),
    bookSlot: vi.fn(),
  };
});

const mockedFetchSlots = vi.mocked(fetchSlots);
const mockedBookSlot = vi.mocked(bookSlot);


describe("App", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("lets the user pick a slot and confirm a booking", async () => {
    mockedFetchSlots.mockResolvedValue([
      { starts_at: "2099-01-01T10:00:00Z", available_doctors: 2 },
    ]);
    mockedBookSlot.mockResolvedValue({
      id: 1,
      starts_at: "2099-01-01T10:00:00Z",
      ends_at: "2099-01-01T10:30:00Z",
      doctor_name: "Dr. Test",
    });

    render(<App />);

    // Wait for the actual slot button, identified by its own accessible
    // text - this only appears once loading has genuinely finished,
    // unlike "any button exists" (the disabled confirm button is present
    // from the very first render).
    const slotButton = await screen.findByRole("button", { name: /doctors? available/i });
    const confirmButton = screen.getByRole("button", { name: /confirm appointment/i });
    expect(confirmButton).toBeDisabled();

    fireEvent.click(slotButton);
    expect(confirmButton).toBeEnabled();

    fireEvent.click(confirmButton);

    await waitFor(() =>
      expect(screen.getByText(/appointment confirmed with dr\. test/i)).toBeInTheDocument()
    );

    expect(mockedBookSlot).toHaveBeenCalledWith("2099-01-01T10:00:00Z");
    // The list is refreshed after a successful booking too.
    expect(mockedFetchSlots).toHaveBeenCalledTimes(2);
  });

  it("shows an error and refetches slots when the slot was just taken", async () => {
    mockedFetchSlots.mockResolvedValue([
      { starts_at: "2099-01-01T10:00:00Z", available_doctors: 1 },
    ]);
    mockedBookSlot.mockRejectedValue(new SlotUnavailableError("taken"));

    render(<App />);

    const slotButton = await screen.findByRole("button", { name: /doctors? available/i });
    const confirmButton = screen.getByRole("button", { name: /confirm appointment/i });

    fireEvent.click(slotButton);
    expect(confirmButton).toBeEnabled();   // <- forces a check that selection landed
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(
        screen.getByRole("alert")
      ).toHaveTextContent(/just booked by someone else/i);
    });

    expect(mockedBookSlot).toHaveBeenCalledWith(
      "2099-01-01T10:00:00Z"
    );

    expect(mockedFetchSlots).toHaveBeenCalledTimes(2);
  });
});