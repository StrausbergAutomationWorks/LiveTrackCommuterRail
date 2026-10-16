"""A railway's track network, and the way a train went between two fixes on it, for the
card's `track_path` (06_MAP_CONTRACT.md D3c-v). No Home Assistant imports.

The network ships with the integration as rail/<operator>_tracks.json.gz, built by
tools/build_tracks.py: lines of [lat, lon] that meet only at their ends (two lines sharing
an end point, to 6 decimals, are joined there). A train passes from one line to the next
only where its direction turns by at most MAX_TURN_DEG, so a path never doubles back
through a switch; it reverses only at a buffer stop.

Finland (SSOT 8.3, backlog 290): Fintraffic's infra-api tracks, CC BY 4.0, modified.
MEASURED on capture round 1 (bin\\ltcr290_measure2.txt, ltcr290_cutids.txt): 152,429
pairs of consecutive commuter fixes, 99.75% routed, p50 0.1 ms, p99 0.4 ms each; the
path's length p99 1.0 times the straight line; up to 257 points.
"""

from __future__ import annotations

import gzip
import heapq
import json
import math
import os
from collections import defaultdict

R_EARTH = 6371000.0
# A fix farther than this from every track is not routed (Digitraffic's commuter fixes sit
# p99 2 m from the infra-api tracks, FI_TRACK_GEOMETRY_20261016.md section 3).
SNAP_M = 15.0
# Tracks considered for a fix: the nearest, and any within this much of it. Parallel
# tracks are about 4.5 m apart, so the nearest alone can be the wrong one.
SNAP_SLACK_M = 6.0
# The sharpest turn a train makes from one track to the next. A switch diverges by a few
# degrees; doubling back is 180.
MAX_TURN_DEG = 60.0
# Reversing at a buffer stop costs this much extra, so a forward way always wins.
REVERSE_PENALTY_M = 200.0
# The direction of a line at its end is read over this far.
DIR_SPAN_M = 10.0
CELL_M = 200.0


