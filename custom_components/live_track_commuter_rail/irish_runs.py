"""Irish Rail's Commuter trains (P and D codes, Dublin and Cork) drawn from their timetable, each placed along its
trip's own shape and published as the map contract's NO-FIX estimate (06_MAP_CONTRACT.md D3d). No Home Assistant
imports. SSOT 13.

Lee 2026-11-09 ~17:5x CST (SSOT 13): Irish Rail's Commuter trains here, Dublin's and Cork's, Cork "drawn from the
timetable with the last known delay, pushed along the track, positions as updates (the Intercity decision)". The runs
are saw-livetrack 0.2.34's (irish_rail.read_timetable, join_stations, RunTracker: Live Track Intercity Rail's engine,
hoisted verbatim and proven equal on its capture, library SSOT 6.35): every P/D trip the timetable runs today or
yesterday; its delay from Irish Rail when the report is THIS run; the report's last location a floor; status T the end.
Irish Rail's positions are signalling points (a new one every ~4 min at the median for Commuter) and Cork's trains are
never positioned at all, so NO train here has a fix: every one is an estimate.

WHERE A RUN IS DRAWN (Intercity's practice for a no-fix train: sources/irish_rail.py with projection.py and
NO_FIX_KEY). Standing at a call: on its trip's shape at that call. Running: along the shape from the call it left
toward the next, by time, from its departure to the next call's arrival (each with the delay). The calls are placed on
the shape once per trip, in order, each within SNAP_M of it and no more than BACK_M behind the call before it (the
shapes are simplified at 10 m). A stretch with an end off the shape, or a trip with no shape: held at the call it is
timed from (Intercity: "where the projector has nothing, the stop it is timed from").

WHAT IS PUBLISHED (D3d, as Intercity's NO_FIX_KEY records): `position_source: "estimated"`; NO `fix_latitude` or
`fix_longitude` (there is no fix to name); `observed_at` and `last_seen` the timetable time the train was last AT
something -- its arrival at the call it stands at, its departure from the call it left, now while it waits at its
origin -- never later than now (Intercity's Obs time); previous_*, segment_duration_s, position_jump and stalled
dropped (no fix was observed, so neither a slide between fixes nor standing is known); the shape's bearing as
`course_deg` while running between calls, held at a call (D4 basis "held"); `track_path` along the shape from the
position published last (as entur_push.py; the contract's second-emitter note under D3d).

THE SHAPES are this integration's own distill of the same zip (statics.py: rail_shapes, trip_shapes), cut to the P/D
trips (operators/irish_rail.py). They are cached here per timetable, NOT through shapepath.line_of: this module runs in
the executor, and line_of's module-wide cache is shared with every other coordinator on the event loop.
"""

from __future__ import annotations

import datetime as dt
import math
from typing import Any, Iterable, Mapping

from saw_livetrack.irish_rail import RunTracker, join_stations, number_of

from .shapepath import Line
from .tracknet import MAX_POINTS, PATH_TOLERANCE_M, simplify

ESTIMATED = "estimated"
# Dropped from every record published here (module docstring, WHAT IS PUBLISHED).
DROPPED = ("previous_latitude", "previous_longitude", "previous_observed_at", "segment_duration_s", "position_jump",
           "stalled", "fix_latitude", "fix_longitude", "track_path", "course_deg", "icon_rotation_deg",
           "icon_rotation_basis")
# A call farther than this from its trip's shape is not placed on it. MEASURED on the NTA zip of 2026-11-08 (bin\
# ie_ltcr_replay.txt): see SSOT 13.
SNAP_M = 500.0
# A call may be placed this far BEHIND the call before it along the shape (simplified at 10 m; a platform's point).
BACK_M = 100.0
# The bearing is taken over this much shape either side of the point drawn.
COURSE_SPAN_M = 50.0
# track_path: both ends must lie this near the line, and the way is looked for within this many times the straight
# distance either side (shapepath's rules).
PATH_SNAP_M = 50.0
DETOUR_FACTOR = 3.0
DETOUR_MIN_M = 1000.0
MIN_MOVE_M = 5.0


def iso(epoch: float) -> str:
    """An epoch as Fleet writes observed_at (an aware UTC datetime's isoformat), to the second."""
    return dt.datetime.fromtimestamp(round(epoch), dt.timezone.utc).isoformat()


def point_at(line: Line, s: float) -> tuple[float, float]:
    """The point `s` metres along `line`, clamped to it."""
    s = max(0.0, min(line.length, s))
    for i in range(1, len(line.cum)):
        if line.cum[i] >= s:
            seg = line.cum[i] - line.cum[i - 1]
            f = 0.0 if seg == 0 else (s - line.cum[i - 1]) / seg
            a, b = line.pts[i - 1], line.pts[i]
            return (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]))
    return line.pts[-1]


def bearing(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, la2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dl)
    return round((math.degrees(math.atan2(y, x)) + 360.0) % 360.0, 1)


