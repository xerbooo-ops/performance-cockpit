# Performance Cockpit

Performance Cockpit ist ein Projekt zur zentralen Erfassung, Aufbereitung und Darstellung relevanter Leistungskennzahlen. Ziel ist ein übersichtliches Cockpit, das operative und strategische Entscheidungen durch konsistente, nachvollziehbare Daten unterstützt.

> **Projektstatus:** Release 1.0.4 überwacht eine ausgewählte lokale Reportdatei und importiert Änderungen automatisch.

## Öffentliche Vorschau

Eine mit Python erzeugte Projektseite wird bei Änderungen an `main` über GitHub Pages veröffentlicht:

<https://xerbooo-ops.github.io/performance-cockpit/>

Die Seite informiert über den Projektstand. Das produktive Dashboard einschließlich Datenimport und
Speicherung läuft ausschließlich in der lokalen Windows-Anwendung.

## Technischer Stack

| Bereich | Technologie |
| --- | --- |
| Oberfläche | Serverseitig erzeugtes HTML ohne JavaScript-Build |
| Anwendung | Python 3.12+ und FastAPI |
| Datenbank | SQLite (Standalone), PostgreSQL 17 (optionale Entwicklung) |
| Datenzugriff | SQLAlchemy und Alembic |
| Tests | pytest und FastAPI TestClient |
| Qualität | Ruff, pytest und Coverage |
| Lokaler Betrieb | Portable Windows-EXE; optional Docker Compose für Entwicklung |
| CI | GitHub Actions |

## Projektstruktur

| Pfad | Zweck |
| --- | --- |
| `frontend/` | Nicht mehr gebauter Legacy-Quellstand der früheren React-Oberfläche |
| `backend/` | FastAPI-Anwendung, Python-Oberfläche, Geschäftslogik und Tests |
| `data/` | Freigegebene Beispieldaten; produktive und sensible Daten werden nicht versioniert |
| `docs/` | Architektur, ADRs, Anforderungen und Roadmap |
| `scripts/` | Hilfs-, Entwicklungs- und Automatisierungsskripte |

## Windows ohne Installation

Der GitHub-Actions-Workflow `Build Windows standalone` erzeugt
`PerformanceCockpit_v1.0.4_Windows.zip` sowie `PerformanceCockpit_v1.0.4_Setup.exe`. Das portable Paket
wird entpackt; anschließend startet `PerformanceCockpit.exe` das Cockpit per Doppelklick.

Zur Laufzeit werden kein Docker, keine separate Python-Installation, Node.js, TypeScript,
PostgreSQL, Internetzugang, Cloud-Dienst oder externe API benötigt. Die Daten bleiben unter
`%LOCALAPPDATA%\PerformanceCockpit` auf dem Gerät.

## Optionaler Entwicklungsstart mit Docker

Voraussetzung ist eine aktuelle Docker-Installation mit Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

Anschließend sind erreichbar:

- Dashboard und Backend: <http://localhost:8000>
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

## Konfiguration

Die Anwendung wird über Umgebungsvariablen konfiguriert. `.env.example` enthält ausschließlich sichere Beispielwerte. Lokale `.env`-Dateien, Zugangsdaten und sensible Daten dürfen nicht eingecheckt werden.

Anwendungsvariablen tragen das Präfix `PERFORMANCE_COCKPIT_`.

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

Aktueller Projektstand: **1.0.4**

## Kurz-Changelog 1.0.4

- lokale Reportdatei einmalig über einen nativen Windows-Dateidialog auswählbar
- Dateiänderungen werden alle fünf Sekunden erkannt und automatisch importiert
- überwachte Datei bleibt über Anwendungsneustarts hinweg gespeichert
- Dashboard aktualisiert sich ohne JavaScript alle zehn Sekunden automatisch
- fehlerhafte Zwischenstände werden verworfen und erneut geprüft

## Kurz-Changelog 1.0.3

- Dashboard vollständig durch FastAPI und Python gerendert
- keine Node.js-, npm-, Vite- oder TypeScript-Schritte in CI und Windows-Build
- Filter, Import, Export, PDF, Backup und Zurücksetzen ohne clientseitiges JavaScript
- GitHub-Pages-Projektseite wird mit einem Python-Skript erzeugt

## Kurz-Changelog 1.0.2

- Teamleiter- und Mitarbeiternamen werden beim Excel-Import verworfen und nicht gespeichert
- individuelle Auswahl ausschließlich über die anonymisierte EPA-Kennung
- automatisch kumulierte Organisationseinheit Potsdam für alle Mitarbeiter
- Zielangaben aus Dashboard und PDF-Bericht entfernt

## Kurz-Changelog 1.0.1

- ursprünglicher Excel-Performance-Report direkt importierbar
- automatische Erkennung von Mitarbeiter- und Tagesübersichten
- KPI-Zuordnung für VVL, BNT, BBCR, TNPS, CS, AHT/CHT, ACW und weitere Reportwerte
- monatlicher AHT-/ACW-Verlauf aus dem Report
- robuste Behandlung leerer Zellen und Excel-Fehlerwerte

## Kurz-Changelog 1.0

- lokaler Windows-Installer zusätzlich zum portablen ZIP
- Systemdiagnose ohne Telemetrie oder sensible Daten
- Sicherheitsheader und verbesserte Tastaturbedienung
- Support- und Release-Dokumentation

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
