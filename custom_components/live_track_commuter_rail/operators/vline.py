"""V/Line's commuter trains (Victoria, Australia): the Geelong, Ballarat, Bendigo, Seymour and Traralgon lines, on
Transport Victoria's V/Line feeds through the shared client. No Home Assistant imports. SSOT section 17.

THE SPLIT (Lee 2026-11-13 01:45 CST, "Build and deploy"; backlog 337; 20_Research/AU_VLINE_COMMUTER_20261113.md
sections 6 and 7): V/Line's commuter routes GEL, BAT, TRN, BGO and SER here, the long-distance routes in Live Track
Intercity Rail's `vline` entry, as Sydney's went. The cut is V/Line's own: its performance page measures exactly these
five as "short distance (commuter)". The shared client saw_livetrack.transport_vic (0.2.38) fetches V/Line's feed once
for both integrations and hands this consumer ("commuter") only these routes; folder 1 of the timetable is the same file
for both (.storage/saw_transport_vic_1.zip). Operator id `vline` (Lee 2026-11-13: Intercity Rail's id for the same
railroad, in this integration's namespace, as nsw_trainlink), entry "V/Line commuter", region AU-VIC.

V/LINE'S FEED RULES are the library's (saw_livetrack.vline, moved there from Intercity Rail the same night): its
positions run on the timetable, not the train (a trip leaves the feed about a minute after its scheduled arrival
wherever the train is, and every fix freezes at about 23:58), so a run keeps its last accepted fix when its row goes;
flips over 70 m/s are refused; a live trip id the timetable lacks takes its one timetable twin (43 of 43 live ids at
07:4xZ 2026-11-13 were missing from the box's copy). The tracker runs per entry in the coordinator; its reports stand in
for a feed here: parse(reports) reads them, vline_stops their next stops.

A STALE FIX IS HELD, THEN DROPPED (Lee 2026-11-13, asked: "Hold, then drop"): a run is drawn at its last accepted fix
until that fix is MAX_FIX_AGE_S old (the family's 10-minute hold, NSW's S2), then not at all. Intercity Rail's timed
estimate is not built here, so a late train vanishes before its terminal, and after the midnight freeze trains go at
about 00:08. A fix ROW_GONE_TIMED_S old never counts as standing (stand_max_fix_age_s): a run whose row has gone stops
being reported on, not moving.

LABEL the line code (GEL, BAT, BGO, SER, TRN; Lee 2026-11-13 01:4x), the train number and the line in the hover
("Train 8037 · Bendigo - Melbourne via Gisborne"). All five share one colour, so the code is what tells them apart.
THE LOOK (06_MAP_CONTRACT.md D4a-direction, hub Southern Cross): #902095 for all five (Lee 2026-11-13 01:28, MEASURED
from the vector paths of Transport Victoria's September 2026 network map: the regional lines' one colour; GTFS's
route_color 8F1A95 is near it and not it). Leaving Melbourne the purple fill, white ring and label; toward it a white
disc, purple ring and label; the label outlined in the fill (as nsw_trainlink, Lee 2026-11-13 00:05). Unknown: leaving.
Direction from the TIMETABLE trip's direction_id, 0 away, 1 toward (MEASURED, bin\\mel_vline_dir.txt: 0 ends farther
from Southern Cross on 4,555 of 4,555 trips, 1 nearer on 4,366 of 4,366; the live feed carries none, on 43 of 43).

LATE from 6 minutes, very late from 12 (V/Line's own rule for commuter services, on time to 5:59; 12 by the 2T
convention used for VR, Norway and Irish Rail here). NEXT STOP: the library's (the timetable plus the update's delay,
never the origin), named as published ("Geelong Station"; the commuter trips call at 70 stops, none named for a
platform, MEASURED on the box's copy, bin\\vl337_zip_probe.txt).

POSITIONS: no speed in the feed (Intercity's measurement); the arrow is the trip's own shape's bearing where the train
is (qr_citytrain.shape_course), as nsw_trainlink. Each user brings a key (header KeyId). CREDIT: text, no logo.
"""

