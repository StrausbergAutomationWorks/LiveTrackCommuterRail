"""Transperth's trains (Perth, Western Australia): ONE config entry. No Home Assistant imports. SSOT 20.

Lee 2026-11-13 20:40 CST: "Perth doesn't release real time info, so if we build anything it has to be simulated from the
timetable like Cork. Read upload for colors."; 20:50: "Record it then let's build it." The eight lines and the Stadium
Special (agency WES-RAI, route_type 2) reach this integration through the shared client's `commuter` consumer
(saw_livetrack.transperth: Transwa's trains to Live Track Intercity Rail, the buses and ferry to Live Track Transit).
Keyless. Every train from its timetable, an estimate along its trip's shape (perth_runs.py, irish_runs.py's machinery).
The timetable is the PTA's zip the shared client keeps, cut to this consumer before it is distilled (transperth.cut,
which also strips stops.txt's spaced header), with the runs' table read from the same bytes (transperth.read_timetable).
Measured: 20_Research/AU_PERTH_TRANSPERTH_20261113.md.

THE LOOK: the line's colour from Lee's map ("Byford Rail Extension System Map", October 2025, 10_Reference), MEASURED
from its vector paths and matched to its legend: Airport #46C3B2, Armadale #F6A800, Ellenbrook #D8292F, Fremantle
#0056B8, Mandurah #D25F15, Midland #960048, Thornlie-Cockburn #A97CCA, Yanchep #959300. The Stadium Special is not on
the map: the timetable's #009645. A line the map does not know: the timetable's colour, else grey. The timetable's
colours differ on every line (Fremantle most, 002F6C): the map wins (V/Line's and Adelaide's precedent).
D4a-direction as Adelaide's (ASSUMED, told to Lee): leaving Perth the line colour filled, white ring and label; toward
it a white disc, the ring and label in the line colour; the label outlined in the fill. Armadale's label is BLACK in
both looks: the timetable gives it route_text_color 000000, the only line with dark text (white on #F6A800 does not
read).

TOWARD PERTH (D4a-direction): direction_id is NOT consistent toward Perth (Armadale 0 = toward, Mandurah 1 = away;
MEASURED), so the stations decide, as Irish Rail's rule: the hub is Perth Stn, Perth Underground Stn and Elizabeth Quay
Stn. A trip ending at the hub runs toward it all the way; one starting there leaves it all the way; one calling at the
hub on the way (the Airport Line, High Wycombe-Claremont through Perth Stn) runs toward it until it LEAVES that
station, then leaves; the rest leave.

LABEL (ASSUMED, told to Lee): the line's first three letters, today's Adelaide rule (Lee 2026-11-13 19:33): AIR, ARM,
ELL, FRE, MAN, MID, THO, YAN, STA. Perth publishes no train number and no line code.
HOVER "Mandurah Line · Perth Underground–Mandurah": the line, then the trip's first and last stations as the timetable
names them without " Stn" (ASSUMED). The next stop is named the same way.

NO LATENESS: no delay exists, so no thresholds are set. CREDIT: the PTA licence's statement
(saw_livetrack.transperth.ATTRIBUTION); no PTA trademark is used with the data, so the entry is not titled after one
(open, Lee's: the operator id and the title).
"""

from __future__ import annotations

import datetime as dt
import re
from typing import Any, Mapping, Sequence

from saw_livetrack.transperth import (ATTRIBUTION, COMMUTER, STATIC_URL, TERMS_URL, cut as tp_cut, local_day,
                                      read_timetable)

from .base import SOURCE_TRANSPERTH, Obs, Operator

WHITE = "#FFFFFF"
BLACK = "#000000"
GREY = "#808080"
RING_WIDTH = 3
# The map's colours by the timetable's route_long_name (THE LOOK).
COLOURS: dict[str, str] = {
    "Airport Line": "#46C3B2",
    "Armadale Line": "#F6A800",
    "Ellenbrook Line": "#D8292F",
    "Fremantle Line": "#0056B8",
    "Mandurah Line": "#D25F15",
    "Midland Line": "#960048",
    "Thornlie-Cockburn Line": "#A97CCA",
    "Yanchep Line": "#959300",
}
# Lines whose label is black (the timetable's route_text_color 000000).
DARK_TEXT = ("Armadale Line",)
HUB = ("Perth Stn", "Perth Underground Stn", "Elizabeth Quay Stn")
LABEL_LEN = 3
_PLATFORM = re.compile(r"\s+Platform\s+\S+$")
# On the 1 km scale of Cork's and Adelaide's: a train is drawn on its own trip's shape, or at a call where a stretch
# cannot be placed on it.
OFF_RAIL_M = 1000.0


def show(name: str) -> str:
    """A station as the hover and the next stop show it: without the timetable's " Stn", and without " Platform <n>"
    where a platform has no parent station to be named by (none measured; read_timetable names a platform by its
    parent)."""
    n = _PLATFORM.sub("", (name or "").strip())
    return n[:-4] if n.endswith(" Stn") else n


