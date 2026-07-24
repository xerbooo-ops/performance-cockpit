const foundations = [
  { label: "Frontend", value: "React + TypeScript", status: "Bereit" },
  { label: "Backend", value: "FastAPI", status: "Bereit" },
  { label: "Datenbank", value: "PostgreSQL", status: "Vorbereitet" },
];

function App() {
  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Release 0.2</p>
        <h1>Performance Cockpit</h1>
        <p>
          Das technische Fundament steht. Kennzahlen und Datenimporte folgen mit dem nächsten
          Release.
        </p>
      </header>

      <section aria-labelledby="foundation-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Systemstatus</p>
            <h2 id="foundation-heading">Technisches Fundament</h2>
          </div>
          <span className="release-badge">0.2.0</span>
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
