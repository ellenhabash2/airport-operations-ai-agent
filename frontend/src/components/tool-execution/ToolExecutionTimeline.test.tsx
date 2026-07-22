import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ToolExecutionTimeline from "./ToolExecutionTimeline";

describe("ToolExecutionTimeline", () => {
  it("renders ordered success and failure steps and hides secrets", () => {
    render(<ToolExecutionTimeline toolCalls={[{ tool: "get_flight_by_number", arguments: { flight_number: "SB2101", api_key: "secret-value" }, failed: false }, { tool: "get_available_gates", arguments: {}, failed: true, error: "Unavailable" }]} />);
    const statuses = screen.getAllByRole("status");
    expect(statuses[0]).toHaveTextContent("Get flight by number");
    expect(statuses[1]).toHaveTextContent("Find available gates");
    expect(screen.getByText("Unavailable")).toBeVisible();
    expect(screen.queryByText(/secret-value/)).not.toBeInTheDocument();
  });

  it("collapses long tool chains by default and can expand", () => {
    render(<ToolExecutionTimeline toolCalls={[1, 2, 3].map((index) => ({ tool: `tool_${index}`, arguments: {}, failed: false }))} />);
    const details = screen.getByText("Operational tools").closest("details");
    expect(details).not.toHaveAttribute("open");
    fireEvent.click(screen.getByText("Operational tools"));
    expect(details).toHaveAttribute("open");
  });

  it("renders nothing when tool calls are missing", () => {
    const { container } = render(<ToolExecutionTimeline />);
    expect(container).toBeEmptyDOMElement();
  });
});
