# ADR 0003: Konfiguration, Logging und Qualität

- **Status:** Angenommen
- **Datum:** 2026-07-24

## Kontext

Lokale Entwicklung und spätere Betriebsumgebungen benötigen unterschiedliche Konfigurationen. Fehler müssen nachvollziehbar sein, ohne sensible Daten zu protokollieren. Qualitätsprüfungen sollen reproduzierbar laufen.

## Entscheidung

- Konfiguration wird über Umgebungsvariablen bereitgestellt und im Backend typisiert validiert.
- Das Backend erzeugt strukturierte JSON-Logs.
- Ruff und pytest prüfen das Backend.
- ESLint, Prettier, TypeScript und Vitest prüfen das Frontend.
- GitHub Actions führt alle Prüfungen bei Pull Requests und auf `main` aus.

## Folgen

- Geheimnisse bleiben außerhalb des Repositorys.
- Fehler lassen sich maschinell auswerten.
- Änderungen werden nur bei erfolgreichen Qualitätsprüfungen freigegeben.
