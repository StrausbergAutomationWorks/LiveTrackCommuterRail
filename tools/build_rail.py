"""Build custom_components/live_track_commuter_rail/rail/<operator>.json.gz: the rail lines a
railroad's trains run on, for the off-rail refusal (saw_livetrack.rail, Fleet's on_rail).

Source: the FRA North American Rail Network (NARN) Lines, published in the US DOT's
National Transportation Atlas Database (NTAD); a US Government work in the public domain.
Kept: every NARN line within CORRIDOR_M of the railroad's own GTFS shapes, except
abandoned, out-of-service and rail-banked track (NET A, X, R); simplified at TOLERANCE_M
(Douglas-Peucker) and rounded to 5 decimals (about 1 m).

Why all rail and not the railroad's own shapes (measured 2026-10-08 on 9,109 real Metra
and NICTD fixes): a shape ends at the last station, so a layover 1.5 km past a terminal
reads as off the line, and a train on another line's approach reads 787 m off its own;
every real fix lay within 210 m of NARN track. Clipping to 3 km and simplifying at 10 m
moved the farthest real fix by 2 m.

Run by a maintainer before a release, never by Home Assistant:
    pip install requests "saw-livetrack>=0.2.4"
    python tools/build_rail.py [operator id ...]
It reads each railroad's public GTFS static zip (never a realtime key) and NARN's
FeatureServer, PAGED: the server stops at 2,000 records without saying so. Output is
deterministic for the same inputs: features in OBJECTID order, gzip timestamp 0.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import importlib
import importlib.machinery
import importlib.util
import io
import json
import math
import os
import sys
import time
import zipfile

import requests
from saw_livetrack.rail import RailIndex

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMP = os.path.join(ROOT, "custom_components", "live_track_commuter_rail")
OUT_DIR = os.path.join(COMP, "rail")
NARN = ("https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/"
        "NTAD_North_American_Rail_Network_Lines/FeatureServer/0")
CORRIDOR_M = 3000
TOLERANCE_M = 10
SKIP_NET = ("A", "X", "R")
PAGE = 2000
UA = "LiveTrackCommuterRail build_rail (+https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail)"
M_PER_DEG = 111195.0


def operators():
    """The component's operator registry, without importing Home Assistant."""
    if "ltcr" not in sys.modules:
        spec = importlib.machinery.ModuleSpec("ltcr", None, is_package=True)
        pkg = importlib.util.module_from_spec(spec)
        pkg.__path__ = [COMP]
        sys.modules["ltcr"] = pkg
    return importlib.import_module("ltcr.operators").OPERATORS


def shapes(raw: bytes) -> list[list[tuple[float, float]]]:
    z = zipfile.ZipFile(io.BytesIO(raw))
    pts: dict[str, list] = {}
    with z.open("shapes.txt") as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig")):
            r = {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}
            pts.setdefault(r["shape_id"], []).append(
                (float(r["shape_pt_sequence"]), float(r["shape_pt_lat"]), float(r["shape_pt_lon"])))
    return [[(a, b) for _, a, b in sorted(v)] for _, v in sorted(pts.items())]


def narn(bbox: tuple[float, float, float, float]) -> list[dict]:
    """Every NARN feature intersecting bbox (west, south, east, north), in OBJECTID order."""
    feats, off = [], 0
    while True:
        r = requests.get(NARN + "/query", headers={"User-Agent": UA}, timeout=120, params={
            "where": "1=1", "geometry": ",".join(f"{v:.5f}" for v in bbox),
            "geometryType": "esriGeometryEnvelope", "inSR": 4326, "spatialRel": "esriSpatialRelIntersects",
            "outFields": "OBJECTID,NET", "returnGeometry": "true", "outSR": 4326, "f": "geojson",
            "orderByFields": "OBJECTID", "resultOffset": off, "resultRecordCount": PAGE})
        r.raise_for_status()
        page = r.json()
        if "error" in page:
            raise RuntimeError(f"NARN answered an error: {page['error']}")
        got = page.get("features", [])
        feats += got
        off += len(got)
        more = (page.get("properties") or {}).get("exceededTransferLimit") or page.get("exceededTransferLimit")
        if len(got) < PAGE and not more:
            break
        time.sleep(1)
    feats.sort(key=lambda f: (f.get("properties") or {}).get("OBJECTID") or 0)
    return feats


