import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { AppointmentSlot, BookingResponse } from "../types";
import { SummaryPanel } from "./SummaryPanel";

const slot: AppointmentSlot = { startsAt: "2099-01-01T10:00:00Z", availableDoctors: 1 };
const booking: BookingResponse = {
  id: 1,
  starts_at: "2099-01-01T10:00:00Z",
  ends_at: "2099-01-01T10:30:00Z",
  doctor_name: "Dr. Test",
};

describe("SummaryPanel", () => {
  it("shows the empty state and a disabled button when nothing is selected", () => {
    render(
      <SummaryPanel selectedSlot={null} isBooking={false} confirmedBooking={null} onConfirm={vi.fn()} />
    );

    expect(screen.getByText("Select a slot to continue.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /confirm appointment/i })).toBeDisabled();
  });

  it("enables the button and shows the selected slot's details", () => {
    render(
      <SummaryPanel selectedSlot={slot} isBooking={false} confirmedBooking={null} onConfirm={vi.fn()} />
    );

    expect(screen.getByRole("button", { name: /confirm appointment/i })).toBeEnabled();
    expect(screen.queryByText("Select a slot to continue.")).not.toBeInTheDocument();
  });

  it("shows 'Booking…' and disables the button while isBooking is true", () => {
    render(
      <SummaryPanel selectedSlot={slot} isBooking={true} confirmedBooking={null} onConfirm={vi.fn()} />
    );

    const button = screen.getByRole("button", { name: /booking/i });
    expect(button).toBeDisabled();
  });

  it("calls onConfirm when clicked", () => {
    const onConfirm = vi.fn();
    render(
      <SummaryPanel selectedSlot={slot} isBooking={false} confirmedBooking={null} onConfirm={onConfirm} />
    );

    fireEvent.click(screen.getByRole("button", { name: /confirm appointment/i }));

    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it("does not call onConfirm when clicked while disabled (nothing selected)", () => {
    const onConfirm = vi.fn();
    render(
      <SummaryPanel selectedSlot={null} isBooking={false} confirmedBooking={null} onConfirm={onConfirm} />
    );

    fireEvent.click(screen.getByRole("button", { name: /confirm appointment/i }));

    expect(onConfirm).not.toHaveBeenCalled();
  });

  it("shows the confirmation message once a booking succeeds", () => {
    render(
      <SummaryPanel selectedSlot={null} isBooking={false} confirmedBooking={booking} onConfirm={vi.fn()} />
    );

    expect(screen.getByText(/appointment confirmed with dr\. test/i)).toBeInTheDocument();
  });

  it("shows no confirmation message when confirmedBooking is null", () => {
    render(
      <SummaryPanel selectedSlot={null} isBooking={false} confirmedBooking={null} onConfirm={vi.fn()} />
    );

    expect(screen.queryByText(/appointment confirmed/i)).not.toBeInTheDocument();
  });
});
