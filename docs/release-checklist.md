# Release-Checkliste

- Backend-Tests, Ruff und Coverage-Grenze erfolgreich
- Frontend-Tests, ESLint, Prettier, TypeScript und Produktions-Build erfolgreich
- Portable EXE startet und beantwortet den Health-Check
- Windows-Installer wird erzeugt und enthält EXE, Hilfe und Beispieldaten
- Import, Filter, Drilldown, XLSX/PDF-Export, Backup und Wiederherstellung geprüft
- Anwendung bindet ausschließlich an `127.0.0.1`
- Keine externen URLs, APIs, Fonts, Skripte oder Telemetriedienste
- Upgrade einer bestehenden lokalen Datenbank geprüft
- Installer auf aktuellem Windows 10 und Windows 11 pilotieren
- Digitale Signatur ergänzen, sobald ein Code-Signing-Zertifikat bereitgestellt ist
