"""The Netherlands: NS's Sprinters (feed type SPR, R-net's Alphen-Gouda among them) on NS's vehicle feed through the
shared client saw_livetrack.ns. No Home Assistant imports.

SSOT 15. Lee 2026-11-11 ~03:00 CST ("Build, ship, publish and deploy"): SPR here, IC and the regional trains to Live
Track Intercity Rail; one shared client in saw-livetrack, one poll per install feeding both. The operator id `ns` is
Intercity Rail's id for NS, in this integration's namespace (Sweden's rule for Västtågen). The lines: ns_lines.py.

FIX TIME, option B (Lee 2026-11-11 02:52, "Use B"; 06_MAP_CONTRACT.md, the observed_at rule under D2): the feed has no
fix time; `observed_at` is the poll that first saw the position (the client's, the same for every consumer), the
record carrying `observed_at_source: "first_seen"`. SPEED (`snelheid`, km/h) and HEADING (`richting`) are NS's own:
this is the first railroad here whose feed reports a speed (D2). NO SNAPPING for accuracy; `horizontaleNauwkeurigheid`
is never published (it is not metres of error; NS note 4.5).

LABEL the train number (Fleet's label). HOVER: "Sprinter <number> · <first>–<last>", e.g. "Sprinter 6632 ·
Dordrecht–Arnhem Centraal".

THE LOOK: NS geel #FFC917 with NS blauw #003082 ring, number and arrow outline, as Intercity Rail's `ns`.

LATE (Lee: "Use 3/10"): NS counts a train on time when it arrives less than 3 minutes late (the 2025-2033 concession's
definitions, NS note 4.3) and reports 10 minutes beside it. Late from 3, very late from 10.

NEXT STOP and DELAY: saw_livetrack.ns.next_call (the first call after the origin whose expected arrival, else aimed plus
the delay last known, is at most 60 s past); a delay only when OVapi's updates carried this trip (D0).

KEYED: each user brings their own NS key (apiportal.ns.nl, product Ns-App; one subscription per account), sent by the
shared client in the header Ocp-Apim-Subscription-Key. CREDIT: saw_livetrack.ns.ATTRIBUTION (NS, and OVapi's CC0
timetable and delays). The lines are NS's SpoorKaart.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Mapping

from saw_livetrack import ns as _ns
from saw_livetrack.ns import ATTRIBUTION, COMMUTER, KEY_URL, OP_NS, TERMS_URL, VEHICLE_URL

from .. import ns_lines
from .base import SOURCE_NS, Obs, Operator

NS_YELLOW = "#FFC917"
NS_BLUE = "#003082"
RING_WIDTH = 3
LATE_MIN = 3
VERY_LATE_MIN = 10
# The lines are SpoorKaart's track and the fixes GPS within metres of it (NS note 4.5); a pair SpoorKaart does not draw
# is a straight leg: the 1 km scale of Sweden's and SE Queensland's.
OFF_RAIL_M = 1000.0


def look() -> dict[str, Any]:
    return {
        "marker_color": NS_YELLOW,
        "marker_ring_color": NS_BLUE,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": NS_BLUE,
        "marker_label_outline_color": "none",
        "marker_arrow_color": NS_YELLOW,
        "marker_arrow_outline_color": NS_BLUE,
    }


def parse(trains: list[Mapping[str, Any]] | None) -> list[Obs]:
    """The client's trains for this operator -> observations, every one in service."""
    out: list[Obs] = []
    seen: set[str] = set()
    for tr in trains or ():
        number = str(tr.get("number") or "")
        lat, lon, when = tr.get("lat"), tr.get("lon"), tr.get("observed_at")
        if not number or not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            continue
        key = ns_lines.identity(number, tr.get("service_date"))
        if key in seen:
            continue
        seen.add(key)
        out.append(Obs(
            vehicle_id=key, lat=round(float(lat), 6), lon=round(float(lon), 6),
            observed_at=(dt.datetime.fromtimestamp(float(when), dt.timezone.utc)
                         if isinstance(when, (int, float)) else None),
            in_service=True, train=number, line=None, reported_course=tr.get("heading"), trip_id=key))
    return out


def hover(tr: Mapping[str, Any]) -> str | None:
    calls = [c for c in tr.get("calls") or () if not c.get("cancelled")]
    if not calls or not calls[0].get("name") or not calls[-1].get("name"):
        return None
    product = tr.get("route_name") or "Sprinter"
    return f"{product} {tr.get('number')} · {calls[0]['name']}–{calls[-1]['name']}"


def ns_stops(trains: list[Mapping[str, Any]] | None, static: dict[str, Any] | None, now: float
             ) -> tuple[dict[str, tuple[str, float | None]], dict[str, int], dict[str, dict[str, Any]]]:
    """(next_stops {trip: (name, eta)}, trip_delays {trip: seconds}, extras {vehicle: keys}). Module docstring."""
    names = (static or {}).get("stops") or {}
    nxt_out: dict[str, tuple[str, float | None]] = {}
    delays: dict[str, int] = {}
    extras: dict[str, dict[str, Any]] = {}
    for tr in trains or ():
        number = str(tr.get("number") or "")
        if not number:
            continue
        key = ns_lines.identity(number, tr.get("service_date"))
        keys: dict[str, Any] = look()
        if tr.get("observed_at") is not None and tr.get("observed_at_source"):
            keys["observed_at_source"] = tr["observed_at_source"]
        if tr.get("speed_kmh") is not None:
            keys["speed_kmh"] = round(float(tr["speed_kmh"]), 1)
        name = hover(tr)
        if name:
            keys["line_name"] = name
        extras[key] = keys
        calls = tr.get("calls") or []
        if calls:
            idx, eta, delay = _ns.next_call(calls, now)
            if idx is not None:
                c = calls[idx]
                stop_name = c.get("name") or names.get(c.get("code") or "")
                if stop_name:
                    nxt_out[key] = (stop_name, eta)
            if tr.get("updated") and delay is not None:
                delays[key] = delay
    return nxt_out, delays, extras


def ns_styling(obs: Obs) -> dict[str, Any]:
    return look()


def ns_decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
    """The lateness rule, in place (the label is Fleet's: the train number)."""
    rec["late_threshold_min"] = LATE_MIN
    rec["very_late_threshold_min"] = VERY_LATE_MIN


NS = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-11 ~03:00 CST: `ns`, Intercity Rail's id for NS.
    id=OP_NS,
    name="NS Sprinter",
    short="NS",
    regions=("NL",),
    positions_url=VEHICLE_URL,
    parse=parse,
    source=SOURCE_NS,
    ns_consumer=COMMUTER,
    parse_stops=ns_stops,
    styling=ns_styling,
    decorate=ns_decorate,
    off_rail_m=OFF_RAIL_M,
    narn=False,
    # ! A marker only: the shared client sends the key in the header Ocp-Apim-Subscription-Key, never as a query
    # parameter.
    key_param="Ocp-Apim-Subscription-Key",
    key_url=KEY_URL,
    attribution=ATTRIBUTION + ". Lines: NS SpoorKaart. This integration is not sponsored by, affiliated with, or "
                              "operated by NS or OVapi.",
    terms_url=TERMS_URL,
)
