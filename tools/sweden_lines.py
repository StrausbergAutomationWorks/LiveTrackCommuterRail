"""Build Sweden's shipped commuter route lines (Trafikverket's station pairs on OpenStreetMap's track) and the end-city
table the direction rule reads. Run by hand, never by Home Assistant; the outputs are committed as
custom_components/live_track_commuter_rail/rail/sweden_lines.json.gz and rail/sweden_ends.json.

    python tools/sweden_lines.py lines OSM.json STATIONS.json ANN.json.gz [...] --routing IR/tools/renfe_spain_lines.py
                                       [--report R.txt] [--out F]
    python tools/sweden_lines.py ends ENDS.json ANN.json.gz [...] [--out F]

Lee 2026-11-10 00:33 CST (backlog 327): Sweden's commuter side here, "Lines from OSM station pairs, shipped", as Live
Track Intercity Rail's Swedish lines (its tools/sweden_lines.py, which this follows). Sweden's timetable has no shapes,
so every station pair the commuter trains run between is routed once on OpenStreetMap's track, and the runtime
assembles each run's line from them (sweden_lines.py). (c) OpenStreetMap contributors, ODbL 1.0 (the map's credit
line carries it).

INPUTS. OSM.json: OpenStreetMap's Swedish rail, as Intercity Rail's `pull` writes it (the same file serves both).
STATIONS.json: saw_livetrack.trafikverket's stations file ({"stations": {signature: {"name", "lat", "lon",
"country"}}}). ANN.json.gz: TrainAnnouncement rows (a JSON list, one or more Stockholm days). Trafikverket, CC0.
ENDS.json: Intercity Rail's data/sweden_ends.json (every station's Statistics Sweden tätort and its population, SCB CC0
1.0), cut here to the signatures this integration's trips start or end at, and the hubs.

THE PAIRS: every run the shared client routes to the COMMUTER consumer (saw_livetrack.trafikverket.route_of: SL
Pendeltåg, Västtågen's pendeltåg, Arlanda Express), split into its trips as the client splits them, its rows in time
order, consecutive distinct signatures, public or not (Arlanda Express advertises no row at all).

THE ROUTING is Live Track Intercity Rail's tools/renfe_spain_lines.py (Graph, joins, candidate snapping, A*), loaded
from that integration's clone (--routing): it imports its own component's modules, so a copy here would not run.
No gauge. A pair with no route, or whose route is over DETOUR_X times its straight line and DETOUR_EXTRA_M
longer, ships no line: the runtime keeps the straight line for that leg, and the report lists each one to be read.
Lines are simplified by Douglas-Peucker at DP_M.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import gzip
import hashlib
import importlib.util
import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAIL = ROOT / "custom_components" / "live_track_commuter_rail" / "rail"
DATA_VERSION = 1
DP_M = 15.0
DETOUR_X = 3.0
DETOUR_EXTRA_M = 10000.0
CONSUMER = "commuter"
# The hubs the direction rule names besides the larger end city (operators/sweden.py HUBS).
HUBS = ("Cst", "Sci")


def _renfe_tool(path):
    spec = importlib.util.spec_from_file_location("renfe_spain_lines_tool", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def patterns(ann_paths, route_of, call_record, split_trips):
    """{signature tuple: trips} of every commuter run in the files, and the runs by brand."""
    runs = collections.defaultdict(list)
    for path in ann_paths:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            rows = json.load(fh)
        for r in rows:
            k = ((r.get("AdvertisedTrainIdent") or "").strip(), (r.get("ScheduledDepartureDateTime") or "")[:10])
            runs[k].append(r)
    pats = collections.Counter()
    brands = collections.Counter()
    for k, rows in runs.items():
        rows.sort(key=lambda r: (r.get("AdvertisedTimeAtLocation") or "", r.get("ActivityType") != "Ankomst"))
        route = route_of(rows)
        if not route or route[0] != CONSUMER:
            continue
        brands[route[1]] += 1
        calls = [call_record(r) for r in rows]
        for trip in split_trips(calls):
            sigs = []
            for c in trip:
                if c["sig"] and (not sigs or sigs[-1] != c["sig"]):
                    sigs.append(c["sig"])
            pats[tuple(sigs)] += 1
    return pats, brands


def pair_key(a, b):
    lo, hi = sorted((a, b))
    return f"{lo}|{hi}"


def encode(points):
    out, pla, plo = [], 0, 0
    for la, lo in points:
        a, b = round(la * 1e5), round(lo * 1e5)
        out += [a - pla, b - plo]
        pla, plo = a, b
    return out


def build(osm_path, stations_path, ann_paths, log, routing):
    from saw_livetrack.trafikverket import call_record, route_of, split_trips  # saw-livetrack 0.2.31 or later
    renfe = _renfe_tool(routing)
    t0 = time.time()
    osm_raw = open(osm_path, "rb").read()
    osm = json.loads(gzip.decompress(osm_raw) if osm_path.endswith(".gz") else osm_raw)
    g = renfe.Graph(osm, log)
    st = json.load(open(stations_path, encoding="utf-8"))["stations"]
    g.stops = {s: (v["lat"], v["lon"], v["name"]) for s, v in st.items()}
    pats, brands = patterns(ann_paths, route_of, call_record, split_trips)
    log("announcement files", [os.path.basename(p) for p in ann_paths], "commuter runs", sum(pats.values()),
        "patterns", len(pats), "by brand", dict(brands))
    pairs = sorted({tuple(sorted((a, b))) for p in pats for a, b in zip(p, p[1:])
                    if a != b and a in g.stops and b in g.stops})
    unknown = sorted({s for p in pats for s in p if s not in g.stops})
    log("distinct station pairs", len(pairs), "signatures with no station", unknown)
    lines, dropped, failed = {}, [], collections.Counter()
    ratios = []
    for a, b in pairs:
        r = g.route(a, b, None)
        straight = renfe.hav(g.stops[a][:2], g.stops[b][:2])
        if r is None:
            failed[g.fails.get((a, b), "?")] += 1
            dropped.append((a, b, g.stops[a][2], g.stops[b][2], round(straight), "no route: " + g.fails.get((a, b), "?")))
            continue
        _, length, nodes, _ = r
        if len(nodes) < 2:
            failed["one node"] += 1
            continue
        if length > DETOUR_X * straight + DETOUR_EXTRA_M:
            dropped.append((a, b, g.stops[a][2], g.stops[b][2], round(straight), "detour %d m" % round(length)))
            continue
        if straight > 500:
            ratios.append(length / straight)
        pts = renfe.dp([g.pts[i] for i in nodes], DP_M)
        lines[pair_key(a, b)] = [round(length, 1), encode(pts)]
    ratios.sort()
    q = lambda f: round(ratios[min(len(ratios) - 1, int(f * len(ratios)))], 2) if ratios else None
    log("pairs with a line", len(lines), "of", len(pairs), "failed", dict(failed), "dropped (straight at runtime)",
        len(dropped))
    log("line length over straight line p50/p90/p99/max", [q(.5), q(.9), q(.99)], round(ratios[-1], 2) if ratios else None)
    for d in dropped:
        log("REVIEW straight leg:", d)
    legs_total = sum(n * (len(p) - 1) for p, n in pats.items())
    legs_lined = sum(n * sum(1 for a, b in zip(p, p[1:]) if pair_key(a, b) in lines) for p, n in pats.items())
    log("run legs with a shipped line", legs_lined, "of", legs_total, f"({100 * legs_lined / max(1, legs_total):.1f}%)")
    meta = {"built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "osm_base": (osm.get("osm3s") or {}).get("timestamp_osm_base"),
            "osm_sha256": hashlib.sha256(osm_raw).hexdigest(),
            "announcements": [os.path.basename(p) for p in ann_paths],
            "consumer": CONSUMER,
            "licence": "ODbL 1.0: (c) OpenStreetMap contributors, openstreetmap.org/copyright",
            "rules": {"join_m": renfe.JOIN_M, "cand_m": renfe.CAND_M, "dp_m": DP_M,
                      "detour": [DETOUR_X, DETOUR_EXTRA_M]},
            "pairs": len(pairs), "lines": len(lines), "points": sum(len(v[1]) // 2 for v in lines.values())}
    log("seconds", round(time.time() - t0))
    return {"v": DATA_VERSION, "meta": meta, "lines": lines}


def ends(ends_path, ann_paths, log):
    """Intercity Rail's end-city table cut to the signatures a commuter trip starts or ends at, and the hubs."""
    from saw_livetrack.trafikverket import call_record, route_of, split_trips
    full = json.load(open(ends_path, encoding="utf-8"))
    pats, _ = patterns(ann_paths, route_of, call_record, split_trips)
    want = {p[0] for p in pats if p} | {p[-1] for p in pats if p} | set(HUBS)
    table = full.get("ends") or {}
    kept = {s: table[s] for s in sorted(want) if s in table}
    log("end signatures", len(want), "in the table", len(kept), "missing", sorted(want - set(kept)))
    out = {k: v for k, v in full.items() if k != "ends"}
    out["cut"] = ("cut by tools/sweden_lines.py ends to the signatures Live Track Commuter Rail's Swedish trips start "
                  "or end at, and the hubs")
    out["ends"] = kept
    return out


