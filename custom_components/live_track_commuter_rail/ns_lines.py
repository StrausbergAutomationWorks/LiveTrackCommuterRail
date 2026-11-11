"""The Netherlands (NS) for the commuter operator: the lines NS's Sprinters run along. No Home Assistant imports.

SSOT 15 (Lee 2026-11-11 ~03:00 CST: SPR here, IC and the regional trains to Live Track Intercity Rail; one shared
client in saw-livetrack). The shared client saw_livetrack.ns polls NS's vehicle feed once for every Live Track
integration and joins each train to its trip in OVapi's timetable; for a train it names, `path` is the SpoorKaart
stations its track passes, in order (its stops placed on SpoorKaart's stations and joined by the shortest path through
SpoorKaart's station graph; Lee 03:1x: "lines from SpoorKaart").

THE LINES. A train's line is its path's legs, each the SpoorKaart line of that station pair (sweden_lines.assemble: a
leg ending short of its station runs on to it; a pair SpoorKaart does not draw is the straight line). Each path is
assembled once, appended to the geometry's `rail_shapes`, and every train on it maps to it in `trip_shapes`: the
off-rail check (rail.RailCheck) and the way between two fixes (shapepath, D3c-v; Lee 2026-10-20, "A train cannot exist
off of the tracks") read it as they read a GTFS railroad's. The geometry's `fetched_at` moves on whenever a pattern is
added, so RailCheck takes the new line before the train on it is checked.

IDENTITY "<number>-<day of the service date>" (Intercity Rail's Dutch form); the bare number for a train the timetable
does not name.
"""

from __future__ import annotations

import time
from typing import Any, Iterable, Mapping

from saw_livetrack.gtfs import STATIC_VERSION

from .sweden_lines import assemble, pair_key, pattern_id


def identity(number: str, service_date: str | None) -> str:
    """'4072', '20261111' -> '4072-11'; the bare number with no usable date."""
    d = (service_date or "").strip()
    if len(d) == 8 and d.isdigit():
        return f"{number}-{int(d[6:8])}"
    return number


def legs_of(path: Iterable[str], lines: Mapping[str, Any], coords: Mapping[str, Any]) -> list[list]:
    """[[from, to, pair key or None], ...] for a SpoorKaart path; a station with no place is left out."""
    ids = [c for c in path if c in coords]
    out = []
    for a, b in zip(ids, ids[1:]):
        if a == b:
            continue
        k = pair_key(a, b)
        out.append([a, b, k if k in lines else None])
    return out


class NsGeometry:
    """The operator's "timetable" for everything downstream that reads one: station names and places, the trains'
    lines assembled per path, and each train's line."""

    def __init__(self) -> None:
        self._patterns: dict[str, int] = {}
        self._base = time.time()
        self._generation = 0
        self._version: Any = None
        self.data: dict[str, Any] = {"v": STATIC_VERSION, "fetched_at": self._base, "stops": {}, "stop_pos": {},
                                     "rail_shapes": [], "trip_shapes": {}, "extras": {}}

    def update(self, trains: Iterable[Mapping[str, Any]], stations: Mapping[str, Mapping[str, Any]],
               lines: Mapping[str, Any], version: Any = None) -> dict[str, Any]:
        """The geometry with this poll's trains' lines in it (the same dict, changed in place)."""
        d = self.data
        changed = False
        if stations and version != self._version:
            self._version = version
            d["stops"] = {s: v.get("name") or s for s, v in stations.items()}
            # A new SpoorKaart or timetable: lines assembled from the old one are not reused.
            self._patterns = {}
            d["rail_shapes"] = []
            changed = True
        coords = {s: (v["lat"], v["lon"]) for s, v in (stations or {}).items()
                  if v.get("lat") is not None and v.get("lon") is not None}
        trips: dict[str, list[int]] = {}
        for tr in trains or ():
            legs = legs_of(tr.get("path") or (), lines or {}, coords)
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
            trips[identity(str(tr.get("number") or ""), tr.get("service_date"))] = [idx, 0]
            # Where it stops (Fleet's platform hold, D4c): its calls' stations, never one it passes.
            for c in tr.get("calls") or ():
                s = c.get("code")
                if s in coords and s not in d["stop_pos"]:
                    d["stop_pos"][s] = [coords[s][0], coords[s][1]]
        d["trip_shapes"] = trips
        if changed:
            self._generation += 1
            d["fetched_at"] = self._base + self._generation
        return d
