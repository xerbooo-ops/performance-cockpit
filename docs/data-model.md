# Datenmodell

Release 0.3 führt ein relationales Datenmodell für Kennzahlen und periodische Messwerte ein.

```mermaid
erDiagram
    METRIC_DEFINITIONS ||--o{ MEASUREMENTS : beschreibt
    IMPORT_BATCHES ||--o{ MEASUREMENTS : erzeugt

    METRIC_DEFINITIONS {
        string key PK
        string display_name
        string unit
        string aggregation
    }
    MEASUREMENTS {
        int id PK
        string metric_key FK
        string organizational_unit
        date period_start
        date period_end
        decimal value
        decimal target_value
    }
    IMPORT_BATCHES {
        int id PK
        string file_name
        string status
        int imported_rows
        int failed_rows
    }
```

## Kennzahlendefinition

Eine Kennzahl wird durch einen stabilen technischen Schlüssel identifiziert. Die Aggregationsart bestimmt, wie mehrere Messwerte in der Summary-API zusammengeführt werden:

- `sum`: Werte und Ziele werden addiert.
- `average`: Werte und vorhandene Ziele werden arithmetisch gemittelt.

## Messwert

Ein Messwert gehört zu genau einer Kennzahl, einer Organisationseinheit und einem Zeitraum. Die Kombination aus Kennzahl, Organisationseinheit, Start und Ende ist eindeutig. Ein erneuter Import aktualisiert deshalb vorhandene Werte, statt Duplikate anzulegen.

## Importprotokoll

Jeder CSV-Import erzeugt einen Import-Batch mit Status und Zeilenzahlen. Fehler werden zusätzlich in der API-Antwort zeilen- und feldbezogen ausgegeben.
