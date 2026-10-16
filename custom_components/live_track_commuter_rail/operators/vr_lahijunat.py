"""VR lähijunat: Finland's commuter trains, VR and HSL, on Fintraffic Digitraffic.
No Home Assistant imports.

SSOT sections 8 and 8.1: measured and decided by Lee on 2026-10-15 (backlog 287).

SOURCE: Digitraffic's rail JSON through the shared client
saw_livetrack.digitraffic_rail (saw-livetrack 0.2.7), ONE poller per Home Assistant
for every Live Track rail integration (shared_digitraffic_rail.py). The client routes
each train to one consumer; this integration registers "commuter" (Digitraffic
category Commuter: types HL, HV, HLV). Every consumer sends the client's own
DEFAULT_USER (Lee 2026-10-14 21:10). Keyless, CC BY 4.0.

A RECORD is one train with a fix: number, departureDate (the FINNISH date of its
first departure), position, speed, fix time, its type and line letter, and the
train's own timetable. There is NO unit id: a run is the object, keyed
"<number>-<day of departureDate>" as Intercity Rail keys VR's (identity()).

IN SERVICE (8.1):
* HL (commuter train): while it has a commercial stop ahead. That includes the
  platform before it leaves (Lee: "Show it, as Metra does").
* HV (line V; positioning moves, not in the passenger GTFS, 100 runs measured, every
  one "commercial" at its first and last rows, 32 with commercial stops between): in
  service only while it has a commercial stop ahead BETWEEN its first and last
  stations; otherwise not in service, NIS <number> in grey while it moves (D8), as
  Metra's equipment.
* A finished run (an HL with no commercial stop ahead; an HV whose last row has an
  actual time) is DROPPED: it stays in train-locations/latest for about 15 minutes
  after its end (p50 905 s), frozen (fi_commuter_stale.txt). A cancelled run too.

STALE FIXES (8.1): kept up to 10 minutes (MAX_FIX_AGE_S, poll.fresh_only), and a fix
2 minutes old or more never counts as standing (STAND_MAX_FIX_AGE_S,
poll.unstall_stale): lines P and I freeze at the ends of the Ring Rail airport tunnel
while the train is underground, and a late one must not pulse there.

THE LOOK (8.1): the line letter on a disc. HSL purple #8C4799 (Digitransit's HSL rail
colour) on the letters with HSL routes, A E I K L P U Y; VR green #00B451 (VR's own
token for Pantone 7481, as Intercity Rail's VR) on the VR-only letters, D G H M O R T
Z, and on V while a line V run is in service. White letter, no outline (VR's long-distance rule: "They don't outline the numbers
in black"); a white ring 2 px, so the commuter disc is not Intercity's dark-ringed
one; the arrow the fill outlined white. Not in service: grey #808080, same ring and
arrow. A letter in neither list: no fill (D4a rule 3), the number as the label.

LATE (SSOT 0, 8.1): VR's commuter rule, late at more than 3 minutes at the departure
station or destination; differenceInMinutes is the delay rounded to the minute, so
late from 4. Red from 8 (2T, Lee).

THE ARROW: the feed has no bearing (none on any train, measured). Fleet's course
between two fixes (NICTD's way): the fixes are GPS, about 30 s apart (fix age p50 4 s
in service), not SE Queensland's fixed points.

OFF RAIL: Finland's own commuter shapes (the passenger GTFS, route_type 109), no NARN,
at 1 km as SE Queensland (OFF_RAIL_M). MEASURED on capture round 1 through this
pipeline (bin\\ltcr_fi_replay.txt): of 202,090 in-service fixes, p99 110 m from a shape,
max 720 m, none over 1 km; 708 over 300 m, 619 of them line O trains standing about
300 m past Kotkan satama's platform before they leave (fi_hv_o_check.txt), where the
shape ends. At Metra's 300 m they would be refused and never shown.
"""

from __future__ import annotations

from typing import Any, Mapping

from saw_livetrack.digitraffic_rail import ATTRIBUTION, BASE, DEFAULT_USER, parse_ts

from .base import SOURCE_DIGITRAFFIC, Obs, Operator

