"""NSW TrainLink's Intercity trains (New South Wales): the Blue Mountains, Hunter, South Coast and Southern Highlands
lines as Transport for NSW's `nswtrains` feed carries them, through the shared client. No Home Assistant imports.
SSOT section 16.

THE SPLIT (Lee 2026-10-20 00:56, backlog 319): `nswtrains` holds three integrations' trains, routed by the shared client
saw_livetrack.tfnsw (one poller per Home Assistant, each entry's own key): route_type 106 (XPT, Xplorer) to Live Track
Intercity Rail, 204/205 (coaches) to Live Track Intercity Buses, 100 "Intercity Train" (agency X000) here, as consumer
"commuter". Operator id `nsw_trainlink` (Lee 2026-11-12; Intercity Rail's id for the same railroad, in this integration's
namespace), region AU-NSW.

⚠ WHAT nswtrains HOLDS (MEASURED 2026-11-12 13:2x Sydney, bin\\nsw100_measure.txt, nsw100_overlap.txt): only the far
ends of four lines, 6 trains at a time (HUN Newcastle-Telarah/Dungog/Scone, SHL Campbelltown-Moss Vale-Goulburn, SCO
Kiama-Bomaderry, BMT Lithgow-Bathurst). The main Intercity network into Central (CCN, and the electric BMT, SCO and SHL
runs: 43-47 at once) is in Sydney Trains' feed (v2 vehiclepos/sydneytrains), which also carries some of these same runs.

SYDNEY TRAINS (saw-livetrack 0.2.37, backlog 319; SSOT 16; design 35_Dependencies/ours/saw-amtraker-client/
DESIGN_319_sydneytrains_20261112.md, its section 8 the split): this operator ASKS the shared client for them
(tfnsw_sydney_trains: client.set_sydney_trains at every claim) and gets ONE entity per run-day across both feeds, the
fresher fix, nswtrains' trip and updates whenever nswtrains has the run-day, Sydney Trains' trips with start_date set,
stop_id and bearing cleared, and a run not yet departed only on a fix at most 300 s old (S1, the client's). Here:
* A SECOND TIMETABLE, Sydney Trains' Intercity cut (SYDNEY_CUT: the routes the client routes to "commuter", the days
  around today, stop_times kept), distilled from the client's copy beside nswtrains' route_type 100 cut and MERGED with
  it (merge). Trip ids never collide (saw_livetrack.tfnsw.timetable_of tells them apart), so each trip is looked up only
  in its own timetable's rows. The two share 353 stop ids, MEASURED 2026-11-13 (bin\\ltcr319_static.txt): 218 named
  alike, 135 differing only as "X Station Platform 1" against "X Station, Platform 1", 19 placed 52-166 m apart; where
  they share one, nswtrains' entry is kept.
* STOP SEQUENCES. Sydney Trains sends stop_sequence 0 and no time on its stop updates (delays only: 16,914 of 18,264
  arrivals without a time, bin\\ltcr319_measure.txt): each Sydney Trains trip's sequences are filled from its own
  stop_times (saw_livetrack.gtfs.realtime.sequence_by_stop) before the origin is taken out and the next stop read.
* EMPTY TRAINS, the cut's "Empty Train" headsign (2,136 of 10,132 Intercity trips): not in service under SSOT 4.3a,
  "NIS <run>" in grey, shown from their first move over 50 m until 10 minutes standing (Fleet), never swapped.
* S2: a fix older than 600 s is not drawn (max_fix_age_s). S3: drop_finished, the run's end being its last scheduled
  arrival plus its latest delay.

IDENTITY: <run>-<day of the run date>, the run being the trip id's first field (KN56.131126.16.N.2.1316 is KN56), which
Sydney Trains' trip ids share (SN47.1421.149.64.N.2.92126706), so a run reads the same from either feed. Sydney Trains'
start_date is the client's (0.2.37); without one, Sydney's day now.

NEXT STOP: saw_livetrack's rule on the trip updates with each trip's origin call taken out (the origin is never a next
stop, Intercity Rail's NSW rule and Norway's here), named by station, never platform (stops_from_updates, station_name).

LABEL the line code (BMT, CCN, HUN, SCO, SHL: Transport for NSW's own "short abbreviated codes"), the run in the hover.
THE LOOK (06_MAP_CONTRACT.md D4a-direction, hub Sydney Central): the line's timetable colour filled, white ring and
label, leaving Sydney; swapped going to it. Direction from the timetable's direction_id (0 away from Central on 57,005
of 57,005 nswtrains trips, MEASURED 2026-10-17; in Sydney Trains' cut right on 9,338 of 9,338 Intercity trips whose
ends differ in distance from Central, where the route's _1/_2 suffix is wrong on 38, MEASURED 2026-11-13,
bin\\ltcr319_dir.txt); the positions carry none. Unknown: the leaving look. CCN's colour (D11F2F) is in Sydney Trains'
timetable only.

LATE (Lee 2026-11-12): from 6, very late from 12 (Transport for NSW's Intercity measure, on time within six minutes).

POSITIONS: speed is 0.0 on every reading (cleared by the client); the bearing is not used: the arrow is the trip's own
shape's bearing where the train is (qr_citytrain.shape_course), held at rest, and no move is a jump (position_jump
dropped). A train still reporting after its run's last stop plus its latest delay, with a fix FINISHED_AGE_S old, is not
drawn (obs_filter, S3; V741 sat at 1,171 s after its 12:29 Newcastle-Telarah run).
"""

