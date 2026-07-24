from pathlib import Path

OUTPUT = Path("release/pages/index.html")

HTML = """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Performance Cockpit</title>
  <style>
    :root { font-family: "Segoe UI", sans-serif; color: #17352d; background: #f4f7f5; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; }
    main { width: min(760px, 88vw); padding: 3rem; background: white; border-radius: 24px;
      box-shadow: 0 20px 60px #17352d1a; }
    span { color: #176c53; font-weight: 700; }
    h1 { font-size: clamp(2.5rem, 8vw, 5rem); margin: .4rem 0; letter-spacing: -.05em; }
    p { font-size: 1.1rem; line-height: 1.6; }
    a { display: inline-block; margin-top: 1rem; padding: .8rem 1rem; border-radius: 10px;
      color: white; background: #176c53; text-decoration: none; font-weight: 700; }
  </style>
</head>
<body>
  <main>
    <span>Performance Cockpit · Python-only</span>
    <h1>Vollständig lokal.</h1>
    <p>Das produktive Dashboard läuft als eigenständige Windows-Anwendung mit FastAPI und SQLite.
    Es benötigt weder Node.js noch TypeScript, Docker, Internetzugang oder externe Dienste.</p>
    <p>Aus Datenschutzgründen verarbeitet die Anwendung Mitarbeiterdaten ausschließlich über EPA
    und bildet zusätzlich die kumulierte Organisationseinheit Potsdam.</p>
    <a href="https://github.com/xerbooo-ops/performance-cockpit">Zum Repository</a>
  </main>
</body>
</html>
"""


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(HTML, encoding="utf-8")


if __name__ == "__main__":
    main()