from __future__ import annotations

import csv
import datetime as dt
import io
import zipfile
from typing import Any

from saw_livetrack.transport_vic import (ATTRIBUTION, CKAN_URL, COMMUTER, REALTIME_BASE, TERMS_URL,
                                         VLINE_COMMUTER_ROUTES, route_code)
from saw_livetrack.vline import ROW_GONE_TIMED_S, next_stop as vline_next_stop

from .base import SOURCE_TRANSPORT_VIC, Obs, Operator
from .qr_citytrain import shape_course

OP_ID = "vline"
KEY_URL = "https://opendata.transport.vic.gov.au/"
PURPLE = "#902095"
WHITE = "#FFFFFF"
RING_WIDTH = 3
LATE_MIN = 6
VERY_LATE_MIN = 12
# Hold, then drop (module docstring): the family's 10-minute hold.
MAX_FIX_AGE_S = 600.0
POSITIONS_URL = REALTIME_BASE + "vline/vehicle-positions"
_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
# extras["trip"] rows: [route_id, shape line, reversed, direction_id or None, first stop name, last stop name]


def _rows(z: zipfile.ZipFile, name: str):
    if name not in z.namelist():
        return
    with z.open(name) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")):
            yield {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}


def _secs(hms: str) -> int | None:
    try:
        h, m, s = (int(x) for x in hms.strip().split(":"))
    except (AttributeError, ValueError):
        return None
    return h * 3600 + m * 60 + s


def short_name(station: str) -> str:
    """'Southern Cross Station' -> 'Southern Cross'."""
    return station[:-len(" Station")] if station.endswith(" Station") else station


def commuter_route(route: dict[str, str]) -> bool:
    """A routes.txt row this operator draws: one of V/Line's commuter routes (static_route_keep)."""
    return route_code(route.get("route_id", "")) in VLINE_COMMUTER_ROUTES


def _today(z: zipfile.ZipFile) -> dt.date:
    tz = next((r.get("agency_timezone", "") for r in _rows(z, "agency.txt")), "")
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo(tz or "Australia/Melbourne")).date()
    except Exception:  # noqa: BLE001 - an unknown zone name in a timetable
        return dt.datetime.now(dt.timezone.utc).date()


def service_days(z: zipfile.ZipFile, days: list[dt.date]) -> dict[str, list[str]]:
    """{service_id: ["YYYYMMDD", ...]}: the days among `days` each service runs, by calendar.txt and that day's
    calendar_dates.txt rows (1 adds, 2 removes)."""
    cal = list(_rows(z, "calendar.txt"))
    extra: dict[str, list[dict[str, str]]] = {}
    for r in _rows(z, "calendar_dates.txt"):
        extra.setdefault(r.get("date", ""), []).append(r)
    out: dict[str, list[str]] = {}
    for day in days:
        wd, ymd = _WEEKDAYS[day.weekday()], day.strftime("%Y%m%d")
        on = {r["service_id"] for r in cal if r.get("service_id") and r.get(wd) == "1"
              and r.get("start_date", "") <= ymd <= r.get("end_date", "")}
        for r in extra.get(ymd, ()):
            if r.get("exception_type") == "1" and r.get("service_id"):
                on.add(r["service_id"])
            elif r.get("exception_type") == "2":
                on.discard(r.get("service_id"))
        for sid in on:
            out.setdefault(sid, []).append(ymd)
    return out


