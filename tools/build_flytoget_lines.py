"""Build Flytoget's lines from Vy's GTFS shapes (Lee 2026-11-08, Commuter Rail SSOT 12, decision 3).

Flytoget publishes 35 shapes of 121 points in all: straight lines between stations, which cannot keep a train on the
tracks. Vy's trains run the same tracks, and Vy's shapes follow them. For every pair of consecutive Flytoget stations
(parent StopPlaces) the line is cut from the Vy shape most used by Vy trains that stop at both stations ONE AFTER THE
OTHER (so an express pair takes the express track: Oslo S > Lillestrom adjacent means Romeriksporten, not the old
line through Grorud). A pair no Vy train makes adjacently is joined through ONE intermediate station where both halves
exist (Oslo S > Oslo lufthavn runs through Lillestrom on Gardermobanen). Each direction is built from its own trains;
with none, the other direction's line is reversed.

Deterministic: same inputs, same bytes (sorted keys, gzip mtime 0). Usage:
    python tools/build_flytoget_lines.py <rb_flt zip> <rb_vyg zip> <out .json.gz>
Data: Entur, NLOD 2.0 (see the file's "credit").
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import math
import sys
import zipfile
from collections import Counter, defaultdict

CREDIT = ("Contains data under the Norwegian licence for Open Government data (NLOD) distributed by Entur; "
          "Flytoget's lines cut from Vy's timetable shapes, modified")
MAX_STATION_OFF_M = 300.0      # a station farther than this from the shape: the shape does not serve it
BUS_VEHICLE_TYPE = "700"


def rows(z, name):
    with z.open(name) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")):
            yield {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}


def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742000.0 * math.asin(math.sqrt(min(1.0, h)))


def length(pts):
    return sum(hav(a, b) for a, b in zip(pts, pts[1:]))


def stations(z):
    """{stop_id: parent StopPlace}, {StopPlace: (lat, lon)}, {StopPlace: name}, {stop_id: vehicle_type}."""
    parent, coord, name, vtype = {}, {}, {}, {}
    for s in rows(z, "stops.txt"):
        sid = s["stop_id"]
        p = s.get("parent_station") or sid
        parent[sid] = p
        vtype[sid] = s.get("vehicle_type", "")
        if not s.get("parent_station"):
            coord[sid] = (float(s["stop_lat"]), float(s["stop_lon"]))
            name[sid] = s.get("stop_name", "")
    return parent, coord, name, vtype


def patterns(z, parent, vtype, rail_trip):
    """{trip_id: [StopPlace, ...]} for the trips rail_trip accepts, bus-quay trips left out."""
    seq = defaultdict(list)
    bus = set()
    for st in rows(z, "stop_times.txt"):
        tid = st["trip_id"]
        if not rail_trip(tid):
            continue
        if vtype.get(st["stop_id"]) == BUS_VEHICLE_TYPE:
            bus.add(tid)
        seq[tid].append((int(st["stop_sequence"]), parent.get(st["stop_id"], st["stop_id"])))
    return {t: [p for _, p in sorted(s)] for t, s in seq.items() if t not in bus}


def project(pts, q):
    """(index of the segment, fraction along it, metres off) of the point of the polyline nearest q (flat earth per
    segment: the segments are short)."""
    best = (0, 0.0, float("inf"))
    kx = math.cos(math.radians(q[0]))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        ax, ay, bx, by, qx, qy = a[1] * kx, a[0], b[1] * kx, b[0], q[1] * kx, q[0]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        f = 0.0 if L2 == 0 else max(0.0, min(1.0, ((qx - ax) * dx + (qy - ay) * dy) / L2))
        p = (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]))
        d = hav(p, q)
        if d < best[2]:
            best = (i, f, d)
    return best


def cut(pts, qa, qb):
    """The polyline from the point nearest qa to the point nearest qb, or None when either station is more than
    MAX_STATION_OFF_M from it or b comes before a."""
    ia, fa, da = project(pts, qa)
    ib, fb, db = project(pts, qb)
    if da > MAX_STATION_OFF_M or db > MAX_STATION_OFF_M or (ib, fb) <= (ia, fa):
        return None

    def at(i, f):
        a, b = pts[i], pts[i + 1]
        return (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]))

    return [at(ia, fa)] + pts[ia + 1:ib + 1] + [at(ib, fb)]


def main(flt_zip, vyg_zip, out_path):
    zf, zv = zipfile.ZipFile(flt_zip), zipfile.ZipFile(vyg_zip)
    fpar, fco, fname, fvt = stations(zf)
    fpat = patterns(zf, fpar, fvt, lambda t: True)
    need = sorted({(a, b) for p in fpat.values() for a, b in zip(p, p[1:])})
    vpar, vco, vname, vvt = stations(zv)
    vroutes = {r["route_id"]: r for r in rows(zv, "routes.txt")}
    vtrips = {t["trip_id"]: t for t in rows(zv, "trips.txt")
              if vroutes.get(t["route_id"], {}).get("route_type") in ("100", "101", "102", "103", "106", "109")
              and "BUS-" not in t["trip_id"]}
    vpat = patterns(zv, vpar, vvt, lambda t: t in vtrips)
    adj = defaultdict(Counter)        # (A, B) -> Counter(shape_id) over Vy trips stopping at A then B
    for tid, p in vpat.items():
        sid = vtrips[tid].get("shape_id")
        if sid:
            for a, b in zip(p, p[1:]):
                adj[(a, b)][sid] += 1
    want_shapes = set()
    plan = {}
    for a, b in need:
        if (a, b) in adj:
            plan[(a, b)] = [(a, b)]
        else:
            vias = sorted(x for (p, x) in adj if p == a and (x, b) in adj)
            if vias:
                plan[(a, b)] = [(a, vias[0]), (vias[0], b)]
        for leg in plan.get((a, b), []):
            want_shapes.update(s for s, _ in adj[leg].most_common(3))
    shapes = defaultdict(list)
    for r in rows(zv, "shapes.txt"):
        if r["shape_id"] in want_shapes:
            shapes[r["shape_id"]].append((int(r["shape_pt_sequence"]), float(r["shape_pt_lat"]), float(r["shape_pt_lon"])))
    shapes = {k: [(la, lo) for _, la, lo in sorted(v)] for k, v in shapes.items()}

    def leg_line(a, b):
        for sid, _ in adj[(a, b)].most_common(3):
            line = cut(shapes[sid], vco.get(a) or fco[a], vco.get(b) or fco[b])
            if line is not None:
                return line, sid
        return None, None

    pairs, report = {}, []
    for a, b in need:
        legs = plan.get((a, b))
        line, used = [], []
        for la, lb in legs or []:
            got, sid = leg_line(la, lb)
            if got is None:
                line = None
                break
            line += got if not line else got[1:]
            used.append(sid)
        label = "%s > %s" % (fname.get(a, a), fname.get(b, b))
        if not legs or line is None:
            report.append("MISSING %s (%s>%s)" % (label, a, b))
            continue
        straight = hav(fco[a], fco[b])
        pairs["%s>%s" % (a, b)] = [[round(la, 6), round(lo, 6)] for la, lo in line]
        report.append("%s: %d points, %.0f m along, %.0f m straight, via %s" % (
            label, len(line), length(line), straight, " + ".join(used)))
    for key in list(pairs):
        a, b = key.split(">")
        rev = "%s>%s" % (b, a)
        if rev not in pairs and (b, a) in set(need):
            pairs[rev] = pairs[key][::-1]
            report.append("REVERSED for %s" % rev)
    feed = next(rows(zv, "feed_info.txt"), {})
    doc = {"credit": CREDIT, "built_from": {"vy_feed_version": feed.get("feed_version", ""),
                                            "vy_zip": vyg_zip.replace("\\", "/").rsplit("/", 1)[-1],
                                            "flytoget_zip": flt_zip.replace("\\", "/").rsplit("/", 1)[-1]},
           "stations": {k: fname[k] for k in sorted({x for ab in need for x in ab})},
           "pairs": dict(sorted(pairs.items()))}
    raw = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with open(out_path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0, filename="") as g:
            g.write(raw)
    print("\n".join(report))
    print("pairs %d of %d needed; %d bytes json, written %s" % (len(pairs), len(need), len(raw), out_path))


if __name__ == "__main__":
    main(*sys.argv[1:4])
