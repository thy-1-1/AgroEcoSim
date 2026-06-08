# Demo Data

`agroecosystem_timeseries.csv` is a deterministic synthetic time series used by
the executable demo pipeline. It provides monthly crop, pest, predator,
pollinator, soil, chemical-pressure, and PSR indicator signals.

Regenerate it with:

```bash
python scripts/generate_demo_data.py
```

The demo data set is intentionally small so tests, examples, and GitHub Actions
can run quickly without external data access.
