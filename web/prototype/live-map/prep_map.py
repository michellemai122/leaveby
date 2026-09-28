# PROTOTYPE data prep: live MTA snapshot -> trajectories JSON for the live-map prototype.
import csv, json, math, os, random, time, urllib.request, collections, sys
from google.transit import gtfs_realtime_pb2 as g

S = "sup"
BASE = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/"
FEEDS = ["gtfs", "gtfs-ace", "gtfs-bdfm", "gtfs-g", "gtfs-jz", "gtfs-nqrw", "gtfs-l", "gtfs-si"]
HORIZON = 25 * 60
BUS_KEY = sys.argv[1] if len(sys.argv) > 1 else ""

def get(url):
    import subprocess
    return subprocess.run(["curl", "-sf", "--max-time", "30", url], capture_output=True, check=True).stdout

routes = {r["route_id"]: r for r in csv.DictReader(open(f"{S}/routes.txt"))}
stops = {s["stop_id"]: (float(s["stop_lon"]), float(s["stop_lat"]), s["stop_name"], s["parent_station"] or s["stop_id"]) for s in csv.DictReader(open(f"{S}/stops.txt"))}
shapes = collections.defaultdict(list)
for r in csv.DictReader(open(f"{S}/shapes.txt")):
    shapes[r["shape_id"]].append((int(r["shape_pt_sequence"]), float(r["shape_pt_lon"]), float(r["shape_pt_lat"])))
shapes = {k: [(x, y) for _, x, y in sorted(v)] for k, v in shapes.items()}

# representative (longest) shape per route+direction
rep = {}
for k, pts in shapes.items():
    if "." not in k:
        continue
    rid, rest = k.split(".", 1)
    rest = rest.lstrip(".")
    d = rest[0]
    if len(pts) > len(shapes.get(rep.get((rid, d)), [])):
        rep[(rid, d)] = k

def dist(a, b):
    return math.hypot((a[0] - b[0]) * math.cos(math.radians(40.7)), a[1] - b[1])

proj_cache = {}
def proj(shape_id, stop_id):
    key = (shape_id, stop_id)
    if key not in proj_cache:
        p = stops[stop_id][:2]
        pts = shapes[shape_id]
        i = min(range(len(pts)), key=lambda i: dist(pts[i], p))
        proj_cache[key] = (i, dist(pts[i], p))
    return proj_cache[key]

# typical segment time between consecutive stops (for placing the previous stop)
seg = {}
prev = None
for r in csv.DictReader(open(f"{S}/stop_times.txt")):
    if prev and prev["trip_id"] == r["trip_id"]:
        k = (prev["stop_id"], r["stop_id"])
        if k not in seg:
            h1, m1, s1 = map(int, prev["departure_time"].split(":")); h2, m2, s2 = map(int, r["arrival_time"].split(":"))
            seg[k] = max(30, (h2 * 3600 + m2 * 60 + s2) - (h1 * 3600 + m1 * 60 + s1))
    prev = r
prev_of = {b: a for (a, b) in seg}

