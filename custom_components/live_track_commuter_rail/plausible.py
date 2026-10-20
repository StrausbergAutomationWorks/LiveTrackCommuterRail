"""Keep a train moving FORWARD along its own line at a speed a train can run, and point its
arrow the way its timetable runs. No Home Assistant imports.

Lee 2026-10-20 02:24, on Madrid: "The trains in Madrid definitely do NOT follow their
tracks. They also apparently achieve super sonic speeds and change direction while
traveling in the same direction." MEASURED that night (Commuter Rail
20_Research/SHAPE_PATHS_20261020.md section 6), on Renfe's RAW feed (capture round 1):
- 45% of the moves of 50 m or more reverse direction along the trip's own shape (143,774
  of 321,150); speed along it since the last position was first seen p90 424 km/h;
- the rows explain it: an INCOMING_AT row places the train at the coordinates of the stop
  it is approaching, a later row puts it back behind; IN_TRANSIT rows can alternate between
  two points 500 m apart every poll; now and then a fix lands kilometres away, on the
  network but not on the trip's line (a Madrid C5 trip published at Guadalajara).

A FIX IS REFUSED when it is farther than OWN_SHAPE_M from the trip's own shape; when it
goes BACK along that shape, against the trip's own direction (its stops in timetable
order), by more than BACK_M; or when it goes forward faster than MAX_KMH, timed from when
the train was first seen at its last good position (Renfe's positions stand, then catch
up). A refused fix is replaced by the last good one, position AND time, for up to HOLD_S,
then the train is left out: the contract's refusal (06_MAP_CONTRACT.md D3c-v, "Refusing is
not snapping"); nothing is moved or invented. CONFIRM refused fixes in a row that agree
with each other (on the shape, forward or within BACK_M of the one before, not too fast)
are taken as the truth: the earlier good position was the wrong one.

A PLACEHOLDER row (Renfe's INCOMING_AT: MEASURED p50 1.6 km, p90 7.2 km ahead of the
trip's next row) is not a position: the train keeps its last good fix. With no good fix to
keep (a new train, or its hold run out) the placeholder is shown, PROVISIONAL - held, 23% of
the published records went missing on the replay, many trains being reported only in such
rows for long stretches - and the first real fix on the trip's own line replaces it without
the back and speed tests.

A train whose trip has no shape, no stops, or no timetable yet passes unjudged.

THE ARROW points along the trip's own shape in the direction its stops run. A shape's
order is not a train's direction (05_SHARED_LESSONS.md C16: Renfe draws both directions of
a line as one shape).
"""

from __future__ import annotations

import dataclasses
import math
from typing import Any, Iterable

from .shapepath import line_of

# MEASURED on capture round 1, the whole pipeline replayed and scored on what is PUBLISHED
# (bin\\ltcr_plaus_replay*.txt; the note's section 6). Without this: 22% of moves back more
# than 100 m along the trip, 21% over 200 km/h, 46% of arrows backwards. With it, CONFIRM 6:
# 3.3%, 0.5%, 3.9%, and 185 of 303,898 records left out. CONFIRM 2 and 4 let Renfe's
# repeated wrong rows through (moves back 6.7% and 4.8%).
OWN_SHAPE_M = 150.0
BACK_M = 100.0
MAX_KMH = 200.0
HOLD_S = 600.0
CONFIRM = 6
# A train not seen for this long is forgotten.
FORGET_S = 1800.0
# The arrow reads the shape this far either side of the train.
SPAN_M = 50.0


@dataclasses.dataclass
class _Track:
    s: float                      # metres along the shape of the last good fix
    lat: float
    lon: float
    since: float                  # when the train was first seen there
    good_at: float                # when it was last accepted
    observed_at: Any              # that fix's own time
    seen: float                   # the last poll the train was in
    cand: list = dataclasses.field(default_factory=list)   # [(s, t)] refused in a row
    provisional: bool = False     # the position is a placeholder's


