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

const history = [
  {
    id: 1,
    file_name: "report.xlsx",
    status: "completed_with_errors",
    total_rows: 8,
    imported_rows: 7,
    failed_rows: 1,
    created_at: "2026-07-24T09:30:00",
    errors: [{ row: 4, field: "value", message: "Input should be a valid decimal" }],
  },
  {
    id: 2,
    file_name: "successful.csv",
    status: "completed",
    total_rows: 8,
    imported_rows: 8,
    failed_rows: 0,
    created_at: "2026-07-23T09:30:00",
    errors: [],
  },
  {
    id: 3,
    file_name: "broken.csv",
    status: "failed",
    total_rows: 0,
    imported_rows: 0,
    failed_rows: 1,
    created_at: "2026-07-22T09:30:00",
    errors: [{ row: 1, field: null, message: "Missing columns" }],
  },
];

function jsonResponse(body: object, ok = true) {
  return Promise.resolve({ ok, json: () => Promise.resolve(body) } as Response);
}

function successfulFetch() {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.includes("/metrics/dashboard/filters")) return jsonResponse(filters);
    if (url.includes("/metrics/dashboard?")) return jsonResponse(dashboard);
    if (url.includes("/measurements?")) {
      return jsonResponse([
        {
          id: 1,
          metric_key: "handled_cases",
          organizational_unit: "Service Nord",
          period_start: "2026-07-01",
          period_end: "2026-07-07",
          value: "110",
          target_value: "100",
          source: "report.xlsx",
        },
      ]);
    }
    if (url.includes("/comparison?")) {
      return jsonResponse({
        metric_key: "handled_cases",
        display_name: "Bearbeitete Vorgänge",
        unit: "Anzahl",
        entries: [{ ...dashboard.summaries[0], organizational_unit: "Service Nord" }],
      });
    }
    if (url.includes("/data/imports")) return jsonResponse(history);
    if (url.includes("/imports/file")) {
      return jsonResponse({ status: "completed", imported_rows: 8, failed_rows: 0 });
    }
    if (url.includes("/data/restore") || url.includes("/data/reset")) {
      return jsonResponse({ status: "completed", message: "done" });
    }
    return jsonResponse({}, Boolean(init));
  });
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("App", () => {
  it("loads dashboard, filters and understandable import history", async () => {
    const fetchMock = successfulFetch();
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    expect(screen.getByRole("heading", { name: "Leistung auf einen Blick." })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Zum Inhalt springen" })).toHaveAttribute(
      "href",
      "#main-content",
    );
    expect(
      await screen.findByRole("heading", { name: "Bearbeitete Vorgänge", level: 3 }),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Qualitätsquote", level: 3 })).toBeInTheDocument();
    expect(screen.getByText("ohne Ziel")).toBeInTheDocument();
    expect(screen.getByText("Mit Hinweisen")).toBeInTheDocument();
    expect(screen.getByText("Erfolgreich")).toBeInTheDocument();
    expect(screen.getByText("Fehlgeschlagen")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Entwicklung und Vergleich" })).toBeInTheDocument();
    expect(screen.getByText("Zeitverlauf · Service Nord")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Excel herunterladen" })).toHaveAttribute(
      "href",
      "/api/v1/data/export.xlsx",
    );
    expect(screen.getByRole("link", { name: "PDF herunterladen" })).toHaveAttribute(
      "href",
      expect.stringContaining("organizational_unit=Service+Nord"),
    );
    await userEvent.selectOptions(screen.getByLabelText("Kennzahl"), "quality");
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/metrics/quality/measurements?"),
      ),
    );
    await userEvent.click(screen.getAllByText("Fehler anzeigen")[0]);
    expect(screen.getByText(/Zeile 4 · value/)).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText("Organisationseinheit"), "Service Süd");
    fireEvent.change(screen.getByLabelText("Von"), { target: { value: "" } });
    await userEvent.click(screen.getByRole("button", { name: "Anwenden" }));
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("organizational_unit=Service+S%C3%BCd"),
      ),
    );
  });

  it("imports a file and reloads local data", async () => {
    const fetchMock = successfulFetch();
    vi.stubGlobal("fetch", fetchMock);
    const { container } = render(<App />);
    await screen.findByRole("heading", { name: "Bearbeitete Vorgänge", level: 3 });

    const input = container.querySelector('input[accept=".csv,.xlsx"]') as HTMLInputElement;
    fireEvent.change(input, {
      target: { files: [new File(["csv"], "data.csv", { type: "text/csv" })] },
    });

    expect(await screen.findByText("8 Zeilen importiert.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/imports/file",
      expect.objectContaining({ method: "POST" }),
    );

    fetchMock.mockImplementationOnce(() =>
      jsonResponse({ status: "completed_with_errors", imported_rows: 7, failed_rows: 1 }),
    );
    fireEvent.change(input, {
      target: { files: [new File(["csv"], "partial.csv", { type: "text/csv" })] },
    });
    expect(await screen.findByText("7 Zeilen importiert, 1 fehlerhaft.")).toBeInTheDocument();
  });

  it("restores a backup and protects reset with an exact confirmation", async () => {
    const fetchMock = successfulFetch();
    vi.stubGlobal("fetch", fetchMock);
    const prompt = vi
      .spyOn(window, "prompt")
      .mockReturnValueOnce("delete")
      .mockReturnValueOnce("DELETE");
    const { container } = render(<App />);
    await screen.findByRole("heading", { name: "Bearbeitete Vorgänge", level: 3 });

    const restoreInput = container.querySelector('input[accept=".db"]') as HTMLInputElement;
    fireEvent.change(restoreInput, {
      target: { files: [new File(["sqlite"], "backup.db")] },
    });
    expect(await screen.findByText("Backup wiederhergestellt.")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Lokal zurücksetzen" }));
    expect(screen.getByText(/Bestätigung war nicht DELETE/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Lokal zurücksetzen" }));
    expect(await screen.findByText("Alle lokalen Daten wurden gelöscht.")).toBeInTheDocument();
    expect(prompt).toHaveBeenCalledTimes(2);
  });

  it("shows loading failures and offers a retry", async () => {
    const fetchMock = successfulFetch();
    fetchMock.mockRejectedValueOnce(new Error("offline"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    expect(
      await screen.findByText("Daten konnten nicht geladen werden. Bitte Anwendung neu starten."),
    ).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Erneut versuchen" }));
    expect(
      await screen.findByRole("heading", { name: "Bearbeitete Vorgänge", level: 3 }),
    ).toBeInTheDocument();
  });

  it("handles a completely empty local database", async () => {
    const fetchMock = successfulFetch();
    fetchMock.mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/filters")) {
        return jsonResponse({ organizational_units: [], period_start: null, period_end: null });
      }
      if (url.includes("/data/imports")) return jsonResponse([]);
      return jsonResponse({ ...dashboard, summaries: [] });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    expect(await screen.findByText("Noch keine Kennzahlen vorhanden.")).toBeInTheDocument();
    expect(screen.getByText("Noch keine Importe vorhanden.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Anwenden" })).toBeDisabled();
  });

  it("shows API errors for imports and data management", async () => {
    const fetchMock = successfulFetch();
    fetchMock.mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (
        url.includes("/imports/file") ||
        url.includes("/data/restore") ||
        url.includes("/data/reset")
      ) {
        return jsonResponse({}, false);
      }
      if (url.includes("/metrics/dashboard/filters")) return jsonResponse(filters);
      if (url.includes("/metrics/dashboard?")) return jsonResponse(dashboard);
      if (url.includes("/data/imports")) return jsonResponse(history);
      return jsonResponse({});
    });
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(window, "prompt").mockReturnValue("DELETE");
    const { container } = render(<App />);
    await screen.findByRole("heading", { name: "Bearbeitete Vorgänge", level: 3 });

    fireEvent.change(container.querySelector('input[accept=".csv,.xlsx"]') as HTMLInputElement, {
      target: { files: [new File(["bad"], "bad.csv")] },
    });
    expect(
      await screen.findByText("Die Datei konnte nicht importiert werden."),
    ).toBeInTheDocument();

    fireEvent.change(container.querySelector('input[accept=".db"]') as HTMLInputElement, {
      target: { files: [new File(["bad"], "bad.db")] },
    });
    expect(
      await screen.findByText("Das Backup konnte nicht wiederhergestellt werden."),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Lokal zurücksetzen" }));
    expect(
      await screen.findByText("Die lokalen Daten konnten nicht zurückgesetzt werden."),
    ).toBeInTheDocument();
  });

  it("reports a failed drilldown request", async () => {
    const fetchMock = successfulFetch();
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    await screen.findByRole("heading", { name: "Bearbeitete Vorgänge", level: 3 });

    fetchMock.mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/metrics/quality/")) return jsonResponse({}, false);
      return successfulFetch()(input);
    });
    await userEvent.selectOptions(screen.getByLabelText("Kennzahl"), "quality");

    expect(
      await screen.findByText("Kennzahlanalyse konnte nicht geladen werden."),
    ).toBeInTheDocument();
  });

  it("shows an empty trend without failing the dashboard", async () => {
    const fetchMock = successfulFetch();
    fetchMock.mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/measurements?")) return jsonResponse([]);
      if (url.includes("/comparison?")) {
        return jsonResponse({
          metric_key: "handled_cases",
          display_name: "Bearbeitete Vorgänge",
          unit: "Anzahl",
          entries: [],
        });
      }
      return successfulFetch()(input);
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    expect(await screen.findByText("Keine Werte im gewählten Zeitraum.")).toBeInTheDocument();
  });

  it("allows cancelling destructive and file actions", async () => {
    vi.stubGlobal("fetch", successfulFetch());
    vi.spyOn(window, "prompt").mockReturnValue(null);
    const { container } = render(<App />);
    await screen.findByRole("heading", { name: "Bearbeitete Vorgänge", level: 3 });

    await userEvent.click(screen.getByRole("button", { name: "Lokal zurücksetzen" }));
    fireEvent.change(container.querySelector('input[accept=".db"]') as HTMLInputElement, {
      target: { files: [] },
    });
    expect(screen.queryByText("Alle lokalen Daten wurden gelöscht.")).not.toBeInTheDocument();
  });
});
