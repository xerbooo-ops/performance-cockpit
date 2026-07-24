Performance Cockpit v1.0.4 – Windows

Start:
1. ZIP-Datei vollständig entpacken.
2. PerformanceCockpit.exe doppelklicken.
3. Das Cockpit öffnet sich automatisch im Standardbrowser.

Es muss nichts installiert werden. Die Anwendung läuft vollständig lokal und benötigt weder
Internetzugang noch Docker, eine separate Python-Installation, Node.js, TypeScript oder PostgreSQL.

Daten:
- CSV- oder XLSX-Datei über „Daten importieren“ auswählen.
- Für automatische Aktualisierungen einmal „Reportdatei auswählen“ anklicken und die lokale
  Reportdatei im Windows-Dialog festlegen.
- Änderungen dieser Datei werden danach alle fünf Sekunden geprüft und automatisch importiert.
- Die Auswahl bleibt nach einem Neustart gespeichert; über „Überwachung beenden“ kann sie
  zurückgesetzt werden.
- Im Performance-Report werden Teamleiter- und Mitarbeiternamen ignoriert und nicht gespeichert.
- Die Auswahl erfolgt ausschließlich über EPA; „Potsdam“ enthält die kumulierten Gesamtwerte.
- Zielwerte werden im Dashboard und PDF-Bericht zunächst nicht angezeigt.
- Eine Beispieldatei liegt im selben Ordner.
- Die lokale Datenbank liegt unter %LOCALAPPDATA%\PerformanceCockpit.
- CSV-Export, vollständiges Backup und Wiederherstellung stehen unter „Lokale Datenverwaltung“ bereit.
- Beim Zurücksetzen muss zur Sicherheit DELETE eingegeben werden.
- Bestehende Daten aus Version 0.4 werden beim ersten Start automatisch aktualisiert.

Beenden:
Das Fenster der Anwendung schließen. Falls kein Fenster sichtbar ist, den Prozess
„PerformanceCockpit“ im Windows-Task-Manager beenden.