def write_gz(obj, path):
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=True, sort_keys=True).encode("ascii")
    with open(path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", compresslevel=9, mtime=0) as gz:
            gz.write(raw)
    return len(raw), os.path.getsize(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p2 = sub.add_parser("lines")
    p2.add_argument("osm")
    p2.add_argument("stations")
    p2.add_argument("ann", nargs="+")
    p2.add_argument("--out", default=str(RAIL / "sweden_lines.json.gz"))
    p2.add_argument("--report")
    p2.add_argument("--routing", required=True,
                    help="Live Track Intercity Rail's tools/renfe_spain_lines.py, in its clone (it imports that "
                         "component's own modules, so it runs from there)")
    p3 = sub.add_parser("ends")
    p3.add_argument("ends")
    p3.add_argument("ann", nargs="+")
    p3.add_argument("--out", default=str(RAIL / "sweden_ends.json"))
    a = ap.parse_args(argv)
    rep = open(a.report, "w", encoding="utf-8") if getattr(a, "report", None) else None

    def log(*x):
        line = " ".join(str(v) for v in x)
        print(line.encode("ascii", "backslashreplace").decode("ascii"), flush=True)
        if rep:
            print(line, file=rep, flush=True)
    if a.cmd == "lines":
        out = build(a.osm, a.stations, a.ann, log, a.routing)
        raw, gz = write_gz(out, a.out)
        log("wrote", a.out, "json", raw, "bytes, gzip", gz, "bytes")
    else:
        out = ends(a.ends, a.ann, log)
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=0, sort_keys=True)
            fh.write("\n")
        log("wrote", a.out)


if __name__ == "__main__":
    main()