def _bearing(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, la2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360.0


def point_at(line: Any, s: float) -> tuple[float, float]:
    """The point s metres along the line, clamped to it."""
    s = max(0.0, min(s, line.length))
    for i in range(1, len(line.cum)):
        if line.cum[i] >= s:
            seg = line.cum[i] - line.cum[i - 1]
            f = 0.0 if seg == 0 else (s - line.cum[i - 1]) / seg
            a, b = line.pts[i - 1], line.pts[i]
            return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
    return line.pts[-1]


_dirs: dict[str, int | None] = {}
_dirs_key: Any = None


def direction(static: dict[str, Any] | None, trip_id: str | None) -> int | None:
    """+1 when the trip's stops, in timetable order, run along its shape's order, -1 when
    against it; None without a shape, stops or positions to tell. Cached per timetable."""
    global _dirs_key
    if not static or not trip_id:
        return None
    key = (id(static), static.get("fetched_at"))
    if key != _dirs_key:
        _dirs.clear()
        _dirs_key = key
    if trip_id in _dirs:
        return _dirs[trip_id]
    out = None
    info = (static.get("trip_shapes") or {}).get(trip_id)
    stops = (static.get("sched") or {}).get(trip_id) or {}
    pos = static.get("stop_pos") or {}
    line = line_of(static, info[0]) if info else None
    if line is not None and isinstance(stops, dict):
        seq = [line.project(*pos[sid])[0] for sid, _ in sorted(stops.items(), key=lambda kv: kv[1])
               if sid in pos]
        votes = sum((b > a) - (b < a) for a, b in zip(seq, seq[1:]) if abs(b - a) >= 1.0)
        out = 1 if votes > 0 else -1 if votes < 0 else None
    _dirs[trip_id] = out
    return out


class Plausible:
    """Per-railroad state: each train's last good position along its own shape."""

    def __init__(self, own_shape_m: float = OWN_SHAPE_M, back_m: float = BACK_M,
                 max_kmh: float = MAX_KMH, hold_s: float = HOLD_S, confirm: int = CONFIRM) -> None:
        self._own_m, self._back_m, self._max_kmh = own_shape_m, back_m, max_kmh
        self._hold_s, self._confirm = hold_s, confirm
        self._t: dict[str, _Track] = {}
        self.refused = 0          # fixes refused, since start
        self.confirmed = 0        # runs of refused fixes taken as the truth
        self.placeholders = 0     # placeholder rows held, since start

    def _ok(self, ahead: float, since: float, now: float) -> bool:
        """`ahead` metres forward along the trip from a position first seen at `since`."""
        if ahead < -self._back_m:
            return False
        return ahead <= 0 or ahead / max(now - since, 1.0) * 3.6 <= self._max_kmh

    def filter(self, observations: Iterable[Any], static: dict[str, Any] | None,
               now: float, untrusted: Any = ()) -> list:
        """The observations to give Fleet: a refused one replaced by the train's last good
        fix (position and time) for up to HOLD_S, after that left out. A vehicle in
        `untrusted` (its row is a placeholder) is held the same way, never judged."""
        shapes = (static or {}).get("trip_shapes") or {}
        out = []
        for o in observations:
            info = shapes.get(o.trip_id) if o.trip_id else None
            line = line_of(static, info[0]) if info else None
            d = direction(static, o.trip_id) if line is not None else None
            if line is None or d is None:
                out.append(o)
                continue
            s, off = line.project(o.lat, o.lon)
            tr = self._t.get(o.vehicle_id)
            if o.vehicle_id in untrusted:
                self.placeholders += 1
                if tr is not None and not tr.provisional and now - tr.good_at <= self._hold_s:
                    tr.seen = now
                    out.append(dataclasses.replace(o, lat=tr.lat, lon=tr.lon, observed_at=tr.observed_at))
                elif off <= self._own_m:
                    # Nothing better to show: the placeholder, provisionally.
                    self._t[o.vehicle_id] = _Track(s, o.lat, o.lon, now, now, o.observed_at, now,
                                                   provisional=True)
                    out.append(o)
                continue
            if tr is None:
                if off <= self._own_m:
                    self._t[o.vehicle_id] = _Track(s, o.lat, o.lon, now, now, o.observed_at, now)
                    out.append(o)
                else:
                    self.refused += 1
                continue
            tr.seen = now
            same = (o.lat, o.lon) == (tr.lat, tr.lon)
            ok = same or (off <= self._own_m and (tr.provisional or self._ok((s - tr.s) * d, tr.since, now)))
            if not ok and off <= self._own_m:
                c = tr.cand
                if c and self._ok((s - c[-1][0]) * d, c[-1][1], now):
                    c.append((s, now))
                else:
                    tr.cand = c = [(s, now)]
                if len(c) >= self._confirm:
                    ok = True
                    self.confirmed += 1
            if ok:
                if not same:
                    tr.s, tr.lat, tr.lon, tr.since = s, o.lat, o.lon, now
                tr.good_at, tr.observed_at, tr.cand, tr.provisional = now, o.observed_at, [], False
                out.append(o)
                continue
            self.refused += 1
            if now - tr.good_at <= self._hold_s:
                out.append(dataclasses.replace(o, lat=tr.lat, lon=tr.lon, observed_at=tr.observed_at))
        for vid in [v for v, t in self._t.items() if now - t.seen > FORGET_S]:
            del self._t[vid]
        return out

    def apply_arrows(self, result: dict[str, Any], observations: Iterable[Any],
                     static: dict[str, Any] | None) -> None:
        """Each published train's arrow along its own shape the way its stops run, in place.
        Without a direction to tell, no arrow rather than a guess."""
        shapes = (static or {}).get("trip_shapes") or {}
        trips = {o.vehicle_id: o.trip_id for o in observations}
        for vid, rec in (result.get("vehicles") or {}).items():
            tid = trips.get(vid)
            info = shapes.get(tid) if tid else None
            line = line_of(static, info[0]) if info else None
            if line is None:
                continue
            d = direction(static, tid)
            if d is None:
                for k in ("icon_rotation_deg", "icon_rotation_basis", "course_deg"):
                    rec.pop(k, None)
                continue
            s, _ = line.project(rec["latitude"], rec["longitude"])
            a, b = point_at(line, s - SPAN_M * d), point_at(line, s + SPAN_M * d)
            if a == b:
                continue
            brg = round(_bearing(a, b), 1)
            rec["icon_rotation_deg"] = brg
            if "course_deg" in rec:
                rec["course_deg"] = brg
            rec.setdefault("icon_rotation_basis", "held")
