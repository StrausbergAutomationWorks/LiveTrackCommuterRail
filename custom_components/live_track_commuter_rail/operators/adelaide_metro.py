"""Adelaide Metro's trains (South Australia), on the shared Adelaide Metro client. No Home Assistant imports. SSOT 19.

Lee 2026-11-13 15:01 CST ("Go for creating an operator module, testing and a mutation check, translations for the new
region, and a deploy"), after reading Adelaide Metro's developer page (CC BY 4.0; credit "Adelaide Metro - Department
for Infrastructure and Transport, South Australia"). Operator id `adelaide_metro` (Lee, asked), region AU-SA. The feed is
every mode at once, so it is read through saw_livetrack.adelaide_metro (saw-livetrack 0.2.39, one poller per Home
Assistant), registered as "commuter": route_type 2, the eleven rail routes. Record of the feed:
35_Dependencies/third_party/adelaide-metro/SSOT.md.

THE FEED (MEASURED 2026-11-13 07:3x Adelaide time, bin\\adl_m1.txt): GPS positions with bearing and speed on every
train (17 at once, fix age 9-32 s), every trip in the timetable, route_id and direction_id on every row. vehicle.id and
vehicle.label are the railcar's own number (3011, 4006): the identity, as Metra's unit. No public train number exists.

LABEL (Lee: "Read the maps of Adelaide that I saved"): the maps print no codes, only line names and colours; Adelaide
Metro's own website names each train route by its code ("FLNDRS - Flinders to City"; Adelaide Railway Station's page
lists BEL, FLNDRS, GAW, GAWC, GRNG, NOAR, OSBORN, OUTHA, PTDOCK, SALIS, SEAFRD), the timetable's route_short_name and
route_id. So the label is the route code, CUT TO ITS FIRST THREE LETTERS (Lee 2026-11-13 19:33 CST: "Use the first 3
letters for Adelaide"), because the full code did not fit the 28 px disc: MEASURED on the live map, GAWC 26 px and
PTDOCK 31 px in a 23 px label box, and "GAWC" read "GAWG" on the white disc (SSOT 19). GAW and GAWC both read GAW;
FLN, GRN, NOA, OSB, OUT, PTD, SAL, SEA, BEL for the rest. HOVER "SEAFRD to Seaford · railcar 4006": the FULL code, the
trip's headsign, the railcar.

THE LOOK: the line's colour from Adelaide Metro's rail network map of 26 January 2026 (10_Reference, its legend,
MEASURED from the vector paths, bin\\adl_map_read.txt): Belair #6ABF4B, Seaford & Flinders #FF7F30, Gawler #C23B33,
Outer Harbor, Port Dock & Grange #007DC3. The timetable's route_color differs for two (Belair 509E2F, Seaford & Flinders
FE5000), as V/Line's GTFS colour differed from its map: the map wins. D4a-direction, hub Adelaide Railway Station (Lee
did not answer; the V/Line and NSW rule, assumed and told to him): leaving the City the line colour filled, white ring
and label; toward it a white disc, the ring and label in the line colour; the label outlined in the fill. Direction from
the timetable trip's direction_id, 0 toward the City and 1 away: MEASURED on all 1,636 rail trips of version 1718 (0
ends nearer Adelaide Railway Station on 818 of 818, 1 farther on 818 of 818). Unknown: the leaving look.

THE ARROW: the feed's own bearing (GPS), Fleet's rule (while moving; held at rest).

LATE (Adelaide Metro's own rule, "On-time running": on time when no more than 4 minutes 59 seconds after the timetable,
every mode): late from 5, very late from 10 (2T, as VR, Norway and Irish Rail here). The trip updates carry
arrival.time only, so the delay is predicted minus scheduled (stop_delays, as for every feed here).

OFF RAIL: more than 1 km from every Adelaide rail shape (no NARN outside the US). A fix older than 5 minutes is refused.
"""

from __future__ import annotations

import csv
import io
import zipfile
from typing import Any

from saw_livetrack.adelaide_metro import ATTRIBUTION, COMMUTER, POSITIONS_URL, STATIC_URL, TERMS_URL

from .base import SOURCE_ADELAIDE_METRO, Obs, Operator, position_of, vehicle_time

OP_ID = "adelaide_metro"
WHITE = "#FFFFFF"
GREY = "#58595B"          # the map's common trunk; a route no line claims
RING_WIDTH = 3
LATE_MIN = 5
VERY_LATE_MIN = 10
MAX_FIX_AGE_S = 300
OFF_RAIL_M = 1000.0
LABEL_LEN = 3             # Lee 2026-11-13 19:33: the label is the route code's first three letters

# The map's four lines (legend wording) and their colours; each route code to its line.
LINES: dict[str, tuple[str, str]] = {
    "belair": ("Belair line", "#6ABF4B"),
    "seaford": ("Seaford & Flinders line", "#FF7F30"),
    "gawler": ("Gawler line", "#C23B33"),
    "outer_harbor": ("Outer Harbor, Port Dock & Grange line", "#007DC3"),
}
ROUTE_LINE: dict[str, str] = {
    "BEL": "belair",
    "FLNDRS": "seaford", "NOAR": "seaford", "SEAFRD": "seaford",
    "GAW": "gawler", "GAWC": "gawler", "SALIS": "gawler",
    "GRNG": "outer_harbor", "OSBORN": "outer_harbor", "OUTHA": "outer_harbor", "PTDOCK": "outer_harbor",
}


