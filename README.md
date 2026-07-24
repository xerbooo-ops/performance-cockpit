# Performance Cockpit

Performance Cockpit ist ein Projekt zur zentralen Erfassung, Aufbereitung und Darstellung relevanter Leistungskennzahlen. Ziel ist ein übersichtliches Cockpit, das operative und strategische Entscheidungen durch konsistente, nachvollziehbare Daten unterstützt.

> **Projektstatus:** Release 0.1 schafft die initiale Projektstruktur. Fachliche Funktionen und die konkrete Technologieauswahl folgen in späteren Releases.

## Ziele

- Kennzahlen aus unterschiedlichen Quellen zentral zusammenführen
- Daten automatisiert validieren und aufbereiten
- Entwicklungen, Zielerreichung und Abweichungen verständlich visualisieren
- Eine wartbare Grundlage für zukünftige Integrationen und Erweiterungen schaffen

## Projektstruktur

| Pfad | Zweck |
| --- | --- |
| `frontend/` | Benutzeroberfläche und Visualisierung |
| `backend/` | API, Geschäftslogik und Datenverarbeitung |
| `data/` | Lokale Beispieldaten; produktive und sensible Daten werden nicht versioniert |
| `docs/` | Architektur, Roadmap und weitere Projektdokumentation |
| `scripts/` | Hilfs-, Entwicklungs- und Automatisierungsskripte |

## Dokumentation

- [Architektur](docs/architecture.md)
- [Roadmap](docs/roadmap.md)

## Lokale Entwicklung

Die konkreten Installations-, Start- und Testbefehle werden ergänzt, sobald der technische Stack für Frontend und Backend festgelegt ist.

Allgemeiner Ablauf:

1. Repository klonen.
2. Abhängigkeiten für Frontend und Backend installieren.
3. Lokale Konfiguration über Umgebungsvariablen anlegen.
4. Backend und Frontend im Entwicklungsmodus starten.
5. Tests und Qualitätsprüfungen ausführen.

Lokale Konfigurationsdateien, Zugangsdaten und sensible Daten dürfen nicht in das Repository eingecheckt werden.

## Entwicklungsprinzipien

- Klare Trennung von Benutzeroberfläche, Geschäftslogik und Datenzugriff
- Nachvollziehbare Datenherkunft und Kennzahlendefinitionen
- Kleine, überprüfbare Änderungen
- Automatisierte Tests und reproduzierbare Builds
- Keine Geheimnisse oder personenbezogenen Daten im Repository

## Mitwirken

Änderungen sollten auf einem eigenen Branch entwickelt, geprüft und über einen Pull Request eingebracht werden. Architekturentscheidungen und neue Kennzahlen sind in `docs/` zu dokumentieren.

## Version

Aktueller Projektstand: **0.1**
