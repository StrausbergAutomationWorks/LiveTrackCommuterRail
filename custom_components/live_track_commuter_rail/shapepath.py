"""`track_path` along the trip's OWN shape, for a railroad that ships no track network
(06_MAP_CONTRACT.md D3c-v). No Home Assistant imports.

Lee 2026-10-20: "A train cannot exist off of the tracks." Before this only Finland sent the
card a way along the tracks (tracknet, from its shipped network); every other railroad's
markers slid in a straight line between fixes and cut across the city. MEASURED on the
box 2026-10-20 (bin\\ltcr_shape_look.py, .txt; pictures ltmc_star_pics\\shape_*.png): 47
Madrid moves, every fix a few metres from its trip's shape, the straight slide p50 114 m,
p90 581 m, at worst 1.9 km away from it.

The trip's shape is the railroad's GTFS shape as the timetable keeps it (rail.shapes_indexed:
simplified at 10 m, 5 decimals; `trip_shapes` maps a trip to [line, reversed]). Both fixes
are projected onto it; the new one only within reach of the old one along the shape, either
way, so a line that loops or doubles back is never cut across. The way between them is the
shape's own points, beginning at the old position and ending exactly at the new one. No way
(None, the card slides straight as before) when the trip has no shape, either fix is farther
than SNAP_M from it, or the train moved less than MIN_MOVE_M along it.

MEASURED on capture round 1 (bin\\ltcr_shape_replay.run1.txt): the shape's ORDER is
not the train's direction - Renfe gives both directions of a line one shape (every C5 trip
runs 10_C5), and 49,515 of 95,406 moves were refused when the new fix had to be ahead; and
no speed limit - Renfe's modelled positions catch up in jumps (4,168 refused over 200 km/h),
and along the trip's own shape a long way is still on the track.
"""

from __future__ import annotations

import math
from typing import Any, Iterable

from .tracknet import MAX_POINTS, PATH_TOLERANCE_M, simplify

_K = 6371008.8 * math.pi / 180
# A fix farther than this from its trip's shape is not routed: the shapes are kept
# simplified at 10 m, and Metra's and NICTD's fixes are GPS, not points on the shape.
SNAP_M = 50.0
# Under this, no path: the card's straight slide is the same thing.
MIN_MOVE_M = 5.0
# The new fix is looked for up to this many times the straight distance along the shape
# either side of the old one, and at least this far beyond it (tracknet's limits).
DETOUR_FACTOR = 3.0
DETOUR_MIN_M = 1000.0


class Line:
    """One shape with distance along it, on a local flat projection."""

    def __init__(self, pts: list) -> None:
        lat0 = math.radians(sum(p[0] for p in pts) / len(pts))
        self.kx = _K * math.cos(lat0)
        self.ky = _K
        self.pts = [(p[0], p[1]) for p in pts]
        self.x = [p[1] * self.kx for p in pts]
        self.y = [p[0] * _K for p in pts]
        self.cum = [0.0]
        for i in range(1, len(pts)):
            self.cum.append(self.cum[-1] + math.hypot(self.x[i] - self.x[i - 1],
                                                      self.y[i] - self.y[i - 1]))
        self.length = self.cum[-1]

    def project(self, lat: float, lon: float, lo: float = -math.inf,
                hi: float = math.inf) -> tuple[float, float] | None:
        """(metres along, metres off) of the nearest point of the shape between lo and hi
        metres along it; None when that stretch is empty."""
        px, py = lon * self.kx, lat * _K
        best = None
        for i in range(1, len(self.x)):
            a, b = self.cum[i - 1], self.cum[i]
            if b < lo or a > hi:
                continue
            ax, ay = self.x[i - 1], self.y[i - 1]
            dx, dy = self.x[i] - ax, self.y[i] - ay
            seg = b - a
            t = 0.0 if seg == 0 else ((px - ax) * dx + (py - ay) * dy) / (seg * seg)
            t_lo = 0.0 if seg == 0 else max(0.0, (lo - a) / seg)
            t_hi = 1.0 if seg == 0 else min(1.0, (hi - a) / seg)
            t = max(t_lo, min(t_hi, t))
            off = math.hypot(px - ax - t * dx, py - ay - t * dy)
            if best is None or off < best[1]:
                best = (a + t * seg, off)
        return best

    def between(self, s0: float, s1: float) -> list[tuple[float, float]]:
        """The shape's own points strictly between s0 and s1 metres along, from s0 to s1."""
        if s0 <= s1:
            return [p for p, c in zip(self.pts, self.cum) if s0 < c < s1]
        return [p for p, c in zip(reversed(self.pts), reversed(self.cum)) if s1 < c < s0]


