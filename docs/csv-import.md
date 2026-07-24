# CSV- und Excel-Import

## Format

Der Import akzeptiert UTF-8-kodierte CSV-Dateien und Excel-Arbeitsmappen im XLSX-Format. Bei XLSX
wird das erste Tabellenblatt gelesen. Beide Formate müssen folgende Spalten enthalten:

| Spalte | Beschreibung | Beispiel |
| --- | --- | --- |
| `metric_key` | Stabiler technischer Schlüssel | `handled_cases` |
| `metric_name` | Anzeigename | `Bearbeitete Vorgänge` |
| `description` | Fachliche Beschreibung | `Abgeschlossene Vorgänge` |
| `unit` | Einheit | `Anzahl` |
| `aggregation` | `sum` oder `average` | `sum` |
| `organizational_unit` | Organisationseinheit | `Service Nord` |
| `period_start` | Start als ISO-Datum | `2026-07-01` |
| `period_end` | Ende als ISO-Datum | `2026-07-07` |
| `value` | Ist-Wert | `110` |
| `target_value` | Optionaler Zielwert | `100` |

Die maximale Dateigröße beträgt 5 MB. Eine Beispieldatei liegt unter
[`data/sample_kpi_measurements.csv`](../data/sample_kpi_measurements.csv).

## Import in der Anwendung

In der lokalen Windows-Anwendung oben rechts „Daten importieren“ wählen und eine CSV- oder
XLSX-Datei öffnen. Das Cockpit lädt die Kennzahlen nach einem erfolgreichen Import automatisch neu.

## Import über API

```bash
curl -X POST http://localhost:8000/api/v1/imports/file \
  -F "file=@data/sample_kpi_measurements.csv"
```

`POST /api/v1/imports/csv` bleibt für bestehende Integrationen erhalten. Die Antwort enthält
Batch-ID, Status, Anzahl importierter und fehlerhafter Zeilen sowie Fehler je Zeile.

Importe sind idempotent: Bereits vorhandene Messwerte für denselben Zeitraum und dieselbe
Organisationseinheit werden aktualisiert.
