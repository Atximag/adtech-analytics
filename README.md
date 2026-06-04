# Adtech Analytics Engineering — dbt + DuckDB

An end-to-end analytics-engineering project modelling a partner **advertising platform**:
raw ad-event streams → cleaned staging models → analytical data marts with advertising KPIs.
Built to demonstrate production-style data modelling, incremental processing, slowly-changing
dimensions, automated data-quality testing and documentation.

> Stack: **dbt** (transformations) · **DuckDB** (OLAP engine) · **Python / pandas** (ingestion)

---

## What this project demonstrates

| Capability | Where |
|---|---|
| Layered modelling (staging → marts) | `models/staging`, `models/marts` |
| Advertising KPIs (CTR, eCPM, CVR) | `fct_campaign_performance` |
| **Incremental** model (process only new days) | `fct_campaign_performance` |
| **Snapshots** / SCD Type 2 (status history) | `snapshots/snap_advertisers.sql` |
| Automated data-quality tests | `models/staging/_staging.yml` |
| Referential integrity (`relationships`) tests | `_staging.yml` |
| Model documentation + lineage graph | `dbt docs` |

---

## Data model

**Sources** (synthetic, generated locally):

- `advertisers` — advertiser dimension (id, name, country, status)
- `campaigns` — campaign dimension (channel, bid CPM, budget)
- `ad_events` — event stream of impressions / clicks / conversions, partitioned by day

**Marts** — `fct_campaign_performance`: daily metrics per campaign:

| Metric | Definition |
|---|---|
| CTR  | clicks / impressions |
| eCPM | revenue / impressions × 1000 |
| CVR  | conversions / clicks |

---

## How to run

```bash
# 1. Environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install dbt-duckdb pandas numpy pyarrow

# 2. Generate the synthetic dataset (~600k events over 30 days)
python generate_data.py

# 3. Build the models
dbt run --profiles-dir .

# 4. Run data-quality tests
dbt test --profiles-dir .

# 5. Capture slowly-changing dimension history
dbt snapshot --profiles-dir .

# 6. Browse documentation + lineage graph
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .    # opens http://localhost:8080
```

### Demonstrating the incremental model

```bash
dbt run --profiles-dir . --full-refresh    # build full history
python add_day.py                          # append one new day of events
dbt run --profiles-dir .                   # only the new day is processed
```

### Demonstrating SCD Type 2

```bash
dbt snapshot --profiles-dir .              # initial capture
python flip_status.py                      # change an advertiser's status
dbt run --profiles-dir . --select stg_advertisers
dbt snapshot --profiles-dir .              # a new version row is recorded
```

---

## Lineage


[Lineage graph](docs/lineage.png)

```
sources (raw)  →  staging  →  marts
                              snapshots
```

---

## Notes

- The fact table is partitioned by day, which is what enables the incremental model
  to load only new partitions instead of reprocessing the full history.
- `country` is intentionally allowed to contain NULLs (simulating dirty source data),
  so it is documented rather than blindly tested with `not_null`.
- Division in metrics is guarded with `nullif(...)` and explicit casting for
  portability across OLAP engines.
