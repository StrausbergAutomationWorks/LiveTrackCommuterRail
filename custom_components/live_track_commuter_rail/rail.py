"""The railroad's rail lines, shipped with the integration (rail/<operator>.json.gz), for the
off-rail refusal (SSOT 7.10, Lee 2026-10-08). No Home Assistant imports.

Built by tools/build_rail.py from the FRA North American Rail Network Lines (NTAD, US DOT),
a US Government work in the public domain, clipped to 3 km around the railroad's own GTFS
shapes and simplified at 10 m. A railroad without a file gets no check, and every fix it
reports is published as before.

Since 2026-10-09 the railroad's own GTFS shapes count as rail too (RailCheck): NARN lacks
lines newer than it, such as NICTD's Monon Corridor south of Hammond.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import math
import os
import zipfile
from typing import Any, Callable

from saw_livetrack.rail import RailIndex

from .const import OFF_RAIL_M

RAIL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rail")
FORMAT = 1


def load(operator_id: str) -> RailIndex | None:
    """The railroad's rail, or None without a usable file. Blocking: run it in an executor."""
    path = os.path.join(RAIL_DIR, f"{operator_id}.json.gz")
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("format") != FORMAT:
        return None
    idx = RailIndex(doc.get("lines") or [])
    return idx if len(idx) else None


def check(idx: RailIndex) -> Callable[[float, float], bool]:
    """Fleet's on_rail: some rail within OFF_RAIL_M."""
    return lambda lat, lon: idx.near(lat, lon, OFF_RAIL_M)


# --- The railroad's own route lines (2026-10-09 00:20; SSOT 7.10) -------------
# NARN does not carry every line: NICTD's Monon Corridor south of Hammond, opened
# in 2025, is absent, and Monon train 1035 was refused on the box 0.2-0.5 m from
# NICTD's own published route and 2.0-2.3 km from any NARN track. So "on rail"
# is within OFF_RAIL_M of NARN track OR of the railroad's own GTFS shapes. The
# shapes come from the timetable each install downloads itself (statics.py); no
# operator data ships with the integration.

SHAPE_TOLERANCE_M = 10.0
_M_PER_DEG = 111195.0


def simplify(pl: list, tol: float) -> list:
    """Douglas-Peucker on a local flat projection; the first and last points stay."""
    if len(pl) < 3:
        return pl
    kx = math.cos(math.radians(pl[0][0])) * _M_PER_DEG
    xy = [(lon * kx, lat * _M_PER_DEG) for lat, lon in pl]
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


def shapes_indexed(raw: bytes) -> tuple[list[list[list[float]]], dict[str, list[int]]]:
    """(lines, {shape_id: [index of its line, 1 when that line is the shape reversed,
    else 0]}). The index lets an operator follow a shape in its own order (SSOT 9,
    SE Queensland's arrow) on the same deduplicated lines the off-rail check uses.

    The railroad's GTFS shapes as lines of [lat, lon]: by sequence, simplified at
    SHAPE_TOLERANCE_M, rounded to 5 decimals, duplicates (either direction) dropped.
    [] when the timetable has no shapes.txt. Keys and values are stripped (Metra
    writes a space after each comma). Blocking: run it in an executor."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    if "shapes.txt" not in z.namelist():
        return [], {}
    pts: dict[str, list] = {}
    with z.open("shapes.txt") as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig")):
            r = {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}
            try:
                pts.setdefault(r["shape_id"], []).append(
                    (float(r["shape_pt_sequence"]), float(r["shape_pt_lat"]), float(r["shape_pt_lon"])))
            except (KeyError, ValueError):
                continue
    out: list = []
    seen: dict[tuple, int] = {}
    index: dict[str, list[int]] = {}
    for sid in sorted(pts):
        pl = simplify([(a, b) for _, a, b in sorted(pts[sid])], SHAPE_TOLERANCE_M)
        q = []
        for a, b in pl:
            p = [round(a, 5), round(b, 5)]
            if not q or q[-1] != p:
                q.append(p)
        key = tuple(map(tuple, q))
        if len(q) < 2:
            continue
        if key in seen:
            index[sid] = [seen[key], 0]
            continue
        if key[::-1] in seen:
            index[sid] = [seen[key[::-1]], 1]
            continue
        seen[key] = len(out)
        index[sid] = [len(out), 0]
        out.append(q)
    return out, index


def trip_shapes(raw: bytes, index: dict[str, list[int]],
                keep: Any = None) -> dict[str, list[int]]:
    """{trip_id: [line, reversed]} from trips.txt and shapes_indexed's index, for the
    trips in `keep` (the distilled timetable's) or every trip when it is None. Ids
    stripped (Renfe pads them, Metra writes a space after each comma). A trip without
    a shape is left out. Blocking: run it in an executor."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    if "trips.txt" not in z.namelist() or not index:
        return {}
    out: dict[str, list[int]] = {}
    with z.open("trips.txt") as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig")):
            r = {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}
            tid, ix = r.get("trip_id"), index.get(r.get("shape_id", ""))
            if tid and ix is not None and (keep is None or tid in keep):
                out[tid] = [ix[0], ix[1]]
    return out


def shapes_from_zip(raw: bytes) -> list[list[list[float]]]:
    """The lines of shapes_indexed. Blocking: run it in an executor."""
    return shapes_indexed(raw)[0]


class RailCheck:
    """Fleet's on_rail: within OFF_RAIL_M of NARN track OR of the railroad's own shapes.

    Until the railroad's timetable has loaded (set_shapes never given one), nothing
    is refused: a line NARN lacks must not be judged on NARN alone. With neither
    NARN nor any shape, nothing is refused either.
    """

    def __init__(self, narn: RailIndex | None, distance_m: float = OFF_RAIL_M) -> None:
        self._narn = narn
        # The operator's own distance (Operator.off_rail_m): 300 m on US track, 1 km in
        # SE Queensland (SSOT 9.1).
        self._m = distance_m
        self._shapes: RailIndex | None = None
        self._key = None

    @property
    def shape_segments(self) -> int | None:
        return None if self._shapes is None else len(self._shapes)

    def set_shapes(self, static: dict | None) -> None:
        """Take the shapes from a distilled timetable; rebuilt only when it changes."""
        if not static or "rail_shapes" not in static:
            return
        key = static.get("fetched_at")
        if self._shapes is not None and key == self._key:
            return
        self._key = key
        self._shapes = RailIndex(static.get("rail_shapes") or [])

    def __call__(self, lat: float, lon: float) -> bool:
        if self._shapes is None:
            return True
        narn = self._narn is not None and len(self._narn) > 0
        if not narn and not len(self._shapes):
            return True
        if narn and self._narn.near(lat, lon, self._m):
            return True
        return self._shapes.near(lat, lon, self._m)
