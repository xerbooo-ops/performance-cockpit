# CSV-Import

## Format

Die Datei muss UTF-8-kodiert sein und folgende Spalten enthalten:

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

Eine Beispieldatei liegt unter [`data/sample_kpi_measurements.csv`](../data/sample_kpi_measurements.csv).

## Import über API

```bash
curl -X POST http://localhost:8000/api/v1/imports/csv \
  -F "file=@data/sample_kpi_measurements.csv"
```

Die Antwort enthält Batch-ID, Status, Anzahl importierter und fehlerhafter Zeilen sowie verständliche Fehler je Zeile.

## Import über Kommandozeile

Nach Installation des Backends und Ausführung der Migrationen:

```bash
performance-cockpit-import ../data/sample_kpi_measurements.csv
```

Importe sind idempotent: Bereits vorhandene Messwerte für denselben Zeitraum und dieselbe Organisationseinheit werden aktualisiert.