def place_calls(line: Line, reverse: bool, points: Iterable[Any]) -> list[float | None]:
    """Metres along `line` of each call, in order (module docstring); None for a call with no position or off the
    shape. `reverse`: the trip runs against the line's order (rail.shapes_indexed stores a reversed shape once)."""
    out: list[float | None] = []
    prev = None
    for p in points:
        if not p:
            out.append(None)
            continue
        if prev is None:
            lo, hi = -math.inf, math.inf
        elif reverse:
            lo, hi = -math.inf, prev + BACK_M
        else:
            lo, hi = prev - BACK_M, math.inf
        got = line.project(float(p[0]), float(p[1]), lo, hi)
        if got is None or got[1] > SNAP_M:
            out.append(None)
            continue
        out.append(got[0])
        prev = got[0]
    return out


def way(s_at: list[float | None], i: int) -> float:
    """+1 or -1, the way the train goes along the line at call i (to its next placed call, else from its previous);
    0 when no other call is placed."""
    here = s_at[i]
    if here is None:
        return 0.0
    for s in s_at[i + 1:]:
        if s is not None and s != here:
            return 1.0 if s > here else -1.0
    for s in reversed(s_at[:i]):
        if s is not None and s != here:
            return 1.0 if here > s else -1.0
    return 0.0


def path_along(line: Line, start: tuple[float, float], end: tuple[float, float]) -> list[list[float]] | None:
    """`track_path` from `start` (published last) to `end` (now) along `line`: [lat, lon] pairs, 2 to MAX_POINTS,
    ending at `end` exactly; None when either is off the line or the train moved less than MIN_MOVE_M along it."""
    if tuple(start) == tuple(end) or line.length <= 0:
        return None
    p0 = line.project(*start)
    if p0 is None or p0[1] > PATH_SNAP_M:
        return None
    straight = math.hypot((end[1] - start[1]) * line.kx, (end[0] - start[0]) * line.ky)
    reach = max(DETOUR_FACTOR * straight, straight + DETOUR_MIN_M)
    p1 = line.project(*end, p0[0] - reach, p0[0] + reach)
    if p1 is None or p1[1] > PATH_SNAP_M or abs(p1[0] - p0[0]) < MIN_MOVE_M:
        return None
    pts = [tuple(start)] + line.between(p0[0], p1[0]) + [tuple(end)]
    tol = PATH_TOLERANCE_M
    out = simplify(pts, tol, line.kx, line.ky)
    while len(out) > MAX_POINTS:
        tol *= 2
        out = simplify(pts, tol, line.kx, line.ky)
    res: list[list[float]] = []
    for la, lo in out:
        p = [round(la, 6), round(lo, 6)]
        if not res or res[-1] != p:
            res.append(p)
    res[-1] = [end[0], end[1]]
    return res if len(res) >= 2 else None