from __future__ import annotations

import csv
import dataclasses
import datetime as dt
import io
import re
import time
import zipfile
from typing import Any, Callable
from zoneinfo import ZoneInfo

from saw_livetrack.gtfs import next_stops, stop_delays
from saw_livetrack.gtfs.realtime import sequence_by_stop
from saw_livetrack.tfnsw import (ATTRIBUTION, COMMUTER, POSITIONS_URL, STATIC_URL, SYDNEY_COMMUTER,
                                 SYDNEY_POSITIONS_URL, SYDNEY_STATIC_URL, SYDNEYTRAINS, TERMS_URL, TIME_ZONE,
                                 sydney_consumer_of, timetable_of)

from .base import SOURCE_TFNSW, Obs, Operator, position_of, vehicle_time
from .qr_citytrain import shape_course

OP_ID = "nsw_trainlink"
KEY_URL = "https://opendata.transport.nsw.gov.au/"
WHITE = "#FFFFFF"
# Not in service (SSOT 4.3a; Metra's and VR's grey).
GREY = "#808080"
RING_WIDTH = 3
LATE_MIN = 6
VERY_LATE_MIN = 12
OFF_RAIL_M = 1000.0
FINISHED_AGE_S = 300.0
# S2 (design section 5): a fix older than this is not drawn, the family's 10-minute hold.
MAX_FIX_AGE_S = 600.0
INTERCITY_ROUTE_TYPE = "100"
# Sydney Trains' timetable names its trips that carry no passengers so (trip_headsign).
EMPTY_HEADSIGN = "Empty Train"
# A trip's service day is the one whose span holds now, from this long before its first time to this long after its last.
RUN_BEFORE_S = 2 * 3600.0
RUN_AFTER_S = 6 * 3600.0
# Used when a route has no colour in the timetable (every route had one on 2026-11-12): NSW TrainLink orange.
DEFAULT_COLOUR = "#F6891F"
# extras["trip"] rows: [route_id, shape line, reversed, direction_id or None, first time s, last time s, first name,
# last name, first stop_sequence, first stop_id, headsign]
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
    """'4T.T.SCO' (nswtrains) and 'SCO_1a' (Sydney Trains, a prefix the shared client routes here) -> 'SCO'."""
    if not isinstance(route_id, str):
        return None
    rid = route_id.strip()
    if rid.startswith("4T.T."):
        return rid[5:] or None
    head, sep, _ = rid.partition("_")
    return head if sep and head in SYDNEY_COMMUTER else None


