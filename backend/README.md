# Performance Cockpit Backend

FastAPI-Anwendung für Kennzahlendefinitionen, Messwerte, CSV-Import und versionierte API-Endpunkte.

```bash
pip install -e ".[dev]"
alembic upgrade head
uvicorn performance_cockpit.main:app --reload
```

Beispieldaten importieren:

```bash
performance-cockpit-import ../data/sample_kpi_measurements.csv
```