class IrishRuns:
    """Per config entry: the runs (RunTracker), the calls placed on each trip's shape, and the position published
    last for each train. poll() in the executor, publish() on the event loop after Fleet; never both at once."""

    def __init__(self) -> None:
        self.tracker = RunTracker()
        self.rows: dict[str, dict[str, Any]] = {}
        self.skipped: dict[str, int] = {}
        # Held at a call this poll where it should run: no shape, or its stretch has an end off the shape.
        self.unplaced = 0
        self._static_key: Any = None
        self._lines: dict[int, Line] = {}
        self._calls: dict[tuple, tuple[Line | None, bool, list]] = {}
        self._join: dict[str, str] = {}
        self._join_key: Any = None
        self._last: dict[str, tuple[float, float]] = {}

    def _fresh(self, static: Mapping[str, Any] | None) -> None:
        key = (id(static), (static or {}).get("fetched_at"))
        if key != self._static_key:
            self._static_key = key
            self._lines.clear()
            self._calls.clear()
            self._join_key = None

    def _line(self, static: Mapping[str, Any], idx: Any) -> Line | None:
        if idx not in self._lines:
            geoms = static.get("rail_shapes") or []
            if not isinstance(idx, int) or not 0 <= idx < len(geoms) or len(geoms[idx]) < 2:
                return None
            self._lines[idx] = Line(geoms[idx])
        return self._lines[idx]

    def stations(self, api: list, table: Mapping[str, Any], version: Any) -> dict[str, str]:
        """API station code -> stop_id (join_stations), once per station list and timetable."""
        key = (version, len(api or ()), self._static_key)
        if key != self._join_key:
            self._join_key = key
            self._join = join_stations(api or [], table.get("stops") or {}, table.get("stop_names") or {})
        return self._join

    def _placed(self, static: Mapping[str, Any], trip_id: str, stops: tuple, pos_of: Mapping[str, Any]
                ) -> tuple[Line | None, bool, list]:
        key = (trip_id, stops)
        got = self._calls.get(key)
        if got is None:
            info = (static.get("trip_shapes") or {}).get(trip_id)
            line = self._line(static, info[0]) if info else None
            if line is None or line.length <= 0:
                got = (None, False, [None] * len(stops))
            else:
                rev = bool(info[1])
                got = (line, rev, place_calls(line, rev, [pos_of.get(s) for s in stops]))
            self._calls[key] = got
        return got

    def poll(self, trains: list | None, api: list | None, stations_version: Any,
             static: Mapping[str, Any] | None, now: float) -> list[dict[str, Any]]:
        """This consumer's trains (the shared client's dicts) -> one row per run drawn, each with where it is drawn.
        Blocking work on the first sight of a trip: run it in the executor."""
        self._fresh(static)
        table = (static or {}).get("table") or {}
        if not table.get("trips"):
            self.rows, self.skipped, self.unplaced = {}, {"no_timetable": 1}, 0
            return []
        stations = self.stations(api or [], table, stations_version)
        runs, skipped = self.tracker.step(trains or [], now, table, stations)
        pos_of = table.get("stops") or {}
        names = table.get("stop_names") or {}
        rows: list[dict[str, Any]] = []
        unplaced = 0
        for run in runs:
            row = self._row(run, now, static or {}, pos_of, names)
            if row is None:
                skipped["no_stop_position"] = skipped.get("no_stop_position", 0) + 1
                continue
            unplaced += row["held"]
            rows.append(row)
        self.rows = {r["key"]: r for r in rows}
        self.skipped, self.unplaced = skipped, unplaced
        return rows

    def _row(self, run: Any, now: float, static: Mapping[str, Any], pos_of: Mapping[str, Any],
             names: Mapping[str, str]) -> dict[str, Any] | None:
        times, i, state = run.times, run.index, run.state
        call, arr, dep, _ = times[i]
        here = pos_of.get(call["stop"])
        if not here:
            return None
        stops = tuple(t[0]["stop"] for t in times)
        line, _rev, s_at = self._placed(static, run.trip_id, stops, pos_of)
        nxt = times[i + 1] if i + 1 < len(times) else None
        s = s_at[i] if line is not None else None
        moving = False
        # Held where it should run: no shape, or a stretch with an end off it.
        held = line is None or s is None
        if s is not None and state == "running" and nxt is not None:
            if s_at[i + 1] is None:
                held = True
            else:
                span = nxt[1] - dep
                frac = 1.0 if span <= 0 else max(0.0, min(1.0, (now - dep) / span))
                s = s_at[i] + frac * (s_at[i + 1] - s_at[i])
                moving = 0.0 < frac < 1.0 and s_at[i + 1] != s_at[i]
        course = None
        if s is not None:
            lat, lon = point_at(line, s)
            sign = way(s_at, i)
            if sign:
                course = bearing(point_at(line, s - sign * COURSE_SPAN_M), point_at(line, s + sign * COURSE_SPAN_M))
        else:
            lat, lon = float(here[0]), float(here[1])
        when = arr if state == "standing" and now >= arr else (dep if state == "running" else now)
        nxt_out = None
        delay = None
        if nxt is not None:
            ncall, narr, _, known = nxt
            name = names.get(ncall["stop"])
            if name:
                nxt_out = (name, narr)
            aimed = ncall.get("aimed_arrival")
            if aimed is None:
                aimed = ncall.get("aimed_departure")
            if known and aimed is not None:
                delay = int(round(narr - aimed))
        if delay is None and run.delay is not None:
            delay = int(run.delay)
        return {
            "key": run.key, "trip_id": run.trip_id, "code": run.code, "number": number_of(run.code) or run.code,
            "lat": round(lat, 6), "lon": round(lon, 6), "at": min(when, now), "state": state, "index": i,
            "names": [names.get(t[0]["stop"], "") for t in times], "next": nxt_out, "delay_s": delay,
            "course": course, "moving": moving, "line": line if s is not None else None, "held": held,
        }

    def publish(self, result: dict[str, Any]) -> int:
        """Every train of this poll as a no-fix estimate (module docstring), in place, after Fleet and everything
        else that touches a record; how many."""
        vehicles = result.get("vehicles") or {}
        n = 0
        for vid, rec in vehicles.items():
            row = self.rows.get(vid)
            if row is None or not rec.get("in_service"):
                continue
            for k in DROPPED:
                rec.pop(k, None)
            rec["position_source"] = ESTIMATED
            rec["observed_at"] = rec["last_seen"] = iso(row["at"])
            if row["course"] is not None:
                rec["icon_rotation_deg"] = row["course"]
                if row["moving"]:
                    rec["course_deg"] = row["course"]
                    rec["icon_rotation_basis"] = "course"
                else:
                    rec["icon_rotation_basis"] = "held"
            here = (rec["latitude"], rec["longitude"])
            last = self._last.get(vid)
            if last is not None and row["line"] is not None:
                path = path_along(row["line"], last, here)
                if path:
                    rec["track_path"] = path
            self._last[vid] = here
            n += 1
        for vid in [v for v in self._last if v not in vehicles]:
            del self._last[vid]
        return n