HSL_PURPLE = "#8C4799"
VR_GREEN = "#00B451"
GREY = "#808080"
WHITE = "#FFFFFF"
RING_WIDTH = 2
# GTFS agency per route_type 109 route, 2026-10-14 (bin\fi_line_agency.txt): these
# letters have HSL routes (and VR routes too: the agency is mixed within a letter).
HSL_LETTERS = frozenset("AEIKLPUY")
# V: line V in service (an HV run with commercial stops between its ends, 8.1); VR's.
VR_LETTERS = frozenset("DGHMORTVZ")
POSITIONING = "HV"

LATE_MIN = 4
VERY_LATE_MIN = 8
MAX_FIX_AGE_S = 600
STAND_MAX_FIX_AGE_S = 120
OFF_RAIL_M = 1000.0

CONSUMER = "commuter"
LOCATIONS_URL = BASE + "/train-locations/latest"
# Passenger GTFS: stops (a parent stop_id IS the station code), shapes and calendars
# of every passenger train (3.3 MB, 2026-10-14); commuter routes are route_type 109.
GTFS_URL = BASE + "/trains/gtfs-passenger-stops.zip"
COMMUTER_ROUTE_TYPE = "109"
TERMS_URL = "https://www.digitraffic.fi/en/railway-traffic/"


def identity(number: str, departure_date: str | None) -> str:
    """'9123', '2026-10-15' -> '9123-15'; the bare number without a usable date."""
    try:
        day = int(str(departure_date)[8:10])
    except (TypeError, ValueError):
        return number
    return f"{number}-{day}" if len(str(departure_date)) == 10 else number


def _rows(train: Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    rows = train.get("timeTableRows") if isinstance(train, Mapping) else None
    return [r for r in rows if isinstance(r, Mapping)] if isinstance(rows, list) else []


def _ahead(row: Mapping[str, Any]) -> bool:
    """A commercial stop the train has not made yet."""
    return (bool(row.get("commercialStop")) and bool(row.get("trainStopping"))
            and not row.get("cancelled") and not row.get("actualTime"))


def _last_actual(rows: list[Mapping[str, Any]]) -> int:
    """Index of the last row with an actual time, -1 with none. A train's progress is
    read from HERE: a stop it made can lack an actual time when a LATER row has one
    (1,076 of 5,224 commuter runs over 10-15 Oct, bin\\fi_noactual.txt; live 2026-10-16,
    1502 made Santala and Skogby with no actual between two that had one)."""
    return max((i for i, r in enumerate(rows) if r.get("actualTime")), default=-1)


def next_commercial(train: Mapping[str, Any] | None) -> tuple[str, Any, int | None] | None:
    """(station code, ETA, delay in minutes) of the next commercial stop after the
    train's last actual row, or None. ETA: the live estimate, else the schedule. Delay:
    that row's differenceInMinutes (rounded to the minute), else the last actual's.
    saw_livetrack.digitraffic_rail.next_stop takes the FIRST row without an actual
    instead, and stalls behind a missed one."""
    rows = _rows(train)
    last = _last_actual(rows)
    fallback = rows[last].get("differenceInMinutes") if last >= 0 else None
    for r in rows[last + 1:]:
        if not _ahead(r):
            continue
        eta = parse_ts(r.get("liveEstimateTime")) or parse_ts(r.get("scheduledTime"))
        delay = r.get("differenceInMinutes")
        if not isinstance(delay, int) or isinstance(delay, bool):
            delay = fallback
        return r.get("stationShortCode"), eta, delay
    return None


def state(rec: Mapping[str, Any]) -> str | None:
    """'service', 'nis', or None (not published: cancelled, finished, or no train)."""
    train = rec.get("train")
    if not isinstance(train, Mapping) or rec.get("cancelled") or train.get("cancelled"):
        return None
    rows = _rows(train)
    if not rows:
        return None
    after = _last_actual(rows) + 1
    if rec.get("train_type") == POSITIONING:
        # Every HV run is "commercial" at its first and last rows (100 of 100, measured:
        # fi_hv_o_check.txt); only a stop between them carries anyone.
        if any(_ahead(r) for r in rows[max(after, 1):-1]):
            return "service"
        return None if rows[-1].get("actualTime") else "nis"
    return "service" if any(_ahead(r) for r in rows[after:]) else None


def parse(records: list[Mapping[str, Any]]) -> list[Obs]:
    """The client's commuter records -> observations."""
    out: list[Obs] = []
    for rec in records or ():
        number = rec.get("number")
        lat, lon = rec.get("lat"), rec.get("lon")
        if not isinstance(number, str) or not number:
            continue
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)) \
                or (lat == 0 and lon == 0):
            continue
        st = state(rec)
        if st is None:
            continue
        vid = identity(number, rec.get("departure_date"))
        in_service = st == "service"
        out.append(Obs(
            vehicle_id=vid,
            lat=round(float(lat), 6),
            lon=round(float(lon), 6),
            observed_at=rec.get("observed_at"),
            in_service=in_service,
            train=number if in_service else None,
            line=rec.get("commuter_line") or None,
            reported_course=None,
            trip_id=vid if in_service else None,
        ))
    return out


