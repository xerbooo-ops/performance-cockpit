const foundations = [
  { label: "Datenmodell", value: "Kennzahlen + Messwerte", status: "Bereit" },
  { label: "API", value: "Versioniert unter /api/v1", status: "Bereit" },
  { label: "Datenimport", value: "CSV mit Validierung", status: "Bereit" },
];

function App() {
  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Release 0.3</p>
        <h1>Performance Cockpit</h1>
        <p>
          Datenmodell, Kennzahlen-API und ein validierter CSV-Import bilden jetzt die fachliche
          Datenbasis.
        </p>
      </header>

      <section aria-labelledby="foundation-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Systemstatus</p>
            <h2 id="foundation-heading">Datenbasis und API</h2>
          </div>
          <span className="release-badge">0.3.0</span>
        </div>

        <div className="card-grid">
          {foundations.map((foundation) => (
            <article className="status-card" key={foundation.label}>
              <span className="status">{foundation.status}</span>
              <h3>{foundation.label}</h3>
              <p>{foundation.value}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