# --- the feed ----------------------------------------------------------------

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
        course = float(v.position.bearing) % 360.0 if v.position.HasField("bearing") else None
        out.append(Obs(
            vehicle_id=vid,
            lat=pos[0],
            lon=pos[1],
            observed_at=vehicle_time(v),
            in_service=bool(trip),
            train=None,
            line=route or None,
            reported_course=course,
            trip_id=trip or None,
        ))
    return out


# --- the timetable's extras (statics.py stores them; decorate reads them) -------

def _rows(z: zipfile.ZipFile, name: str):
    if name not in z.namelist():
        return
    with z.open(name) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")):
            yield {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}


def extras(z: zipfile.ZipFile, distilled: dict[str, Any], shape_index: dict[str, list[int]]) -> dict[str, Any]:
    """From the rail-only zip: each route's code and colour; the route, direction and headsign of each trip the distilled
    timetable keeps (yesterday, today, tomorrow)."""
    route = {r["route_id"]: [r.get("route_short_name") or r["route_id"], r.get("route_color", "").upper()]
             for r in _rows(z, "routes.txt") if r.get("route_id")}
    window = distilled.get("sched") or {}
    trip: dict[str, list[str]] = {}
    for r in _rows(z, "trips.txt"):
        tid = r.get("trip_id")
        if tid and tid in window:
            trip[tid] = [r.get("route_id", ""), r.get("direction_id", ""), r.get("trip_headsign", "")]
    return {"route": route, "trip": trip}


# --- one published record ----------------------------------------------------

def line_colour(code: str | None, gtfs_colour: str | None = None) -> str:
    """The map's colour for a route code; a route no line claims takes the timetable's colour, else the trunk's grey."""
    line = ROUTE_LINE.get((code or "").upper())
    if line is not None:
        return LINES[line][1]
    c = (gtfs_colour or "").strip().lstrip("#").upper()
    return "#" + c if len(c) == 6 else GREY


def toward_city(info: list | None) -> bool | None:
    """True going to Adelaide Railway Station, False leaving, None unknown: the timetable trip's direction_id (0 toward,
    1 away)."""
    if not info or len(info) < 2:
        return None
    return {"0": True, "1": False}.get(info[1])


def look(colour: str, toward: bool | None) -> dict[str, Any]:
    """D4a-direction: the line colour filled, white ring and label, leaving the City; swapped going to it; the label
    outlined in the fill."""
    fill, other = (WHITE, colour) if toward is True else (colour, WHITE)
    return {"marker_color": fill, "marker_ring_color": other, "marker_ring_width": RING_WIDTH,
            "marker_label_color": other, "marker_label_outline_color": fill,
            "marker_arrow_color": fill, "marker_arrow_outline_color": other}


def decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
    """Label, hover line, lateness and look, in place (poll.decorate_all)."""
    ex = (static or {}).get("extras") or {}
    info = (ex.get("trip") or {}).get(obs.trip_id or "")
    rid = obs.line or (info[0] if info else "")
    route = (ex.get("route") or {}).get(rid)
    code = (route[0] if route else rid) or None
    if not obs.in_service:
        return
    if code:
        rec["marker_label"] = code[:LABEL_LEN]
    head = info[2] if info and len(info) > 2 and info[2] else None
    parts = [code + (" to " + head if head else "")] if code else []
    parts.append("railcar " + obs.vehicle_id)
    rec["line_name"] = " · ".join(parts)
    rec["late_threshold_min"] = LATE_MIN
    rec["very_late_threshold_min"] = VERY_LATE_MIN
    rec.update(look(line_colour(code, route[1] if route else None), toward_city(info)))


ADELAIDE_METRO = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-13: "adelaide_metro".
    id=OP_ID,
    name="Adelaide Metro",
    short="Adelaide",
    regions=("AU-SA",),
    positions_url=POSITIONS_URL,
    source=SOURCE_ADELAIDE_METRO,
    adelaide_metro_consumer=COMMUTER,
    parse=parse,
    # The timetable from the shared client's own copy (raw_source); this URL names the dataset. Every mode in one zip
    # (15.4 MB, version 1718); trains are route_type 2.
    static_url=STATIC_URL,
    static_route_types=("2",),
    static_max_bytes=64 * 1024 * 1024,
    static_timeout_s=180,
    static_extras=extras,
    decorate=decorate,
    max_fix_age_s=MAX_FIX_AGE_S,
    off_rail_m=OFF_RAIL_M,
    narn=False,
    attribution=ATTRIBUTION + ". This integration is not sponsored by, affiliated with, or operated by Adelaide Metro or "
                              "the Government of South Australia.",
    terms_url=TERMS_URL,
)
