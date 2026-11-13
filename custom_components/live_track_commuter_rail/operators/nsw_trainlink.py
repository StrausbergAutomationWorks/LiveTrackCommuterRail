"""NSW TrainLink's Intercity trains (New South Wales): the Blue Mountains, Hunter, South Coast and Southern Highlands
lines as Transport for NSW's `nswtrains` feed carries them, through the shared client. No Home Assistant imports.
SSOT section 16.

THE SPLIT (Lee 2026-10-20 00:56, backlog 319): `nswtrains` holds three integrations' trains, routed by the shared client
saw_livetrack.tfnsw (one poller per Home Assistant, each entry's own key): route_type 106 (XPT, Xplorer) to Live Track
Intercity Rail, 204/205 (coaches) to Live Track Intercity Buses, 100 "Intercity Train" (agency X000) here, as consumer
"commuter". Operator id `nsw_trainlink` (Lee 2026-11-12; Intercity Rail's id for the same railroad, in this integration's
namespace), region AU-NSW.

⚠ WHAT THIS FEED HOLDS (MEASURED 2026-11-12 13:2x Sydney, bin\\nsw100_measure.txt, nsw100_overlap.txt): only the far
ends of four lines, 6 trains at a time (HUN Newcastle-Telarah/Dungog/Scone, SHL Campbelltown-Moss Vale-Goulburn, SCO
Kiama-Bomaderry, BMT Lithgow-Bathurst). The main Intercity network into Central (CCN, and the electric BMT, SCO and SHL
runs: 43-47 at once) is in Sydney Trains' feed (v2 vehiclepos/sydneytrains), which also carries some of these same runs
(KN56, SN47 seen in both). Not read here: SSOT section 16.

IDENTITY: <run>-<day of the run date>, the run being the trip id's first field (KN56.131126.16.N.2.1316 is KN56), which
Sydney Trains' trip ids share (SN47.1421.149.64.N.2.92126706), so a run reads the same from either feed.

NEXT STOP: saw_livetrack's rule on the trip updates with each trip's origin call taken out (the origin is never a next
stop, Intercity Rail's NSW rule and Norway's here), named by station, never platform (stops_from_updates, station_name).

LABEL the line code (BMT, HUN, SCO, SHL: Transport for NSW's own "short abbreviated codes"), the run in the hover. THE
LOOK (06_MAP_CONTRACT.md D4a-direction, hub Sydney Central): the line's timetable colour filled, white ring and label,
leaving Sydney; swapped going to it. Direction from the timetable's direction_id (0 away from Central on 57,005 of
57,005 trips, MEASURED 2026-10-17); the positions carry none. Unknown: the leaving look.

LATE (Lee 2026-11-12): from 6, very late from 12 (Transport for NSW's Intercity measure, on time within six minutes).

POSITIONS: speed is 0.0 on every reading (cleared by the client); the bearing is not used: the arrow is the trip's own
shape's bearing where the train is (qr_citytrain.shape_course), held at rest, and no move is a jump (position_jump
dropped). A train still reporting after its run's last stop, with a fix FINISHED_AGE_S old, is not drawn (obs_filter;
V741 sat at 1,171 s after its 12:29 Newcastle-Telarah run).
"""

from __future__ import annotations

import csv
import datetime as dt
import io
import re
import time
import zipfile
from typing import Any, Callable
from zoneinfo import ZoneInfo

from saw_livetrack.gtfs import next_stops, stop_delays
from saw_livetrack.tfnsw import ATTRIBUTION, COMMUTER, POSITIONS_URL, STATIC_URL, TERMS_URL, TIME_ZONE

from .base import SOURCE_TFNSW, Obs, Operator, position_of, vehicle_time
from .qr_citytrain import shape_course

