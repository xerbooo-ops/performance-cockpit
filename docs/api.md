# API

Die HTTP-API ist unter `/api/v1` versioniert. Die interaktive OpenAPI-Dokumentation ist lokal unter `/docs` erreichbar.

## Endpunkte

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Anwendungsstatus |
| `POST` | `/api/v1/imports/file` | CSV- oder XLSX-Datei validieren und importieren |
| `POST` | `/api/v1/imports/csv` | Bestehender CSV-Endpunkt |
| `GET` | `/api/v1/metrics/dashboard/filters` | Organisationseinheiten und Zeitraum laden |
| `GET` | `/api/v1/metrics/dashboard` | Kennzahlen und Datenstatus für das Cockpit laden |
| `GET` | `/api/v1/metrics` | Kennzahlendefinitionen auflisten |
| `GET` | `/api/v1/metrics/{key}/measurements` | Messwerte filtern und auflisten |
| `GET` | `/api/v1/metrics/{key}/summary` | Aggregierten Wert, Ziel, Abweichung und Zielerreichung berechnen |

## Dashboard-Filter

Das Dashboard erfordert `organizational_unit` und akzeptiert optional `date_from` und `date_to`.
Die Antwort enthält Kennzahlzusammenfassungen, Zeitraum, Quelldateien und den Zeitpunkt des letzten
Imports.

## Messwert-Filter

Messwerte akzeptieren optional:

- `organizational_unit`
- `date_from`
- `date_to`

Für eine Summary ist `organizational_unit` erforderlich.

Beispiel:

```text
GET /api/v1/metrics/handled_cases/summary?organizational_unit=Service%20Nord
```

## Fehlerverhalten

- `404`: Kennzahl oder Messwerte für die Filter nicht gefunden
- `413`: Datei überschreitet 5 MB
- `415`: Upload ist weder CSV noch XLSX
- `422`: Ungültige Anfrage oder nicht lesbare Datei

Fachliche Zeilenfehler führen zu einem Importstatus `completed_with_errors`; gültige Zeilen werden
weiterhin verarbeitet.