def lines_of(feats: list[dict]) -> list[list[tuple[float, float]]]:
    out = []
    for f in feats:
        if (f.get("properties") or {}).get("NET") in SKIP_NET:
            continue
        geo = f.get("geometry") or {}
        parts = geo.get("coordinates") or []
        parts = parts if geo.get("type") == "MultiLineString" else [parts] if geo.get("type") == "LineString" else []
        for part in parts:
            pl = [(c[1], c[0]) for c in part]
            if len(pl) > 1:
                out.append(pl)
    return out


def clip(lines, corridor: RailIndex):
    """Runs of segments with at least one end within CORRIDOR_M of the railroad's shapes."""
    out = []
    for pl in lines:
        near = [corridor.near(a, b, CORRIDOR_M) for a, b in pl]
        cur = []
        for i in range(len(pl) - 1):
            if near[i] or near[i + 1]:
                cur = cur or [pl[i]]
                cur.append(pl[i + 1])
            elif cur:
                out.append(cur)
                cur = []
        if cur:
            out.append(cur)
    return out


def simplify(pl, tol: float):
    """Douglas-Peucker on a local flat projection."""
    if len(pl) < 3:
        return pl
    kx = math.cos(math.radians(pl[0][0])) * M_PER_DEG
    xy = [(lon * kx, lat * M_PER_DEG) for lat, lon in pl]
    keep = [False] * len(pl)
    keep[0] = keep[-1] = True
    stack = [(0, len(pl) - 1)]
    while stack:
        i, j = stack.pop()
        (ax, ay), (bx, by) = xy[i], xy[j]
        dx, dy = bx - ax, by - ay
        den = dx * dx + dy * dy
        best, bi = -1.0, None
        for k in range(i + 1, j):
            px, py = xy[k]
            t = 0.0 if den == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / den))
            d = math.hypot(px - ax - t * dx, py - ay - t * dy)
            if d > best:
                best, bi = d, k
        if bi is not None and best > tol:
            keep[bi] = True
            stack += [(i, bi), (bi, j)]
    return [p for p, k in zip(pl, keep) if k]


def round5(lines):
    out = []
    for pl in lines:
        q = []
        for a, b in pl:
            p = [round(a, 5), round(b, 5)]
            if not q or q[-1] != p:
                q.append(p)
        if len(q) > 1:
            out.append(q)
    return out


def build(op) -> dict:
    raw = requests.get(op.static_url, headers={"User-Agent": UA}, timeout=120).content
    own = shapes(raw)
    lats = [p[0] for pl in own for p in pl]
    lons = [p[1] for pl in own for p in pl]
    dlat = CORRIDOR_M / M_PER_DEG
    dlon = CORRIDOR_M / (M_PER_DEG * math.cos(math.radians((min(lats) + max(lats)) / 2)))
    bbox = (min(lons) - dlon, min(lats) - dlat, max(lons) + dlon, max(lats) + dlat)
    feats = narn(bbox)
    kept = round5([simplify(pl, TOLERANCE_M) for pl in clip(lines_of(feats), RailIndex(own))])
    return {
        "format": 1,
        "operator": op.id,
        "source": "FRA North American Rail Network Lines (NTAD, US DOT); US Government work, public domain",
        "source_url": NARN,
        "built": time.strftime("%Y-%m-%d", time.gmtime()),
        "corridor_m": CORRIDOR_M,
        "tolerance_m": TOLERANCE_M,
        "net_excluded": list(SKIP_NET),
        "narn_features": len(feats),
        "lines": kept,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("ops", nargs="*", help="operator ids (default: every operator with a static timetable)")
    args = ap.parse_args()
    ops = operators()
    chosen = args.ops or [k for k, o in ops.items() if o.static_url]
    os.makedirs(OUT_DIR, exist_ok=True)
    for oid in chosen:
        doc = build(ops[oid])
        data = json.dumps(doc, separators=(",", ":")).encode("utf-8")
        path = os.path.join(OUT_DIR, f"{oid}.json.gz")
        buf = io.BytesIO()
        with gzip.GzipFile(filename="", mode="wb", fileobj=buf, compresslevel=9, mtime=0) as gz:
            gz.write(data)
        with open(path, "wb") as fh:
            fh.write(buf.getvalue())
        n = sum(len(pl) for pl in doc["lines"])
        print(f"{oid}: {doc['narn_features']} NARN features, {len(doc['lines'])} lines, {n} points, "
              f"{len(data)} b JSON, {len(buf.getvalue())} b gzip -> {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
