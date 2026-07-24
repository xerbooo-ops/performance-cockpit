# Performance Cockpit

Performance Cockpit ist ein Projekt zur zentralen Erfassung, Aufbereitung und Darstellung relevanter Leistungskennzahlen. Ziel ist ein übersichtliches Cockpit, das operative und strategische Entscheidungen durch konsistente, nachvollziehbare Daten unterstützt.

> **Projektstatus:** Release 0.7 ergänzt formatierte Excel-Exporte und lokale PDF-Berichte.

## Öffentliche Vorschau

Das Frontend wird bei Änderungen an `main` automatisch über GitHub Pages veröffentlicht:

<https://xerbooo-ops.github.io/performance-cockpit/>

Die Vorschau zeigt Release 0.7 mit Demodaten. Datenimport und Speicherung erfolgen ausschließlich in
der lokalen Windows-Anwendung.

## Technischer Stack

| Bereich | Technologie |
| --- | --- |
| Frontend | React 19, TypeScript 6 und Vite 8 |
| Backend | Python 3.12+ und FastAPI |
| Datenbank | SQLite (Standalone), PostgreSQL 17 (optionale Entwicklung) |
| Datenzugriff | SQLAlchemy und Alembic |
| Tests | Vitest, Testing Library und pytest |
| Qualität | ESLint, Prettier und Ruff |
| Lokaler Betrieb | Portable Windows-EXE; optional Docker Compose für Entwicklung |
| CI | GitHub Actions |

## Projektstruktur

| Pfad | Zweck |
| --- | --- |
| `frontend/` | React-Anwendung, UI-Tests und Frontend-Konfiguration |
| `backend/` | FastAPI-Anwendung, Konfiguration, Logging und API-Tests |
| `data/` | Freigegebene Beispieldaten; produktive und sensible Daten werden nicht versioniert |
| `docs/` | Architektur, ADRs, Anforderungen und Roadmap |
| `scripts/` | Hilfs-, Entwicklungs- und Automatisierungsskripte |

## Windows ohne Installation

Der GitHub-Actions-Workflow `Build Windows standalone` erzeugt
`PerformanceCockpit_v0.7_Windows.zip`. Nach dem Entpacken startet
`PerformanceCockpit.exe` das Cockpit per Doppelklick.

Zur Laufzeit werden kein Docker, Python, Node.js, PostgreSQL, Internetzugang, Cloud-Dienst oder
externe API benötigt. Die Daten bleiben unter `%LOCALAPPDATA%\PerformanceCockpit` auf dem Gerät.

## Optionaler Entwicklungsstart mit Docker

Voraussetzung ist eine aktuelle Docker-Installation mit Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

Anschließend sind erreichbar:

- Frontend: <http://localhost:5173>
- Backend: <http://localhost:8000>
- API-Dokumentation: <http://localhost:8000/docs>
- Health-Endpunkt: <http://localhost:8000/api/v1/health>

Beim Start führt das Backend ausstehende Datenbankmigrationen automatisch aus.

Beispieldaten importieren:

```bash
curl -X POST http://localhost:8000/api/v1/imports/csv \
  -F "file=@data/sample_kpi_measurements.csv"
```

Beenden:

```bash
docker compose down
```

## Entwicklung ohne Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
alembic upgrade head
uvicorn performance_cockpit.main:app --reload
```

Qualitätsprüfungen:

```bash
ruff check .
ruff format --check .
pytest
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

Qualitätsprüfungen:

```bash
npm run lint
npm run format:check
npm run typecheck
npm run test
npm run build
```

## Konfiguration

Die Anwendung wird über Umgebungsvariablen konfiguriert. `.env.example` enthält ausschließlich sichere Beispielwerte. Lokale `.env`-Dateien, Zugangsdaten und sensible Daten dürfen nicht eingecheckt werden.

Backend-Variablen tragen das Präfix `PERFORMANCE_COCKPIT_`. Frontend-Variablen, die im Browser verfügbar sein dürfen, tragen das Präfix `VITE_`.

## Dokumentation

- [Architektur](docs/architecture.md)
- [Datenmodell](docs/data-model.md)
- [API](docs/api.md)
- [CSV-Import](docs/csv-import.md)
- [Windows-Standalone](docs/windows-standalone.md)
- [Anforderungen und Kennzahlen](docs/requirements.md)
- [Roadmap](docs/roadmap.md)
- [Architecture Decision Records](docs/adr/)

## Entwicklungsprinzipien

- Klare Trennung von Benutzeroberfläche, Geschäftslogik und Datenzugriff
- Nachvollziehbare Datenherkunft und Kennzahlendefinitionen
- Kleine, überprüfbare Änderungen
- Automatisierte Tests und reproduzierbare Builds
- Keine Geheimnisse oder personenbezogenen Daten im Repository

## Mitwirken

Änderungen sollten auf einem eigenen Branch entwickelt, geprüft und über einen Pull Request eingebracht werden. Architekturentscheidungen und neue Kennzahlen sind gemeinsam mit der Implementierung zu dokumentieren.

## Version

Aktueller Projektstand: **0.7**

## Kurz-Changelog 0.7

- formatierter XLSX-Export aller Messwerte
- lokaler PDF-Bericht für die aktive Auswahl
- Downloads direkt aus dem Cockpit

## Kurz-Changelog 0.6

- Zeitverläufe für die ausgewählte Kennzahl
- Vergleich der Organisationseinheiten im Filterzeitraum
- Lokale Drilldown-Ansicht ohne externe Diagrammdienste

## Kurz-Changelog 0.5

- Importhistorie mit verständlichen Zeilen- und Feldfehlern
- lokaler CSV-Gesamtexport
- vollständiges SQLite-Backup und geprüfte Wiederherstellung
- geschütztes Zurücksetzen aller lokalen Daten
- automatische Migration bestehender Release-0.4-Datenbanken