def cells(u: tuple[float, float], v: tuple[float, float], size: float) -> set:
    """The grid cells a segment passes through (walked along it, so a long straight
    segment costs its length, not its bounding box)."""
    n = max(1, int(math.dist(u, v) / (size / 2)) + 1)
    out = set()
    for k in range(n + 1):
        x = u[0] + (v[0] - u[0]) * k / n
        y = u[1] + (v[1] - u[1]) * k / n
        out.add((int(x // size), int(y // size)))
    return out


class _Line:
    __slots__ = ("pts", "xy", "cum", "n0", "n1", "d0", "d1")


class Network:
    def __init__(self, lines: list, lat0: float | None = None) -> None:
        if lat0 is None:
            s = n = 0
            for ln in lines:
                for la, _ in ln:
                    s += la
                    n += 1
            lat0 = s / n if n else 0.0
        # One flat scale for the whole network: over Finland's commuter area (59.8 to
        # 61.6 N) east-west distances are off by at most about 3%.
        self.lat0 = lat0
        self.kx = math.cos(math.radians(self.lat0)) * R_EARTH * math.pi / 180.0
        self.ky = R_EARTH * math.pi / 180.0
        node_id: dict = {}
        self.lines: list[_Line] = []
        self.at: dict[int, list[tuple[int, int]]] = defaultdict(list)
        self.grid: dict = defaultdict(list)
        for ln in lines:
            if len(ln) < 2:
                continue
            L = _Line()
            L.pts = [(float(a), float(b)) for a, b in ln]
            L.xy = [self.xy(a, b) for a, b in L.pts]
            cum = [0.0]
            for p, q in zip(L.xy, L.xy[1:]):
                cum.append(cum[-1] + math.dist(p, q))
            if cum[-1] <= 0:
                continue
            L.cum = cum
            k0 = (round(L.pts[0][0], 6), round(L.pts[0][1], 6))
            k1 = (round(L.pts[-1][0], 6), round(L.pts[-1][1], 6))
            L.n0 = node_id.setdefault(k0, len(node_id))
            L.n1 = node_id.setdefault(k1, len(node_id))
            L.d0 = self._dir(L, 0)
            L.d1 = self._dir(L, 1)
            i = len(self.lines)
            self.lines.append(L)
            self.at[L.n0].append((i, 0))
            self.at[L.n1].append((i, 1))
            for j, (p, q) in enumerate(zip(L.xy, L.xy[1:])):
                for c in cells(p, q, CELL_M):
                    self.grid[c].append((i, j))
        self._cos_turn = math.cos(math.radians(MAX_TURN_DEG))

    def __len__(self) -> int:
        return len(self.lines)

    def xy(self, lat: float, lon: float) -> tuple[float, float]:
        return (lon * self.kx, lat * self.ky)

    def ll(self, x: float, y: float) -> tuple[float, float]:
        return (y / self.ky, x / self.kx)

    def _dir(self, L: _Line, end: int) -> tuple[float, float]:
        """Unit vector of travel leaving the line through this end (pointing out of it)."""
        if end == 0:
            base = L.xy[0]
            far = self._point_at(L, min(DIR_SPAN_M, L.cum[-1]))
        else:
            base = L.xy[-1]
            far = self._point_at(L, max(0.0, L.cum[-1] - DIR_SPAN_M))
        dx, dy = base[0] - far[0], base[1] - far[1]
        n = math.hypot(dx, dy) or 1.0
        return (dx / n, dy / n)

    @staticmethod
    def _point_at(L: _Line, s: float) -> tuple[float, float]:
        cum = L.cum
        s = max(0.0, min(cum[-1], s))
        lo, hi = 0, len(cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        seg = cum[hi] - cum[lo]
        t = 0.0 if seg <= 0 else (s - cum[lo]) / seg
        (ax, ay), (bx, by) = L.xy[lo], L.xy[hi]
        return (ax + (bx - ax) * t, ay + (by - ay) * t)

    def snap(self, lat: float, lon: float) -> list[tuple[float, int, float]]:
        """[(distance m, line, distance along it)] for the tracks the point may be on,
        nearest first; [] when none is within SNAP_M."""
        px, py = self.xy(lat, lon)
        cx, cy = int(px // CELL_M), int(py // CELL_M)
        best: dict[int, tuple[float, float]] = {}
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for i, j in self.grid.get((cx + dx, cy + dy), ()):
                    L = self.lines[i]
                    (ax, ay), (bx, by) = L.xy[j], L.xy[j + 1]
                    vx, vy = bx - ax, by - ay
                    l2 = vx * vx + vy * vy
                    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / l2))
                    d = math.hypot(px - ax - t * vx, py - ay - t * vy)
                    if d <= SNAP_M and (i not in best or d < best[i][0]):
                        best[i] = (d, L.cum[j] + t * (L.cum[j + 1] - L.cum[j]))
        if not best:
            return []
        out = sorted((d, i, s) for i, (d, s) in best.items())
        lim = out[0][0] + SNAP_SLACK_M
        return [c for c in out if c[0] <= lim]

    def _turn_ok(self, arr: tuple[float, float], dep_out: tuple[float, float]) -> bool:
        """arr: travel direction arriving at the node (out of the line arrived on).
        dep_out: the next line's end direction pointing OUT of it; travel along it is the
        reverse."""
        return -(arr[0] * dep_out[0] + arr[1] * dep_out[1]) >= self._cos_turn

    def route(self, a: tuple[float, float], b: tuple[float, float],
              max_m: float) -> list[tuple[float, float]] | None:
        """The shortest way along the tracks from a to b, as [lat, lon] points from a's
        place on its track to b's; None when either is off the network or nothing is
        found within max_m of travel (the snap distances count as travel)."""
        self.last_lines = ()
        ca = self.snap(*a)
        cb = self.snap(*b)
        if not ca or not cb:
            return None
        goals: dict[int, list[tuple[float, float]]] = defaultdict(list)
        for d, i, s in cb:
            goals[i].append((s, d))
        best = None  # (cost, ((line, from, to), ...))
        for da, i, sa in ca:
            for sb, db in goals.get(i, ()):
                c = abs(sb - sa) + da + db
                if c <= max_m and (best is None or c < best[0]):
                    best = (c, ((i, sa, sb),))
        heap: list = []
        seen: set = set()
        tie = 0
        for da, i, sa in ca:
            L = self.lines[i]
            for end, cost in ((1, L.cum[-1] - sa), (0, sa)):
                node = L.n1 if end == 1 else L.n0
                tie += 1
                heapq.heappush(heap, (cost + da, tie, node, i, end,
                                      ((i, sa, L.cum[-1] if end == 1 else 0.0),)))
        while heap:
            c, _, node, li, lend, spec = heapq.heappop(heap)
            if c > max_m or (best is not None and c >= best[0]):
                break
            key = (node, li, lend)
            if key in seen:
                continue
            seen.add(key)
            Larr = self.lines[li]
            arr = Larr.d1 if lend == 1 else Larr.d0
            inc = self.at[node]
            if len(inc) == 1:
                # A buffer stop: a train reverses at a terminus platform. Back along the
                # same line, at a cost, so any forward way wins.
                cr = c + REVERSE_PENALTY_M
                s_from = Larr.cum[-1] if lend == 1 else 0.0
                for sb, db in goals.get(li, ()):
                    cc = cr + abs(sb - s_from) + db
                    if cc <= max_m and (best is None or cc < best[0]):
                        best = (cc, spec + ((li, s_from, sb),))
                cn = cr + Larr.cum[-1]
                if cn <= max_m and (best is None or cn < best[0]):
                    tie += 1
                    heapq.heappush(heap, (cn, tie, Larr.n0 if lend == 1 else Larr.n1, li,
                                          0 if lend == 1 else 1,
                                          spec + ((li, s_from, Larr.cum[-1] - s_from),)))
                continue
            for j, jend in inc:
                if j == li and jend == lend:
                    continue
                Lj = self.lines[j]
                if not self._turn_ok(arr, Lj.d1 if jend == 1 else Lj.d0):
                    continue
                s_from = Lj.cum[-1] if jend == 1 else 0.0
                for sb, db in goals.get(j, ()):
                    cc = c + abs(sb - s_from) + db
                    if cc <= max_m and (best is None or cc < best[0]):
                        best = (cc, spec + ((j, s_from, sb),))
                cn = c + Lj.cum[-1]
                if cn <= max_m and (best is None or cn < best[0]):
                    far_end = 0 if jend == 1 else 1
                    tie += 1
                    heapq.heappush(heap, (cn, tie, Lj.n0 if far_end == 0 else Lj.n1, j, far_end,
                                          spec + ((j, s_from, Lj.cum[-1] - s_from),)))
        if best is None:
            self.last_lines = ()
            return None
        self.last_lines = tuple(i for i, _, _ in best[1])
        pts: list[tuple[float, float]] = []
        for i, s0, s1 in best[1]:
            for p in self._piece(self.lines[i], s0, s1):
                if not pts or abs(pts[-1][0] - p[0]) + abs(pts[-1][1] - p[1]) > 1e-7:
                    pts.append(p)
        return pts

    def _piece(self, L: _Line, s0: float, s1: float) -> list[tuple[float, float]]:
        """[lat, lon] points of the line from s0 to s1 along it, in that order."""
        lo, hi = (s0, s1) if s0 <= s1 else (s1, s0)
        xy = [self._point_at(L, lo)]
        xy += [p for p, s in zip(L.xy, L.cum) if lo < s < hi]
        xy.append(self._point_at(L, hi))
        if s0 > s1:
            xy.reverse()
        return [self.ll(x, y) for x, y in xy]


def simplify(pts: list, tol_m: float, kx: float, ky: float) -> list:
    """Douglas-Peucker in metres on [lat, lon] points; the first and last points stay."""
    if len(pts) < 3:
        return list(pts)
    xy = [(lo * kx, la * ky) for la, lo in pts]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        (ax, ay), (bx, by) = xy[i], xy[j]
        vx, vy = bx - ax, by - ay
        l2 = vx * vx + vy * vy
        bd, bk = -1.0, None
        for k in range(i + 1, j):
            px, py = xy[k]
            t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / l2))
            d = math.hypot(px - ax - t * vx, py - ay - t * vy)
            if d > bd:
                bd, bk = d, k
        if bk is not None and bd > tol_m:
            keep[bk] = True
            stack += [(i, bk), (bk, j)]
    return [p for p, k in zip(pts, keep) if k]


TRACKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rail")
FORMAT = 1
# The shortest way is searched up to this many times the straight distance, and at
# least this far beyond it (MEASURED: path/straight p99 1.0; a pair needing more doubled
# back, and gets no path).
DETOUR_FACTOR = 3.0
DETOUR_MIN_M = 1000.0
# A path implying more than this is a position jump, not a run (MEASURED: 142 of
# 152,429 pairs, up to 34 km in 30 s; VR's commuter trains run at most 160 km/h).
MAX_KMH = 200.0
# The contract's limits (D3c-v): 2 to 500 points.
MAX_POINTS = 500
PATH_TOLERANCE_M = 1.0


def load(operator_id: str) -> Network | None:
    """The railroad's track network, or None without a usable file. Blocking: run it in
    an executor."""
    path = os.path.join(TRACKS_DIR, f"{operator_id}_tracks.json.gz")
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("format") != FORMAT:
        return None
    net = Network(doc.get("lines") or [], doc.get("lat0"))
    return net if len(net) else None


def track_path(net: Network, start: tuple[float, float], end: tuple[float, float],
               seconds: float | None) -> list[list[float]] | None:
    """`track_path` from the position published last to the new one: [lat, lon] pairs
    along the tracks, beginning at `start` and ending at `end` exactly. None when either
    is off the network, no way is found within the detour limit, or the way implies more
    than MAX_KMH over `seconds`."""
    if start == end:
        return None
    straight = math.dist(net.xy(*start), net.xy(*end))
    pts = net.route(start, end, max(DETOUR_FACTOR * straight, straight + DETOUR_MIN_M))
    if pts is None:
        return None
    length = sum(math.dist(net.xy(*a), net.xy(*b)) for a, b in zip(pts, pts[1:]))
    if seconds is not None and seconds > 0 and length / seconds * 3.6 > MAX_KMH:
        return None
    pts = [tuple(start)] + pts + [tuple(end)]
    tol = PATH_TOLERANCE_M
    out = simplify(pts, tol, net.kx, net.ky)
    while len(out) > MAX_POINTS:
        tol *= 2
        out = simplify(pts, tol, net.kx, net.ky)
    res: list[list[float]] = []
    for la, lo in out:
        p = [round(la, 6), round(lo, 6)]
        if not res or res[-1] != p:
            res.append(p)
    res[-1] = [end[0], end[1]]
    return res if len(res) >= 2 else None