T0 = int(time.time())
trips, alerts_by_route = [], collections.defaultdict(list)
rng = random.Random(7)
for f in FEEDS:
    m = g.FeedMessage(); m.ParseFromString(get(BASE + "nyct%2F" + f))
    for e in m.entity:
        if not e.HasField("trip_update"):
            continue
        tu = e.trip_update
        rid = tu.trip.route_id
        su = [(u.stop_id, (u.arrival.time or u.departure.time)) for u in tu.stop_time_update if (u.arrival.time or u.departure.time) and u.stop_id in stops]
        su = [x for x in su if x[1] <= T0 + HORIZON]
        if not su or su[0][1] < T0 - 60:
            continue
        d = su[0][0][-1]
        sid = tu.trip.trip_id.split("_", 1)[-1] if "_" in tu.trip.trip_id else ""
        shape = sid if sid in shapes else rep.get((rid, d)) or rep.get((rid.rstrip("X"), d))
        if not shape:
            continue
        p0 = prev_of.get(su[0][0])
        if p0 and p0 in stops:
            su = [(p0, su[0][1] - seg[(p0, su[0][0])])] + su
        if su[0][1] > T0 + 20:  # train hasn't started yet
            continue
        path, ts = [], []
        for (a, ta), (b, tb) in zip(su, su[1:]):
            ia, ea = proj(shape, a); ib, eb = proj(shape, b)
            if ea > 0.004 or eb > 0.004:
                seg_pts = [stops[a][:2], stops[b][:2]]
            else:
                step = 1 if ib >= ia else -1
                seg_pts = shapes[shape][ia: ib + step: step] or [stops[a][:2], stops[b][:2]]
            cum = [0.0]
            for p, q in zip(seg_pts, seg_pts[1:]):
                cum.append(cum[-1] + dist(p, q))
            tot = cum[-1] or 1
            for p, c in zip(seg_pts, cum):
                if path and p == path[-1]:
                    continue
                path.append([round(p[0], 5), round(p[1], 5)]); ts.append(round(ta - T0 + (tb - ta) * c / tot))
        if len(path) < 2:
            continue
        # MOCK "model" prediction: official time + drifting offset (seconds). Real model comes in v2.
        bias = rng.gauss(0, 25); drift = rng.gauss(0, 0.06)
        mts = [t + round(bias + drift * max(0, t)) for t in ts]
        trips.append({"r": rid, "p": path, "t": ts, "m": mts, "d": d, "to": stops[su[-1][0]][2], "nx": stops[su[1][0] if len(su) > 1 else su[0][0]][2]})

try:
    aj = json.loads(get(BASE + "camsys%2Fsubway-alerts.json"))
    for e in aj.get("entity", []):
        a = e.get("alert", {})
        txt = next((t["text"] for t in a.get("header_text", {}).get("translation", []) if t.get("language") == "en"), "")
        for ie in a.get("informed_entity", []):
            if ie.get("route_id") and txt and txt not in alerts_by_route[ie["route_id"]]:
                alerts_by_route[ie["route_id"]].append(txt)
except Exception as ex:
    print("alerts failed", ex)

ene = []
try:
    for o in json.loads(get(BASE + "nyct%2Fnyct_ene.json")):
        if o.get("isupcomingoutage") == "N" and o.get("equipmenttype") == "EL":
            ene.append({"s": o["station"], "l": o["trainno"], "w": o["serving"], "b": o["estimatedreturntoservice"]})
except Exception as ex:
    print("ene failed", ex)

buses = []
if BUS_KEY:
    m = g.FeedMessage(); m.ParseFromString(get(f"https://gtfsrt.prod.obanyc.com/vehiclePositions?key={BUS_KEY}"))
    for e in m.entity:
        v = e.vehicle
        if v.HasField("position"):
            buses.append([round(v.position.longitude, 5), round(v.position.latitude, 5), round(v.position.bearing), v.trip.route_id])

lines = []
for (rid, d), k in rep.items():
    if d == "N" and rid in routes:
        pts = shapes[k][::2] + [shapes[k][-1]]
        lines.append({"r": rid, "p": [[round(x, 5), round(y, 5)] for x, y in pts]})

stations = sorted({(round(v[0], 5), round(v[1], 5), v[2]) for k, v in stops.items() if k == v[3]})
out = {
    "t0": T0,
    "routes": {k: {"c": "#" + (v["route_color"] or "808183"), "n": v["route_short_name"]} for k, v in routes.items()},
    "trips": trips, "lines": lines, "stations": stations, "buses": buses,
    "alerts": {k: v[:2] for k, v in alerts_by_route.items()}, "elevators": ene,
}
open("map_data.js", "w").write("window.LEAVEBY_DATA=" + json.dumps(out, separators=(",", ":")) + ";")
print("trips", len(trips), "buses", len(buses), "alerts", len(alerts_by_route), "elevators out", len(ene), "bytes", os.path.getsize("map_data.js"))
