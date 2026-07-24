# ADR 0001: Technologie-Stack

- **Status:** Angenommen
- **Datum:** 2026-07-24

## Kontext

Das Performance Cockpit benötigt eine responsive Weboberfläche, eine klar dokumentierte API, zuverlässige Datenvalidierung und eine relationale Persistenz. Der Stack soll gut testbar, verbreitet und lokal reproduzierbar sein.

## Entscheidung

- React mit TypeScript und Vite für das Frontend
- FastAPI mit Python für Backend und Geschäftslogik
- PostgreSQL für persistente Daten
- Docker Compose für die lokale Umgebung
- GitHub Actions für Continuous Integration

## Folgen

- Frontend und Backend können unabhängig entwickelt und getestet werden.
- OpenAPI-Dokumentation entsteht aus den FastAPI-Verträgen.
- Das Team benötigt Kompetenzen in TypeScript und Python.
- Gemeinsame API-Verträge und eine konsequente Versionsstrategie sind erforderlich.
