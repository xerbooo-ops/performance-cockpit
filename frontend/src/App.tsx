import { ChangeEvent, useCallback, useEffect, useState } from "react";

type MetricSummary = {
  metric_key: string;
  display_name: string;
  unit: string;
  value: string;
  target_value: string | null;
  deviation: string | null;
  attainment_percent: string | null;
  measurement_count: number;
};

type DashboardData = {
  organizational_unit: string;
  period_start: string | null;
  period_end: string | null;
  last_imported_at: string | null;
  source_files: string[];
  summaries: MetricSummary[];
};

type DashboardFilters = {
  organizational_units: string[];
  period_start: string | null;
  period_end: string | null;
};

type ImportResult = {
  status: "completed" | "completed_with_errors" | "failed";
  imported_rows: number;
  failed_rows: number;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";

const demoFilters: DashboardFilters = {
  organizational_units: ["Service Nord", "Service Süd"],
  period_start: "2026-07-01",
  period_end: "2026-07-14",
};

const demoDashboard: DashboardData = {
  organizational_unit: "Service Nord",
  period_start: "2026-07-01",
  period_end: "2026-07-14",
  last_imported_at: "2026-07-24T09:30:00",
  source_files: ["sample_kpi_measurements.csv"],
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
      metric_key: "quality_rate",
      display_name: "Qualitätsquote",
      unit: "Prozent",
      value: "92.25",
      target_value: "90.00",
      deviation: "2.25",
      attainment_percent: "102.50",
      measurement_count: 2,
    },
  ],
};

function formatNumber(value: string, unit: string) {
  return `${new Intl.NumberFormat("de-DE", { maximumFractionDigits: 2 }).format(Number(value))} ${
    unit === "Prozent" ? "%" : unit
  }`;
}

function formatDate(value: string | null) {
  return value ? new Intl.DateTimeFormat("de-DE").format(new Date(value)) : "–";
}

