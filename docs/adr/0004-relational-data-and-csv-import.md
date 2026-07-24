# ADR 0004: Relationales Datenmodell und CSV-Import

- **Status:** Angenommen
- **Datum:** 2026-07-24

## Kontext

Kennzahlen müssen nachvollziehbar, periodisch auswertbar und ohne doppelte Messwerte importierbar sein. Die erste Datenquelle soll ohne Abhängigkeit von einem konkreten Fremdsystem getestet werden können.

## Entscheidung

- PostgreSQL speichert Kennzahlendefinitionen, Messwerte und Importprotokolle.
- SQLAlchemy bildet das Modell ab; Alembic versioniert Schemaänderungen.
- CSV ist das erste unterstützte Importformat.
- Messwerte sind je Kennzahl, Organisationseinheit und Zeitraum eindeutig.
- Importfehler werden zeilen- und feldbezogen zurückgegeben.

## Folgen

- Das Datenmodell bleibt unabhängig von einem konkreten Quellsystem.
- Beispiel- und Testdaten können einfach erstellt werden.
- Produktive Quellen benötigen später Adapter auf dieselben fachlichen Strukturen.
- Alle Schemaänderungen erfordern eine Migration.
