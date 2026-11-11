"""Irish Rail's Commuter trains, Dublin's and Cork's (P and D codes): ONE config entry, operator id `irish_rail`. No
Home Assistant imports. SSOT 13.

Lee 2026-11-09 ~17:5x CST (SSOT 13): "Commuter trains go to Commuter Rail. Cork divides in the same way." The P/D codes
reach this integration through the shared client's `commuter` claim (saw_livetrack.irish_rail.consumer_of: A and B to
Live Track Intercity Rail, E (DART) and BUS to Live Track Transit). Keyless. Every train from its timetable, an
estimate along its trip's shape (irish_runs.py). The timetable is the NTA's zip the shared client keeps, cut to the P/D
trips before it is distilled (statics.py, gtfs_filter.keep_trips), with the runs' table read from the same bytes
(saw_livetrack.irish_rail.read_timetable).

LABEL the number without its letter, P508 -> 508 (Lee 2026-11-11 ~01:1x CST: Intercity's Irish rule). MEASURED on the
NTA zip of 2026-11-08 (bin\\ie_ltcr_label_measure.txt): on Tuesday 2026-11-10, 121 numbers are both a P and a D train,
71 of those pairs within 10 minutes of each other (P504 and D504 both leave at 07:00); P runs toward the city and D
away, so the direction look below tells them apart.
HOVER "Irish Rail P508 · Maynooth–Dublin Connolly": the code, then the trip's first and last stations as the timetable
names them, Connolly as "Dublin Connolly" (Lee 2026-11-11 ~01:1x CST, as Intercity's Irish hover). The next stop is
named the same way.

THE LOOK (Lee 2026-11-10 23:47, amended 23:54 and 2026-11-11 00:21 CST; SSOT 13): a disc in the line's colour from
TFI's June 2026 poster.
* Northern `#1E9DD8` and Cork `#7171A3`: white ring and number. Toward the hub swapped: a white disc, the ring and
  number in the line's colour.
* Western `#FDE709` and South Western `#FBB042`: a 3 px band inside a black 2 px outer ring (06_MAP_CONTRACT.md
  D4a-inner-ring), Western's band `#FFFDE7`, South Western's `#F67320`; black number. Toward the hub: a black disc,
  the number and outer ring in the line's colour, the band unchanged.
* The ring is 2 px on all four (Northern's and Cork's width is this chat's choice: the decision names no width for
  them; the same as Western's and South Western's outer ring).
THE LINE by the trip's end stations (research note 20_Research/IE_COMMUTER_20261110.md section 4): Drogheda or Dundalk
Northern; Maynooth, M3 Parkway, Clonsilla, Longford, Mullingar Western; Hazelhatch, Newbridge, Kildare, Portlaoise,
Dublin Heuston South Western; Cork (Kent), Cobh, Midleton, Mallow, Charleville Cork. MEASURED: every P/D end pair falls
in exactly one set except one P trip Bray-Connolly, which Lee ruled Northern; a trip with no end in any set is drawn
Northern by that ruling.
TOWARD THE HUB (D4a-direction): the hub is Dublin (Connolly, Tara Street, Dublin Pearse, Grand Canal Dock, Docklands,
Dublin Heuston) and Cork (Kent). A trip ending at the hub, or at Clonsilla (Lee: "toward Clonsilla counts as toward
Dublin"), runs toward it all the way; one starting at the hub leaves it all the way; any other trip that calls at
Connolly, Dublin Heuston or Cork (Kent) on the way runs toward it until it LEAVES that station, then leaves the hub (Lee:
"a through train flips to leaving after it passes Connolly, Heuston or Cork (Kent)"); the rest leave.

LATE from 5 minutes, very late from 10 (Irish Rail's punctuality rule for DART, Dublin Commuter and Cork Commuter, "on
time or within 5 minutes"; 2T as VR and Norway here; SSOT 13). CREDIT: Live Track Intercity Rail's Irish line (its SSOT
8.10; saw_livetrack.irish_rail.ATTRIBUTION), linked to the NTA's page.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Mapping, Sequence

from saw_livetrack.irish_rail import (ATTRIBUTION, COMMUTER, HACON_URL, NTA_URL, STATIC_URL, consumer_of, local_day,
                                      read_timetable)

from .. import gtfs_filter
from .base import SOURCE_IRISH_RAIL, Obs, Operator

WHITE = "#FFFFFF"
BLACK = "#000000"
NORTHERN = "northern"
WESTERN = "western"
SOUTH_WESTERN = "south_western"
CORK = "cork"
# line -> (colour, the band inside the outer ring or None)
LINES: dict[str, tuple[str, str | None]] = {
    NORTHERN: ("#1E9DD8", None),
    WESTERN: ("#FDE709", "#FFFDE7"),
    SOUTH_WESTERN: ("#FBB042", "#F67320"),
    CORK: ("#7171A3", None),
}
RING_WIDTH = 2
BAND_WIDTH = 3
# The end stations of each line, matched at the start of the timetable's name, lower case (THE LINE).
ENDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (NORTHERN, ("drogheda", "dundalk")),
    (WESTERN, ("maynooth", "m3 parkway", "clonsilla", "longford", "mullingar")),
    (SOUTH_WESTERN, ("hazelhatch", "newbridge", "kildare", "portlaoise", "dublin heuston")),
    (CORK, ("cork", "cobh", "midleton", "mallow", "charleville")),
)
HUB = ("Connolly", "Tara Street", "Dublin Pearse", "Grand Canal Dock", "Docklands", "Dublin Heuston", "Cork (Kent)")
TOWARD_ALSO = ("Clonsilla",)
FLIP = ("Connolly", "Dublin Heuston", "Cork (Kent)")
LATE_MIN = 5
VERY_LATE_MIN = 10
# On the 1 km scale of Sweden and SE Queensland: a train is drawn on its own trip's shape, or at a call where a
# stretch cannot be placed on it, and a station's point can sit off the line.
OFF_RAIL_M = 1000.0


def show(name: str) -> str:
    """A station as the hover and the next stop show it: Connolly as "Dublin Connolly" (Lee 2026-11-11)."""
    return "Dublin Connolly" if name == "Connolly" else name


def line_of(name: str) -> str | None:
    n = (name or "").strip().lower()
    for line, ends in ENDS:
        if any(n.startswith(e) for e in ends):
            return line
    return None


def trip_line(first: str, last: str) -> str:
    """The line by the trip's end stations (THE LINE). Two different lines at the two ends (none measured): the end
    that is not the hub's."""
    a, b = line_of(first), line_of(last)
    if a and b and a != b:
        return b if first in HUB else a
    return a or b or NORTHERN


