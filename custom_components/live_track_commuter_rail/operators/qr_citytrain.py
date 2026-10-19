"""Queensland Rail Citytrain, SE Queensland, on Translink's GTFS and GTFS-Realtime.
No Home Assistant imports.

SSOT section 9: decided by Lee 2026-10-15 20:09 (9.1) on the capture of 2026-10-11 to
10-13 (20_Research/SEQ_CAPTURE1_ANALYSIS_20261015.md), and re-measured on the static
timetable of 2026-10-14 before this was built (bin\\seq_build_measure.txt, _2.txt).

THE FEED (no key, CC BY 4.0, credit Translink):
* vehicle.id    a 32-hex string, "_", the run number. The hex was the SAME on every
                vehicle measured (57 live on 2026-10-15, 330,056 captured rows), so it
                names the run. Identity, used whole (Lee: entity id from vehicle.id).
* label         the run number (1E15, D135). Riders do not know it; they know the
                line's T number, which comes from the route's colour (world note 8).
* trip_id       in the static timetable, or UNPLANNED-<n> (not in it).
* route_id      "<four letters>-<version>" (BRFG-5167): the two end codes, BR Brisbane
                City, FG Ferny Grove. The version changes with the timetable.
* position      a FIXED POINT on the track, not GPS (analysis section 1): it steps up to
                3.7 km at once. No speed is derived from two fixes, and none is a jump:
                position_jump is dropped (saw_livetrack's FixTracker calls 0.45% of the
                real moves jumps, over 322 km/h implied). 0,0 is refused (position_of).
* bearing, speed, odometer, trip.direction_id, trip.start_date: NEVER set. No motion
                (06_MAP_CONTRACT.md D3b fails at condition 1): no max_extrapolation_s.
* timestamp     on every row. Ghosts, fixes frozen until the service day ends, are
                refused at 5 minutes (max_fix_age_s; poll.fresh_only).

THE LOOK (world note section 8, Lee 2026-10-11): Translink's line badges. Northbound
(direction_id 1): the badge as published, the line colour as the ring round #0A1116,
the white T number unoutlined. Southbound (0): swapped, the line colour as the fill in a
#0A1116 ring, the number outlined #0A1116. The arrow the line colour outlined black both
ways. The grey city-only and special runs (route colour 666D8E) have no T number: a full
white star (06 D4a-symbol), outlined #0A1116 southbound.

DIRECTION: the timetabled trip's direction_id; an UNPLANNED trip takes its route's when
every trip of the route shares one (501 of 511 rail routes on 2026-10-14; the ten
shuttles and loops BRBR, CLCL, IPIP, SHSH carry both). Unknown: the badge as published.

THE ARROW (SSOT 9.1, Lee: "From the trip's shape"): the trip's own GTFS shape's bearing
where the train is, in the shape's point order, over 50 m either side, the way Live Track
Intercity Rail draws a train whose source sends no bearing (its geometry.Projector.course:
the line's bearing over a 100 m chord, kept inside the line's ends). Moving by Fleet's
rule (a move of over 50 m in 90 s): course_deg and the arrow with basis "course"; at
rest the arrow held there, no course_deg (D3c-iii). An UNPLANNED trip uses the nearest
shape of its route when the route has one direction. No shape, or the fix more than 1 km
from it: Fleet's own course between two fixes, as on NICTD.

STALLED: after 366 s standing wherever the train stands (STALL_M below; Lee 2026-10-15).

LATE (Queensland Rail's own rule; SSOT section 0, Lee 2026-10-15 14:26): on time within
3:59, within 5:59 on the interurban services (Gold Coast, Rosewood, Sunshine Coast). So
late_threshold_min 4, or 6 on a route with an end at Varsity Lakes (VL), Rosewood (RW),
Nambour (NA) or Gympie North (GY). No very_late_threshold_min: QR defines no second tier,
and the card's default is 15 (Lee 2026-10-15 20:48).

OFF RAIL (SSOT 9.1): more than 1 km from every SE Queensland rail shape (rail.RailCheck,
off_rail_m; no NARN outside the US). Rosewood platform 1 is placed 637 m from any line.
"""