def stops(records: list[Mapping[str, Any]], static: dict[str, Any] | None,
          now: float) -> tuple[dict[str, tuple[str, float | None]], dict[str, int],
                                dict[str, dict[str, Any]]]:
    """(next_stops {trip: (name, eta)}, trip_delays {trip: seconds}, extras {vehicle:
    keys}) for the trains in service. A station is named from the timetable's parent
    stops (stop_id = station code), never shown as a code (D4b)."""
    names = (static or {}).get("stops") or {}
    nxt_out: dict[str, tuple[str, float | None]] = {}
    delays: dict[str, int] = {}
    extras: dict[str, dict[str, Any]] = {}
    for rec in records or ():
        number = rec.get("number")
        if not isinstance(number, str) or not number or state(rec) != "service":
            continue
        vid = identity(number, rec.get("departure_date"))
        train = rec["train"]
        nxt = next_commercial(train)
        if nxt is not None:
            code, eta, delay = nxt
            name = names.get(code) if isinstance(code, str) else None
            if name:
                nxt_out[vid] = (name, eta.timestamp() if eta is not None else None)
            if isinstance(delay, int) and not isinstance(delay, bool):
                delays[vid] = delay * 60
        rows = _rows(train)
        first = names.get(rows[0].get("stationShortCode")) if rows else None
        last = names.get(rows[-1].get("stationShortCode")) if rows else None
        if first and last:
            extras[vid] = {"line_name": f"{first} - {last}"}
    return nxt_out, delays, extras


def styling(obs: Obs) -> dict[str, Any]:
    """The disc's colours: by letter in service, grey out of service."""
    if obs.in_service:
        letter = (obs.line or "").upper()
        fill = HSL_PURPLE if letter in HSL_LETTERS else VR_GREEN if letter in VR_LETTERS else None
    else:
        fill = GREY
    keys: dict[str, Any] = {
        "marker_ring_color": WHITE,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": WHITE,
        "marker_label_outline_color": "none",
        "marker_arrow_outline_color": WHITE,
    }
    if fill is not None:
        keys["marker_color"] = fill
        keys["marker_arrow_color"] = fill
    return keys


def decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
    """The label and lateness rule, in place."""
    if obs.in_service:
        letter = (obs.line or "").upper()
        if letter in HSL_LETTERS or letter in VR_LETTERS:
            rec["marker_label"] = letter
        rec["late_threshold_min"] = LATE_MIN
        rec["very_late_threshold_min"] = VERY_LATE_MIN
    else:
        # D8: NIS <number>; the run's number, without the day.
        rec["marker_label"] = "NIS " + obs.vehicle_id.split("-", 1)[0]


VR_LAHIJUNAT = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-10-15: "vr_lahijunat".
    id="vr_lahijunat",
    name="VR lähijunat, commuter trains (Finland)",
    short="VR lähijunat",
    regions=("FI",),
    positions_url=LOCATIONS_URL,
    parse=parse,
    source=SOURCE_DIGITRAFFIC,
    digitraffic_consumer=CONSUMER,
    parse_stops=stops,
    static_url=GTFS_URL,
    static_route_types=(COMMUTER_ROUTE_TYPE,),
    static_headers={"Digitraffic-User": DEFAULT_USER},
    styling=styling,
    decorate=decorate,
    max_fix_age_s=MAX_FIX_AGE_S,
    stand_max_fix_age_s=STAND_MAX_FIX_AGE_S,
    off_rail_m=OFF_RAIL_M,
    narn=False,
    attribution=(
        ATTRIBUTION + ". This integration is not sponsored by, affiliated with, or "
        "operated by Fintraffic, VR or HSL."
    ),
    terms_url=TERMS_URL,
)