def toward_hub(names: Sequence[str], index: int, state: str) -> bool:
    """Whether a train at call `index` ("standing" there or "running" from it) of a trip calling at `names` runs
    toward the hub (TOWARD THE HUB)."""
    if not names:
        return False
    first, last = names[0], names[-1]
    if last in HUB or last in TOWARD_ALSO:
        return True
    if first in HUB:
        return False
    flips = [k for k, n in enumerate(names) if n in FLIP and 0 < k < len(names) - 1]
    if not flips:
        return False
    h = flips[-1]
    return index < h or (index == h and state == "standing")


def look(line: str, toward: bool) -> dict[str, Any]:
    """The marker keys for one line, leaving the hub or (toward) going to it (THE LOOK)."""
    colour, band = LINES[line]
    if band is None:
        fill, edge = (WHITE, colour) if toward else (colour, WHITE)
        keys = {}
    else:
        fill, edge = (BLACK, colour) if toward else (colour, BLACK)
        keys = {"marker_inner_ring_color": band, "marker_inner_ring_width": BAND_WIDTH}
    return {"marker_color": fill, "marker_ring_color": edge, "marker_ring_width": RING_WIDTH,
            "marker_label_color": edge, "marker_label_outline_color": "none", "marker_arrow_color": fill,
            "marker_arrow_outline_color": edge, **keys}


