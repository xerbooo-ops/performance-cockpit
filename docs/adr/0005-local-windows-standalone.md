# ADR 0005: Lokale Windows-Standalone-Anwendung

**Status:** Angenommen  
**Datum:** 2026-07-24

## Entscheidung

Die Zielanwendung wird als portable Windows-10/11-EXE ausgeliefert. React-Frontend, FastAPI-Backend
und Python-Laufzeit werden mit PyInstaller gebündelt. Die Anwendung bindet ausschließlich an
`127.0.0.1`, öffnet die Oberfläche im Standardbrowser und speichert Daten in einer eingebetteten
SQLite-Datenbank unter `%LOCALAPPDATA%\PerformanceCockpit`.

Für die Laufzeit werden weder Docker noch Python, Node.js, PostgreSQL, Internetzugang, Cloud-Dienste
oder externe APIs benötigt. PostgreSQL und Docker bleiben ausschließlich optionale
Entwicklungswerkzeuge.

## Folgen

- Start per Doppelklick ohne Installation zusätzlicher Komponenten
- lokale Datenhaltung und Verarbeitung
- Windows-Build und Starttest über GitHub Actions
- Datenbankschema wird beim ersten Start automatisch angelegt
- künftige Releases müssen lokale Migration, Sicherung und Wiederherstellung berücksichtigen
