# Historical MTA realtime archives

Answers ticket #4.

## TL;DR
- **Subway: yes, current.** subwaydata.nyc publishes a raw GTFS-rt dump for every day 2021-04-01 → yesterday (~2,006 days), updated daily ~7am.
- Raw snapshots preserve the **official MTA predictions**, so replay gives MTA-prediction-vs-actual at every lead time: exactly the scoreboard's data.
- Bootstrap v2 with 2–4 weeks of weekday history (~1–2 GB). Download once, only what we need.
- **Buses: no prediction archive found.** Start our own collector tonight.

## subwaydata.nyc
- Raw: per-day `.tar.xz`, ~33–62 MB, all 8 feeds. URLs include a hash; enumerate via https://subwaydata.nyc/explore-the-data.
- Processed: per-day `trips.csv` + `stop_times.csv` (~1 MB/day), actual stop times *inferred* from the feed.
- Maintainers note the full dump is >50 GB and bandwidth costs them money: be a good citizen.
- Code repo is MIT; data has no stated license. Raw-snapshot content rests on `etl/gtfsrt_readme.md` and file names; a 2026 dump was not fully decoded.

## Older archive
kenyoneda's AWS archive (30 s snapshots from 2018-04-27) still serves files but ends ~April 2021, with gaps. A decoded 2021-01-01 snapshot does contain future-stop predictions.

## Buses
Nothing found. Not yet checked: data.ny.gov, MTA developer pages, Transitland archives.
