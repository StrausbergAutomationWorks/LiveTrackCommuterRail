"""Renfe Cercanias and Rodalies (Spain), one operator per network, on the shared Renfe
client (saw_livetrack.renfe, saw-livetrack 0.2.9). No Home Assistant imports.

SSOT section 10. Measured on capture round 1 (Fri 2026-10-16 23:50 to Mon 10-19 08:43
Spain time, 7,710 trips): 20_Research/ES_RENFE_CERCANIAS_FEED_20261016.md.

ONE FEED, EVERY NETWORK. Renfe publishes one GTFS-Realtime feed for all its commuter
networks (up to 495 trains at once, Monday 08:18). Each network is its own operator here
(region first, then the network: Lee's setup rule, SSOT 0), and every entry draws from
the ONE client per Home Assistant, registered as "commuter". The client has already:
routed the buses (route_type 3) and Catalonia's regional lines elsewhere; dropped 0,0;
kept one row per trip; held a position returning to where it was two fixes back.

THE TRIP ID IS THE IDENTITY (entity.id is not: it repeats across networks). It names
the network (its first two digits; 7,707 of 7,710 trips, the rest SPECIAL_... ones with
no network, drawn by nobody), the train number and the line: 3087V23743C5 is Seville's
train 23743 on C5. vehicle_id = trip_id, so an entity lasts one run.

THE LOOK (Lee 2026-10-16): the route's own colour from Renfe's timetable, per ROUTE, not
per line: Murcia C2 is green or pink by route, Barcelona R1 light or dark blue
(research section 2). The trip's route is looked up in the timetable; a trip the
timetable does not know takes its network and line's most common colour. The label is
the line (C5, R2N), white with the card's dark outline, as Renfe draws it. A WHITE disc
(white route colour; Valencia's ER24) gets a thin black ring and black-outlined label
(Lee 2026-10-16: "use a thin black outline of the circle and the letter or number").
The train number and the line's name go in the hover box.

POSITIONS are modelled onto the trip's shape, not GPS: they stand (p50 79 s) and jump
(p50 785 m). So:
* no speed is derived and no move is a jump (position_jump dropped), as SE Queensland;
* the arrow is the trip's own shape's bearing where the train is (research section 6:
  p99 0 m from the shape), held at rest (D3c-iii); the feed has no bearing;
* STALLED: one wait, 366 s anywhere (Fleet's 90 s rule away from a stop would fire on
  every train standing 90-240 s between two jumps; p90 of a stand is 240 s).
* OFF RAIL: more than 1 km from every shape of the network (no NARN in Spain).
LATE: Renfe publishes no on-time rule of its own that was found (press reports of a 3
and a 5 minute figure, no Renfe source; research section 9), so Metra's applies (SSOT 0):
nothing is sent, and the card's defaults are Metra's.
"""

from __future__ import annotations

import csv
import io
import math
import zipfile
from collections import Counter
from typing import Any

from saw_livetrack.renfe import ATTRIBUTION, COMMUTER, TERMS_URL, parse_trip_id

from .base import SOURCE_RENFE, Obs, Operator, position_of, vehicle_time
from .qr_citytrain import shape_course

WHITE = "#FFFFFF"
BLACK = "#000000"
RING_WIDTH = 1
OFF_RAIL_M = 1000.0
STALL_M = math.inf


def make_parse(networks: frozenset[str]):
    """parse(feed) for one operator: the vehicles of its networks only."""

    def parse(feed) -> list[Obs]:
        out: list[Obs] = []
        for ent in feed.entity:
            if not ent.HasField("vehicle"):
                continue
            v = ent.vehicle
            trip = (v.trip.trip_id or "").strip() if v.HasField("trip") else ""
            network, number, _ = parse_trip_id(trip)
            if network not in networks:
                continue
            pos = position_of(v)
            if pos is None:
                continue
            out.append(Obs(
                vehicle_id=trip,
                lat=pos[0],
                lon=pos[1],
                observed_at=vehicle_time(v),
                in_service=True,
                train=number,
                line=None,
                reported_course=None,
                trip_id=trip,
            ))
        return out

    return parse