def label(line: str) -> str:
    """The line's first three letters, upper case (LABEL)."""
    return "".join(ch for ch in (line or "") if ch.isalpha())[:LABEL_LEN].upper()


def colour(line: str, gtfs: str | None) -> str:
    """The map's colour, else the timetable's, else grey (THE LOOK)."""
    return COLOURS.get(line) or (gtfs if gtfs and len(gtfs) == 7 and gtfs.startswith("#") else None) or GREY


def toward_hub(names: Sequence[str], index: int, state: str) -> bool:
    """Whether a train at call `index` ("standing" there or "running" from it) of a trip calling at `names` runs
    toward Perth (TOWARD PERTH)."""
    if not names:
        return False
    if names[-1] in HUB:
        return True
    if names[0] in HUB:
        return False
    hubs = [k for k, n in enumerate(names) if n in HUB]      # neither end is the hub here (returned above)
    if not hubs:
        return False
    h = hubs[-1]
    return index < h or (index == h and state == "standing")


def look(fill_colour: str, toward: bool, dark_text: bool = False) -> dict[str, Any]:
    """The marker keys for one line, leaving Perth or (toward) going to it (THE LOOK)."""
    fill, edge = (WHITE, fill_colour) if toward else (fill_colour, WHITE)
    text = BLACK if dark_text else edge
    return {"marker_color": fill, "marker_ring_color": edge, "marker_ring_width": RING_WIDTH,
            "marker_label_color": text, "marker_label_outline_color": fill, "marker_arrow_color": fill,
            "marker_arrow_outline_color": edge}


def hover(line: str, names: Sequence[str]) -> str:
    """"Mandurah Line · Perth Underground–Mandurah" (HOVER)."""
    ends = "–".join(show(n) for n in (names[0], names[-1]) if n) if names else ""
    return f"{line} · {ends}" if line and ends else (line or ends)


def parse(rows: list[Mapping[str, Any]]) -> list[Obs]:
    """perth_runs' rows -> observations, every one in service, at the position it is drawn. No train number."""
    out: list[Obs] = []
    for r in rows or ():
        out.append(Obs(
            vehicle_id=r["key"], lat=r["lat"], lon=r["lon"],
            observed_at=dt.datetime.fromtimestamp(r["at"], dt.timezone.utc), in_service=True,
            train=None, line=None, reported_course=None, trip_id=r["key"]))
    return out


def perth_stops(rows: list[Mapping[str, Any]], static: dict[str, Any] | None, now: float
                ) -> tuple[dict[str, tuple[str, float | None]], dict[str, int], dict[str, dict[str, Any]]]:
    """(next_stops {trip: (name, eta)}, trip_delays {} (none exists), extras {vehicle: keys}): the next stop from each
    run's times, the label, the hover and the look."""
    routes = (((static or {}).get("table") or {}).get("routes")) or {}
    nxt: dict[str, tuple[str, float | None]] = {}
    extras: dict[str, dict[str, Any]] = {}
    for r in rows or ():
        key, names = r["key"], r["names"]
        if r["next"] is not None:
            nxt[key] = (show(r["next"][0]), r["next"][1])
        line, gtfs = (routes.get(r["code"]) or [r["code"], ""])[:2]
        keys: dict[str, Any] = {"line_name": hover(line, names),
                                **look(colour(line, gtfs), toward_hub(names, r["index"], r["state"]),
                                       line in DARK_TEXT)}
        code = label(line)
        if code:
            keys["marker_label"] = code
        extras[key] = keys
    return nxt, {}, extras


def cut(raw: bytes) -> bytes:
    """The PTA's zip cut to Transperth's trains before it is distilled (it holds every mode and Transwa)."""
    return tp_cut(raw, COMMUTER)


def table(raw: bytes) -> dict[str, Any]:
    """The runs' table (transperth.read_timetable) for today in Perth, from the same bytes as the shapes."""
    import time
    return read_timetable(raw, COMMUTER, local_day(time.time()))


PERTH = Operator(
    # ! Permanent once released (operators/__init__.py). PROPOSED, Lee's to confirm before the first deploy: the city,
    # not the brand (the PTA licence bars its trademarks with the data).
    id="perth",
    name="Perth trains",
    short="Perth",
    regions=("AU-WA",),
    positions_url=STATIC_URL,
    parse=parse,
    source=SOURCE_TRANSPERTH,
    transperth_consumer=COMMUTER,
    parse_stops=perth_stops,
    # The shared client's copy of the PTA's zip (coordinator: raw_source); the URL only marks that there is one.
    static_url=STATIC_URL,
    static_rewrite=cut,
    static_table=table,
    off_rail_m=OFF_RAIL_M,
    narn=False,
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
)