OP_ID = "nsw_trainlink"
KEY_URL = "https://opendata.transport.nsw.gov.au/"
WHITE = "#FFFFFF"
RING_WIDTH = 3
LATE_MIN = 6
VERY_LATE_MIN = 12
OFF_RAIL_M = 1000.0
FINISHED_AGE_S = 300.0
INTERCITY_ROUTE_TYPE = "100"
# A trip's service day is the one whose span holds now, from this long before its first time to this long after its last.
RUN_BEFORE_S = 2 * 3600.0
RUN_AFTER_S = 6 * 3600.0
# Used when a route has no colour in the timetable (every route had one on 2026-11-12): NSW TrainLink orange.
DEFAULT_COLOUR = "#F6891F"
# extras["trip"] rows: [route_id, shape line, reversed, direction_id or None, first time s, last time s, first name,
# last name, first stop_sequence, first stop_id]
_ZONE = ZoneInfo(TIME_ZONE)
_RUN = re.compile(r"^[A-Za-z0-9]{2,8}$")
# Tests patch this.
clock: Callable[[], float] = time.time


def epoch(value: Any) -> float | None:
    """A fix time as POSIX seconds (Obs.observed_at is a datetime); a number as it is; anything else None."""
    if isinstance(value, dt.datetime):
        return value.timestamp()
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def run_of(trip_id: Any) -> str | None:
    """'KN56.131126.16.N.2.1316' -> 'KN56': the trip id's first field, when it looks like a run."""
    if not isinstance(trip_id, str):
        return None
    head = trip_id.strip().split(".", 1)[0]
    return head if _RUN.match(head) else None


def sydney_day(now: float) -> int:
    return dt.datetime.fromtimestamp(now, _ZONE).day


def identity(run: str, start_date: str | None, now: float) -> str:
    """'KN56' + '20261113' -> 'KN56-13'; without a run date, Sydney's day now."""
    s = (start_date or "").strip()
    day = int(s[6:8]) if len(s) == 8 and s.isdigit() else sydney_day(now)
    return "%s-%d" % (run, day)


def line_of(route_id: Any) -> str | None:
    """'4T.T.SCO' -> 'SCO'."""
    if not isinstance(route_id, str):
        return None
    rid = route_id.strip()
    return rid[5:] or None if rid.startswith("4T.T.") else None


def parse(feed) -> list[Obs]:
    """The commuter consumer's positions feed (already cut to route_type 100 and cleaned by the client) -> observations."""
    now = clock()
    out: list[Obs] = []
    for ent in feed.entity:
        if not ent.HasField("vehicle"):
            continue
        v = ent.vehicle
        trip = (v.trip.trip_id or "").strip()
        run = run_of(trip)
        pos = position_of(v)
        if run is None or pos is None:
            continue
        out.append(Obs(
            vehicle_id=identity(run, v.trip.start_date, now),
            lat=pos[0],
            lon=pos[1],
            observed_at=vehicle_time(v),
            in_service=True,
            train=run,
            line=line_of(v.trip.route_id),
            reported_course=None,
            trip_id=trip,
        ))
    return out


def _hex(value: Any) -> str | None:
    s = value.strip().lstrip("#").upper() if isinstance(value, str) else ""
    return "#" + s if len(s) == 6 and all(c in "0123456789ABCDEF" for c in s) else None


def _secs(hms: str) -> int | None:
    try:
        h, m, s = (int(x) for x in hms.strip().split(":"))
    except (AttributeError, ValueError):
        return None
    return h * 3600 + m * 60 + s


def _rows(z: zipfile.ZipFile, name: str):
    if name not in z.namelist():
        return
    with z.open(name) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")):
            yield {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}


_PLATFORM = re.compile(r",?\s+Platform\s+\S+$")


def station_name(stop: str) -> str:
    """'Berry Station Platform 1' and 'Mittagong Station, Platform 1' -> the station: the timetable names the platform
    a trip calls at, 124 of its names with a comma (MEASURED 2026-11-12, the replay and the box); the hover names the
    station, as Intercity Rail's NSW TrainLink does."""
    return _PLATFORM.sub("", stop)


def short_name(station: str) -> str:
    """'Kiama Station' -> 'Kiama'; 'Central Station Platform 1' is never asked (parents are used)."""
    return station[:-len(" Station")] if station.endswith(" Station") else station