def _colour(value: str | None) -> str | None:
    """'fecb00' -> '#FECB00'; None for anything that is not six hex digits."""
    v = (value or "").strip().lstrip("#").upper()
    if len(v) == 6 and all(c in "0123456789ABCDEF" for c in v):
        return "#" + v
    return None


def extras(z: zipfile.ZipFile, distilled: dict[str, Any],
           shape_index: dict[str, list[int]]) -> dict[str, Any]:
    """From the cut zip: each route's colours and name; the route and shape of each trip
    the distilled timetable keeps; each network and line's most common colours."""
    def rows(name: str):
        if name not in z.namelist():
            return
        with z.open(name) as fh:
            for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")):
                yield {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}

    routes: dict[str, list] = {}
    by_route: dict[str, Counter] = {}
    for r in rows("routes.txt"):
        rid = r.get("route_id")
        if rid:
            routes[rid] = [_colour(r.get("route_color")), _colour(r.get("route_text_color")),
                           r.get("route_short_name", "")]
            if routes[rid][0] is not None and routes[rid][2]:
                by_route.setdefault("%s %s" % (rid[:2], routes[rid][2]), Counter())[
                    (routes[rid][0], routes[rid][1])] += 1
    window = distilled.get("sched") or {}
    trip: dict[str, list] = {}
    votes: dict[str, Counter] = {}
    for r in rows("trips.txt"):
        tid, rid = r.get("trip_id"), r.get("route_id")
        if not tid or not rid or rid not in routes:
            continue
        bg, fg, short = routes[rid]
        if bg is not None and short:
            votes.setdefault("%s %s" % (rid[:2], short), Counter())[(bg, fg)] += 1
        if tid in window:
            ix = shape_index.get(r.get("shape_id", ""))
            trip[tid] = [rid, ix[0], ix[1]] if ix is not None else [rid, -1, 0]
    # A line with routes but no trip in the window (a line running as buses that day,
    # Valencia's ER24) takes its routes' most common colours.
    for k, c in by_route.items():
        votes.setdefault(k, c)
    return {
        "route": {rid: v[:2] for rid, v in routes.items()},
        "trip": trip,
        "line_colour": {k: list(c.most_common(1)[0][0]) for k, c in votes.items()},
    }


def marker_keys(bg: str, fg: str | None) -> dict[str, Any]:
    """The disc in the route's colours; a white one ringed and outlined black."""
    keys: dict[str, Any] = {"marker_color": bg, "marker_arrow_color": bg}
    if fg is not None:
        keys["marker_label_color"] = fg
    if bg == WHITE:
        keys["marker_ring_color"] = BLACK
        keys["marker_ring_width"] = RING_WIDTH
        keys["marker_label_outline_color"] = BLACK
    return keys


def decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
    """Label, look, line name and arrow for one record Fleet published, in place."""
    rec.pop("position_jump", None)
    network, _, line = parse_trip_id(obs.trip_id)
    if line:
        rec["marker_label"] = line
    ex = (static or {}).get("extras") or {}
    info = (ex.get("trip") or {}).get(obs.trip_id or "")
    look = None
    if info is not None:
        look = (ex.get("route") or {}).get(info[0])
        name = ((static or {}).get("routes") or {}).get(info[0])
        if name:
            rec["line_name"] = name
    if (look is None or look[0] is None) and line:
        look = (ex.get("line_colour") or {}).get("%s %s" % (network, line))
    if look is not None and look[0] is not None:
        rec.update(marker_keys(look[0], look[1]))
    if info is None:
        return
    crs = shape_course(static, [info[1:3]], rec["latitude"], rec["longitude"])
    if crs is None:
        return
    if "course_deg" in rec:
        rec["course_deg"] = crs
        rec["icon_rotation_basis"] = "course"
    else:
        rec["icon_rotation_basis"] = "held"
    rec["icon_rotation_deg"] = crs