def extras(z: zipfile.ZipFile, distilled: dict[str, Any], shape_index: dict[str, list[int]],
           today: dt.date | None = None) -> dict[str, Any]:
    """static_extras: each route's [short name, colour, long name]; each kept trip's row (extras["trip"], above); its
    stop rows [[sequence, stop_id, arrival s, departure s], ...] (extras["rows"]: both times, which the library's next
    stop and end read) and the days of the window its service runs (extras["runs"]: the trip-id fallback). The zip is
    already cut to the commuter routes and the days around today (static_window, static_route_keep)."""
    routes = {r["route_id"]: [r.get("route_short_name", ""), r.get("route_color", ""), r.get("route_long_name", "")]
              for r in _rows(z, "routes.txt") if r.get("route_id")}
    names = {r["stop_id"]: r.get("stop_name", "") for r in _rows(z, "stops.txt") if r.get("stop_id")}
    trips_txt = {r["trip_id"]: r for r in _rows(z, "trips.txt") if r.get("trip_id")}
    rows: dict[str, list] = {}
    for r in _rows(z, "stop_times.txt"):
        tid = r.get("trip_id", "")
        if tid not in trips_txt:
            continue
        try:
            seq = int(r.get("stop_sequence", ""))
        except ValueError:
            continue
        rows.setdefault(tid, []).append([seq, r.get("stop_id", ""), _secs(r.get("arrival_time", "")),
                                         _secs(r.get("departure_time", ""))])
    for tid in rows:
        rows[tid].sort(key=lambda x: x[0])
    day = today or _today(z)
    days = service_days(z, [day + dt.timedelta(days=d) for d in (-1, 0, 1)])
    trips: dict[str, list] = {}
    runs: dict[str, list[str]] = {}
    for tid, r in trips_txt.items():
        stops = rows.get(tid)
        if not stops:
            continue
        ix = shape_index.get(r.get("shape_id", ""), [-1, 0])
        d = r.get("direction_id", "")
        trips[tid] = [r.get("route_id", ""), ix[0], ix[1], d if d in ("0", "1") else None,
                      short_name(names.get(stops[0][1], "")), short_name(names.get(stops[-1][1], ""))]
        runs[tid] = days.get(r.get("service_id", ""), [])
    return {"route": routes, "trip": trips, "rows": {t: rows[t] for t in trips}, "runs": runs}


class Timetable:
    """The distilled timetable's extras behind saw_livetrack.vline.Timetable's four names."""

    def __init__(self, static: dict[str, Any] | None) -> None:
        ex = (static or {}).get("extras") or {}
        self.rows = ex.get("rows") or {}
        self.runs = ex.get("runs") or {}
        # The twin index is rebuilt when the timetable is another object.
        self.token = self.rows

    def __contains__(self, trip_id: object) -> bool:
        return trip_id in self.rows

    def twin_candidates(self):
        return iter(self.rows)

    def runs_on(self, trip_id: str, start_date: str) -> bool:
        return start_date in (self.runs.get(trip_id) or ())

    def stop_rows(self, trip_id: str) -> list:
        return self.rows.get(trip_id) or []


def parse(reports) -> list[Obs]:
    """The library's reports (saw_livetrack.vline.VLineRuns.update, run by the coordinator) -> observations, each at
    its run's last accepted fix; the trip is the timetable's (the twin for a live id it lacks)."""
    out: list[Obs] = []
    for rep in reports or ():
        run = rep.run
        if run.lat is None or run.lon is None:
            continue
        out.append(Obs(
            vehicle_id=rep.key,
            lat=run.lat,
            lon=run.lon,
            observed_at=run.observed,
            in_service=True,
            train=run.number,
            line=route_code(run.route_id) if run.route_id else None,
            reported_course=None,
            trip_id=run.table_id or run.trip_id,
        ))
    return out


def vline_stops(reports, static: dict[str, Any] | None, now: float) -> tuple[dict, dict, dict]:
    """(next_stops {trip: (name, eta)}, trip_delays {trip: seconds}, extras {}): each run's next stop by the library's
    rule (the timetable plus the update's delay, never the origin), named as published; a delay only where the update
    gave one (D0)."""
    names = (static or {}).get("stops") or {}
    stops: dict[str, tuple[str, float | None]] = {}
    delays: dict[str, int] = {}
    for rep in reports or ():
        run = rep.run
        trip = run.table_id or run.trip_id
        nxt = vline_next_stop(run.rows, run.delays, run.skipped, now)
        if nxt is None:
            continue
        _, stop, delay, eta = nxt
        name = names.get(stop)
        if name:
            stops[trip] = (name, eta)
        if run.delays:
            delays[trip] = int(delay)
    return stops, delays, {}


