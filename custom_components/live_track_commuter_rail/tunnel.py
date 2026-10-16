"""A train pushed through a tunnel where its fixes stop: the map contract's along-route
ESTIMATE (06_MAP_CONTRACT.md D3d). No Home Assistant imports.

Finland (SSOT 8.3 step 3, backlog 290; 20_Research/FI_RING_TUNNEL_20261016.md): lines I
and P lose GPS in the Lentoasema tunnel under Helsinki airport. The last fix freezes at
the entry portal for 7-8 minutes (dark p50 415 s for I, 485 s for P) and the next one is
7-8 km on, past the far portal. Lee 2026-10-16 01:15: "push the train along the track,
stop at the airport station and then go to where it normally reappears by the quickest
time it can make there... then the reported locations can take over again."

THE WAY: each tunnel is one way along the shipped track network (tracknet), from a
station before the entry portal to one past the far portal, with its marks in metres
along it: the entry portal, the two tunnel stops, the far portal, and the comeback point
where the quickest measured passage came back (I 197 m past the west portal, P 138 m past
the east; bin\\ltcr290s3_measure.txt).

THE CLOCK, from the train's own timetable (StopClock), set out in Way.schedule():
 * from the fix to the first stop, arriving at its actual arrival when published
   (Digitraffic publishes an arrival p50 17 s after the fact), else its live estimate,
   else the schedule; never faster than MAX_KMH from the fix.
 * there until its DEPARTURE's live estimate, never its actual: actual departures come
   p50 57 s late, and Digitraffic drops liveEstimateTime from a row once its actual is in
   (0 of 2,276 LEN/AVP rows of the cached train lists carry both), so the last estimate
   seen is remembered. Only with no estimate ever seen: the actual, then the schedule.
 * to the second stop in the quickest measured time (I 80 s, P 82 s), or at its actual
   arrival when that is later; there until its departure's estimate.
 * through the far portal to the comeback point in the quickest measured time (I 135 s,
   P 89 s), and held there. The next fresh fix takes over.

WHEN: a train in service on the tunnel's line whose fix lies on the way (within
LATERAL_M) between ZONE_OUT_M outside the entry portal and the first stop. A fix past the
first stop (the comeback) is published as it is.

WHAT IS PUBLISHED (D3d): `position_source: "estimated"`; latitude/longitude the estimate,
on the way; `fix_latitude`/`fix_longitude` the frozen fix; `observed_at` unchanged;
previous_*, segment_duration_s and position_jump dropped (they describe the fix); never
`stalled` (its standing is not known); the way's bearing, as the course while moving and
held at a stop and at the comeback; `track_path` along the way from the position
published last (D3c-v); the next stop from where it is DRAWN (next_stop and
arrival_estimated_at: the stop ahead at its arrival, the stop it stands at at its
departure, past the second stop the first one after the tunnel; Lee 2026-10-16 12:42).
Never backwards. Every other train in service carries
`position_source: "observed"`, and the first fix after an estimate gets its `track_path`
from the estimate it replaces.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from . import tracknet

ESTIMATED = "estimated"
OBSERVED = "observed"
# The fix's own segment: with an estimate a card would slide from the frozen fix in a
# straight line (D3d), or place the marker (position_jump).
SEGMENT_KEYS = ("previous_latitude", "previous_longitude", "previous_observed_at",
                "segment_duration_s", "position_jump")
# A fix or a mark this far from the way is not on it. MEASURED: the dark fixes lie p50
# 0.2 m (I) and 7.9 m (P, the other track) off; LEN and AVP 17.4 m (another platform
# track).
LATERAL_M = 30.0
# A fix this far outside the entry portal is in the push's zone. MEASURED (capture round
# 1, along the way): I went dark p10 25 m outside the portal, P p10 26 m, P at most 207 m.
ZONE_OUT_M = 300.0
# Never faster than this from the fix to the first stop: the speed reported at the
# portal (117-121 km/h, FI_RING_TUNNEL_20261016.md section 1).
MAX_KMH = 120.0
# The bearing is read over this much of the way either side.
COURSE_SPAN_M = 50.0
# The way between its two stations is searched up to this far.
MAX_WAY_M = 30000.0
# A train's clocks carry, under this key, its first commercial stop after the tunnel:
# its next stop once the push has taken it past the second.
AFTER = "_after"
# Drawn this close to a stop's mark, the train stands at it.
AT_STOP_M = 0.5


@dataclass(frozen=True)
class StopClock:
    """One tunnel stop's times from the train's timetable, as POSIX seconds. Under the
    key AFTER: the first commercial stop after the tunnel, with its station `code`."""

    code: str | None = None
    arr_actual: float | None = None
    arr_estimate: float | None = None
    arr_scheduled: float | None = None
    dep_actual: float | None = None
    dep_estimate: float | None = None
    dep_scheduled: float | None = None


@dataclass(frozen=True)
class Tunnel:
    """A tunnel a line runs through, its two stops inside, and the measured timings."""

    line: str                                   # the commuter line letter
    start: tuple[float, float]                  # on the tracks, before the entry portal
    end: tuple[float, float]                    # on the tracks, past the comeback point
    portal_in: tuple[float, float]
    stops: tuple[tuple[str, tuple[float, float]], tuple[str, tuple[float, float]]]
    portal_out: tuple[float, float]
    back_past_portal_m: float                   # the comeback point, past portal_out
    between_s: float                            # quickest, first stop to second
    back_s: float                               # quickest, second stop to the comeback


def _first(*values: float | None) -> float | None:
    for v in values:
        if v is not None:
            return v
    return None


def _ts(iso: Any) -> float | None:
    if not isinstance(iso, str) or not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


class Way:
    """A tunnel's way along the tracks, with its marks in metres along it. ValueError
    when the network has no such way or a mark is off it or out of order."""

    def __init__(self, net: tracknet.Network, tunnel: Tunnel) -> None:
        self.tunnel = tunnel
        pts = net.route(tuple(tunnel.start), tuple(tunnel.end), MAX_WAY_M)
        if not pts or len(pts) < 2:
            raise ValueError("no way along the tracks")
        self._net = net
        self.pts = [tuple(p) for p in pts]
        self.xy = [net.xy(*p) for p in self.pts]
        cum = [0.0]
        for u, v in zip(self.xy, self.xy[1:]):
            cum.append(cum[-1] + math.dist(u, v))
        self.cum = cum
        self.length = cum[-1]
        self.portal_in = self._mark(tunnel.portal_in)
        self.stop1 = self._mark(tunnel.stops[0][1])
        self.stop2 = self._mark(tunnel.stops[1][1])
        self.portal_out = self._mark(tunnel.portal_out)
        self.back = self.portal_out + tunnel.back_past_portal_m
        if not (0.0 <= self.portal_in - ZONE_OUT_M and self.portal_in < self.stop1
                < self.stop2 < self.portal_out < self.back < self.length):
            raise ValueError("marks out of order")

    def _mark(self, ll: tuple[float, float]) -> float:
        off, s = self.project(*ll)
        if off > LATERAL_M:
            raise ValueError("mark off the way")
        return s

    def project(self, lat: float, lon: float) -> tuple[float, float]:
        """(metres off the way, metres along it) of the nearest point."""
        px, py = self._net.xy(lat, lon)
        best = (math.inf, 0.0)
        for j in range(len(self.xy) - 1):
            (ax, ay), (bx, by) = self.xy[j], self.xy[j + 1]
            vx, vy = bx - ax, by - ay
            l2 = vx * vx + vy * vy
            t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / l2))
            d = math.hypot(px - ax - t * vx, py - ay - t * vy)
            if d < best[0]:
                best = (d, self.cum[j] + t * (self.cum[j + 1] - self.cum[j]))
        return best

    def _xy_at(self, s: float) -> tuple[float, float]:
        cum = self.cum
        s = max(0.0, min(self.length, s))
        lo, hi = 0, len(cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        seg = cum[hi] - cum[lo]
        t = 0.0 if seg <= 0 else (s - cum[lo]) / seg
        (ax, ay), (bx, by) = self.xy[lo], self.xy[hi]
        return (ax + (bx - ax) * t, ay + (by - ay) * t)

    def at(self, s: float) -> tuple[float, float]:
        """[lat, lon] of the point s metres along, to 6 decimals."""
        la, lo = self._net.ll(*self._xy_at(s))
        return (round(la, 6), round(lo, 6))

    def bearing(self, s: float) -> float:
        """Compass bearing of the way at s, the way it runs, to 0.1 deg."""
        (ax, ay), (bx, by) = self._xy_at(s - COURSE_SPAN_M), self._xy_at(s + COURSE_SPAN_M)
        return round(math.degrees(math.atan2(bx - ax, by - ay)) % 360.0, 1)

    def between(self, s0: float, s1: float) -> list[tuple[float, float]]:
        """The way's own points strictly between s0 and s1 (s0 < s1), in order."""
        return [p for p, s in zip(self.pts, self.cum) if s0 < s < s1]

    def schedule(self, s0: float, t0: float, c1: StopClock, c2: StopClock,
                 dep1: float | None, dep2: float | None
                 ) -> tuple[float, float, float, float, float] | None:
        """(arrive first stop, leave it, arrive second, leave it, at the comeback point),
        POSIX seconds, for a train whose fix at t0 lay s0 along; None without times.
        dep1, dep2: the last departure estimates seen for the two stops."""
        t = self.tunnel
        a1 = _first(c1.arr_actual, c1.arr_estimate, c1.arr_scheduled)
        d1 = _first(dep1, c1.dep_actual, c1.dep_scheduled)
        d2 = _first(dep2, c2.dep_actual, c2.dep_scheduled)
        if a1 is None or d1 is None or d2 is None:
            return None
        a1 = max(a1, t0 + (self.stop1 - s0) / (MAX_KMH / 3.6))
        d1 = max(d1, a1)
        if c2.arr_actual is not None:
            # The second stop's arrival is a fact: the train left the first by then.
            d1 = max(a1, min(d1, c2.arr_actual - t.between_s))
            a2 = max(d1 + t.between_s, c2.arr_actual)
        else:
            a2 = d1 + t.between_s
        d2 = max(d2, a2)
        return a1, d1, a2, d2, d2 + t.back_s

    def position(self, s0: float, t0: float,
                 times: tuple[float, float, float, float, float],
                 now: float) -> tuple[float, bool]:
        """(metres along at `now`, moving)."""
        a1, d1, a2, d2, b = times
        if now <= t0:
            return s0, False
        if now < a1:
            return s0 + (self.stop1 - s0) * (now - t0) / (a1 - t0), True
        if now < d1:
            return self.stop1, False
        if now < a2:
            return self.stop1 + (self.stop2 - self.stop1) * (now - d1) / (a2 - d1), True
        if now < d2:
            return self.stop2, False
        if now < b:
            return self.stop2 + (self.back - self.stop2) * (now - d2) / (b - d2), True
        return self.back, False

    def next_stop(self, s: float, times: tuple[float, float, float, float, float],
                  after: StopClock | None) -> tuple[str | None, float | None]:
        """(station code, time) of the next stop of a train DRAWN s along: the stop ahead
        with its arrival, the stop it stands at with its departure (as the timetable
        shows a train standing at a station), and past the second stop the first one
        after the tunnel at its own time (code None when not known)."""
        a1, d1, a2, d2, _ = times
        (code1, _), (code2, _) = self.tunnel.stops
        if s < self.stop1 - AT_STOP_M:
            return code1, a1
        if s <= self.stop1 + AT_STOP_M:
            return code1, d1
        if s < self.stop2 - AT_STOP_M:
            return code2, a2
        if s <= self.stop2 + AT_STOP_M:
            return code2, d2
        if after is None:
            return None, None
        return after.code, _first(after.arr_actual, after.arr_estimate, after.arr_scheduled)


