import { ChangeEvent, MouseEvent, useCallback, useEffect, useState } from "react";

type MetricSummary = {
  metric_key: string;
  display_name: string;
  unit: string;
  value: string;
  target_value: string | null;
  deviation: string | null;
  attainment_percent: string | null;
  measurement_count: number;
  organizational_unit?: string;
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

type ImportError = {
  row: number;
  field: string | null;
  message: string;
};

type ImportRecord = {
  id: number;
  file_name: string;
  status: "completed" | "completed_with_errors" | "failed";
  total_rows: number;
  imported_rows: number;
  failed_rows: number;
  created_at: string;
  errors: ImportError[];
};

type Measurement = {
  id: number;
  metric_key: string;
  organizational_unit: string;
  period_start: string;
  period_end: string;
  value: string;
  target_value: string | null;
  source: string;
};

type OrganizationComparison = {
  metric_key: string;
  display_name: string;
  unit: string;
  entries: MetricSummary[];
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

const demoHistory: ImportRecord[] = [
  {
    id: 1,
    file_name: "sample_kpi_measurements.csv",
    status: "completed",
    total_rows: 8,
    imported_rows: 8,
    failed_rows: 0,
    created_at: "2026-07-24T09:30:00",
    errors: [],
  },
];

const demoMeasurements: Measurement[] = [
  {
    id: 1,
    metric_key: "handled_cases",
    organizational_unit: "Service Nord",
    period_start: "2026-07-01",
    period_end: "2026-07-07",
    value: "110",
    target_value: "100",
    source: "sample_kpi_measurements.csv",
  },
  {
    id: 2,
    metric_key: "handled_cases",
    organizational_unit: "Service Nord",
    period_start: "2026-07-08",
    period_end: "2026-07-14",
    value: "95",
    target_value: "100",
    source: "sample_kpi_measurements.csv",
  },
];

const demoComparison: OrganizationComparison = {
  metric_key: "handled_cases",
  display_name: "Bearbeitete Vorgänge",
  unit: "Anzahl",
  entries: [
    demoDashboard.summaries[0],
    { ...demoDashboard.summaries[0], value: "175", attainment_percent: "87.50" },
  ].map((entry, index) => ({
    ...entry,
    organizational_unit: index === 0 ? "Service Nord" : "Service Süd",
  })) as MetricSummary[],
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
  const [history, setHistory] = useState<ImportRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [importMessage, setImportMessage] = useState("");
  const [importing, setImporting] = useState(false);
  const [managing, setManaging] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState("");
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [comparison, setComparison] = useState<OrganizationComparison | null>(null);

  const loadAnalytics = useCallback(
    async (metricKey: string, selectedUnit: string, from: string, to: string) => {
      setSelectedMetric(metricKey);
      if (!metricKey || !selectedUnit) {
        setMeasurements([]);
        setComparison(null);
        return;
      }
      if (DEMO_MODE) {
        setMeasurements(demoMeasurements);
        setComparison(demoComparison);
        return;
      }
      const params = new URLSearchParams();
      if (from) params.set("date_from", from);
      if (to) params.set("date_to", to);
      const trendParams = new URLSearchParams(params);
      trendParams.set("organizational_unit", selectedUnit);
      const [trendResponse, comparisonResponse] = await Promise.all([
        fetch(`${API_BASE}/metrics/${metricKey}/measurements?${trendParams}`),
        fetch(`${API_BASE}/metrics/${metricKey}/comparison?${params}`),
      ]);
      if (!trendResponse.ok || !comparisonResponse.ok) {
        throw new Error("Kennzahlanalyse konnte nicht geladen werden.");
      }
      setMeasurements((await trendResponse.json()) as Measurement[]);
      setComparison((await comparisonResponse.json()) as OrganizationComparison);
    },
    [],
  );

  const loadDashboard = useCallback(
    async (selectedUnit: string, from: string, to: string) => {
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
          await loadAnalytics(demoDashboard.summaries[0].metric_key, selectedUnit, from, to);
          return;
        }
        const params = new URLSearchParams({ organizational_unit: selectedUnit });
        if (from) params.set("date_from", from);
        if (to) params.set("date_to", to);
        const response = await fetch(`${API_BASE}/metrics/dashboard?${params}`);
        if (!response.ok) throw new Error("Dashboard konnte nicht geladen werden.");
        const data = (await response.json()) as DashboardData;
        setDashboard(data);
        const metricKey = data.summaries[0]?.metric_key ?? "";
        await loadAnalytics(metricKey, selectedUnit, from, to);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unbekannter Fehler");
      } finally {
        setLoading(false);
      }
    },
    [loadAnalytics],
  );

  const loadHistory = useCallback(async () => {
    if (DEMO_MODE) {
      setHistory(demoHistory);
      return;
    }
    const response = await fetch(`${API_BASE}/data/imports`);
    if (!response.ok) throw new Error("Importhistorie konnte nicht geladen werden.");
    setHistory((await response.json()) as ImportRecord[]);
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
      await Promise.all([
        loadDashboard(firstUnit, loadedFilters.period_start ?? "", loadedFilters.period_end ?? ""),
        loadHistory(),
      ]);
    } catch {
      setError("Daten konnten nicht geladen werden. Bitte Anwendung neu starten.");
      setLoading(false);
    }
  }, [loadDashboard, loadHistory]);

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

  function changeMetric(metricKey: string) {
    void loadAnalytics(metricKey, unit, dateFrom, dateTo).catch((analyticsError) => {
      setError(
        analyticsError instanceof Error
          ? analyticsError.message
          : "Kennzahlanalyse fehlgeschlagen.",
      );
    });
  }

  function handleLocalDownload(event: MouseEvent<HTMLAnchorElement>) {
    if (!DEMO_MODE) return;
    event.preventDefault();
    setImportMessage("Export und Backup sind in der lokalen Windows-Version verfügbar.");
  }

  async function handleRestore(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (DEMO_MODE) {
      setImportMessage("Die Wiederherstellung ist in der lokalen Windows-Version verfügbar.");
      return;
    }
    setManaging(true);
    setError("");
    try {
      const body = new FormData();
      body.append("file", file);
      const response = await fetch(`${API_BASE}/data/restore`, { method: "POST", body });
      if (!response.ok) throw new Error("Das Backup konnte nicht wiederhergestellt werden.");
      setImportMessage("Backup wiederhergestellt.");
      await loadFilters();
    } catch (restoreError) {
      setError(
        restoreError instanceof Error ? restoreError.message : "Wiederherstellung fehlgeschlagen.",
      );
    } finally {
      setManaging(false);
    }
  }

  async function handleReset() {
    if (DEMO_MODE) {
      setImportMessage("Das Zurücksetzen ist in der lokalen Windows-Version verfügbar.");
      return;
    }
    const confirmation = window.prompt(
      "Alle lokalen Kennzahlen und Importe werden gelöscht. Zum Bestätigen DELETE eingeben:",
    );
    if (confirmation === null) return;
    if (confirmation !== "DELETE") {
      setError("Zurücksetzen abgebrochen: Bestätigung war nicht DELETE.");
      return;
    }
    setManaging(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/data/reset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ confirmation }),
      });
      if (!response.ok) throw new Error("Die lokalen Daten konnten nicht zurückgesetzt werden.");
      setImportMessage("Alle lokalen Daten wurden gelöscht.");
      await loadFilters();
    } catch (resetError) {
      setError(resetError instanceof Error ? resetError.message : "Zurücksetzen fehlgeschlagen.");
    } finally {
      setManaging(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">PC</span>
          <div>
            <strong>Performance Cockpit</strong>
            <span>Release 0.7 · Berichte und Export</span>
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

        {dashboard?.summaries.length ? (
          <section className="analytics-section" aria-labelledby="analytics-heading">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Drilldown</p>
                <h2 id="analytics-heading">Entwicklung und Vergleich</h2>
              </div>
              <label className="metric-picker">
                Kennzahl
                <select
                  value={selectedMetric}
                  onChange={(event) => changeMetric(event.target.value)}
                >
                  {dashboard.summaries.map((metric) => (
                    <option value={metric.metric_key} key={metric.metric_key}>
                      {metric.display_name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="analytics-grid">
              <article className="analytics-card">
                <h3>Zeitverlauf · {unit}</h3>
                {measurements.length ? (
                  <div className="trend-chart" role="img" aria-label="Zeitverlauf der Messwerte">
                    {measurements.map((item) => {
                      const maximum = Math.max(
                        ...measurements.map((point) => Number(point.value)),
                        1,
                      );
                      return (
                        <div className="trend-column" key={item.id}>
                          <span
                            className="trend-bar"
                            style={{
                              height: `${Math.max((Number(item.value) / maximum) * 100, 4)}%`,
                            }}
                          />
                          <strong>
                            {new Intl.NumberFormat("de-DE").format(Number(item.value))}
                          </strong>
                          <small>{formatDate(item.period_end)}</small>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="analytics-empty">Keine Werte im gewählten Zeitraum.</p>
                )}
              </article>
              <article className="analytics-card">
                <h3>Organisationseinheiten</h3>
                <div className="comparison-list">
                  {(comparison?.entries ?? []).map((entry) => {
                    const maximum = Math.max(
                      ...(comparison?.entries ?? []).map((item) => Number(item.value)),
                      1,
                    );
                    return (
                      <div className="comparison-row" key={entry.organizational_unit}>
                        <div>
                          <strong>{entry.organizational_unit ?? "Unbekannt"}</strong>
                          <span>{formatNumber(entry.value, comparison?.unit ?? "")}</span>
                        </div>
                        <div className="comparison-track">
                          <span style={{ width: `${(Number(entry.value) / maximum) * 100}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </article>
            </div>
          </section>
        ) : null}

        <section className="management-section" aria-labelledby="management-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Lokale Datenverwaltung</p>
              <h2 id="management-heading">Deine Daten. Deine Kontrolle.</h2>
            </div>
          </div>
          <div className="management-grid">
            <article className="management-card">
              <span className="management-icon" aria-hidden="true">
                ↗
              </span>
              <h3>Daten exportieren</h3>
              <p>Alle Messwerte als CSV- oder formatierte Excel-Datei sichern.</p>
              <div className="download-links">
                <a href={`${API_BASE}/data/export.xlsx`} onClick={handleLocalDownload}>
                  Excel herunterladen
                </a>
                <a href={`${API_BASE}/data/export.csv`} onClick={handleLocalDownload}>
                  CSV herunterladen
                </a>
              </div>
            </article>
            <article className="management-card">
              <span className="management-icon" aria-hidden="true">
                ⎙
              </span>
              <h3>PDF-Bericht</h3>
              <p>Die aktuell gefilterten Kennzahlen als lokalen Bericht weitergeben.</p>
              <a
                href={`${API_BASE}/data/report.pdf?${new URLSearchParams({
                  organizational_unit: unit,
                  ...(dateFrom ? { date_from: dateFrom } : {}),
                  ...(dateTo ? { date_to: dateTo } : {}),
                })}`}
                onClick={handleLocalDownload}
              >
                PDF herunterladen
              </a>
            </article>
            <article className="management-card">
              <span className="management-icon" aria-hidden="true">
                ◫
              </span>
              <h3>Backup</h3>
              <p>Eine vollständige Kopie der lokalen Cockpit-Datenbank erstellen.</p>
              <a href={`${API_BASE}/data/backup`} onClick={handleLocalDownload}>
                Backup speichern
              </a>
            </article>
            <article className="management-card">
              <span className="management-icon" aria-hidden="true">
                ↻
              </span>
              <h3>Wiederherstellen</h3>
              <p>Ein geprüftes Performance-Cockpit-Backup lokal einspielen.</p>
              <label className={`text-action ${managing ? "disabled" : ""}`}>
                <input type="file" accept=".db" onChange={handleRestore} disabled={managing} />
                Backup auswählen
              </label>
            </article>
            <article className="management-card danger-card">
              <span className="management-icon" aria-hidden="true">
                ×
              </span>
              <h3>Daten zurücksetzen</h3>
              <p>Alle Kennzahlen und Importprotokolle nach Bestätigung löschen.</p>
              <button type="button" onClick={() => void handleReset()} disabled={managing}>
                Lokal zurücksetzen
              </button>
            </article>
          </div>
        </section>

        <section className="history-section" aria-labelledby="history-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Nachvollziehbarkeit</p>
              <h2 id="history-heading">Importhistorie</h2>
            </div>
            <span className="period">{history.length} Importe</span>
          </div>
          {history.length ? (
            <div className="history-list">
              {history.map((record) => (
                <article className="history-item" key={record.id}>
                  <div>
                    <strong>{record.file_name}</strong>
                    <span>
                      {new Intl.DateTimeFormat("de-DE", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      }).format(new Date(record.created_at))}
                    </span>
                  </div>
                  <div className="history-counts">
                    <span>{record.imported_rows} importiert</span>
                    <span className={record.failed_rows ? "failed" : ""}>
                      {record.failed_rows} fehlerhaft
                    </span>
                  </div>
                  <span className={`history-status ${record.status}`}>
                    {record.status === "completed"
                      ? "Erfolgreich"
                      : record.status === "failed"
                        ? "Fehlgeschlagen"
                        : "Mit Hinweisen"}
                  </span>
                  {record.errors.length > 0 && (
                    <details>
                      <summary>Fehler anzeigen</summary>
                      <ul>
                        {record.errors.map((item, index) => (
                          <li key={`${item.row}-${item.field}-${index}`}>
                            Zeile {item.row}
                            {item.field ? ` · ${item.field}` : ""}: {item.message}
                          </li>
                        ))}
                      </ul>
                    </details>
                  )}
                </article>
              ))}
            </div>
          ) : (
            <div className="state-card empty">
              <strong>Noch keine Importe vorhanden.</strong>
              <span>Neue Dateiimporte erscheinen automatisch an dieser Stelle.</span>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
