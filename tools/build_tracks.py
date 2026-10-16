"""Build custom_components/live_track_commuter_rail/rail/<operator>_tracks.json.gz: the
railroad's track network, for the card's track_path (tracknet.py; 06_MAP_CONTRACT.md D3c-v).

Finland (vr_lahijunat; SSOT 8.3, backlog 290). Source: Fintraffic's infra-api tracks
(raiteet, https://rata.digitraffic.fi/infra-api/), CC BY 4.0, credit "Source: Fintraffic /
digitraffic.fi", MODIFIED: only the tracks listed in tools/fi_commuter_tracks.txt (by the
infra-api's own id, tunniste) are kept, joined where they meet, split there, simplified at
SIMPLIFY_M and rounded to 6 decimals.

The list is the tracks Finland's commuter trains used in capture round 1 (2026-10-11
08:39Z to 10-13 12:00Z; bin\\ltcr290_cutids.py): 846 of 4,903. A network built from them
alone routed every one of 152,429 pairs of consecutive commuter fixes as the whole
country's network did (5 differed, by at most 6 m; none lost).

Why join and split (measured 2026-10-16 on the whole country, bin\\ltcr290_topo.txt): the
infra-api's tracks do not all end where they meet. 3,063 track ends lie on another
track's interior, where a switch's diverging track leaves the through track.
  1. ends within JOIN_M of each other are made one point;
  2. a track end within JOIN_M of another track's interior is inserted into it;
  3. every track is split at those points, so lines meet only at their ends;
  4. each line is simplified at SIMPLIFY_M and rounded to 6 decimals.

Run by a maintainer before a release, never by Home Assistant:
    pip install requests
    python tools/build_tracks.py [--source raiteet.geojson]
Without --source it fetches the whole country (about 1.7 MB gzipped, 12 MB of JSON) with
the shared client's identifying header. Output is deterministic for the same input:
lines in track-list order, gzip timestamp 0.
"""
from __future__ import annotations

import argparse
import datetime
import gzip
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
COMPONENT = os.path.join(os.path.dirname(HERE), "custom_components", "live_track_commuter_rail")
sys.path.insert(0, COMPONENT)
from tracknet import cells, simplify  # noqa: E402

OPERATOR = "vr_lahijunat"
IDS = os.path.join(HERE, "fi_commuter_tracks.txt")
URL = ("https://rata.digitraffic.fi/infra-api/0.8/raiteet.geojson?srsName=epsg:4326"
       "&bbox=59.5,19.0,70.2,31.7&propertyName=tunniste,tunnus,paaraide,geometria")
HEADERS = {"Digitraffic-User": "StrausbergAutomationWorks/saw-livetrack",
           "Accept-Encoding": "gzip"}
CREDIT = ("Source: Fintraffic / digitraffic.fi, CC BY 4.0, modified "
          "(infra-api tracks: a subset, joined, split and simplified)")
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
# The flat scale tracknet uses for this network (its measurement used 60.5 N).
LAT0 = 60.5

JOIN_M = 1.0
SIMPLIFY_M = 0.5
R = 6371000.0


def read(path: str) -> list[dict]:
    """[{'id', 'name', 'main', 'pts': [(lat, lon), ...]}] from a raiteet geojson."""
    d = json.load(open(path, encoding="utf-8"))
    out = []
    for f in d["features"]:
        g = f.get("geometry") or {}
        parts = g.get("coordinates") or []
        if g.get("type") == "LineString":
            parts = [parts]
        p = f.get("properties") or {}
        for ln in parts:
            pts = [(float(a), float(b)) for a, b in ln]
            if len(pts) >= 2:
                out.append({"id": p.get("tunniste"), "name": p.get("tunnus"),
                            "main": bool(p.get("paaraide")), "pts": pts})
    return out