class TunnelPush:
    """Per config entry: pushes the trains in its tunnels, and remembers what it last
    published for each train."""

    def __init__(self, net: tracknet.Network, tunnels: Iterable[Tunnel]) -> None:
        self.net = net
        self.ways: dict[str, Way] = {}
        for t in tunnels:
            try:
                self.ways[t.line.upper()] = Way(net, t)
            except ValueError:
                continue
        self._s: dict[str, float] = {}                  # metres along, while pushed
        self._pub: dict[str, tuple[float, float]] = {}  # position published last
        self._dep: dict[tuple[str, str], float] = {}    # last departure estimate seen

    def apply(self, result: dict[str, Any], observations: Iterable[Any],
              clocks: Mapping[str, Mapping[str, StopClock]] | None,
              now: float, names: Mapping[str, str] | None = None) -> dict[str, int]:
        """Push the published trains that are in a tunnel, in place; {"estimated": n,
        "observed": n} over the trains in service. names: {station code: name}, the
        static timetable's, for an estimated train's next stop (D4b: never a code)."""
        counts = {ESTIMATED: 0, OBSERVED: 0}
        vehicles = result.get("vehicles") or {}
        by_vid = {o.vehicle_id: o for o in observations}
        clocks = clocks or {}
        for vid, clock in clocks.items():
            for code, c in clock.items():
                if c.dep_estimate is not None:
                    self._dep[(vid, code)] = c.dep_estimate
        for vid, rec in vehicles.items():
            if not rec.get("in_service"):
                self._s.pop(vid, None)
                continue
            obs = by_vid.get(vid)
            line = (getattr(obs, "line", None) or "").upper() if obs is not None else ""
            way = self.ways.get(line)
            clock = clocks.get(vid) or {}
            est = self._estimate(vid, rec, way, clock, now) if way is not None else None
            if est is None:
                rec["position_source"] = OBSERVED
                counts[OBSERVED] += 1
                if self._s.pop(vid, None) is not None:
                    # The fix that takes over: along the tracks from the estimate.
                    self._path_from_pub(rec, vid)
                continue
            s, moving, times = est
            self._write(vid, rec, way, s, moving)
            self._next_stop(rec, way, s, times, clock.get(AFTER), names or {})
            counts[ESTIMATED] += 1
        self._pub = {vid: (rec["latitude"], rec["longitude"]) for vid, rec in vehicles.items()}
        for vid in set(self._s) - set(vehicles):
            del self._s[vid]
        self._dep = {k: v for k, v in self._dep.items() if k[0] in vehicles or k[0] in clocks}
        return counts

    def _estimate(self, vid: str, rec: dict[str, Any], way: Way,
                  clock: Mapping[str, StopClock], now: float
                  ) -> tuple[float, bool, tuple[float, float, float, float, float]] | None:
        (code1, _), (code2, _) = way.tunnel.stops
        c1, c2 = clock.get(code1), clock.get(code2)
        if c1 is None or c2 is None:
            return None
        off, s0 = way.project(rec["latitude"], rec["longitude"])
        if off > LATERAL_M or not (way.portal_in - ZONE_OUT_M <= s0 < way.stop1):
            return None
        t0 = _ts(rec.get("observed_at"))
        if t0 is None:
            return None
        times = way.schedule(s0, t0, c1, c2, self._dep.get((vid, code1)),
                             self._dep.get((vid, code2)))
        if times is None:
            return None
        s, moving = way.position(s0, t0, times, now)
        last = self._s.get(vid)
        if last is not None and s < last:
            return last, False, times  # never backwards: held where it was drawn
        return s, moving, times

    @staticmethod
    def _next_stop(rec: dict[str, Any], way: Way, s: float,
                   times: tuple[float, float, float, float, float],
                   after: StopClock | None, names: Mapping[str, str]) -> None:
        """The next stop from where the push DRAWS the train, not the timetable's: a
        stop's departure row counts as ahead until its actual is in, p50 57 s late, so
        the timetable kept a pushed train a stop behind (8660, live 2026-10-16: "Next:
        Aviapolis" standing at Lentoasema). Unnamed: Fleet's is left as it was."""
        code, eta = way.next_stop(s, times, after)
        name = names.get(code) if isinstance(code, str) else None
        if not name:
            return
        rec["next_stop"] = name
        if eta is not None:
            rec["arrival_estimated_at"] = datetime.fromtimestamp(
                round(eta), tz=timezone.utc).isoformat()
        else:
            rec.pop("arrival_estimated_at", None)

    def _write(self, vid: str, rec: dict[str, Any], way: Way, s: float,
               moving: bool) -> None:
        fix = (rec["latitude"], rec["longitude"])
        here = way.at(s)
        rec["fix_latitude"], rec["fix_longitude"] = fix
        rec["latitude"], rec["longitude"] = here
        rec["position_source"] = ESTIMATED
        for key in SEGMENT_KEYS:
            rec.pop(key, None)
        rec.pop("stalled", None)
        crs = way.bearing(s)
        rec["icon_rotation_deg"] = crs
        if moving:
            rec["course_deg"] = crs
            rec["icon_rotation_basis"] = "course"
        else:
            rec.pop("course_deg", None)
            rec["icon_rotation_basis"] = "held"
        rec.pop("track_path", None)
        prev = self._pub.get(vid)
        if prev is not None and tuple(prev) != here:
            path = self._way_path(way, prev, s, here)
            if path is None:
                path = tracknet.track_path(self.net, tuple(prev), here, None)
            if path:
                rec["track_path"] = path
        self._s[vid] = s

    @staticmethod
    def _way_path(way: Way, prev: tuple[float, float], s: float,
                  here: tuple[float, float]) -> list[list[float]] | None:
        """[prev, the way's points up to s, here], when prev lies on the way behind s."""
        off, sp = way.project(*prev)
        if off > LATERAL_M or sp >= s:
            return None
        out: list[list[float]] = []
        for la, lo in [tuple(prev)] + way.between(sp, s) + [here]:
            p = [round(la, 6), round(lo, 6)]
            if not out or out[-1] != p:
                out.append(p)
        out[-1] = [here[0], here[1]]
        if len(out) < 2 or len(out) > tracknet.MAX_POINTS:
            return None
        return out

    def _path_from_pub(self, rec: dict[str, Any], vid: str) -> None:
        prev = self._pub.get(vid)
        here = (rec["latitude"], rec["longitude"])
        if prev is None or tuple(prev) == here:
            return
        path = tracknet.track_path(self.net, tuple(prev), here, None)
        if path:
            rec["track_path"] = path