def parse(feed) -> list[Obs]:
    """The commuter consumer's positions feed (nswtrains' route_type 100 and Sydney Trains' Intercity lines, one entity per
    run-day, already merged and cleaned by the client) -> observations. Empty Trains are marked by refine, which has the
    timetable."""
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
                      short_name(name(e[2])), short_name(name(e[5])), e[0], e[2], r.get("trip_headsign", "")]
    return {"route": routes, "trip": trips}


def sydney_intercity(route: dict[str, str]) -> bool:
    """A Sydney Trains routes.txt row this operator draws: one the shared client routes to "commuter" (CCN, BMT, SCO,
    SHL, HUN; a prefix it does not list by the row's agency, NSWTrains), so the cut holds every trip it can hand over."""
    rid = route.get("route_id", "")
    return sydney_consumer_of(rid, {rid: route.get("agency_id", "")}) == COMMUTER


def merge(first: dict[str, Any] | None, second: dict[str, Any] | None) -> dict[str, Any] | None:
    """nswtrains' cut (first) and Sydney Trains' Intercity cut (second) as ONE distilled timetable (Operator.static_merge).

    Keyed by trip (sched, stop_times, trip_routes, trip_shapes, extras' trips): the two never share a trip id
    (timetable_of), so a trip's rows are its own timetable's. Keyed by stop or route: the union, nswtrains' entry where
    both have one (353 stop ids shared, the same stations, module docstring). The second's shape lines follow the
    first's, its line indexes shifted to match. `fetched_at` is the SUM of the two, an identity token as ns_lines' and
    sweden_lines' are: it moves when either cut is replaced, so the off-rail check and the shape caches rebuild."""
    if second is None:
        return first
    if first is None:
        return second
    shift = len(first.get("rail_shapes") or ())

    def moved(ix: Any) -> Any:
        return ix + shift if isinstance(ix, int) and not isinstance(ix, bool) and ix >= 0 else ix

    out = dict(first)
    for key in ("stops", "stop_pos", "routes", "sched", "stop_times", "trip_routes"):
        if key in first or key in second:
            out[key] = {**(second.get(key) or {}), **(first.get(key) or {})}
    out["rail_shapes"] = list(first.get("rail_shapes") or ()) + list(second.get("rail_shapes") or ())
    out["trip_shapes"] = {**{t: [moved(v[0]), *v[1:]] for t, v in (second.get("trip_shapes") or {}).items()},
                          **(first.get("trip_shapes") or {})}
    ex1, ex2 = first.get("extras") or {}, second.get("extras") or {}
    out["extras"] = {"route": {**(ex2.get("route") or {}), **(ex1.get("route") or {})},
                     "trip": {**{t: [r[0], moved(r[1]), *r[2:]] for t, r in (ex2.get("trip") or {}).items()},
                              **(ex1.get("trip") or {})}}
    out["fetched_at"] = float(first.get("fetched_at") or 0) + float(second.get("fetched_at") or 0)
    return out


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
    """D4a-direction: the line's colour filled, white ring and label, leaving Sydney; swapped going to it. The label's
    glyphs are outlined in the FILL (Lee 2026-11-13 00:05: "outlined in the fill color so they are readable when they
    enter the outer ring"): a label the same colour as the ring stays legible where it crosses it."""
    c = colour or DEFAULT_COLOUR
    fill, other = (WHITE, c) if toward is True else (c, WHITE)
    return {"marker_color": fill, "marker_ring_color": other, "marker_ring_width": RING_WIDTH,
            "marker_label_color": other, "marker_label_outline_color": fill,
            "marker_arrow_color": fill, "marker_arrow_outline_color": other}


