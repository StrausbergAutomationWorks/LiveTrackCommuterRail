"""Sweden (Trafikverket) for the commuter operators: which runs are drawn, and the lines they are drawn along. No Home
Assistant imports.

SSOT 14 (Lee 2026-11-10 00:33 CST, backlog 327). The shared client saw_livetrack.trafikverket polls Trafikverket once
for every Live Track integration and routes each run to ONE consumer and brand (06_MAP_CONTRACT.md D1): `Pendeltåg`
(SL Pendeltåg, Västtågen's pendeltåg) and Arlanda Express here. A run is one train with a fix and the calls of the
trip it is on (call_record: sig, activity, advertised, estimated, actual, public, canceled).

IDENTITY "<advertised number>-<day of the run date>", Live Track Intercity Rail's Swedish form: one number runs on
consecutive dates.

SKIPPED (RunFilter, the rules Intercity Rail's Swedish operators have run since 2026-11-08): no calls; every public
call cancelled; a first sight with a fix over MAX_FIRST_AGE_S old (a train Trafikverket stopped reporting); a run whose
last call's time has passed with a fix over FINISHED_AGE_S old (a finished run still in the position window).

THE LINES. Sweden's timetable has no shapes (the national GTFS, measured 2026-11-08). "Lines from OSM station pairs,
shipped" (Lee): tools/sweden_lines.py routes every station pair the commuter trains run between once on OpenStreetMap's
track and writes rail/sweden_lines.json.gz (ODbL 1.0, its `meta`). A trip's line is its legs, one per pair of
consecutive station signatures in its calls (public or not, as the build took them): the shipped line of that pair;
else, for a pair the build never saw, the shortest chain of shipped pairs between the two stations when it is not much
longer than their straight line (chain); else the straight line (the build report lists each). A shipped leg ending
short of its station runs on to the station's point (assemble). Each stop pattern is
assembled once, appended to the geometry's `rail_shapes`, and every trip on it maps to it in `trip_shapes`: the
off-rail check (rail.RailCheck) and the way between two fixes (shapepath, D3c-v) read the same geometry as for a
railroad with a GTFS timetable. The geometry's `fetched_at` moves on whenever a pattern is added, so RailCheck takes
the new line before the train on it is checked.

Points are 1e-5 degree integers, the first absolute and every later one a difference, from the lower signature to the
higher (Python string order).
"""

from __future__ import annotations

import gzip
import hashlib
import heapq
import json
import math
import os
import time
from typing import Any, Iterable, Mapping, Sequence

from saw_livetrack.gtfs import STATIC_VERSION

RAIL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rail")
LINES_FILE = os.path.join(RAIL_DIR, "sweden_lines.json.gz")
ENDS_FILE = os.path.join(RAIL_DIR, "sweden_ends.json")
# The shipped files' own format; a file of another version is not read.
DATA_VERSION = 1

# A shipped leg ending farther than this from its station runs on to the station's point (assemble).
STUB_M = 50.0
# A pair with no shipped line takes a chain of shipped pairs no longer than this (chain).
CHAIN_X = 1.5
CHAIN_EXTRA_M = 2000.0
MAX_FIRST_AGE_S = 300.0
FINISHED_AGE_S = 300.0
FORGET_S = 3600.0


def identity(number: str, date: str | None) -> str:
    """'2241', '2026-11-10' -> '2241-10'; the bare number with no usable date."""
    d = (date or "").strip()
    if len(d) == 10 and d[8:10].isdigit():
        return f"{number}-{int(d[8:10])}"
    return number


def pair_key(a: str, b: str) -> str:
    lo, hi = sorted((a, b))
    return f"{lo}|{hi}"


def decode(encoded: Sequence[int]) -> list[tuple[float, float]]:
    """The shipped delta-encoded integers -> [(lat, lon), ...]."""
    out: list[tuple[float, float]] = []
    la = lo = 0
    for i in range(0, len(encoded) - 1, 2):
        la += int(encoded[i])
        lo += int(encoded[i + 1])
        out.append((la / 1e5, lo / 1e5))
    return out


