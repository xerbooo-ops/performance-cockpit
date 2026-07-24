# Support und Fehlerdiagnose

## Lokaler Selbsttest

Die Anwendung stellt unter `/api/v1/system/diagnostics` einen rein lokalen Diagnose-Endpunkt bereit.
Er bestätigt Version, Datenbankzugriff und die Anzahl der lokal gespeicherten Datensätze, gibt aber
keine Dateipfade oder Inhalte aus.

## Häufige Schritte

1. Anwendung schließen und erneut starten.
2. Unter **Backup** eine Sicherung der lokalen Daten erstellen.
3. Diagnose im Browser über `http://127.0.0.1:<Port>/api/v1/system/diagnostics` prüfen.
4. Bei beschädigten Daten ein zuvor erstelltes `.db`-Backup wiederherstellen.

Die Anwendung sendet keine Telemetrie und benötigt keinen Internetzugang. Produktive Daten liegen
unter `%LOCALAPPDATA%\PerformanceCockpit` und werden beim Deinstallieren nicht automatisch gelöscht.

## Support-Paket

Für eine Fehlermeldung genügen die App-Version, die Diagnoseausgabe, die Windows-Version und eine
Beschreibung der letzten Aktion. Personenbezogene CSV-, XLSX-, PDF- oder Datenbankdateien sollen
nicht ungeprüft weitergegeben werden.
