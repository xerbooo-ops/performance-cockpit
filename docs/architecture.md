# Architektur

## Zweck

Dieses Dokument beschreibt die Architektur des Performance Cockpits ab Release 0.6. Die wesentlichen Technologieentscheidungen sind in den [Architecture Decision Records](adr/) dokumentiert.

## Architekturüberblick

Das System wird in klar getrennte Schichten gegliedert:

1. **Frontend** – React-Anwendung für Kennzahlen, Filter und Statusinformationen.
2. **Backend** – FastAPI-Anwendung mit versionierter HTTP-API und Geschäftslogik.
3. **Datenverarbeitung** – validiert und importiert CSV-Messwerte im Backend.
4. **Persistenz** – SQLite in der Standalone-Anwendung; PostgreSQL optional für Entwicklung.
5. **Lokale Quellen** – CSV- und XLSX-Dateien werden ohne externe Verbindung verarbeitet.

```mermaid
flowchart LR
    S[Lokale CSV/XLSX] --> P[Import und Validierung]
    P --> D[(SQLite)]
    D --> B[Gebündeltes Backend]
    B --> F[Lokales Cockpit]
```

## Komponenten

| Komponente | Verantwortung |
| --- | --- |
| React-Frontend | Darstellung, Navigation, Filterzustand und Aufruf der API |
| FastAPI-Backend | API-Verträge, Validierung, Geschäftslogik und Datenzugriff |
| SQLite | Eingebettete lokale Speicherung ohne separaten Datenbankdienst |
| SQLAlchemy und Alembic | Datenmodell, Datenzugriff und versionierte Migrationen |
| PyInstaller | Bündelung von Backend, Laufzeit und gebautem Frontend als Windows-EXE |
| Docker Compose | Optionale reproduzierbare Entwicklungsumgebung |
| GitHub Actions | Linting, Tests, Containerprüfung und Windows-Standalone-Build |

## Konfiguration und Logging

- Backend-Konfiguration wird typisiert über `pydantic-settings` geladen.
- Backend-Variablen verwenden das Präfix `PERFORMANCE_COCKPIT_`.
- Browserseitig sichtbare Variablen verwenden das Präfix `VITE_`.
- Strukturierte JSON-Logs werden mit `structlog` erzeugt.
- Geheimnisse werden ausschließlich zur Laufzeit bereitgestellt.
- `.env.example` dokumentiert sichere Beispielwerte; `.env` wird ignoriert.

## Schnittstellenprinzipien

- Das Frontend greift ausschließlich über die Backend-API auf Daten zu.
- Die API beginnt unter `/api/v1` und wird bei inkompatiblen Änderungen versioniert.
- Pydantic-Modelle definieren und dokumentieren Request- und Response-Verträge.
- Eingehende Daten werden vor der Verarbeitung validiert.
- Kennzahlberechnungen erfolgen zentral im Backend, nicht parallel im Frontend.
- Importfehler werden zeilen- und feldbezogen maschinenlesbar ausgegeben.

## Qualitätssicherung

| Bereich | Prüfungen |
| --- | --- |
| Backend | Ruff Linting, Ruff Formatcheck, pytest und Coverage-Schwelle |
| Frontend | ESLint, Prettier, TypeScript, Vitest und Produktions-Build |
| Integration | Docker-Compose-Konfiguration und Container-Build |

Die Continuous-Integration-Pipeline führt diese Prüfungen für Pull Requests und Änderungen an `main` aus.

## Sicherheits- und Datenschutzgrundsätze

- Geringstmögliche Berechtigungen für Dienste und Workflows
- Keine Secrets, Produktivdaten oder personenbezogenen Daten im Repository
- Nicht privilegierter Benutzer im Backend-Container
- Minimierte, versionierte API-Oberfläche
- Abhängigkeiten und Container werden regelmäßig aktualisiert

## Standalone-Betrieb

- Die Anwendung bindet nur an `127.0.0.1` und ist nicht aus dem Netzwerk erreichbar.
- Das gebaute React-Frontend wird vom lokalen FastAPI-Prozess ausgeliefert.
- Die Oberfläche öffnet sich beim Start automatisch im Standardbrowser.
- Daten liegen unter `%LOCALAPPDATA%\PerformanceCockpit`.
- Zur Laufzeit werden keine externen Dienste oder Internetressourcen aufgerufen.
- Alembic-Migrationen aktualisieren bestehende lokale Datenbanken beim Start.
- Export, Backup, Wiederherstellung und Zurücksetzen laufen ausschließlich auf dem Gerät.
- Backups werden vor einer Wiederherstellung auf Integrität und Cockpit-Tabellen geprüft.
