"""Norway's trains pushed through Oslo's tunnels where Entur's fixes freeze: the map contract's along-route ESTIMATE
(06_MAP_CONTRACT.md D3d). No Home Assistant imports. SSOT section 12.

Lee 2026-11-07 18:10 (for Norway): "the long tunnels around Oslo should be handled like the tunnel in Helsinki. Hold a
frozen train once its next stop's estimate has passed." The tunnels and the rule that finds one are saw_livetrack's
(entur.TUNNELS, tunnel_at, tunnel_time; saw-livetrack 0.2.28, hoisted from Live Track Intercity Rail, which measured
them on the capture of 2026-11-07).

WHEN: a train in service whose fix is FROZEN (older than FROZEN_S: Entur keeps a fix's time while it has no newer one)
and, between the stop it left and its next by the timetable with its delay, lies at a tunnel's way in going the
tunnel's way, or already inside it (tunnel_at).

THE PUSH: from max(the fix's time, its leaving the stop before by the timetable with the delay), along the trip's own
shape to the tunnel's comeback point, in the quickest dark time measured, scaled to the distance left (tunnel_time);
held there until a fresh fix. Before that departure: held where the fix stands. Once begun on a fix, a push runs on
whatever the timetable says meanwhile, until a fresh fix (Intercity's train 1678 went 14 km back the way two wandering
fixes pointed when a push stopped mid-Lieraasen).

THE HOLD: a frozen train NOT at a tunnel is left where its fix is (Fleet publishes the fix). It is never moved on to
its next stop.

WHAT IS PUBLISHED (D3d, as tunnel.py for Helsinki): `position_source: "estimated"`; latitude/longitude the estimate on
the shape; `fix_latitude`/`fix_longitude` the frozen fix; `observed_at` unchanged; previous_*, segment_duration_s and
position_jump dropped; never `stalled`; the shape's bearing as the course while moving, held at the comeback;
`track_path` along the shape from the position drawn last. The first fresh fix after an estimate gets its
`track_path` from the estimate it replaces. Every other train of the railroad carries `position_source: "observed"`.
"""

from __future__ import annotations

import math
from typing import Any, Iterable

from saw_livetrack.entur import tunnel_at, tunnel_time

from . import shapepath
from .operators.norway import epoch, service_seconds

ESTIMATED = "estimated"
OBSERVED = "observed"
FROZEN_S = 60.0
SEGMENT_KEYS = ("previous_latitude", "previous_longitude", "previous_observed_at", "segment_duration_s",
                "position_jump")
# The fix and the comeback point must lie this near the trip's shape (the shapes are simplified at 10 m; the freeze
# fixes spread up to 534 m along the track, not across it).
SNAP_M = 300.0
COURSE_SPAN_M = 50.0


def _bearing(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, la2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dl)
    return round((math.degrees(math.atan2(y, x)) + 360.0) % 360.0, 1)


def point_at(line: shapepath.Line, s: float) -> tuple[float, float]:
    s = max(0.0, min(line.length, s))
    for i in range(1, len(line.cum)):
        if line.cum[i] >= s:
            seg = line.cum[i] - line.cum[i - 1]
            f = 0.0 if seg == 0 else (s - line.cum[i - 1]) / seg
            a, b = line.pts[i - 1], line.pts[i]
            return (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]))
    return line.pts[-1]


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def where(info: list | None, svc: float, delay_s: float) -> tuple[int, int] | None:
    """(the stop the train left, its next) by the trip's calls (operators/norway.py extras) and the delay, seconds
    `svc` into its service day; None before its first departure, after its last, or STANDING at a stop (arrived and
    not yet left: never pushed)."""
    rows = info[9] if info and len(info) > 9 and isinstance(info[9], list) else []
    for i, row in enumerate(rows):
        _, _, arr, dep = (list(row) + [None, None, None, None])[:4]
        leave = dep if _num(dep) else arr
        if not _num(leave) or leave + delay_s <= svc:
            continue
        reach = arr if _num(arr) else dep
        if i == 0 or reach + delay_s <= svc:
            return None
        return i - 1, i
    return None


