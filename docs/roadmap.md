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

**Status:** geplant

- Erstes Datenmodell definieren
- Datenbankmigrationen einführen
- Import für eine priorisierte Datenquelle implementieren
- Datenvalidierung und verständliche Fehlerberichte ergänzen
- Versionierte API für Kennzahlen bereitstellen
- Beispiel- und Testdaten dokumentieren
- Tests für Import und Kennzahlberechnung erstellen

## Release 0.4 – Cockpit MVP

**Status:** geplant

- Dashboard-Grundlayout umsetzen
- Kernkennzahlen, Filter und Zeiträume darstellen
- Lade-, Leer- und Fehlerzustände gestalten
- Datenaktualität und Datenquelle sichtbar machen
- Nutzerfeedback zum MVP erheben und priorisieren

## Release 0.5 – Sicherheit und Betrieb

**Status:** geplant

- Authentifizierung und rollenbasierte Berechtigungen umsetzen
- Datenschutz- und Aufbewahrungskonzept dokumentieren
- Monitoring, strukturierte Logs und Alarmierung ergänzen
- Backup- und Wiederherstellungsprozess definieren
- Deployment für eine Testumgebung automatisieren

## Release 1.0 – Produktiver Start

**Status:** geplant

- Abnahmekriterien und nichtfunktionale Anforderungen erfüllen
- Barrierefreiheit, Performance und Sicherheit prüfen
- Betriebs- und Supportdokumentation abschließen
- Pilotbetrieb durchführen und Erkenntnisse einarbeiten
- Produktionsfreigabe und Release-Prozess etablieren

## Übergreifende Leitlinien

Für jedes Release gelten:

- Kennzahlen und Akzeptanzkriterien vor der Umsetzung definieren
- Automatisierte Tests für neue Fachlogik ergänzen
- Datenschutz und Informationssicherheit frühzeitig berücksichtigen
- Dokumentation gemeinsam mit der Implementierung aktualisieren
- Feedback und technische Risiken transparent festhalten