from __future__ import annotations

import csv
import io
import math
import zipfile
from typing import Any

from .base import Obs, Operator, position_of, vehicle_time

DARK = "#0A1116"
BLACK = "#000000"
WHITE = "#FFFFFF"
RING_WIDTH = 4

# GTFS route_color -> (T number, the badge's colour). The badge colours were measured
# from Translink's badges Lee sent on 2026-10-11; the GTFS carries a slightly darker
# shade of each (world note section 8).
BADGE: dict[str, tuple[str | None, str]] = {
    "27855A": ("T1", "#2E9C69"),
    "6CC6E9": ("T2", "#6DC7E9"),
    "9B60A6": ("T3", "#A769AB"),
    "4778B2": ("T4", "#4E85C5"),
    "FFC425": ("T5", "#FFC628"),
    "D53E45": ("T6", "#EF474F"),
    "666D8E": (None, "#666D8E"),
}

NORTHBOUND = 1
INTERURBAN_ENDS = frozenset({"VL", "RW", "NA", "GY"})
LATE_MIN = 4
LATE_INTERURBAN_MIN = 6

MAX_FIX_AGE_S = 300
OFF_RAIL_M = 1000.0
# STALLED (Lee 2026-10-15: "One wait: 366 s anywhere"): Fleet's 90 s rule away from a stop
# fires on MOVING trains here, held on one fixed point between two (Monday 2026-10-12,
# bin\\ltcr_seq_stall.txt: 288 such spells on time and 11 late, feed IN_TRANSIT_TO, next
# step p50 1.5 km) and on platform dwells placed over 300 m from the stop (344 and 14).
# With no stop out of reach, every fix takes the platform rule, PLATFORM_HOLD_S (366 s).
STALL_M = math.inf
# The arrow: the shape's bearing over this far either side (Intercity Rail's
# COURSE_SPAN_M), and no arrow from a shape the fix is farther than this from
# (Intercity Rail's MAX_FIX_OFF_M).
COURSE_SPAN_M = 50.0
MAX_FIX_OFF_M = 1000.0

POSITIONS_URL = "https://gtfsrt.api.translink.com.au/api/realtime/SEQ/VehiclePositions/Rail"
TRIP_UPDATES_URL = "https://gtfsrt.api.translink.com.au/api/realtime/SEQ/TripUpdates/Rail"
STATIC_URL = "https://gtfsrt.api.translink.com.au/GTFS/SEQ_GTFS.zip"
TERMS_URL = "https://translink.com.au/about-translink/open-data"


# --- the feed --------------------------------------------------------------

def parse(feed) -> list[Obs]:
    out: list[Obs] = []
    for ent in feed.entity:
        if not ent.HasField("vehicle"):
            continue
        v = ent.vehicle
        vid = (v.vehicle.id or "").strip()
        pos = position_of(v)
        if not vid or pos is None:
            continue
        trip = (v.trip.trip_id or "").strip() if v.HasField("trip") else ""
        route = (v.trip.route_id or "").strip() if v.HasField("trip") else ""
        label = (v.vehicle.label or "").strip()
        in_service = bool(trip)
        out.append(Obs(
            vehicle_id=vid,
            lat=pos[0],
            lon=pos[1],
            observed_at=vehicle_time(v),
            in_service=in_service,
            train=(label or None) if in_service else None,
            line=route or None,
            reported_course=None,
            trip_id=trip or None,
        ))
    return out


def route_code(route_id: str | None) -> str:
    """'BRFG-5167' -> 'BRFG'."""
    return (route_id or "").split("-", 1)[0].strip().upper()


def interurban(route_id: str | None) -> bool:
    """A route with an end on the Gold Coast, Rosewood or Sunshine Coast lines."""
    code = route_code(route_id)
    return len(code) == 4 and bool({code[:2], code[2:]} & INTERURBAN_ENDS)


# --- the timetable's extras (statics.py stores them; decorate reads them) -------

