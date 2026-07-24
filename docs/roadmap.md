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

**Status:** abgeschlossen

- Importhistorie und verständliche Fehleranzeige in der Oberfläche
- Lokale Sicherung und geprüfte Wiederherstellung
- CSV-Datenexport und Zurücksetzen mit Sicherheitsabfrage
- Schema-Migrationen für bestehende lokale Datenbanken
- Aktualisiertes portables Windows-ZIP-Paket

## Release 0.6 – Analyse und Drilldown

**Status:** abgeschlossen

- Zeitverlauf einer ausgewählten Kennzahl
- Vergleich aller Organisationseinheiten
- Kennzahl-Drilldown mit Zeitraumfilter
- Lokale Visualisierung ohne externe Bibliotheken oder Webzugriffe

## Release 0.7 – Berichte und Export

**Status:** abgeschlossen

- Formatierter Excel-Export aller Messwerte
- PDF-Bericht für Organisationseinheit und Filterzeitraum
- Direkte Downloads in der lokalen Oberfläche
- Vollständig lokale Berichtserzeugung ohne Cloud-Dienste

## Release 1.0 – Produktiver Start

**Status:** abgeschlossen

- Sicherheitsheader, Tastaturfokus und reduzierte Bewegung
- Lokale Systemdiagnose ohne Telemetrie oder Dateninhalte
- Supportdokumentation und reproduzierbare Release-Checkliste
- Portables ZIP und installierbares Windows-Setup
- Automatisierter Start- und Health-Check des Windows-Builds
- Weiterhin vollständig lokaler Betrieb ohne Laufzeitinstallationen

Vor einer breiten organisatorischen Verteilung bleiben ein Pilot auf den konkret eingesetzten
Windows-10-/11-Systemen und – sobald ein Zertifikat vorliegt – die digitale Signatur empfohlen.

## Release 1.0.1 – Excel-Kompatibilität

**Status:** abgeschlossen

- Ursprünglichen Performance-Report im Breitformat automatisch erkennen
- Kopfzeilen außerhalb der ersten Tabellenzeile verarbeiten
- Mitarbeiterdaten oder ersatzweise Tageszusammenfassung importieren
- Prozentformate korrekt in Dashboardwerte umrechnen
- Monatlichen AHT-/ACW-Verlauf übernehmen
- Leere Zellen und Excel-Fehlerwerte sicher überspringen

## Release 1.0.2 – EPA-Anonymisierung

**Status:** abgeschlossen

- Teamleiter- und Mitarbeiternamen beim Reportimport vollständig verwerfen
- Individuelle Kennzahlen ausschließlich über EPA auswählbar machen
- `Potsdam` als kumulierte Gesamteinheit aller Mitarbeiter berechnen
- Anzahl-KPI summieren und Quoten-, Punkte- sowie Zeit-KPI mitteln
- Zielangaben aus Dashboard und PDF-Bericht entfernen

## Übergreifende Leitlinien

Für jedes Release gelten:

- Kennzahlen und Akzeptanzkriterien vor der Umsetzung definieren
- Automatisierte Tests für neue Fachlogik ergänzen
- Datenschutz und Informationssicherheit frühzeitig berücksichtigen
- Dokumentation gemeinsam mit der Implementierung aktualisieren
- Feedback und technische Risiken transparent festhalten
