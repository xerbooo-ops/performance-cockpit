import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const filters = {
  organizational_units: ["Service Nord", "Service Süd"],
  period_start: "2026-07-01",
  period_end: "2026-07-14",
};

const dashboard = {
  organizational_unit: "Service Nord",
  period_start: "2026-07-01",
  period_end: "2026-07-14",
  last_imported_at: "2026-07-24T09:30:00",
  source_files: ["report.xlsx"],
  summaries: [
    {
      metric_key: "handled_cases",
      display_name: "Bearbeitete Vorgänge",
      unit: "Anzahl",
      value: "205.00",
      target_value: "200.00",
      deviation: "5.00",
      attainment_percent: "102.50",
      measurement_count: 2,
    },
    {
      metric_key: "quality",
      display_name: "Qualitätsquote",
      unit: "Prozent",
      value: "85.00",
      target_value: null,
      deviation: null,
      attainment_percent: null,
      measurement_count: 1,
    },
  ],
};

function jsonResponse(body: object, ok = true) {
  return Promise.resolve({ ok, json: () => Promise.resolve(body) } as Response);
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("App", () => {
  it("loads the dashboard and applies changed filters", async () => {
    const fetchMock = vi
      .fn()
      .mockImplementationOnce(() => jsonResponse(filters))
      .mockImplementation(() => jsonResponse(dashboard));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    expect(screen.getByRole("heading", { name: "Leistung auf einen Blick." })).toBeInTheDocument();
    expect(await screen.findByText("Bearbeitete Vorgänge")).toBeInTheDocument();
    expect(screen.getByText("Qualitätsquote")).toBeInTheDocument();
    expect(screen.getByText("ohne Ziel")).toBeInTheDocument();
    expect(screen.getByText("report.xlsx", { exact: false })).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText("Organisationseinheit"), "Service Süd");
    await userEvent.click(screen.getByRole("button", { name: "Anwenden" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenLastCalledWith(
        expect.stringContaining("organizational_unit=Service+S%C3%BCd"),
      ),
    );
  });

  it("imports an Excel file and reloads the filters", async () => {
    const fetchMock = vi
      .fn()
      .mockImplementationOnce(() => jsonResponse(filters))
      .mockImplementationOnce(() => jsonResponse(dashboard))
      .mockImplementationOnce(() =>
        jsonResponse({ status: "completed_with_errors", imported_rows: 7, failed_rows: 1 }),
      )
      .mockImplementationOnce(() => jsonResponse(filters))
      .mockImplementationOnce(() => jsonResponse(dashboard));
    vi.stubGlobal("fetch", fetchMock);
    const { container } = render(<App />);
    await screen.findByText("Bearbeitete Vorgänge");

    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["workbook"], "report.xlsx", {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    fireEvent.change(input, { target: { files: [file] } });

    expect(await screen.findByText("7 Zeilen importiert, 1 fehlerhaft.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/imports/file",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("shows loading failures and offers a retry", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new Error("offline"))
      .mockImplementationOnce(() => jsonResponse(filters))
      .mockImplementation(() => jsonResponse({ ...dashboard, summaries: [] }));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    expect(
      await screen.findByText("Daten konnten nicht geladen werden. Bitte Anwendung neu starten."),
    ).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Erneut versuchen" }));
    expect(await screen.findByText("Noch keine Kennzahlen vorhanden.")).toBeInTheDocument();
  });

  it("handles an empty local database", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => jsonResponse({ organizational_units: [], period_start: null, period_end: null })),
    );
    render(<App />);

    expect(await screen.findByText("Noch keine Kennzahlen vorhanden.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Anwenden" })).toBeDisabled();
  });

  it("shows dashboard and import API errors", async () => {
    const fetchMock = vi
      .fn()
      .mockImplementationOnce(() => jsonResponse(filters))
      .mockImplementationOnce(() => jsonResponse({}, false))
      .mockImplementationOnce(() => jsonResponse({}, false));
    vi.stubGlobal("fetch", fetchMock);
    const { container } = render(<App />);

    expect(await screen.findByText("Dashboard konnte nicht geladen werden.")).toBeInTheDocument();
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, {
      target: { files: [new File(["bad"], "bad.csv", { type: "text/csv" })] },
    });
    expect(
      await screen.findByText("Die Datei konnte nicht importiert werden."),
    ).toBeInTheDocument();
  });

  it("reports an import without row errors", async () => {
    const fetchMock = vi
      .fn()
      .mockImplementationOnce(() => jsonResponse(filters))
      .mockImplementationOnce(() => jsonResponse(dashboard))
      .mockImplementationOnce(() =>
        jsonResponse({ status: "completed", imported_rows: 8, failed_rows: 0 }),
      )
      .mockImplementationOnce(() => jsonResponse(filters))
      .mockImplementationOnce(() => jsonResponse(dashboard));
    vi.stubGlobal("fetch", fetchMock);
    const { container } = render(<App />);
    await screen.findByText("Bearbeitete Vorgänge");

    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, {
      target: { files: [new File(["csv"], "data.csv", { type: "text/csv" })] },
    });

    expect(await screen.findByText("8 Zeilen importiert.")).toBeInTheDocument();
  });
});