_lines: dict[int, Line] = {}
_lines_key: Any = None


def line_of(static: dict[str, Any], idx: int) -> Line | None:
    """Shape `idx` of this timetable, cached per timetable (which one AND when)."""
    global _lines_key
    key = (id(static), static.get("fetched_at"))
    if key != _lines_key:
        _lines.clear()
        _lines_key = key
    if idx not in _lines:
        geoms = static.get("rail_shapes") or []
        if not isinstance(idx, int) or not 0 <= idx < len(geoms) or len(geoms[idx]) < 2:
            return None
        _lines[idx] = Line(geoms[idx])
    return _lines[idx]


def trip_path(static: dict[str, Any] | None, trip_id: str | None,
              start: tuple[float, float], end: tuple[float, float]) -> list[list[float]] | None:
    """`track_path` from `start` (published last) to `end` (now) along the trip's own
    shape: [lat, lon] pairs, 2 to MAX_POINTS, ending at `end` exactly; None for no way."""
    if not static or not trip_id or tuple(start) == tuple(end):
        return None
    info = (static.get("trip_shapes") or {}).get(trip_id)
    if not info:
        return None
    line = line_of(static, info[0])
    if line is None or line.length <= 0:
        return None
    p0 = line.project(*start)
    if p0 is None or p0[1] > SNAP_M:
        return None
    s0 = p0[0]
    straight = math.hypot((end[1] - start[1]) * line.kx, (end[0] - start[0]) * line.ky)
    reach = max(DETOUR_FACTOR * straight, straight + DETOUR_MIN_M)
    p1 = line.project(*end, s0 - reach, s0 + reach)
    if p1 is None or p1[1] > SNAP_M:
        return None
    s1 = p1[0]
    if abs(s1 - s0) < MIN_MOVE_M:
        return None
    pts = [tuple(start)] + line.between(s0, s1) + [tuple(end)]
    tol = PATH_TOLERANCE_M
    out = simplify(pts, tol, line.kx, line.ky)
    while len(out) > MAX_POINTS:
        tol *= 2
        out = simplify(pts, tol, line.kx, line.ky)
    res: list[list[float]] = []
    for la, lo_ in out:
        p = [round(la, 6), round(lo_, 6)]
        if not res or res[-1] != p:
            res.append(p)
    res[-1] = [end[0], end[1]]
    return res if len(res) >= 2 else None


def add_shape_paths(result: dict[str, Any], observations: Iterable[Any],
                    static: dict[str, Any] | None) -> int:
    """`track_path` along its trip's shape on every published record that moved since its
    last fix, in place; how many. Nothing without the timetable's `trip_shapes`."""
    if not static or not static.get("trip_shapes"):
        return 0
    trips = {o.vehicle_id: o.trip_id for o in observations}
    n = 0
    for vid, rec in (result.get("vehicles") or {}).items():
        rec.pop("track_path", None)
        if "previous_latitude" not in rec or "previous_longitude" not in rec:
            continue
        p = trip_path(static, trips.get(vid), (rec["previous_latitude"], rec["previous_longitude"]),
                      (rec["latitude"], rec["longitude"]))
        if p:
            rec["track_path"] = p
            n += 1
    return n