def look_not_in_service() -> dict[str, Any]:
    """SSOT 4.3a: grey with a white ring and label, never swapped by direction (VR's rule here); the label outlined in
    the fill, as look()."""
    return {"marker_color": GREY, "marker_ring_color": WHITE, "marker_ring_width": RING_WIDTH,
            "marker_label_color": WHITE, "marker_label_outline_color": GREY,
            "marker_arrow_color": GREY, "marker_arrow_outline_color": WHITE}


def decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
    """Label, hover line, lateness, look and arrow, in place (poll.decorate_all). Not in service (an Empty Train):
    "NIS <run>" (06_MAP_CONTRACT.md D8; the run without the day, as VR's), grey, no lateness; the arrow as any train's."""
    rec.pop("position_jump", None)
    ex = (static or {}).get("extras") or {}
    info = (ex.get("trip") or {}).get(obs.trip_id or "")
    route = (ex.get("route") or {}).get(info[0]) if info else None
    if not obs.in_service:
        rec["marker_label"] = "NIS " + obs.vehicle_id.split("-", 1)[0]
        rec.update(look_not_in_service())
    else:
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


def rows_of(static: dict[str, Any] | None, trip_id: str) -> list[tuple[int, str]]:
    """(stop_sequence, stop_id) of a trip in its timetable's order, from the distilled stop_times (Sydney Trains' cut
    keeps them); [] for a trip it does not hold."""
    st = ((static or {}).get("stop_times") or {}).get(trip_id) or {}
    out = []
    for seq, row in st.items():
        try:
            out.append((int(seq), str(row[0])))
        except (TypeError, ValueError, IndexError):
            continue
    return sorted(out)


def fill_sequences(feed, static: dict[str, Any] | None) -> int:
    """Each Sydney Trains trip update's stop sequences from its own timetable rows, in place (sequence_by_stop: a stop
    update the rows cannot place is removed, so a trip the cut lacks keeps none); how many stop updates placed. Sydney
    Trains sends 0 on every one (design #5): left so, the next stop is simply the first update listed, which may be a
    stop already behind the train. nswtrains' trips are left as sent: theirs are the timetable's."""
    placed = 0
    for ent in feed.entity:
        if not ent.HasField("trip_update"):
            continue
        tu_ = ent.trip_update
        tid = tu_.trip.trip_id.strip()
        if timetable_of(tid) != SYDNEYTRAINS:
            continue
        placed += sequence_by_stop(tu_, rows_of(static, tid))
    return placed


def stops_from_updates(tu, static: dict[str, Any] | None, now: float) -> tuple[dict, dict]:
    """saw_livetrack's next stops and delays, from the trip updates WITHOUT each trip's origin call: the origin is
    never a next stop (Intercity Rail's rule for NSW TrainLink, and Norway's here). MEASURED live 2026-11-12 20:54: V945
    waiting at Newcastle Interchange read "next Newcastle Interchange". Sydney Trains' sequences are filled first
    (fill_sequences), so its origin is found by sequence too and its delays land on the timetable's stops."""
    trips = ((static or {}).get("extras") or {}).get("trip") or {}
    cut = type(tu)()
    cut.CopyFrom(tu)
    fill_sequences(cut, static)
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


def latest_delays(updates) -> dict[str, int]:
    """{trip_id: seconds late at its LAST stop update that carries a delay (arrival's, else departure's)}: the run's
    end as forecast. Nothing for a trip with none, or without updates."""
    out: dict[str, int] = {}
    for ent in (updates.entity if updates is not None else ()):
        if not ent.HasField("trip_update"):
            continue
        tu_ = ent.trip_update
        tid = tu_.trip.trip_id.strip()
        for u in tu_.stop_time_update:
            for ev in ("arrival", "departure"):
                if u.HasField(ev) and getattr(u, ev).HasField("delay"):
                    out[tid] = int(getattr(u, ev).delay)
                    break
    return out


