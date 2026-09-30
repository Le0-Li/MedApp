import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { AppointmentSlot } from "../types";
import { SlotButton } from "./SlotButton";

const slot: AppointmentSlot = { startsAt: "2099-01-01T10:00:00Z", availableDoctors: 2 };

describe("SlotButton", () => {
  it("shows how many doctors are available", () => {
    render(<SlotButton slot={slot} isSelected={false} onSelect={vi.fn()} />);

    expect(screen.getByText("2 doctors available")).toBeInTheDocument();
  });

  it("uses singular wording for exactly one doctor", () => {
    render(
      <SlotButton
        slot={{ ...slot, availableDoctors: 1 }}
        isSelected={false}
        onSelect={vi.fn()}
      />
    );

    expect(screen.getByText("1 doctor available")).toBeInTheDocument();
  });

  it("calls onSelect with the slot when clicked", () => {
    const onSelect = vi.fn();
    render(<SlotButton slot={slot} isSelected={false} onSelect={onSelect} />);

    fireEvent.click(screen.getByRole("button"));

    expect(onSelect).toHaveBeenCalledWith(slot);
  });

  it("applies the selected class when isSelected is true", () => {
    render(<SlotButton slot={slot} isSelected onSelect={vi.fn()} />);

    expect(screen.getByRole("button")).toHaveClass("selected");
  });

  it("does not apply the selected class when isSelected is false", () => {
    render(<SlotButton slot={slot} isSelected={false} onSelect={vi.fn()} />);

    expect(screen.getByRole("button")).not.toHaveClass("selected");
  });
});