def hover(code: str, names: Sequence[str]) -> str:
    """"Irish Rail P508 · Maynooth–Dublin Connolly" (HOVER)."""
    ends = "–".join(show(n) for n in (names[0], names[-1]) if n) if names else ""
    return f"Irish Rail {code} · {ends}" if ends else f"Irish Rail {code}"


def parse(rows: list[Mapping[str, Any]]) -> list[Obs]:
    """irish_runs' rows -> observations, every one in service, at the position it is drawn (irish_runs.py)."""
    out: list[Obs] = []
    for r in rows or ():
        out.append(Obs(
            vehicle_id=r["key"], lat=r["lat"], lon=r["lon"],
            observed_at=dt.datetime.fromtimestamp(r["at"], dt.timezone.utc), in_service=True,
            train=r["number"], line=None, reported_course=None, trip_id=r["key"]))
    return out


def irish_stops(rows: list[Mapping[str, Any]], static: dict[str, Any] | None, now: float
                ) -> tuple[dict[str, tuple[str, float | None]], dict[str, int], dict[str, dict[str, Any]]]:
    """(next_stops {trip: (name, eta)}, trip_delays {trip: seconds}, extras {vehicle: keys}): the next stop and the
    delay from each run's times (irish_runs.py), the hover and the look."""
    nxt: dict[str, tuple[str, float | None]] = {}
    delays: dict[str, int] = {}
    extras: dict[str, dict[str, Any]] = {}
    for r in rows or ():
        key, names = r["key"], r["names"]
        if r["next"] is not None:
            nxt[key] = (show(r["next"][0]), r["next"][1])
        if r["delay_s"] is not None:
            delays[key] = r["delay_s"]
        line = trip_line(names[0], names[-1]) if names else NORTHERN
        extras[key] = {"line_name": hover(r["code"], names),
                       **look(line, toward_hub(names, r["index"], r["state"]))}
    return nxt, delays, extras


def irish_decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
    """The lateness rule, in place (the label is Fleet's: the number without its letter)."""
    rec["late_threshold_min"] = LATE_MIN
    rec["very_late_threshold_min"] = VERY_LATE_MIN


def commuter_trip(row: Mapping[str, str]) -> bool:
    """A trips.txt row of this integration's: a P or D code (saw_livetrack.irish_rail.consumer_of)."""
    return consumer_of((row.get("trip_short_name") or "").strip().upper()) == COMMUTER


def cut(raw: bytes) -> bytes:
    """The NTA's Irish Rail zip cut to the P/D trips before it is distilled (it holds InterCity, Commuter and DART)."""
    return gtfs_filter.keep_trips(raw, commuter_trip)


def table(raw: bytes) -> dict[str, Any]:
    """The runs' table (saw_livetrack.irish_rail.read_timetable) for today in Dublin, from the same bytes as the
    shapes."""
    import time
    return read_timetable(raw, COMMUTER, local_day(time.time()))


IRISH_RAIL = Operator(
    # ! Permanent (operators/__init__.py): the same id as Live Track Intercity Rail's Irish Rail entry, in this
    # integration's namespace (as `vasttagen`, SSOT 14).
    id="irish_rail",
    name="Irish Rail",
    short="Irish Rail",
    regions=("IE",),
    positions_url=HACON_URL,
    parse=parse,
    source=SOURCE_IRISH_RAIL,
    irish_rail_consumer=COMMUTER,
    parse_stops=irish_stops,
    decorate=irish_decorate,
    # The shared client's copy of the NTA's zip (coordinator: raw_source); the URL only marks that there is one.
    static_url=STATIC_URL,
    static_rewrite=cut,
    static_table=table,
    off_rail_m=OFF_RAIL_M,
    narn=False,
    attribution=ATTRIBUTION,
    terms_url=NTA_URL,
)
