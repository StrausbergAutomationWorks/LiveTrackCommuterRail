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

THE LOOK (Lee 2026-10-16 00:10; research note 20_Research/FI_HSL_VR_MODES_20261016.md):
the line letter on a disc, coloured by PLACE, as HSL's own commuter map and station
posters draw it: HSL purple #8C4799 (HSL's screen colour for commuter trains) while the
train's next commercial stop is in HSL's fare area, else the last station it made; VR
green #00B451 (VR's token for Pantone 7481, as Intercity Rail's VR) outside it, "VR
maksualue". So R, D, T, Z and H turn green beyond Jokela, Haarajoki and Siuntio, and G, M
and O (not HSL lines) are always green. HSL's area is the 50 stations its own GTFS puts
in zones A-E (HSL_STATIONS). With neither station known: by line, HSL's 13 lines purple.
White letter, no outline; a white ring 2 px; the arrow the fill outlined white. Not in
service: grey #808080, same ring and arrow. An unknown letter: the number as the label.
It read (2dded1f to 87da98a): purple on the letters with HSL routes, green on the others,
which drew R, D, T, Z and H green inside Helsinki, where every sign is purple.

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
# HSL's 13 commuter lines (route_type 109 in HSL's own GTFS, feed_version 2026-10-16
# 04:35:27); G, M, O and V are VR's alone. The fallback colour, and the letters shown.
HSL_LINES = frozenset("ADEHIKLPRTUYZ")
VR_ONLY_LINES = frozenset("GMOV")
LETTERS = HSL_LINES | VR_ONLY_LINES
# HSL's fare area: the stations HSL's GTFS puts in zones A-E, matched to Digitraffic
# codes by position (every one within 179 m, Tapanila the farthest;
# bin\fi_hsl\hsl_zone_stations.json, built 2026-10-16 in a Claude session from HSL's
# GTFS and Digitraffic's station list; no build script was kept). Data: HSL, CC BY 4.0.
# Rebuild when HSL's zones change.
HSL_STATIONS = frozenset((
    "AIN", "AVP", "EPO", "HAA", "HKH", "HKI", "HPL", "ILA", "JK", "JP",
    "JRS", "KAN", "KE", "KEA", "KIL", "KKN", "KLH", "KNI", "KRS", "KTÖ",
    "KVH", "KVY", "KÄP", "LEN", "LNÄ", "LOH", "LPV", "MAS", "ML", "MLO",
    "MRL", "MYR", "MÄK", "OLK", "PJM", "PLA", "PMK", "POH", "PSL", "RKL",
    "SAU", "SAV", "STI", "TKL", "TNA", "TOL", "TRL", "VEH", "VKS", "VMO",
))
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
        keys: dict[str, Any] = {}
        fill = area_colour(train, nxt[0] if nxt is not None else None)
        if fill is not None:
            keys["marker_color"] = fill
            keys["marker_arrow_color"] = fill
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
            keys["line_name"] = f"{first} - {last}"
        if keys:
            extras[vid] = keys
    return nxt_out, delays, extras


def area_colour(train: Mapping[str, Any] | None, next_code: str | None) -> str | None:
    """HSL purple if the train's next commercial stop is in HSL's fare area, VR green if
    not; with no next stop, by the last station it made; None with neither."""
    code = next_code
    if not code:
        rows = _rows(train)
        last = _last_actual(rows)
        code = rows[last].get("stationShortCode") if last >= 0 else None
    if not isinstance(code, str) or not code:
        return None
    return HSL_PURPLE if code.rstrip(",") in HSL_STATIONS else VR_GREEN


def styling(obs: Obs) -> dict[str, Any]:
    """The disc's colours: by line in service (HSL's lines purple), grey out of service.
    The PLACE overrides the line where a station is known (stops, area_colour)."""
    if obs.in_service:
        letter = (obs.line or "").upper()
        fill = HSL_PURPLE if letter in HSL_LINES else VR_GREEN if letter in VR_ONLY_LINES else None
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
        if letter in LETTERS:
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
        ATTRIBUTION + ". Fare zones: HSL, hsl.fi, CC BY 4.0 (HSL's timetable of "
        "2026-10-16). This integration is not sponsored by, affiliated with, or "
        "operated by Fintraffic, VR or HSL."
    ),
    terms_url=TERMS_URL,
)
