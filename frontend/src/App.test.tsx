import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("shows the data foundation for release 0.3", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Performance Cockpit" })).toBeInTheDocument();
    expect(screen.getByText("Kennzahlen + Messwerte")).toBeInTheDocument();
    expect(screen.getByText("Versioniert unter /api/v1")).toBeInTheDocument();
    expect(screen.getByText("CSV mit Validierung")).toBeInTheDocument();
  });
});
