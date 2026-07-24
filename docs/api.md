# API

Die HTTP-API ist unter `/api/v1` versioniert. Die interaktive OpenAPI-Dokumentation ist lokal unter `/docs` erreichbar.

## Endpunkte

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Anwendungsstatus |
| `POST` | `/api/v1/imports/csv` | CSV-Datei validieren und importieren |
| `GET` | `/api/v1/metrics` | Kennzahlendefinitionen auflisten |
| `GET` | `/api/v1/metrics/{key}/measurements` | Messwerte filtern und auflisten |
| `GET` | `/api/v1/metrics/{key}/summary` | Aggregierten Wert, Ziel, Abweichung und Zielerreichung berechnen |

## Filter

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
- `413`: CSV-Datei überschreitet 5 MB
- `415`: Upload ist keine CSV-Datei
- `422`: Ungültige Anfrage oder nicht UTF-8-kodierte CSV-Datei

Fachliche CSV-Zeilenfehler führen zu einem Importstatus `completed_with_errors`; gültige Zeilen werden weiterhin verarbeitet.
