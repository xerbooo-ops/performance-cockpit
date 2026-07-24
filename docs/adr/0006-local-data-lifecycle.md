# ADR 0006: Lokaler Datenlebenszyklus

**Status:** Angenommen  
**Datum:** 2026-07-24

## Entscheidung

Export, Backup, Wiederherstellung und Zurücksetzen werden vollständig durch den lokalen
Anwendungsprozess ausgeführt. Backups sind konsistente SQLite-Kopien und werden vor der
Wiederherstellung auf Integrität und erforderliche Tabellen geprüft. Das Zurücksetzen erfordert die
exakte Bestätigung `DELETE`.

Die eingebettete Anwendung führt beim Start Alembic-Migrationen aus. Datenbanken aus Release 0.4,
die noch keine Alembic-Versionsmarkierung besitzen, werden als Revision `0001` übernommen und
anschließend regulär migriert.

## Folgen

- keine Übertragung von Nutzdaten an externe Systeme
- vorhandene lokale Daten bleiben bei Anwendungsupdates erhalten
- vollständige Sicherung und Wiederherstellung ohne Zusatzsoftware
- expliziter Schutz vor versehentlichem Löschen
- Importfehler bleiben dauerhaft nachvollziehbar
