# LeaveBy — Domain Glossary

- **Leave-by time**: the latest moment the rider can leave their origin and still reach the destination by the target arrival time, given predicted (not scheduled) transit arrivals.
- **Alarm**: a push notification fired at the leave-by time. It is re-computed as predictions change; an alarm can move earlier or later.
- **Official prediction**: the arrival estimate the MTA publishes in its realtime feed (what countdown clocks show).
- **Model prediction**: LeaveBy's own arrival estimate for the same vehicle and stop.
- **Commute**: a rider's recurring trip: origin, destination, target arrival time, preferences (e.g. avoid transfers).
- **Origin**: where a leave-by calculation starts. The rider's **saved origin** (e.g. Home) by default, replaced by their **live location** while the commute panel is open.
- **Walk time**: time from origin to the boarding station, at the rider's chosen walk pace (relaxed / normal / brisk).
- **Trip record**: the stored facts about one completed commute (rounded start point, left-at time, station entered, boarded-at time, actual walk time). Not a movement trail.