function App() {
  const [filters, setFilters] = useState<DashboardFilters | null>(null);
  const [unit, setUnit] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [importMessage, setImportMessage] = useState("");
  const [importing, setImporting] = useState(false);

  const loadDashboard = useCallback(async (selectedUnit: string, from: string, to: string) => {
    if (!selectedUnit) {
      setDashboard(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError("");
    try {
      if (DEMO_MODE) {
        setDashboard({ ...demoDashboard, organizational_unit: selectedUnit });
        return;
      }
      const params = new URLSearchParams({ organizational_unit: selectedUnit });
      if (from) params.set("date_from", from);
      if (to) params.set("date_to", to);
      const response = await fetch(`${API_BASE}/metrics/dashboard?${params}`);
      if (!response.ok) throw new Error("Dashboard konnte nicht geladen werden.");
      setDashboard((await response.json()) as DashboardData);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unbekannter Fehler");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadFilters = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const loadedFilters = DEMO_MODE
        ? demoFilters
        : ((await (
            await fetch(`${API_BASE}/metrics/dashboard/filters`)
          ).json()) as DashboardFilters);
      setFilters(loadedFilters);
      setDateFrom(loadedFilters.period_start ?? "");
      setDateTo(loadedFilters.period_end ?? "");
      const firstUnit = loadedFilters.organizational_units[0] ?? "";
      setUnit(firstUnit);
      await loadDashboard(
        firstUnit,
        loadedFilters.period_start ?? "",
        loadedFilters.period_end ?? "",
      );
    } catch {
      setError("Daten konnten nicht geladen werden. Bitte Anwendung neu starten.");
      setLoading(false);
    }
  }, [loadDashboard]);

  useEffect(() => {
    void loadFilters();
  }, [loadFilters]);

  async function handleImport(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (DEMO_MODE) {
      setImportMessage("Der Import ist in der lokalen Windows-Version verfügbar.");
      return;
    }
    setImporting(true);
    setImportMessage("");
    setError("");
    try {
      const body = new FormData();
      body.append("file", file);
      const response = await fetch(`${API_BASE}/imports/file`, { method: "POST", body });
      if (!response.ok) throw new Error("Die Datei konnte nicht importiert werden.");
      const result = (await response.json()) as ImportResult;
      setImportMessage(
        `${result.imported_rows} Zeilen importiert${
          result.failed_rows ? `, ${result.failed_rows} fehlerhaft` : ""
        }.`,
      );
      await loadFilters();
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : "Import fehlgeschlagen.");
    } finally {
      setImporting(false);
    }
  }

  function applyFilters() {
    void loadDashboard(unit, dateFrom, dateTo);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">PC</span>
          <div>
            <strong>Performance Cockpit</strong>
            <span>Release 0.4 · lokal & unabhängig</span>
          </div>
        </div>
        <label className={`import-button ${importing ? "disabled" : ""}`}>
          <input type="file" accept=".csv,.xlsx" onChange={handleImport} disabled={importing} />
          {importing ? "Import läuft …" : "Daten importieren"}
        </label>
      </header>

      <main>
        <section className="hero">
          <div>
            <p className="eyebrow">Cockpit MVP</p>
            <h1>Leistung auf einen Blick.</h1>
            <p className="hero-copy">
              Kennzahlen filtern, Zielerreichung prüfen und neue Excel- oder CSV-Daten direkt
              einlesen.
            </p>
          </div>
          <span className="local-badge">
            <span aria-hidden="true">●</span> vollständig lokal
          </span>
        </section>

        <section className="filter-panel" aria-label="Dashboard-Filter">
          <label>
            Organisationseinheit
            <select value={unit} onChange={(event) => setUnit(event.target.value)}>
              {(filters?.organizational_units ?? []).map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            Von
            <input
              type="date"
              value={dateFrom}
              onChange={(event) => setDateFrom(event.target.value)}
            />
          </label>
          <label>
            Bis
            <input type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
          </label>
          <button type="button" onClick={applyFilters} disabled={!unit || loading}>
            Anwenden
          </button>
        </section>

        {importMessage && <p className="notice success">{importMessage}</p>}
        {error && (
          <div className="notice error" role="alert">
            <span>{error}</span>
            <button type="button" onClick={() => void loadFilters()}>
              Erneut versuchen
            </button>
          </div>
        )}

        <section aria-labelledby="metrics-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Aktueller Stand</p>
              <h2 id="metrics-heading">{unit || "Noch keine Daten"}</h2>
            </div>
            {dashboard && (
              <span className="period">
                {formatDate(dashboard.period_start)} – {formatDate(dashboard.period_end)}
              </span>
            )}
          </div>

          {loading ? (
            <div className="state-card">Kennzahlen werden geladen …</div>
          ) : dashboard?.summaries.length ? (
            <div className="metric-grid">
              {dashboard.summaries.map((metric) => {
                const attainment = Number(metric.attainment_percent ?? 0);
                return (
                  <article className="metric-card" key={metric.metric_key}>
                    <div className="metric-title">
                      <h3>{metric.display_name}</h3>
                      <span className={attainment >= 100 ? "positive" : "warning"}>
                        {metric.attainment_percent
                          ? `${new Intl.NumberFormat("de-DE").format(attainment)} %`
                          : "ohne Ziel"}
                      </span>
                    </div>
                    <strong className="metric-value">
                      {formatNumber(metric.value, metric.unit)}
                    </strong>
                    <div className="progress" aria-label={`Zielerreichung ${attainment} Prozent`}>
                      <span style={{ width: `${Math.min(attainment, 100)}%` }} />
                    </div>
                    <dl>
                      <div>
                        <dt>Ziel</dt>
                        <dd>
                          {metric.target_value
                            ? formatNumber(metric.target_value, metric.unit)
                            : "Nicht definiert"}
                        </dd>
                      </div>
                      <div>
                        <dt>Messwerte</dt>
                        <dd>{metric.measurement_count}</dd>
                      </div>
                    </dl>
                  </article>
                );
              })}
            </div>
          ) : (
            <div className="state-card empty">
              <strong>Noch keine Kennzahlen vorhanden.</strong>
              <span>Importiere eine CSV- oder XLSX-Datei, um das Cockpit zu füllen.</span>
            </div>
          )}
        </section>

        {dashboard && (
          <footer className="data-status">
            <span>
              Zuletzt aktualisiert:{" "}
              {dashboard.last_imported_at
                ? new Intl.DateTimeFormat("de-DE", {
                    dateStyle: "medium",
                    timeStyle: "short",
                  }).format(new Date(dashboard.last_imported_at))
                : "–"}
            </span>
            <span>Quelle: {dashboard.source_files.join(", ") || "keine"}</span>
          </footer>
        )}
      </main>
    </div>
  );
}

export default App;
