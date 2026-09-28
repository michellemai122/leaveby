# Routing and transfers

Answers ticket #5.

## Recommendation
- **v1 (today):** Google Routes API `computeRoutes`, `travelMode: TRANSIT`, `arrivalTime`, `allowedTravelModes [SUBWAY, BUS]`, alternatives on. Use it **only for the itinerary** (lines, board/alight stops, transfers). Compute leave-by ourselves by walking backward from the target over MTA realtime predictions per leg. No infra; call Google only when a commute changes, so within free tier.
- **Later:** own RAPTOR in Python over MTA static GTFS, fed by our model's predictions, so delays can change the *route*, not just the time. Fallback: self-hosted OTP2. Skip r5 (Conveyal positions it for accessibility analysis, not trip planning).

## Comparison
| Option | Cost | Realtime | Hosting | Effort |
|---|---|---|---|---|
| Google Routes API (transit) | Essentials: 10k free/month, then $5/1k | Not documented for transit | None | Hours |
| Transitland Routing (beta) | 1k free/month, then paid | None (no TripUpdates/VehiclePositions) | None | Hours, quota too small |
| HERE Transit v8 | Not checked | Not stated | None | No reason over Google |
| OTP2 self-hosted | VM only | Yes, `stop-time-updater` w/ custom headers | Java; NYC ≥4 GB (community figure) | ≥1 day |
| Own RAPTOR (Python) | Free | Best fit for own predictions | In-process | Days |

## Inputs
MTA supplemented subway GTFS (7 days of service changes, hourly) + 6 borough bus GTFS files (quarterly).

## Open risks
- Google returns stop names/coords, not GTFS stop_ids: we must match to MTA stops.
- Check Google Maps Platform Terms on caching itineraries and display without a Google map before launch.
- No latency measured for any option.

## Sources
developers.google.com/maps/documentation/routes/transit-route · /routes/usage-and-billing · /billing-and-pricing/pricing · transit.land/documentation/routing-api/ · transit.land/plans-pricing/ · docs.here.com/transit/docs/readme-public-transit-api-v8 · docs.opentripplanner.org (RouterConfiguration, Basic-Tutorial, System-Requirements) · github.com/opentripplanner/OpenTripPlanner/wiki/PerformanceNYC · github.com/conveyal/r5 · Microsoft Research "Round-Based Public Transit Routing" · mta.info/developers · bustime.mta.info/wiki/Developers/GTFSRt
