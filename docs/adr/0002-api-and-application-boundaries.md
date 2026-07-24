# ADR 0002: API und Anwendungsgrenzen

- **Status:** Angenommen
- **Datum:** 2026-07-24

## Kontext

Kennzahlen dürfen nicht unterschiedlich im Browser und Backend berechnet werden. Gleichzeitig soll die Benutzeroberfläche unabhängig von Datenquellen bleiben.

## Entscheidung

- Das Frontend kommuniziert ausschließlich über eine versionierte HTTP-API mit dem Backend.
- Die erste API-Version liegt unter `/api/v1`.
- Fachliche Berechnungen und Validierungen liegen im Backend.
- Pydantic-Modelle definieren API-Verträge.

## Folgen

- Berechnungsregeln haben eine zentrale Quelle.
- Frontend und Backend benötigen abgestimmte Verträge.
- Inkompatible Änderungen erfordern eine neue API-Version oder eine Migration.