def extras(z: zipfile.ZipFile, distilled: dict[str, Any], shape_index: dict[str, list[int]]) -> dict[str, Any]:
    """static_extras: each route's [short name, colour, long name]; each kept trip's row (extras["trip"], above)."""
    routes = {r["route_id"]: [r.get("route_short_name", ""), _hex(r.get("route_color")), r.get("route_long_name", "")]
              for r in _rows(z, "routes.txt") if r.get("route_id")}
    stops = {r["stop_id"]: r for r in _rows(z, "stops.txt") if r.get("stop_id")}

    def name(sid: str) -> str:
        s = stops.get(sid) or {}
        return (stops.get(s.get("parent_station", "")) or s).get("stop_name", "")

    keep = distilled.get("sched") or {}
    ends: dict[str, list] = {}
    for r in _rows(z, "stop_times.txt"):
        tid = r.get("trip_id", "")
        if tid not in keep:
            continue
        try:
            seq = int(r.get("stop_sequence", ""))
        except ValueError:
            continue
        dep, arr = _secs(r.get("departure_time", "")), _secs(r.get("arrival_time", ""))
        t = dep if dep is not None else arr
        a = arr if arr is not None else t
        e = ends.get(tid)
        if e is None:
            ends[tid] = [seq, t, r.get("stop_id", ""), seq, a, r.get("stop_id", "")]
            continue
        if seq < e[0]:
            e[0], e[1], e[2] = seq, t, r.get("stop_id", "")
        if seq > e[3]:
            e[3], e[4], e[5] = seq, a, r.get("stop_id", "")
    trips: dict[str, list] = {}
    for r in _rows(z, "trips.txt"):
        tid = r.get("trip_id", "")
        e = ends.get(tid)
        if e is None:   # ends holds the kept trips only
            continue
        ix = shape_index.get(r.get("shape_id", ""), [-1, 0])
        d = r.get("direction_id", "")
        trips[tid] = [r.get("route_id", ""), ix[0], ix[1], d if d in ("0", "1") else None, e[1], e[4],
                      short_name(name(e[2])), short_name(name(e[5])), e[0], e[2]]
    return {"route": routes, "trip": trips}


def service_seconds(now: float, first: Any, last: Any) -> float:
    """Seconds into the trip's service day at `now` (Sydney): today's, else yesterday's (times past 24:00) when only that
    one spans the trip (RUN_BEFORE_S before its first time to RUN_AFTER_S after its last)."""
    local = dt.datetime.fromtimestamp(now, _ZONE)
    s = local.hour * 3600 + local.minute * 60 + local.second + local.microsecond / 1e6
    if isinstance(first, (int, float)) and isinstance(last, (int, float)):
        for cand in (s, s + 86400.0):
            if first - RUN_BEFORE_S <= cand <= last + RUN_AFTER_S:
                return cand
    return s


def toward_sydney(info: list | None) -> bool | None:
    """True going to Sydney Central, False leaving it, None unknown: the timetable's direction_id (1 toward, 0 away)."""
    if not info or len(info) < 4:
        return None
    return {"1": True, "0": False}.get(info[3])


def look(colour: str | None, toward: bool | None) -> dict[str, Any]:
    """D4a-direction: the line's colour filled, white ring and label, leaving Sydney; swapped going to it."""
    c = colour or DEFAULT_COLOUR
    fill, other = (WHITE, c) if toward is True else (c, WHITE)
    return {"marker_color": fill, "marker_ring_color": other, "marker_ring_width": RING_WIDTH,
            "marker_label_color": other, "marker_label_outline_color": "none",
            "marker_arrow_color": fill, "marker_arrow_outline_color": other}


def decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
    """Label, hover line, lateness, look and arrow, in place (poll.decorate_all)."""
    rec.pop("position_jump", None)
    ex = (static or {}).get("extras") or {}
    info = (ex.get("trip") or {}).get(obs.trip_id or "")
    route = (ex.get("route") or {}).get(info[0]) if info else None
    code = (route[0] if route and route[0] else None) or obs.line
    if code:
        rec["marker_label"] = code
    if obs.train:
        ends = "%s–%s" % (info[6], info[7]) if info and info[6] and info[7] else None
        rec["line_name"] = "Train %s · %s" % (obs.train, ends) if ends else "Train %s" % obs.train
    if isinstance(rec.get("next_stop"), str):
        rec["next_stop"] = station_name(rec["next_stop"])
    rec["late_threshold_min"] = LATE_MIN
    rec["very_late_threshold_min"] = VERY_LATE_MIN
    rec.update(look(route[1] if route else None, toward_sydney(info)))
    if not info or info[1] is None or info[1] < 0:
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