def split(tracks: list[dict], origin: list | None = None) -> list[list[tuple[float, float]]]:
    """Lines meeting only at their ends. `origin`, when given, receives the index in
    `tracks` of each line's track, in step with the lines returned."""
    lat0 = sum(t["pts"][0][0] for t in tracks) / len(tracks)
    kx = math.cos(math.radians(lat0)) * R * math.pi / 180
    ky = R * math.pi / 180
    xy = lambda p: (p[1] * kx, p[0] * ky)
    C = 10.0
    # 1. ends within JOIN_M: one point (the first seen).
    ends = []
    for ti, t in enumerate(tracks):
        ends.append((ti, 0))
        ends.append((ti, len(t["pts"]) - 1))
    grid = defaultdict(list)
    canon: dict[tuple[int, int], tuple[float, float]] = {}
    for ti, k in ends:
        p = tracks[ti]["pts"][k]
        x, y = xy(p)
        hit = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for q in grid.get((int(x // C) + dx, int(y // C) + dy), ()):
                    if math.dist((x, y), xy(q)) <= JOIN_M:
                        hit = q
                        break
                if hit:
                    break
            if hit:
                break
        if hit is None:
            grid[(int(x // C), int(y // C))].append(p)
            canon[(ti, k)] = p
        else:
            canon[(ti, k)] = hit
    for (ti, k), p in canon.items():
        tracks[ti]["pts"][k] = p
    # how many tracks share each end point
    share = defaultdict(int)
    for (ti, k), p in canon.items():
        share[p] += 1
    # 2. a lone end on another track's interior: insert it there.
    S = 50.0
    sgrid = defaultdict(list)
    for ti, t in enumerate(tracks):
        P = [xy(p) for p in t["pts"]]
        for j, (u, v) in enumerate(zip(P, P[1:])):
            for c in cells(u, v, S):
                sgrid[c].append((ti, j))
    inserts = defaultdict(list)  # ti -> [(j, t, point)]
    owners = defaultdict(set)    # point -> tracks having it as an end
    for (ti, k), p in canon.items():
        owners[p].add(ti)
    for p, own in owners.items():
        x, y = xy(p)
        best: dict[int, tuple] = {}  # per other track, its nearest segment
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for tj, j in sgrid.get((int(x // S) + dx, int(y // S) + dy), ()):
                    if tj in own:
                        continue
                    a, b = xy(tracks[tj]["pts"][j]), xy(tracks[tj]["pts"][j + 1])
                    vx, vy = b[0] - a[0], b[1] - a[1]
                    l2 = vx * vx + vy * vy
                    u = 0.0 if l2 == 0 else max(0.0, min(1.0, ((x - a[0]) * vx + (y - a[1]) * vy) / l2))
                    d = math.hypot(x - a[0] - u * vx, y - a[1] - u * vy)
                    if d <= JOIN_M and (tj not in best or d < best[tj][0]):
                        best[tj] = (d, j, u)
        for tj, (_, j, u) in best.items():
            inserts[tj].append((j, u, p))
    # 3. split
    lines = []

    def emit(line, ti):
        if len(line) >= 2:
            lines.append(line)
            if origin is not None:
                origin.append(ti)

    for ti, t in enumerate(tracks):
        pts = t["pts"]
        cuts = defaultdict(list)
        for j, u, p in inserts.get(ti, ()):
            cuts[j].append((u, p))
        cur = [pts[0]]
        for j in range(len(pts) - 1):
            for u, p in sorted(cuts.get(j, ()), key=lambda c: c[0]):
                if p != cur[-1]:
                    cur.append(p)
                emit(cur, ti)
                cur = [p]
            nxt = pts[j + 1]
            if nxt != cur[-1]:
                cur.append(nxt)
            # an interior vertex that is another track's end
            if 0 < j + 1 < len(pts) - 1 and share.get(nxt, 0) >= 1:
                emit(cur, ti)
                cur = [nxt]
        emit(cur, ti)
    return lines


def simplify_round(lines, tol=SIMPLIFY_M, origin=None):
    """Each line simplified at tol metres and rounded to 6 decimals; ends kept. A line
    that collapses to one point is dropped, and with it its entry in `origin`."""
    lat0 = sum(l[0][0] for l in lines) / len(lines)
    kx = math.cos(math.radians(lat0)) * R * math.pi / 180
    ky = R * math.pi / 180
    out, org = [], []
    for k, ln in enumerate(lines):
        s = simplify(ln, tol, kx, ky)
        q = []
        for a, b in s:
            p = [round(a, 6), round(b, 6)]
            if not q or q[-1] != p:
                q.append(p)
        if len(q) >= 2:
            out.append(q)
            if origin is not None:
                org.append(origin[k])
    if origin is not None:
        origin[:] = org
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="a saved raiteet geojson (srsName epsg:4326)")
    args = ap.parse_args()
    if args.source:
        src = args.source
        fetched = datetime.datetime.fromtimestamp(os.path.getmtime(src), datetime.timezone.utc)
    else:
        import requests
        r = requests.get(URL, headers=HEADERS, timeout=600)
        r.raise_for_status()
        src = os.path.join(HERE, "_raiteet.geojson")
        with open(src, "wb") as fh:
            fh.write(r.content)
        fetched = datetime.datetime.now(datetime.timezone.utc)
    keep = [ln.strip() for ln in open(IDS, encoding="utf-8")
            if ln.strip() and not ln.startswith("#")]
    order = {tid: k for k, tid in enumerate(keep)}
    tracks = [t for t in read(src) if t["id"] in order]
    tracks.sort(key=lambda t: order[t["id"]])
    missing = len(set(keep) - {t["id"] for t in tracks})
    lines = simplify_round(split(tracks))
    doc = {
        "format": 1,
        "operator": OPERATOR,
        "credit": CREDIT,
        "license": LICENSE_URL,
        "source": "https://rata.digitraffic.fi/infra-api/0.8/raiteet",
        "fetched": fetched.strftime("%Y-%m-%d"),
        "lat0": LAT0,
        "lines": lines,
    }
    raw = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    out = os.path.join(COMPONENT, "rail", f"{OPERATOR}_tracks.json.gz")
    with open(out, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", compresslevel=9, mtime=0) as gz:
            gz.write(raw)
    print(f"tracks kept {len(tracks)} of {len(keep)} listed ({missing} not in the source); "
          f"lines {len(lines)}, points {sum(len(l) for l in lines)}; {os.path.getsize(out)} b -> {out}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
