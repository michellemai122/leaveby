# MTA bus realtime data

Answers ticket #3. Live pull 2026-09-28 ~11:11 ET.

## TL;DR
- Use **GTFS-realtime** from Bus Time: one protobuf (~320 KB) with every bus.
- 2,353/2,353 vehicles had lat/lon, bearing, route_id, trip_id across 285 routes; median position age 52 s (p90 63 s).
- Key required per docs (free, emailed within ~30 min). A keyless pull worked today; don't rely on it.
- Don't poll all-vehicle calls faster than every 30 s.

## Endpoints
- GTFS-rt: `https://gtfsrt.prod.obanyc.com/vehiclePositions?key=KEY`, `/tripUpdates`, `/alerts` (bustime.mta.info/developers/gtfs-realtime/)
- SIRI (alternative): `https://bustime-classic.mta.info/api/siri/vehicle-monitoring.json`, `/stop-monitoring.json` with `key`, `version=2`, `LineRef`, `VehicleRef`, `MonitoringRef`. `/api/2/siri/...` includes cancelled trips. Extras: occupancy, distance-away, layover status.

## Key signup
https://register.developer.obanyc.com/ — name, email, project name, app URL, platforms. Free; key emailed "within half an hour". Support: groups.google.com/group/mtadeveloperresources.

## Rate limits
No numeric quota published. Vehicle-monitoring docs warn that all-vehicle calls at under 30 s intervals may get the key revoked. Poll ≥30 s from a single backend.

## Static GTFS
`https://rrgtfsfeeds.s3.amazonaws.com/` → `gtfs_bx.zip`, `gtfs_b.zip`, `gtfs_m.zip`, `gtfs_q.zip`, `gtfs_si.zip`, `gtfs_busco.zip` (MTA Bus Co). Updated ~quarterly; detours generally not included.

## Terms (mta.info/developers/terms-and-conditions)
- Free. Apps must not make data available "directly from MTA's server(s)": proxy through our backend, keep the key server-side.
- Disclose lag > 1 minute. No implied endorsement; don't claim accuracy/timeliness; don't modify the data.
- MTA marks require a (free-for-free-apps) license. Access revocable anytime.