class EnturPush:
    """Per railroad: the push under way for each train, keyed by its fix."""

    def __init__(self) -> None:
        self._runs: dict[str, dict[str, Any]] = {}

    def _start(self, obs: Any, rec: dict[str, Any], static: dict[str, Any] | None, now: float) -> dict | None:
        info = (((static or {}).get("extras") or {}).get("trip") or {}).get(obs.trip_id or "")
        shape = ((static or {}).get("trip_shapes") or {}).get(obs.trip_id or "")
        pos = (static or {}).get("stop_pos") or {}
        if not info or not shape:
            return None
        delay = rec.get("delay_min")
        delay_s = delay * 60.0 if _num(delay) else 0.0
        svc = service_seconds(now, info[5], info[6])
        at = where(info, svc, delay_s)
        if at is None:
            return None
        prev, nxt = info[9][at[0]], info[9][at[1]]
        prev_leave = prev[3] if _num(prev[3]) else prev[2]
        fix = (obs.lat, obs.lon)
        t = tunnel_at(fix, pos.get(prev[1]), pos.get(nxt[1]))
        if t is None:
            return None
        line = shapepath.line_of(static, shape[0])
        if line is None or line.length <= 0:
            return None
        p0, p1 = line.project(*fix), line.project(*t[2])
        if p0 is None or p1 is None or p0[1] > SNAP_M or p1[1] > SNAP_M or abs(p1[0] - p0[0]) < 1.0:
            return None
        leave = now - (svc - (prev_leave + delay_s))
        return {"fix_t": obs.observed_at, "tunnel": t[0], "start": max(epoch(obs.observed_at), leave),
                "dur": tunnel_time(fix, t), "s0": p0[0], "s1": p1[0], "idx": shape[0], "last": fix}

    def apply(self, result: dict[str, Any], observations: Iterable[Any], static: dict[str, Any] | None,
              now: float) -> int:
        """Push, hold or release every train of one poll, in place; how many are estimated."""
        vehicles = result.get("vehicles") or {}
        by_vid = {o.vehicle_id: o for o in observations}
        n = 0
        for vid, rec in vehicles.items():
            obs = by_vid.get(vid)
            if obs is None or not rec.get("in_service"):
                continue
            run = self._runs.get(vid)
            fixed = epoch(obs.observed_at)
            if fixed is None or now - fixed < FROZEN_S:
                if run is not None:
                    # The first fresh fix after an estimate slides from the estimate it replaces.
                    self._runs.pop(vid, None)
                    path = shapepath.trip_path(static, obs.trip_id, run["last"], (rec["latitude"], rec["longitude"]))
                    rec["previous_latitude"], rec["previous_longitude"] = run["last"]
                    if path:
                        rec["track_path"] = path
                    else:
                        rec.pop("track_path", None)
                rec["position_source"] = OBSERVED
                continue
            if run is None or run["fix_t"] != obs.observed_at:
                run = self._start(obs, rec, static, now)
                if run is None:
                    self._runs.pop(vid, None)
                    rec["position_source"] = OBSERVED
                    continue
                self._runs[vid] = run
            self._draw(rec, obs, run, static, now)
            n += 1
        for vid in [v for v in self._runs if v not in vehicles]:
            del self._runs[vid]
        return n

    def _draw(self, rec: dict[str, Any], obs: Any, run: dict[str, Any], static: dict[str, Any] | None,
              now: float) -> None:
        line = shapepath.line_of(static, run["idx"]) if static else None
        if line is None:
            return
        frac = 0.0 if run["dur"] <= 0 else max(0.0, min(1.0, (now - run["start"]) / run["dur"]))
        s = run["s0"] + (run["s1"] - run["s0"]) * frac
        here = point_at(line, s)
        sign = 1.0 if run["s1"] >= run["s0"] else -1.0
        crs = _bearing(point_at(line, s - sign * COURSE_SPAN_M), point_at(line, s + sign * COURSE_SPAN_M))
        for k in SEGMENT_KEYS + ("stalled", "track_path"):
            rec.pop(k, None)
        rec["position_source"] = ESTIMATED
        rec["fix_latitude"], rec["fix_longitude"] = obs.lat, obs.lon
        last = run["last"]
        rec["latitude"], rec["longitude"] = round(here[0], 6), round(here[1], 6)
        p_last = line.project(*last)
        if p_last is not None and abs(s - p_last[0]) >= shapepath.MIN_MOVE_M:
            pts = [tuple(last)] + line.between(p_last[0], s) + [(rec["latitude"], rec["longitude"])]
            tol = shapepath.PATH_TOLERANCE_M
            out = shapepath.simplify(pts, tol, line.kx, line.ky)
            while len(out) > shapepath.MAX_POINTS:
                tol *= 2
                out = shapepath.simplify(pts, tol, line.kx, line.ky)
            path = [[round(a, 6), round(b, 6)] for a, b in out]
            path[-1] = [rec["latitude"], rec["longitude"]]
            if len(path) >= 2:
                rec["track_path"] = path
        run["last"] = (rec["latitude"], rec["longitude"])
        if 0.0 < frac < 1.0:
            rec["course_deg"] = crs
            rec["icon_rotation_basis"] = "course"
        else:
            rec.pop("course_deg", None)
            rec["icon_rotation_basis"] = "held"
        rec["icon_rotation_deg"] = crs
