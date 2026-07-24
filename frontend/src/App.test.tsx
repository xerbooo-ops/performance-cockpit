import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("shows the release and all foundation components", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Performance Cockpit" })).toBeInTheDocument();
    expect(screen.getByText("React + TypeScript")).toBeInTheDocument();
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
    expect(screen.getByText("PostgreSQL")).toBeInTheDocument();
  });
});
