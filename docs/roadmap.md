# Roadmap

Die Roadmap beschreibt die geplante Entwicklung des Performance Cockpits. Inhalte und Prioritäten werden anhand des fachlichen Feedbacks fortlaufend überprüft.

## Release 0.1 – Initiale Projektstruktur

**Status:** abgeschlossen

- Grundlegende Verzeichnisstruktur
- README, `.gitignore`, Architektur und Roadmap

## Release 0.2 – Technisches Fundament

**Status:** abgeschlossen

- Fachliche Kernanforderungen und erste Kennzahlen priorisiert
- Technologieentscheidungen als Architecture Decision Records dokumentiert
- React-Frontend und FastAPI-Backend initialisiert
- PostgreSQL und Docker Compose vorbereitet
- Typisierte Konfiguration und strukturierte Logs umgesetzt
- Linting, Formatierung und automatisierte Tests eingerichtet
- Continuous Integration für Prüfungen und Builds ergänzt

## Release 0.3 – Datenbasis und API

**Status:** abgeschlossen

- Relationales Datenmodell für Kennzahlen, Messwerte und Importprotokolle
- Alembic-Migrationen und automatische Migration beim Containerstart
- Idempotenter CSV-Import über API und Kommandozeile
- Zeilen- und feldbezogene Validierungsberichte
- Versionierte API für Definitionen, Messwerte und Zusammenfassungen
- Dokumentierte Beispiel- und Testdaten
- Tests für Import, Aktualisierung, Filter und Kennzahlberechnung

## Release 0.4 – Cockpit MVP

**Status:** abgeschlossen

- Dashboard mit Kernkennzahlen, Filtern und Zeiträumen
- Lade-, Leer- und Fehlerzustände
- Sichtbare Datenaktualität und Datenquelle
- CSV- und Excel-Import direkt in der Oberfläche
- Lokale SQLite-Standarddatenbank
- Portable Windows-EXE mit gebündeltem Frontend und Backend
- Automatisierter Windows-Build mit Starttest und ZIP-Paket

## Release 0.5 – Lokale Datenverwaltung

**Status:** geplant

- Importhistorie und verständliche Fehleranzeige in der Oberfläche
- Lokale Sicherung und Wiederherstellung
- Datenexport und Zurücksetzen mit Sicherheitsabfrage
- Schema-Migrationen für bestehende lokale Datenbanken
- Signierter Windows-Installer zusätzlich zur portablen EXE

## Release 1.0 – Produktiver Start

**Status:** geplant

- Abnahmekriterien und nichtfunktionale Anforderungen erfüllen
- Barrierefreiheit, Performance und Sicherheit prüfen
- Betriebs- und Supportdokumentation abschließen
- Pilotbetrieb auf Windows 10/11 durchführen und Erkenntnisse einarbeiten
- Produktionsfreigabe und Release-Prozess etablieren

## Übergreifende Leitlinien

Für jedes Release gelten:

- Kennzahlen und Akzeptanzkriterien vor der Umsetzung definieren
- Automatisierte Tests für neue Fachlogik ergänzen
- Datenschutz und Informationssicherheit frühzeitig berücksichtigen
- Dokumentation gemeinsam mit der Implementierung aktualisieren
- Feedback und technische Risiken transparent festhalten