def extras(z: zipfile.ZipFile, distilled: dict[str, Any],
           shape_index: dict[str, list[int]]) -> dict[str, Any]:
    """From the rail-only zip: each route's colour; the shape and direction of each trip
    the distilled timetable keeps (yesterday, today, tomorrow); each route's direction
    and shapes where all its trips share one direction."""
    def rows(name: str):
        if name not in z.namelist():
            return
        with z.open(name) as fh:
            for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")):
                yield {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}

    colour = {r["route_id"]: r.get("route_color", "").upper()
              for r in rows("routes.txt") if r.get("route_id")}
    window = distilled.get("sched") or {}
    trip: dict[str, list[int]] = {}
    dirs: dict[str, set[int]] = {}
    shapes: dict[str, set[tuple[int, int]]] = {}
    for r in rows("trips.txt"):
        tid, rid = r.get("trip_id"), r.get("route_id")
        if not tid or not rid:
            continue
        try:
            d = int(r.get("direction_id", ""))
        except ValueError:
            d = None
        if d is not None:
            dirs.setdefault(rid, set()).add(d)
        ix = shape_index.get(r.get("shape_id", ""))
        if ix is not None:
            shapes.setdefault(rid, set()).add((ix[0], ix[1]))
        if tid in window and d is not None:
            trip[tid] = [ix[0], ix[1], d] if ix is not None else [-1, 0, d]
    one_way = {rid: next(iter(ds)) for rid, ds in dirs.items() if len(ds) == 1}
    return {
        "route_color": colour,
        "trip": trip,
        "route_dir": one_way,
        "route_shapes": {rid: sorted(map(list, shapes.get(rid, ()))) for rid in one_way},
    }


# --- the shape's bearing ---------------------------------------------------

_R = 6371008.8
_K = _R * math.pi / 180


class _Line:
    """One polyline with distance along it, on a local flat projection."""

    def __init__(self, pts: list) -> None:
        lat0 = math.radians(sum(p[0] for p in pts) / len(pts))
        self.kx = _K * math.cos(lat0)
        self.x = [p[1] * self.kx for p in pts]
        self.y = [p[0] * _K for p in pts]
        self.cum = [0.0]
        for i in range(1, len(pts)):
            self.cum.append(self.cum[-1] + math.hypot(self.x[i] - self.x[i - 1],
                                                      self.y[i] - self.y[i - 1]))
        self.length = self.cum[-1]

    def project(self, lat: float, lon: float) -> tuple[float, float]:
        """(metres along, metres off) of the nearest point."""
        px, py = lon * self.kx, lat * _K
        best = (0.0, float("inf"))
        for i in range(1, len(self.x)):
            ax, ay, bx, by = self.x[i - 1], self.y[i - 1], self.x[i], self.y[i]
            dx, dy = bx - ax, by - ay
            den = dx * dx + dy * dy
            t = 0.0 if den == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / den))
            off = math.hypot(px - ax - t * dx, py - ay - t * dy)
            if off < best[1]:
                best = (self.cum[i - 1] + t * math.sqrt(den), off)
        return best

    def point(self, d: float) -> tuple[float, float]:
        d = max(0.0, min(d, self.length))
        for i in range(1, len(self.cum)):
            if self.cum[i] >= d:
                seg = self.cum[i] - self.cum[i - 1]
                t = 0.0 if seg == 0 else (d - self.cum[i - 1]) / seg
                x = self.x[i - 1] + t * (self.x[i] - self.x[i - 1])
                y = self.y[i - 1] + t * (self.y[i] - self.y[i - 1])
                return y / _K, x / self.kx
        return self.y[-1] / _K, self.x[-1] / self.kx


