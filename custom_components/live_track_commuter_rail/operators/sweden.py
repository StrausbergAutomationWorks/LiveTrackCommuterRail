"""Sweden's commuter trains on Trafikverket through the shared client: SL Pendeltåg (Stockholm), Västtågen's pendeltåg
(Göteborg) and Arlanda Express. No Home Assistant imports.

SSOT 14. Lee 2026-11-08 (Intercity Rail chat, backlog 327): Trafikverket's TypeOfTraffic splits Sweden as Norway's line
letter did: every `Tåg` to Live Track Intercity Rail, `Pendeltåg` and Arlanda Express (operator ATRAIN, as Flytoget)
here, `Buss` to Live Track Transit; one config entry per BRAND. Lee 2026-11-10 00:33 CST, the go: operator ids
`sl_pendeltag` and `arlanda_express` (new, permanent) and `vasttagen` (Intercity Rail's id for the same brand, in this
integration's namespace). Which run is whose: saw_livetrack.trafikverket (route_of, BRANDS). The runs, the lines and
the skip rules: sweden_lines.py.

LABEL the advertised train number (Fleet's label; backlog 327, Sweden's rule): the number on the departure boards.
HOVER: "<brand> <number> · <first>–<last>", the trip's first and last stations, e.g. "SL Pendeltåg 2241 · Märsta–
Södertälje Centrum".

THE LOOK: each brand's fill, ring and label, leaving the hub. Going TO it, 06_MAP_CONTRACT.md D4a-direction as
Norway's and Intercity Rail's Sweden: the fill takes the label's colour and the ring and label take the fill's.
* SL Pendeltåg: #F166A7 and white (Lee 2026-11-10 00:33 CST): pink fill, white ring and number; toward the hub a white
  disc, pink ring and number.
* Västtågen: #00ACEA, ring and number #00394D (Lee 2026-11-08 17:41 CST, Intercity Rail's Västtågen).
* Arlanda Express: #FEF380 with black (Lee's table, 2026-11-08: "white fails, black reads"); the ring black, as
  Intercity Rail's Värmlandstrafik, the other yellow brand.

THE HUB (Sweden's rule, Intercity SSOT 8.9 decision 6: Stockholm C, else the trip's larger end city): Stockholm C,
or Stockholm City for SL Pendeltåg, which has called at City, not C, since Citybanan opened in 2017 (no pendeltåg
trip calls at Cst in 19 days of announcements, 2026-11-05..23; 16,150 calls at Sci, bin\\se_ltcr_measure.txt). A trip
calling at neither takes the larger of its two end cities by population (rail/sweden_ends.json, Statistics Sweden's
2023 tätorter, cut from Intercity Rail's table); both in one tätort: the leaving look.

LATE (this integration's rule, SSOT 0: a railroad's own published rule, else Metra's):
* SL Pendeltåg: Region Stockholm's traffic administration counts a pendeltåg punctual when it arrives and departs
  within 3 minutes of its time; the operator's reports state it as departing less than 3 minutes late (links in SSOT
  14). So late from 3 whole minutes; very late at double, 6 (2T, as VR lähijunat and Norway here).
* Västtågen and Arlanda Express: Trafikverket's RT+5, on time to 5:59 at the final station, so late from 6; very late
  12 (Lee's go: "else 6/12"; Intercity Rail's Sweden).

NEXT STOP: the first ARRIVAL at a station the train stops at (sweden_lines.is_stop) after its last call with an actual
time, uncancelled, not the origin, whose time (estimated, else advertised plus the delay last known) is no more than
NEXT_GRACE_S past. The delay is that stop's estimate against its advertised time, else the last actual's.

KEYED: each user brings Trafikverket's free key (KEY_URL). CREDIT: CC0 asks none; the wording is Lee's
(saw_livetrack.trafikverket.ATTRIBUTION). The lines are OpenStreetMap's (ODbL), credited by the map.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Callable, Mapping, Sequence

from saw_livetrack.trafikverket import ATTRIBUTION, COMMUTER, KEY_URL, TERMS_URL, URL

from .. import sweden_lines
from .base import SOURCE_TRAFIKVERKET, Obs, Operator

WHITE = "#FFFFFF"
BLACK = "#000000"
RING_WIDTH = 3
ARRIVAL = "Ankomst"
# A stop whose time has passed by more than this, with no actual, is taken as passed.
NEXT_GRACE_S = 60.0
# Stockholm C; Stockholm City (SL Pendeltåg's).
HUBS = ("Cst", "Sci")
# On the 1 km scale of SE Queensland and Finland: the lines are OpenStreetMap's track, the fixes GPS, and a pair with
# no shipped line is a straight leg.
OFF_RAIL_M = 1000.0
# Not one Arlanda Express row is advertised; these are its stations (Stockholm C, Arlanda S for terminals 2-4,
# Arlanda N for terminal 5), the signatures in every one of its 3,162 trips of 2026-11-05..23.
ARLANDA_STOPS = ("Cst", "Arns", "Arnn")

# operator id -> (setup name, short, fill, ring, label, late, very late, the operator's own stations)
BRANDS: dict[str, tuple[str, str, str, str, str, int, int, tuple[str, ...]]] = {
    "sl_pendeltag": ("SL Pendeltåg (Stockholm)", "SL Pendeltåg", "#F166A7", WHITE, WHITE, 3, 6, ()),
    "vasttagen": ("Västtågen pendeltåg (Göteborg)", "Västtågen", "#00ACEA", "#00394D", "#00394D", 6, 12, ()),
    "arlanda_express": ("Arlanda Express (Stockholm C–Arlanda)", "Arlanda Express", "#FEF380", BLACK, BLACK, 6, 12,
                        ARLANDA_STOPS),
}


def look(fill: str, ring: str, label: str, toward: bool) -> dict[str, Any]:
    """The marker keys for one brand, leaving the hub or (toward) going to it."""
    if toward:
        fill, ring, label = label, fill, fill
    return {
        "marker_color": fill,
        "marker_ring_color": ring,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": label,
        "marker_label_outline_color": "none",
        "marker_arrow_color": fill,
        "marker_arrow_outline_color": ring,
    }


def hub_index(sigs: Sequence[str], ends: Mapping[str, Mapping[str, Any]]) -> int | None:
    """The index of a trip's hub among its stations: its LAST Stockholm C or City; else its larger end city by
    population; None when neither end is known, or both are as large."""
    if not sigs:
        return None
    hubs = [i for i, s in enumerate(sigs) if s in HUBS]
    if hubs:
        return hubs[-1]

    def pop(s: str) -> Any:
        v = (ends.get(s) or {}).get("population")
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    a, b = pop(sigs[0]), pop(sigs[-1])
    if (a is None and b is None) or a == b:
        return None
    if b is None or (a is not None and a > b):
        return 0
    return len(sigs) - 1


def delay_and_next(calls: Sequence[Mapping[str, Any]], now: float, fallback_stops: Sequence[str] = ()
                   ) -> tuple[int | None, Mapping[str, Any] | None, float | None]:
    """(delay in s or None, the next stop's call or None, its time). Module docstring, NEXT STOP."""
    has_public = any(c.get("public") for c in calls)
    last_actual = -1
    delay = None
    for i, c in enumerate(calls):
        if c.get("actual") is not None and c.get("advertised") is not None:
            last_actual = i
            delay = int(c["actual"] - c["advertised"])
    origin = calls[0].get("sig") if calls else None
    for c in calls[last_actual + 1:]:
        if (c.get("activity") != ARRIVAL or c.get("canceled") or c.get("sig") == origin
                or not sweden_lines.is_stop(c, has_public, fallback_stops)):
            continue
        if c.get("actual") is not None or c.get("advertised") is None:
            continue
        if c.get("estimated") is not None:
            when = c["estimated"]
            delay = int(c["estimated"] - c["advertised"])
        else:
            when = c["advertised"] + (delay or 0)
        if when >= now - NEXT_GRACE_S:
            return delay, c, when
    return delay, None, None


def parse(runs: list[Mapping[str, Any]]) -> list[Obs]:
    """The client's runs (already kept by sweden_lines.RunFilter) -> observations, every one in service."""
    out: list[Obs] = []
    for run in runs or ():
        pos = run.get("position") or {}
        number = str(run.get("number") or "")
        lat, lon, ts = pos.get("lat"), pos.get("lon"), pos.get("ts")
        if not number or not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            continue
        key = sweden_lines.identity(number, run.get("date"))
        out.append(Obs(
            vehicle_id=key, lat=round(float(lat), 6), lon=round(float(lon), 6),
            observed_at=(dt.datetime.fromtimestamp(int(ts), dt.timezone.utc)
                         if isinstance(ts, (int, float)) else None),
            in_service=True, train=number, line=None, reported_course=pos.get("bearing"), trip_id=key))
    return out


def stops_for(op_id: str) -> Callable[[Any, dict[str, Any] | None, float], tuple[dict, dict, dict]]:
    _, short, fill, ring, label, _, _, fallback = BRANDS[op_id]

    def sweden_stops(runs: list[Mapping[str, Any]], static: dict[str, Any] | None, now: float
                     ) -> tuple[dict[str, tuple[str, float | None]], dict[str, int], dict[str, dict[str, Any]]]:
        """(next_stops {trip: (name, eta)}, trip_delays {trip: seconds}, extras {vehicle: keys}). A station is named
        from Trafikverket's station list, never shown as a code (D4b)."""
        names = (static or {}).get("stops") or {}
        ends = ((static or {}).get("extras") or {}).get("ends") or {}
        nxt_out: dict[str, tuple[str, float | None]] = {}
        delays: dict[str, int] = {}
        extras: dict[str, dict[str, Any]] = {}
        for run in runs or ():
            number = str(run.get("number") or "")
            if not number:
                continue
            key = sweden_lines.identity(number, run.get("date"))
            calls = list(run.get("calls") or ())
            delay, nxt, eta = delay_and_next(calls, now, fallback)
            order = sweden_lines.stop_signatures(calls, fallback)
            keys: dict[str, Any] = {}
            if order and names.get(order[0]) and names.get(order[-1]):
                keys["line_name"] = f"{short} {number} · {names[order[0]]}–{names[order[-1]]}"
            hub = hub_index(order, ends)
            toward = False
            if hub is not None:
                if nxt is None:
                    toward = hub == len(order) - 1
                else:
                    index = order.index(nxt["sig"]) if nxt["sig"] in order else len(order) - 1
                    toward = hub >= index
            keys.update(look(fill, ring, label, toward))
            extras[key] = keys
            if nxt is not None and names.get(nxt["sig"]):
                nxt_out[key] = (names[nxt["sig"]], eta)
            if delay is not None:
                delays[key] = delay
        return nxt_out, delays, extras

    return sweden_stops


def styling_for(op_id: str) -> Callable[[Obs], dict[str, Any]]:
    _, _, fill, ring, label, _, _, _ = BRANDS[op_id]

    def sweden_styling(obs: Obs) -> dict[str, Any]:
        """The leaving look until the stops say which way the train runs (poll.apply_extras)."""
        return look(fill, ring, label, False)

    return sweden_styling


def decorate_for(op_id: str) -> Callable[[dict[str, Any], Obs, dict[str, Any] | None], None]:
    late, very = BRANDS[op_id][5], BRANDS[op_id][6]

    def sweden_decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
        """The lateness rule, in place (the label is Fleet's: the advertised number)."""
        rec["late_threshold_min"] = late
        rec["very_late_threshold_min"] = very

    return sweden_decorate


def _operator(op_id: str) -> Operator:
    name, short = BRANDS[op_id][0], BRANDS[op_id][1]
    return Operator(
        # ! Permanent (operators/__init__.py). Lee 2026-11-10 00:33 CST (SSOT 14).
        id=op_id,
        name=name,
        short=short,
        regions=("SE",),
        positions_url=URL,
        parse=parse,
        source=SOURCE_TRAFIKVERKET,
        trafikverket_consumer=COMMUTER,
        trafikverket_brand=op_id,
        parse_stops=stops_for(op_id),
        styling=styling_for(op_id),
        decorate=decorate_for(op_id),
        off_rail_m=OFF_RAIL_M,
        narn=False,
        # ! A marker only: the shared client sends the key in the request BODY, never as a query parameter.
        key_param="authenticationkey",
        key_url=KEY_URL,
        attribution=ATTRIBUTION + ". Lines: (c) OpenStreetMap contributors, ODbL 1.0. This integration is not "
                                  "sponsored by, affiliated with, or operated by Trafikverket or " + short + ".",
        terms_url=TERMS_URL,
        extra={"fallback_stops": BRANDS[op_id][7]},
    )


SWEDEN: tuple[Operator, ...] = tuple(_operator(op_id) for op_id in BRANDS)