def toward_melbourne(info: list | None) -> bool | None:
    """True going to Southern Cross, False leaving, None unknown: the timetable trip's direction_id (1 toward, 0 away)."""
    if not info or len(info) < 4:
        return None
    return {"1": True, "0": False}.get(info[3])


def look(toward: bool | None) -> dict[str, Any]:
    """D4a-direction: the purple filled, white ring and label, leaving Melbourne; swapped going to it; the label
    outlined in the fill."""
    fill, other = (WHITE, PURPLE) if toward is True else (PURPLE, WHITE)
    return {"marker_color": fill, "marker_ring_color": other, "marker_ring_width": RING_WIDTH,
            "marker_label_color": other, "marker_label_outline_color": fill,
            "marker_arrow_color": fill, "marker_arrow_outline_color": other}


def decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
    """Label, hover line, lateness, look and arrow, in place (poll.decorate_all)."""
    ex = (static or {}).get("extras") or {}
    info = (ex.get("trip") or {}).get(obs.trip_id or "")
    route = (ex.get("route") or {}).get(info[0]) if info else None
    code = obs.line or (route_code(info[0]) if info and info[0] else None)
    if code:
        rec["marker_label"] = code
    if obs.train:
        line = route[2] if route and route[2] else None
        rec["line_name"] = "Train %s · %s" % (obs.train, line) if line else "Train %s" % obs.train
    rec["late_threshold_min"] = LATE_MIN
    rec["very_late_threshold_min"] = VERY_LATE_MIN
    rec.update(look(toward_melbourne(info)))
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


def check_key(key: str, opener: Any = None) -> str | None:
    """One read of the positions with `key` through a PRIVATE client (blocking; the config flow's executor): None when
    Transport Victoria accepts it, "invalid_key" when it refuses it (the trip updates refused it too: the client's own
    rule), "cannot_connect" otherwise. Never a message: the key is in a header."""
    from saw_livetrack.transport_vic import AuthRefused, KeyedError, KeyRefused, TransportVicClient
    if not isinstance(key, str) or not key.strip():
        return "invalid_key"
    try:
        # The client's key ring strips the key itself.
        TransportVicClient({COMMUTER: key}, opener=opener, background=False).for_consumer(COMMUTER, force=True)
    except (KeyRefused, AuthRefused):
        return "invalid_key"
    except KeyedError:
        return "cannot_connect"
    return None


VLINE = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-13: vline, Intercity Rail's id, this integration's namespace.
    id=OP_ID,
    name="V/Line commuter",
    short="V/Line",
    regions=("AU-VIC",),
    positions_url=POSITIONS_URL,
    source=SOURCE_TRANSPORT_VIC,
    transport_vic_consumer=COMMUTER,
    parse=parse,
    parse_stops=vline_stops,
    # The timetable from the client's own copy of folder 1 on disk (raw_source); this URL names the dataset.
    static_url=CKAN_URL,
    static_window=True,
    static_route_keep=commuter_route,
    static_max_bytes=128 * 1024 * 1024,
    static_timeout_s=600,
    static_extras=extras,
    decorate=decorate,
    max_fix_age_s=MAX_FIX_AGE_S,
    stand_max_fix_age_s=ROW_GONE_TIMED_S,
    narn=False,
    # ! A marker only: the shared client sends the key in the header `KeyId`, never as a query parameter.
    key_param="KeyId",
    key_url=KEY_URL,
    attribution=ATTRIBUTION + ". This integration is not sponsored by, affiliated with, or operated by Transport "
                              "Victoria or V/Line.",
    terms_url=TERMS_URL,
)
