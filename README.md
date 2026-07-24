# Performance Cockpit

Performance Cockpit ist ein Projekt zur zentralen Erfassung, Aufbereitung und Darstellung relevanter Leistungskennzahlen. Ziel ist ein übersichtliches Cockpit, das operative und strategische Entscheidungen durch konsistente, nachvollziehbare Daten unterstützt.

> **Projektstatus:** Release 0.2 stellt das technische Fundament mit React, FastAPI, PostgreSQL, Docker Compose, Tests und Continuous Integration bereit.

## Technischer Stack

| Bereich | Technologie |
| --- | --- |
| Frontend | React 19, TypeScript 6 und Vite 8 |
| Backend | Python 3.12+ und FastAPI |
| Datenbank | PostgreSQL 17 |
| Tests | Vitest, Testing Library und pytest |
| Qualität | ESLint, Prettier und Ruff |
| Lokaler Betrieb | Docker Compose |
| CI | GitHub Actions |

## Projektstruktur

| Pfad | Zweck |
| --- | --- |
| `frontend/` | React-Anwendung, UI-Tests und Frontend-Konfiguration |
| `backend/` | FastAPI-Anwendung, Konfiguration, Logging und API-Tests |
| `data/` | Freigegebene Beispieldaten; produktive und sensible Daten werden nicht versioniert |
| `docs/` | Architektur, ADRs, Anforderungen und Roadmap |
| `scripts/` | Hilfs-, Entwicklungs- und Automatisierungsskripte |

## Schnellstart mit Docker

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

Aktueller Projektstand: **0.2**