def is_origin(update: Any, info: list | None) -> bool:
    """A stop time update for the trip's first call: by stop_sequence where the update carries one (TfNSW's are the
    timetable's, MEASURED on capture round 1), else by stop_id."""
    if not info or len(info) < 10:
        return False
    if update.HasField("stop_sequence"):
        return update.stop_sequence == info[8]
    return bool(update.stop_id) and update.stop_id == info[9]


def stops_from_updates(tu, static: dict[str, Any] | None, now: float) -> tuple[dict, dict]:
    """saw_livetrack's next stops and delays, from the trip updates WITHOUT each trip's origin call: the origin is
    never a next stop (Intercity Rail's rule for NSW TrainLink, and Norway's here). MEASURED live 2026-11-12 20:54: V945
    waiting at Newcastle Interchange read "next Newcastle Interchange"."""
    trips = ((static or {}).get("extras") or {}).get("trip") or {}
    cut = type(tu)()
    cut.CopyFrom(tu)
    for ent in cut.entity:
        if not ent.HasField("trip_update"):
            continue
        tu_ = ent.trip_update
        info = trips.get(tu_.trip.trip_id.strip())
        keep = [u for u in tu_.stop_time_update if not is_origin(u, info)]
        if len(keep) != len(tu_.stop_time_update):
            del tu_.stop_time_update[:]
            tu_.stop_time_update.extend(keep)
    return next_stops(cut, static, now), stop_delays(cut, static, now)


def drop_finished(observations: list[Obs], static: dict[str, Any] | None, now: float) -> list[Obs]:
    """Observations without the trains whose run's last stop is FINISHED_AGE_S behind them and whose fix is that old
    too. Without the timetable, or a trip it does not know, nothing is dropped."""
    trips = ((static or {}).get("extras") or {}).get("trip") or {}
    out = []
    for o in observations:
        info = trips.get(o.trip_id or "")
        fixed = epoch(o.observed_at)
        old = fixed is not None and now - fixed > FINISHED_AGE_S
        if old and info and isinstance(info[5], (int, float)) \
                and service_seconds(now, info[4], info[5]) > info[5] + FINISHED_AGE_S:
            continue
        out.append(o)
    return out


def check_key(key: str, opener: Any = None) -> str | None:
    """One read of the positions with `key` through a PRIVATE client (blocking; the config flow's executor): None when
    Transport for NSW accepts it, "invalid_key" when it refuses it (the trip updates refused it too: the client's own
    rule), "cannot_connect" otherwise. Never a message: the key is in a header."""
    from saw_livetrack.tfnsw import AuthRefused, KeyedError, KeyRefused, TfnswClient
    if not isinstance(key, str) or not key.strip():
        return "invalid_key"
    try:
        # The client's key ring strips the key itself.
        TfnswClient({COMMUTER: key}, opener=opener, background=False).for_consumer(COMMUTER, force=True)
    except (KeyRefused, AuthRefused):
        return "invalid_key"
    except KeyedError:
        return "cannot_connect"
    return None


NSW_TRAINLINK = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-12: nsw_trainlink, Intercity Rail's id, this integration's
    # namespace.
    id=OP_ID,
    name="NSW TrainLink Intercity",
    short="NSW TrainLink",
    regions=("AU-NSW",),
    positions_url=POSITIONS_URL,
    source=SOURCE_TFNSW,
    tfnsw_consumer=COMMUTER,
    parse=parse,
    # The timetable from the client's own copy on disk (statics, raw_source); this URL names the dataset.
    static_url=STATIC_URL,
    static_route_types=(INTERCITY_ROUTE_TYPE,),
    static_window=True,
    static_max_bytes=128 * 1024 * 1024,
    static_timeout_s=600,
    static_extras=extras,
    decorate=decorate,
    obs_filter=drop_finished,
    stops_from_updates=stops_from_updates,
    off_rail_m=OFF_RAIL_M,
    narn=False,
    # ! A marker only: the shared client sends the key in the header `Authorization: apikey <key>`, never as a query
    # parameter.
    key_param="Authorization",
    key_url=KEY_URL,
    attribution=ATTRIBUTION + ". This integration is not sponsored by, affiliated with, or operated by Transport for "
                              "NSW or NSW TrainLink.",
    terms_url=TERMS_URL,
)
