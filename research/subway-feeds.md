# MTA subway realtime feeds

Answers ticket #2. Verified against live feeds on 2026-09-28 (~15:10 UTC).

## TL;DR
- 8 GTFS-realtime protobuf feeds, **no API key required**; full snapshots ~20–30 s old.
- Trip updates with per-stop predicted arrival/departure; vehicle entities carry **no lat/lon** (0 of 663).
- Live map is still possible: interpolate each train between previous stop and next predicted arrival, snapped to `shapes.txt`.
- Realtime `trip_id` is only a suffix of the static one; match on origin time + route + direction.
- Terms: serve from our own backend, lag disclaimer, no endorsement implied.

## Endpoints
Base `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/`:

| Feed | Path |
|---|---|
| 1-7, S | `nyct%2Fgtfs` |
| A C E, H, FS | `nyct%2Fgtfs-ace` |
| B D F M | `nyct%2Fgtfs-bdfm` |
| G | `nyct%2Fgtfs-g` |
| J Z | `nyct%2Fgtfs-jz` |
| N Q R W | `nyct%2Fgtfs-nqrw` |
| L | `nyct%2Fgtfs-l` |
| SIR | `nyct%2Fgtfs-si` |

**Service alerts** (GTFS-rt, `.json` variants available): `camsys%2Fsubway-alerts`, `camsys%2Fbus-alerts`, `camsys%2Fall-alerts`, `camsys%2Flirr-alerts`, `camsys%2Fmnr-alerts`.

**Elevator & escalator** (JSON and XML): `nyct%2Fnyct_ene.json` (current outages; also carries upcoming rows flagged `isupcomingoutage`), `nyct%2Fnyct_ene_upcoming.json`, `nyct%2Fnyct_ene_equipments.json`. Fields: station, trainno, equipment, equipmenttype (EL/ES), serving, ADA, outagedate, estimatedreturntoservice, reason. 80 rows (52 elevators, 28 escalators) on 2026-09-28. Source: api.mta.info/#/EAndEFeeds.

## Auth
api.mta.info states keys "are no longer required". All 8 feeds return HTTP 200 to a plain GET. `HEAD` returns 403, so health checks must use GET. Buses are **not** here; Bus Time still needs a key (see bus-data research).

## Update cadence
Each fetch is a full snapshot; header timestamp ~20–30 s behind wall clock. Poll every ~15–30 s.

## Fields
- `trip_update.stop_time_update[]`: stop_id (with N/S suffix), arrival/departure time: the **official prediction**.
- `vehicle`: current stop, status, timestamp; **no position**.
- `delay` and `direction_id` only populated on the L feed.
- NYCT extension (field 1001): train_id, is_assigned, scheduled/actual track, trip-replacement period. Within the replacement window, static trips absent from the feed should be treated as cancelled.

## Known quirks
- Realtime trip_id `060550_1..N15R` vs static `...Weekday-00_060550_1..N03R`: match on origin time + route + direction.
- Match rate against static GTFS **not measured** yet (script drafted, not run).
- Use the *supplemented* static GTFS (next 7 days of service changes, refreshed hourly).

## Terms (mta.info/developers/terms-and-conditions)
Free, as-is, revocable without notice. Data must be served from our own server, not fetched by clients from MTA. No implied MTA endorsement; warn users if data may lag > 1 minute.

## Map without lat/lon
Place each train between its previous stop and next predicted arrival by time fraction, then snap to the route shape in `shapes.txt`. Accuracy ≈ one station segment.

## Sources
- https://api.mta.info (#/subwayRealTimeFeeds, #/serviceAlerts, #/EAndEFeeds)
- https://www.mta.info/developers
- https://www.mta.info/developers/terms-and-conditions
- NYCT GTFS-rt extension proto (OneBusAway mirror, linked by MTA)
- Live decode of all 8 feeds + supplemented static GTFS, 2026-09-28
