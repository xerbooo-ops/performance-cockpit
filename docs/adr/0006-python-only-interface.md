# ADR 0006: Python-only-Oberfläche

## Status

Akzeptiert – ersetzt die aktive Frontend-Entscheidung aus ADR 0001 für Release 1.0.3.

## Kontext

Der React-/TypeScript-Build erforderte Node.js, npm, Vite und TypeScript. Diese zusätzliche
Werkzeugkette verursachte fehlerhafte Actions-Builds und widersprach dem Ziel eines möglichst
einfach reproduzierbaren Standalone-Pakets.

## Entscheidung

FastAPI liefert das Dashboard als serverseitig erzeugtes HTML aus. Filter, Dateiimport,
Datensicherung und Zurücksetzen verwenden normale HTTP-Formulare. Styles sind im Python-Paket
enthalten. Die Oberfläche benötigt weder einen JavaScript-Build noch clientseitiges JavaScript.

GitHub Actions installieren ausschließlich Python. Die Windows-EXE bündelt Python-Anwendung,
Migrationen und SQLite-Zugriff direkt über PyInstaller. Die GitHub-Pages-Seite ist nur eine
statische Projektinformation, die mit einem Python-Skript erzeugt wird.

## Konsequenzen

- Ein einziger aktiver Technologie-Stack für Build und Anwendung
- Keine Abhängigkeit von Node.js, npm, Vite oder TypeScript
- Filterwechsel und Aktionen laden die Seite neu
- Die frühere React-Oberfläche bleibt vorerst als nicht gebauter Legacy-Quellstand erhalten
