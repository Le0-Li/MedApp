import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { AppointmentSlot } from "../types";
import { SlotGrid } from "./SlotGrid";

const slots: AppointmentSlot[] = [
  { startsAt: "2099-01-01T10:00:00Z", availableDoctors: 1 },
  { startsAt: "2099-01-01T10:30:00Z", availableDoctors: 2 },
  { startsAt: "2099-01-02T09:00:00Z", availableDoctors: 1 },
];

describe("SlotGrid", () => {
  it("groups slots that fall on the same calendar day together", () => {
    const { container } = render(
      <SlotGrid slots={slots} selectedSlot={null} onSelect={vi.fn()} />
    );

    // Fixture data spans two distinct UTC calendar days -> two day groups.
    expect(container.querySelectorAll(".day-group")).toHaveLength(2);
  });

  it("renders exactly one button per slot", () => {
    render(<SlotGrid slots={slots} selectedSlot={null} onSelect={vi.fn()} />);

    expect(screen.getAllByRole("button")).toHaveLength(3);
  });

  it("marks only the currently selected slot's button", () => {
    render(<SlotGrid slots={slots} selectedSlot={slots[1]} onSelect={vi.fn()} />);

    const selectedButtons = screen
      .getAllByRole("button")
      .filter((button) => button.className.includes("selected"));

    expect(selectedButtons).toHaveLength(1);
  });

  it("renders nothing when there are no slots", () => {
    const { container } = render(
      <SlotGrid slots={[]} selectedSlot={null} onSelect={vi.fn()} />
    );

    expect(container.querySelectorAll(".day-group")).toHaveLength(0);
  });
});
