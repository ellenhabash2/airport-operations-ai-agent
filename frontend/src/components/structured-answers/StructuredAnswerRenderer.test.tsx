import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import StructuredAnswerRenderer from "./StructuredAnswerRenderer";

const flight = {
  id: 18, flight_number: "SB2101", airline_name: "SkyBridge Airways", status: "scheduled",
  origin: "SFO", destination: "AMI", departure_time: "2026-06-18T12:06:00Z",
  arrival_time: "2026-06-18T18:52:00Z", terminal: "A", gate_number: "A03",
  runway_code: "08L/26R", aircraft_type: "Airbus A321neo", aircraft_registration: "N202AM",
};

describe("StructuredAnswerRenderer", () => {
  it("renders verified flight status fields and UTC times", () => {
    render(<StructuredAnswerRenderer presentation={{ type: "flight_status", data: flight }} />);
    expect(screen.getByRole("heading", { name: "SB2101" })).toBeVisible();
    expect(screen.getByText("SkyBridge Airways")).toBeVisible();
    expect(screen.getByText("18 Jun 2026, 12:06 UTC")).toBeVisible();
    expect(screen.getByText("Airbus A321neo · N202AM")).toBeVisible();
  });

  it("uses safe missing-value fallbacks", () => {
    render(<StructuredAnswerRenderer presentation={{ type: "flight_status", data: { ...flight, gate_number: null, runway_code: null, aircraft_type: null } }} />);
    expect(screen.getAllByText("Not assigned")).toHaveLength(2);
    expect(screen.getByText(/Not available/)).toBeVisible();
    expect(screen.queryByText(/null|undefined|Invalid Date|NaN/)).not.toBeInTheDocument();
  });

  it("falls back silently for an unknown presentation type", () => {
    const { container } = render(<StructuredAnswerRenderer presentation={{ type: "future_type", data: { value: 1 } }} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders flight lists in source order and supports selection", () => {
    const onOpenFlight = vi.fn();
    render(<StructuredAnswerRenderer presentation={{ type: "flight_list", data: { flights: [flight, { ...flight, id: 19, flight_number: "SB2102" }] } }} onOpenFlight={onOpenFlight} />);
    const rows = screen.getAllByRole("button");
    expect(rows[0]).toHaveTextContent("SB2101");
    expect(rows[1]).toHaveTextContent("SB2102");
    fireEvent.click(rows[0]);
    expect(onOpenFlight).toHaveBeenCalledWith(expect.objectContaining({ id: 18 }));
  });

  it.each([
    ["success", "Assignment completed in A."],
    ["failed", "The gate assignment could not be completed."],
  ])("renders a %s gate assignment", (status, expected) => {
    render(<StructuredAnswerRenderer presentation={{ type: "gate_assignment", data: { flight_number: "SB2101", previous_gate: "A01", new_gate: "A03", terminal: "A", status } }} />);
    expect(screen.getByText(expected)).toBeVisible();
  });

  it("renders runway status lists", () => {
    render(<StructuredAnswerRenderer presentation={{ type: "runway_status", data: { runways: [{ runway_code: "08L/26R", status: "closed", closure_reason: "Inspection" }] } }} />);
    expect(screen.getByText("08L/26R")).toBeVisible();
    expect(screen.getByText("Closed")).toBeVisible();
    expect(screen.getByText("Inspection")).toBeVisible();
  });
});