def signatures(calls: Iterable[Mapping[str, Any]]) -> list[str]:
    """A trip's calls in order -> its station signatures, consecutive repeats dropped."""
    out: list[str] = []
    for c in calls:
        s = c.get("sig")
        if s and (not out or out[-1] != s):
            out.append(s)
    return out


def plan(sigs: Sequence[str], has_line, coords: Mapping[str, Any]) -> list[list]:
    """[[from, to, pair key or None], ...] for a trip's signatures; a signature with no coordinates is left out, a
    repeat makes no leg, a pair with no shipped line is None (the straight line)."""
    ids = [s for s in sigs if s in coords]
    out = []
    for a, b in zip(ids, ids[1:]):
        if a == b:
            continue
        out.append([a, b, pair_key(a, b) if has_line(a, b) else None])
    return out


def pair_graph(lines: Mapping[str, Sequence[int]]) -> dict[str, dict[str, float]]:
    """{signature: {neighbour: metres}} over the shipped pairs, each pair's length along its line."""
    g: dict[str, dict[str, float]] = {}
    for key, enc in lines.items():
        a, b = key.split("|", 1)
        pts = decode(enc)
        length = sum(_metres(p, q) for p, q in zip(pts, pts[1:]))
        g.setdefault(a, {})[b] = length
        g.setdefault(b, {})[a] = length
    return g


def chain(a: str, b: str, graph: Mapping[str, Mapping[str, float]], coords: Mapping[str, Sequence[float]]
          ) -> list[str] | None:
    """The shortest run of shipped pairs from station a to b, as its signatures [a, ..., b], when it is no longer
    than CHAIN_X times their straight line plus CHAIN_EXTRA_M; None otherwise. MEASURED live 2026-11-10
    (bin\\se_ltcr_off.txt): some Arlanda Express runs announce Ulriksdal and then Arlanda S, a pair the 19 days the
    lines were built from never held, and its straight leg cut 25 km across country while the shipped pairs along
    the track join the two."""
    if a not in graph or b not in graph or a not in coords or b not in coords:
        return None
    limit = CHAIN_X * _metres(coords[a], coords[b]) + CHAIN_EXTRA_M
    best = {a: 0.0}
    prev: dict[str, str] = {}
    heap = [(0.0, a)]
    while heap:
        d, s = heapq.heappop(heap)
        if s == b:
            out = [b]
            while out[-1] != a:
                out.append(prev[out[-1]])
            return out[::-1]
        if d > best.get(s, math.inf) or d > limit:
            continue
        for t, w in graph.get(s, {}).items():
            nd = d + w
            if nd <= limit and nd < best.get(t, math.inf):
                best[t] = nd
                prev[t] = s
                heapq.heappush(heap, (nd, t))
    return None


def expand(legs: Sequence[Sequence[Any]], graph: Mapping[str, Mapping[str, float]],
           coords: Mapping[str, Sequence[float]]) -> list[list]:
    """The legs with every straight one (no shipped line) replaced by its chain of shipped pairs where one exists."""
    out: list[list] = []
    for a, b, key in legs:
        path = chain(a, b, graph, coords) if key is None else None
        if path is None:
            out.append([a, b, key])
            continue
        for x, y in zip(path, path[1:]):
            out.append([x, y, pair_key(x, y)])
    return out