def _bearing(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, la2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360.0


_lines: dict[int, _Line] = {}
_lines_key: Any = None


def _line(static: dict[str, Any], idx: int) -> _Line | None:
    global _lines_key
    # Which timetable as well as when: Renfe's operators read lines through here too
    # (operators/renfe.py), and two timetables may carry the same fetched_at.
    key = (id(static), static.get("fetched_at"))
    if key != _lines_key:
        _lines.clear()
        _lines_key = key
    if idx not in _lines:
        geoms = static.get("rail_shapes") or []
        if not 0 <= idx < len(geoms) or len(geoms[idx]) < 2:
            return None
        _lines[idx] = _Line(geoms[idx])
    return _lines[idx]


def shape_course(static: dict[str, Any] | None, candidates: list, lat: float,
                 lon: float) -> float | None:
    """The bearing, degrees true to 0.1, of the nearest candidate shape [index,
    reversed] where (lat, lon) is, in the shape's own order; None with no candidate
    within MAX_FIX_OFF_M."""
    if not static or not candidates:
        return None
    best = None
    for idx, rev in candidates:
        if idx is None or idx < 0:
            continue
        line = _line(static, idx)
        if line is None or line.length <= 0:
            continue
        d, off = line.project(lat, lon)
        if off <= MAX_FIX_OFF_M and (best is None or off < best[2]):
            best = (line, d, off, -1.0 if rev else 1.0)
    if best is None:
        return None
    line, d, _, sign = best
    span = COURSE_SPAN_M
    d = min(max(d, span), max(line.length - span, span))
    a, b = line.point(d - sign * span), line.point(d + sign * span)
    if a == b:
        return None
    return round(_bearing(a, b), 1)


# --- one published record --------------------------------------------------

def marker_keys(badge: tuple[str | None, str], direction: int | None) -> dict[str, Any]:
    """The disc for a line badge. Northbound, or direction unknown: as published."""
    number, colour = badge
    north = direction != 0
    keys: dict[str, Any] = {
        "marker_color": DARK if north else colour,
        "marker_ring_color": colour if north else DARK,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": WHITE,
        "marker_label_outline_color": "none" if north else DARK,
        "marker_arrow_color": colour,
        "marker_arrow_outline_color": BLACK,
    }
    if number is None:
        keys["marker_symbol"] = "star"
        if not north:
            keys["marker_symbol_outline_color"] = DARK
    return keys


def decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
    """Label, look, lateness and arrow for one record Fleet published, in place."""
    rec.pop("position_jump", None)
    ex = ((static or {}).get("extras") or {})
    route = obs.line or ""
    info = (ex.get("trip") or {}).get(obs.trip_id or "")
    direction = info[2] if info else (ex.get("route_dir") or {}).get(route)
    if obs.in_service:
        rec["late_threshold_min"] = LATE_INTERURBAN_MIN if interurban(route) else LATE_MIN
        badge = BADGE.get((ex.get("route_color") or {}).get(route, ""))
        if badge is not None:
            rec.update(marker_keys(badge, direction))
            if badge[0] is not None:
                rec["marker_label"] = badge[0]
    if info is not None and info[0] >= 0:
        candidates = [info[:2]]
    elif direction is not None:
        candidates = (ex.get("route_shapes") or {}).get(route) or []
    else:
        candidates = []
    crs = shape_course(static, candidates, rec["latitude"], rec["longitude"])
    if crs is None:
        return
    if "course_deg" in rec:
        rec["course_deg"] = crs
        rec["icon_rotation_basis"] = "course"
    else:
        rec["icon_rotation_basis"] = "held"
    rec["icon_rotation_deg"] = crs


QR_CITYTRAIN = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-10-15: "qr_citytrain".
    id="qr_citytrain",
    name="Queensland Rail Citytrain (SE Queensland)",
    short="SEQ",
    regions=("AU-QLD",),
    positions_url=POSITIONS_URL,
    trip_updates_url=TRIP_UPDATES_URL,
    static_url=STATIC_URL,
    # Every mode in one zip (35.97 MB on 2026-10-14); trains are route_type 2.
    static_route_types=("2",),
    static_max_bytes=64 * 1024 * 1024,
    static_extras=extras,
    parse=parse,
    decorate=decorate,
    max_fix_age_s=MAX_FIX_AGE_S,
    off_rail_m=OFF_RAIL_M,
    narn=False,
    stall_m=STALL_M,
    attribution=(
        "Data: Translink, Queensland Government, CC BY 4.0. This integration is not "
        "sponsored by, affiliated with, or operated by Translink or Queensland Rail."
    ),
    terms_url=TERMS_URL,
)