def drop_finished(observations: list[Obs], static: dict[str, Any] | None, now: float,
                  delays: dict[str, int] | None = None) -> list[Obs]:
    """Observations without the trains whose run's end is FINISHED_AGE_S behind them and whose fix is that old too (S3).
    The end is the last stop's scheduled arrival plus the run's latest delay where it is late (`delays`, latest_delays);
    never earlier for a train running early. Without the timetable, or a trip it does not know, nothing is dropped."""
    trips = ((static or {}).get("extras") or {}).get("trip") or {}
    late = delays or {}
    out = []
    for o in observations:
        info = trips.get(o.trip_id or "")
        fixed = epoch(o.observed_at)
        old = fixed is not None and now - fixed > FINISHED_AGE_S
        if old and info and isinstance(info[5], (int, float)):
            end = info[5] + max(0, late.get(o.trip_id or "", 0))
            if service_seconds(now, info[4], info[5]) > end + FINISHED_AGE_S:
                continue
        out.append(o)
    return out


def is_empty(info: list | None) -> bool:
    """An Empty Train: the timetable's headsign says so (a row from before 2026-11-13 has none: never)."""
    return bool(info) and len(info) > 10 and info[10] == EMPTY_HEADSIGN


def refine(observations: list[Obs], static: dict[str, Any] | None, now: float, updates: Any = None) -> list[Obs]:
    """The operator's refusals and marks after fresh_only (Operator.obs_filter, given the trip updates): finished runs
    dropped (S3, drop_finished with each run's latest delay), Empty Trains not in service (SSOT 4.3a: no train number, so
    Fleet shows them only from their first move over 50 m until 10 minutes standing, labelled NIS, no next stop or
    lateness). The trip stays, for the arrow and the way along its shape."""
    kept = drop_finished(observations, static, now, latest_delays(updates))
    trips = ((static or {}).get("extras") or {}).get("trip") or {}
    return [dataclasses.replace(o, in_service=False, train=None) if is_empty(trips.get(o.trip_id or "")) else o
            for o in kept]


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


SYDNEY_CUT = Operator(
    # NOT an entry and never registered (operators/__init__.py): it configures only the second timetable, Sydney Trains'
    # Intercity cut, distilled from the shared client's copy (tfnsw_timetable) into .storage/saw_gtfs_<this id>.json.
    id=OP_ID + "_sydneytrains",
    name="NSW TrainLink Intercity (Sydney Trains timetable)",
    short="NSW TrainLink",
    regions=(),
    positions_url=SYDNEY_POSITIONS_URL,
    source=SOURCE_TFNSW,
    parse=parse,
    static_url=SYDNEY_STATIC_URL,
    tfnsw_timetable=SYDNEYTRAINS,
    # Every route type (all 2), the days around today, the routes the client hands this operator.
    static_window=True,
    static_route_keep=sydney_intercity,
    # Its trip updates name stops by id with sequence 0 and carry delays without times: the rows place them
    # (fill_sequences) and give the scheduled time the delay is added to (saw_livetrack.gtfs.schedule._resolve).
    static_stop_times=True,
    static_max_bytes=128 * 1024 * 1024,
    static_timeout_s=600,
    static_extras=extras,
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
)


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
    # Sydney Trains' Intercity lines too, merged by the client one per run-day (saw-livetrack 0.2.37, SSOT 16).
    tfnsw_sydney_trains=True,
    parse=parse,
    # The timetable from the client's own copy on disk (statics, raw_source); this URL names the dataset.
    static_url=STATIC_URL,
    static_route_types=(INTERCITY_ROUTE_TYPE,),
    static_window=True,
    static_max_bytes=128 * 1024 * 1024,
    static_timeout_s=600,
    static_extras=extras,
    static_second=SYDNEY_CUT,
    static_merge=merge,
    decorate=decorate,
    max_fix_age_s=MAX_FIX_AGE_S,
    obs_filter=refine,
    obs_filter_updates=True,
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