def pattern_id(legs: Sequence[Sequence[Any]]) -> str:
    """A stable id for a trip's line: the digest of its legs."""
    return "se" + hashlib.sha1(json.dumps(legs, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]


def _metres(p: Sequence[float], q: Sequence[float]) -> float:
    k = 111195.0
    return math.hypot((p[0] - q[0]) * k, (p[1] - q[1]) * k * math.cos(math.radians(p[0])))


def assemble(legs: Sequence[Sequence[Any]], lines: Mapping[str, Sequence[int]],
             coords: Mapping[str, Sequence[float]]) -> list[list[float]]:
    """The legs -> one line of [lat, lon] at 5 decimals, each leg the shipped line (reversed when run from the higher
    signature to the lower) or the straight line, the shared ends once.

    A shipped leg whose end lies more than STUB_M from its station runs on to the station's point. MEASURED live
    2026-11-10 (bin\\se_ltcr_off.txt, se_ltcr_pairs.txt): the router snapped some stations to track up to 500 m away
    (G|Gas starts 500 m from Göteborg C, Söc|Söd ends 484 m from Södertälje hamn, Jbo|Vhe 372 m short of
    Västerhaninge), so consecutive legs did not meet and trains at those platforms sat 350-560 m off their line."""
    out: list[list[float]] = []
    for a, b, key in legs:
        if key is not None and key in lines:
            pts = decode(lines[key])
            if a > b:
                pts.reverse()
            if pts and _metres(pts[0], coords[a]) > STUB_M:
                pts.insert(0, tuple(coords[a]))
            if pts and _metres(pts[-1], coords[b]) > STUB_M:
                pts.append(tuple(coords[b]))
        else:
            pts = [tuple(coords[a]), tuple(coords[b])]
        for la, lo in pts:
            p = [round(float(la), 5), round(float(lo), 5)]
            if not out or out[-1] != p:
                out.append(p)
    return out


def load_lines(path: str = LINES_FILE) -> dict[str, list[int]]:
    """{pair key: encoded points} from the shipped file; {} when missing or of another version. Blocking."""
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(d, dict) or d.get("v") != DATA_VERSION:
        return {}
    return {k: list(v[1]) for k, v in (d.get("lines") or {}).items()}


def load_ends(path: str = ENDS_FILE) -> dict[str, dict[str, Any]]:
    """{signature: {"name", "settlement", "population", ...}}: the end-city table; {} when missing or unreadable.
    Blocking."""
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(d, dict) or d.get("v") != DATA_VERSION:
        return {}
    return dict(d.get("ends") or {})


def is_stop(call: Mapping[str, Any], has_public: bool, fallback_stops: Sequence[str]) -> bool:
    """A call the train stops at for passengers: a public one; on a trip with NO public call (Arlanda Express
    advertises none, measured on 3,162 trips 2026-11-05..23), one at the operator's own stations."""
    if has_public:
        return bool(call.get("public"))
    return call.get("sig") in fallback_stops


def stop_signatures(calls: Sequence[Mapping[str, Any]], fallback_stops: Sequence[str]) -> list[str]:
    """The uncancelled stations a trip stops at, in order, each once (is_stop)."""
    has_public = any(c.get("public") for c in calls)
    out: list[str] = []
    for c in calls:
        s = c.get("sig")
        if s and not c.get("canceled") and is_stop(c, has_public, fallback_stops) and s not in out:
            out.append(s)
    return out


def terminal_time(calls: list[Mapping[str, Any]], delay: int | None) -> float | None:
    """When the trip's last call falls: its actual, else its estimate, else advertised plus the last delay."""
    for c in reversed(calls):
        if c.get("canceled") or c.get("advertised") is None:
            continue
        if c.get("actual") is not None:
            return c["actual"]
        if c.get("estimated") is not None:
            return c["estimated"]
        return c["advertised"] + (delay or 0)
    return None


def last_delay(calls: list[Mapping[str, Any]]) -> int | None:
    """The delay at the trip's last call with an actual time, in seconds; None with none."""
    delay = None
    for c in calls:
        if c.get("actual") is not None and c.get("advertised") is not None:
            delay = int(c["actual"] - c["advertised"])
    return delay


class RunFilter:
    """Per config entry: which runs are drawn this poll (module docstring, SKIPPED), and which have been seen."""

    def __init__(self) -> None:
        self._seen: dict[str, float] = {}
        self.skipped: dict[str, int] = {}

    def keep(self, runs: Iterable[Mapping[str, Any]] | None, now: float) -> list[Mapping[str, Any]]:
        out = []
        skipped: dict[str, int] = {}

        def skip(reason: str) -> None:
            skipped[reason] = skipped.get(reason, 0) + 1

        for run in runs or ():
            pos = run.get("position") or {}
            calls = list(run.get("calls") or ())
            if not calls or pos.get("lat") is None or pos.get("lon") is None:
                skip("no_calls")
                continue
            public = [c for c in calls if c.get("public")]
            if public and all(c.get("canceled") for c in public):
                skip("canceled")
                continue
            key = identity(str(run.get("number") or ""), run.get("date"))
            age = now - float(pos.get("ts") or 0.0)
            if key not in self._seen and age > MAX_FIRST_AGE_S:
                skip("stale_first_sight")
                continue
            end = terminal_time(calls, last_delay(calls))
            if end is not None and now > end and age > FINISHED_AGE_S:
                skip("finished")
                continue
            self._seen[key] = now
            out.append(run)
        for k in [k for k, t in self._seen.items() if now - t > FORGET_S]:
            self._seen.pop(k, None)
        self.skipped = skipped
        return out


class SwedenGeometry:
    """The operator's "timetable" for everything downstream that reads one: station names and places, the shipped
    lines assembled per stop pattern, each trip's line, and the end-city table (under "extras"). Blocking the first
    time (the shipped files)."""

    def __init__(self, fallback_stops: Iterable[str] = (), lines_path: str = LINES_FILE,
                 ends_path: str = ENDS_FILE) -> None:
        self._fallback_stops = tuple(fallback_stops)
        self._lines_path, self._ends_path = lines_path, ends_path
        self._lines: dict[str, list[int]] | None = None
        self._graph: dict[str, dict[str, float]] = {}
        self._ends: dict[str, dict[str, Any]] | None = None
        self._patterns: dict[str, int] = {}
        self._base = time.time()
        self._generation = 0
        self._stations_version: Any = None
        self.data: dict[str, Any] = {"v": STATIC_VERSION, "fetched_at": self._base, "stops": {},
                                     "stop_pos": {}, "rail_shapes": [], "trip_shapes": {}, "extras": {"ends": {}}}

    @property
    def shipped_pairs(self) -> int:
        return len(self._lines or {})

    def update(self, runs: Iterable[Mapping[str, Any]], stations: Mapping[str, Mapping[str, Any]],
               stations_version: Any = None) -> dict[str, Any]:
        """The geometry with this poll's runs' lines in it (the same dict, changed in place)."""
        if self._lines is None:
            self._lines = load_lines(self._lines_path)
            self._graph = pair_graph(self._lines)
            self._ends = load_ends(self._ends_path)
            self.data["extras"] = {"ends": self._ends}
        d = self.data
        changed = False
        if stations and stations_version != self._stations_version:
            self._stations_version = stations_version
            d["stops"] = {s: v.get("name") or s for s, v in stations.items()}
            changed = True
        coords = {s: (v["lat"], v["lon"]) for s, v in (stations or {}).items()
                  if v.get("lat") is not None and v.get("lon") is not None}
        lines = self._lines

        def has(a: str, b: str) -> bool:
            return pair_key(a, b) in lines
        trips: dict[str, list[int]] = {}
        for run in runs or ():
            sigs = signatures(run.get("calls") or ())
            legs = expand(plan(sigs, has, coords), self._graph, coords)
            if not legs:
                continue
            pid = pattern_id(legs)
            idx = self._patterns.get(pid)
            if idx is None:
                pts = assemble(legs, lines, coords)
                if len(pts) < 2:
                    continue
                idx = len(d["rail_shapes"])
                d["rail_shapes"].append(pts)
                self._patterns[pid] = idx
                changed = True
            trips[identity(str(run.get("number") or ""), run.get("date"))] = [idx, 0]
            # Where it stops (Fleet's platform hold, D4c): its stations, never a timing point it passes.
            for s in stop_signatures(run.get("calls") or (), self._fallback_stops):
                if s in coords and s not in d["stop_pos"]:
                    d["stop_pos"][s] = [coords[s][0], coords[s][1]]
        d["trip_shapes"] = trips
        if changed:
            self._generation += 1
            d["fetched_at"] = self._base + self._generation
        return d