# (operator id, setup name, entity short name, regions, network codes). ! The ids are
# permanent once installed (operators/__init__.py). Regions: ISO 3166-2 autonomous
# communities. Network 90 (Cercedilla - Cotos) is Madrid's: its C9 runs as Madrid's (10).
NETWORKS: tuple[tuple[str, str, str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("renfe_madrid", "Renfe Cercanías Madrid", "Renfe Madrid", ("ES-MD",), ("10", "90")),
    ("renfe_asturias", "Renfe Cercanías Asturias", "Renfe Asturias", ("ES-AS",), ("20",)),
    ("renfe_sevilla", "Renfe Cercanías Sevilla", "Renfe Sevilla", ("ES-AN",), ("30",)),
    ("renfe_cadiz", "Renfe Cercanías Cádiz", "Renfe Cadiz", ("ES-AN",), ("31",)),
    ("renfe_malaga", "Renfe Cercanías Málaga", "Renfe Malaga", ("ES-AN",), ("32",)),
    ("renfe_valencia", "Renfe Cercanías Valencia", "Renfe Valencia", ("ES-VC",), ("40",)),
    ("renfe_murcia_alicante", "Renfe Cercanías Murcia/Alicante", "Renfe Murcia Alicante",
     ("ES-MC", "ES-VC"), ("41",)),
    ("renfe_cartagena", "Renfe Cercanías Cartagena", "Renfe Cartagena", ("ES-MC",), ("45",)),
    ("renfe_ferrol", "Renfe Cercanías Ferrol", "Renfe Ferrol", ("ES-GA",), ("46",)),
    ("renfe_leon", "Renfe Cercanías León", "Renfe Leon", ("ES-CL",), ("47",)),
    ("renfe_barcelona", "Renfe Rodalies Barcelona", "Renfe Barcelona", ("ES-CT",), ("51",)),
    ("renfe_bilbao", "Renfe Cercanías Bilbao", "Renfe Bilbao", ("ES-PV",), ("60",)),
    ("renfe_san_sebastian", "Renfe Cercanías San Sebastián", "Renfe San Sebastian",
     ("ES-PV",), ("61",)),
    ("renfe_cantabria", "Renfe Cercanías Cantabria", "Renfe Cantabria", ("ES-CB",), ("62",)),
    ("renfe_zaragoza", "Renfe Cercanías Zaragoza", "Renfe Zaragoza", ("ES-AR",), ("70",)),
)


def _operator(op_id: str, name: str, short: str, regions: tuple[str, ...],
              networks: tuple[str, ...]) -> Operator:
    return Operator(
        id=op_id,
        name=name,
        short=short,
        regions=regions,
        # The config flow's check: one GET of the feed the shared client reads.
        positions_url="https://gtfsrt.renfe.com/vehicle_positions.pb",
        source=SOURCE_RENFE,
        renfe_consumer=COMMUTER,
        parse=make_parse(frozenset(networks)),
        # The timetable from the client's own download (statics, raw_source); this URL
        # is what a refresh without the client would fetch.
        static_url="https://ssl.renfe.com/ftransit/Fichero_CER_FOMENTO/fomento_transit.zip",
        static_route_types=("2",),
        static_window=True,
        static_route_prefixes=networks,
        static_max_bytes=64 * 1024 * 1024,
        static_timeout_s=180,
        static_extras=extras,
        decorate=decorate,
        off_rail_m=OFF_RAIL_M,
        narn=False,
        stall_m=STALL_M,
        attribution=(
            ATTRIBUTION + ", modified. This integration is not sponsored by, affiliated "
            "with, or operated by Renfe."
        ),
        terms_url=TERMS_URL,
    )


RENFE_OPERATORS: tuple[Operator, ...] = tuple(_operator(*n) for n in NETWORKS)
