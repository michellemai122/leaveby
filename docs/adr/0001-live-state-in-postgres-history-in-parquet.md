# Live state in Postgres, feed history as Parquet on R2, queried with DuckDB

LeaveBy collects every subway (15 s) and bus (30 s) realtime snapshot so it can train and score its own arrival model. That grows to gigabytes within weeks, while app state (commutes, push subscriptions, alarms) stays tiny and transactional. We keep app state in Postgres (Neon) and append raw feed history as Parquet files to Cloudflare R2, read by DuckDB for modelling. The same DuckDB path reads the subwaydata.nyc backfill, so historical and self-collected data share one pipeline.

**Considered:** everything in Postgres/Timescale (simpler ops, but expensive storage and a poor fit for columnar model training); everything in DuckDB on disk (no concurrent writes from the API, disk tied to one host).
