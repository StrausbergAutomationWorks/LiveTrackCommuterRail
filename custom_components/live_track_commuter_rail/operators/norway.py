"""Norway's commuter trains on Entur: what Vy's L lines, Go-Ahead Norge's L5 and Flytoget share. No Home Assistant
imports. SSOT section 12.

THE SPLIT (Lee 2026-11-07, backlog 326): every Norwegian train is route_type 100 (Flytoget 101), so the LINE LETTER
decides: L lines and all of Flytoget here, F, RE, RX and R in Live Track Intercity Rail. The shared client
(saw_livetrack.entur, one poller per Home Assistant) has already routed each vehicle to ONE consumer; this integration
registers "commuter" for its operator's codespace (VYG, GOA, FLT) and gets rail only (rail-replacement buses go to
"bus").

IDENTITY: <train number>-<day of the run date>, as Live Track Intercity Rail keys Norway's runs and VR lahijunat here.
The number is Entur's own privateCode (MEASURED 2026-11-08 on the Journey Planner, bin\\no_jp_number.txt): the
leading digits of Vy's and Go-Ahead's trip ids (VYG:ServiceJourney:2218_443612-R is 2218, GOA:...:3001_63033-R is
3001), and the third field of Flytoget's (FLT:ServiceJourney:1-2614-3724-20261108 is 3724). The run date is the
position's start_date (the client sets it; Flytoget's since saw-livetrack 0.2.28).

LABEL the line code (L1, FLY1; Lee 2026-11-07), from the route; the hover line is "Train 2218 · Spikkestad-Oslo
S-Lillestrom" (the card shows line_name, never train: 06_MAP_CONTRACT.md D4b). Flytoget's routes have no long name:
the trip's two end stations stand in.

THE LOOK (06_MAP_CONTRACT.md D4a-direction): filled in the line's colour with a white ring and label leaving the hub,
the swapped look going to it (Lee 2026-11-07 for Norway). The hub: the trip's LAST stop at Oslo S, else Bergen, else
Stavanger (L4 Bergen-Arna and L5 Jaerbanen: his rule, the larger end city, which for these lines is always Bergen or
Stavanger). Flytoget's hub is Oslo lufthavn with its own two-colour look (operators/flytoget.py). A trip that starts at
its hub is leaving it the whole way; one that ends there is going to it the whole way; one that passes through goes to
it until its time there (with the delay) has passed. Direction unknown: the leaving look.

LATE (Lee 2026-11-07, Norway's rule): on time within 3:59 for local trains and Flytoget, so late from 4; very late 8
(2T, as VR lahijunat here; no second tier is published).

POSITIONS (saw_livetrack.entur, MEASURED 2026-11-07): GraphQL fixes, no speed, no bearing (GraphQL's is a chord, not
passed on). So the arrow is the trip's own shape's bearing where the train is (qr_citytrain.shape_course), held at rest,
and no move is a jump (position_jump dropped), as Renfe here. A fix FREEZES in a long tunnel and while a train stands:
Oslo's tunnels are pushed through (entur_push.py); elsewhere a frozen train stays where its fix is (Lee's hold).
FINISHED RUNS: a train still in GraphQL after its run's last stop, with a fix over FINISHED_AGE_S old, is not drawn
(obs_filter; Flytoget's turned trains at the airport sat at 1,305 s on 2026-11-08 08:48Z).
"""

from __future__ import annotations

import csv
import datetime as dt
import io
import math
import re
import time
import zipfile
from typing import Any, Callable, Iterable
from zoneinfo import ZoneInfo

from saw_livetrack.entur import (ATTRIBUTION, COMMUTER, TERMS_URL, TIME_ZONE, TRIP_UPDATES_URL, letters,
                                 line_from_route_id, local_id)
from saw_livetrack.gtfs.schedule import next_by_timetable, update_delays

from .base import SOURCE_ENTUR, Obs, Operator, position_of, vehicle_time
from .qr_citytrain import shape_course

WHITE = "#FFFFFF"
RING_WIDTH = 3
LATE_MIN = 4
VERY_LATE_MIN = 8
OFF_RAIL_M = 1000.0
STALL_M = math.inf
HUBS = ("Oslo S", "Bergen stasjon", "Stavanger stasjon")
FINISHED_AGE_S = 300.0
# A service day is this trip's when now lies from this long before its first time to this long after its last (Entur's
# run date is not always the GTFS service day: Intercity Rail's train 1179, 2026-11-08).
RUN_BEFORE_S = 2 * 3600.0
RUN_AFTER_S = 6 * 3600.0
# extras["trip"] rows: [route_id, shape line, reversed, hub kind, hub time, first time, last time, first name,
# last name, [[stop_sequence, stop_id, arrival s, departure s], ...] in order] (the distilled sched holds arrivals
# only and no sequence; the next stop and the tunnel push need both). Hub kinds:
NO_HUB, HUB_FIRST, HUB_LAST, HUB_MID = 0, 1, 2, 3

_ZONE = ZoneInfo(TIME_ZONE)
_NUMBER = re.compile(r"^(\d{1,5})(?=[-_]|$)")
# Tests patch this.
clock: Callable[[], float] = time.time


def epoch(value: Any) -> float | None:
    """An observation's fix time as POSIX seconds: Obs.observed_at is a datetime (saw_livetrack.gtfs.vehicle_time);
    a number is taken as it is; None stays None."""
    if isinstance(value, dt.datetime):
        return value.timestamp()
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def number_of(trip_id: Any) -> str | None:
    """The train number (Entur's privateCode) from a trip id: Flytoget's third field, else the leading digits."""
    local = local_id(trip_id)
    if not local:
        return None
    if isinstance(trip_id, str) and trip_id.strip().startswith("FLT:"):
        parts = local.split("-")
        return parts[2] if len(parts) >= 4 and parts[2].isdigit() else None
    m = _NUMBER.match(local)
    return m.group(1) if m else None


def oslo_day(now: float) -> int:
    return dt.datetime.fromtimestamp(now, _ZONE).day


def identity(number: str, start_date: str | None, now: float) -> str:
    """'2218' + '20261108' -> '2218-8'; without a run date, Oslo's day now."""
    s = (start_date or "").strip()
    day = int(s[6:8]) if len(s) == 8 and s.isdigit() else oslo_day(now)
    return "%s-%d" % (number, day)


def parse(feed) -> list[Obs]:
    """The commuter consumer's positions feed (already cut to rail, this codespace) -> observations."""
    now = clock()
    out: list[Obs] = []
    for ent in feed.entity:
        if not ent.HasField("vehicle"):
            continue
        v = ent.vehicle
        trip = (v.trip.trip_id or "").strip()
        number = number_of(trip)
        pos = position_of(v)
        if number is None or pos is None:
            continue
        out.append(Obs(
            vehicle_id=identity(number, v.trip.start_date, now),
            lat=pos[0],
            lon=pos[1],
            observed_at=vehicle_time(v),
            in_service=True,
            train=number,
            line=line_from_route_id(v.trip.route_id),
            reported_course=None,
            trip_id=trip,
        ))
    return out


def keep_route(row: dict[str, str]) -> bool:
    """The timetable's L-line routes (gtfs_filter route_keep); Flytoget keeps every route (keep_all)."""
    return letters(row.get("route_short_name")) == "L"


def keep_all(row: dict[str, str]) -> bool:
    return True


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


def hub(names: list[str], hubs: Iterable[str]) -> int | None:
    """The index of a trip's hub among its stop names: its LAST stop at the first of `hubs` it calls at."""
    for h in hubs:
        at = [i for i, n in enumerate(names) if n == h]
        if at:
            return at[-1]
    return None


def make_extras(hubs: Iterable[str]):
    """static_extras for one railroad: each route's [short name, colour, long name]; each kept trip's row (above)."""
    hubs = tuple(hubs)

    def extras(z: zipfile.ZipFile, distilled: dict[str, Any], shape_index: dict[str, list[int]]) -> dict[str, Any]:
        routes = {r["route_id"]: [r.get("route_short_name", ""), _hex(r.get("route_color")),
                                  r.get("route_long_name", "")] for r in _rows(z, "routes.txt") if r.get("route_id")}
        stops = {r["stop_id"]: r for r in _rows(z, "stops.txt") if r.get("stop_id")}

        def name(sid: str) -> str:
            s = stops.get(sid) or {}
            return (stops.get(s.get("parent_station", "")) or s).get("stop_name", "")

        keep = distilled.get("sched") or {}
        calls: dict[str, list] = {}
        for r in _rows(z, "stop_times.txt"):
            tid = r.get("trip_id", "")
            if tid in keep:
                try:
                    seq = int(r.get("stop_sequence", ""))
                except ValueError:
                    continue
                calls.setdefault(tid, []).append((seq, r.get("stop_id", ""), _secs(r.get("arrival_time", "")),
                                                  _secs(r.get("departure_time", ""))))
        trips: dict[str, list] = {}
        for r in _rows(z, "trips.txt"):
            tid, rid = r.get("trip_id", ""), r.get("route_id", "")
            c = sorted(calls.get(tid) or [])
            if tid not in keep or not c:
                continue
            ix = shape_index.get(r.get("shape_id", ""), [-1, 0])
            names = [name(sid) for _, sid, _, _ in c]
            h = hub(names, hubs)
            kind = (NO_HUB if h is None else HUB_FIRST if h == 0 else HUB_LAST if h == len(c) - 1 else HUB_MID)
            hub_t = None if h is None else (c[h][2] if c[h][2] is not None else c[h][3])
            first = c[0][3] if c[0][3] is not None else c[0][2]
            last = c[-1][2] if c[-1][2] is not None else c[-1][3]
            trips[tid] = [rid, ix[0], ix[1], kind, hub_t, first, last, names[0], names[-1],
                          [[seq, sid, a, d] for seq, sid, a, d in c]]
        return {"route": routes, "trip": trips}

    return extras


def service_seconds(now: float, first: Any, last: Any) -> float:
    """Seconds into the trip's service day at `now` (Oslo): today's, else yesterday's (times past 24:00) when only that
    one spans the trip (RUN_BEFORE_S before its first time to RUN_AFTER_S after its last)."""
    local = dt.datetime.fromtimestamp(now, _ZONE)
    s = local.hour * 3600 + local.minute * 60 + local.second + local.microsecond / 1e6
    if isinstance(first, (int, float)) and isinstance(last, (int, float)):
        for cand in (s, s + 86400.0):
            if first - RUN_BEFORE_S <= cand <= last + RUN_AFTER_S:
                return cand
    return s


def toward_hub(info: list | None, delay_s: float, now: float) -> bool | None:
    """True going to the hub, False leaving it, None unknown (module docstring)."""
    if not info or len(info) < 7:
        return None
    kind, hub_t = info[3], info[4]
    if kind == HUB_FIRST:
        return False
    if kind == HUB_LAST:
        return True
    if kind == HUB_MID and isinstance(hub_t, (int, float)):
        return service_seconds(now, info[5], info[6]) - delay_s < hub_t
    return None


def line_look(colour: str, toward: bool | None) -> dict[str, Any]:
    """Norway's look (Lee 2026-11-07): the colour filled with a white ring and label leaving the hub, swapped going
    to it; unknown: leaving."""
    fill, other = (WHITE, colour) if toward is True else (colour, WHITE)
    return {"marker_color": fill, "marker_ring_color": other, "marker_ring_width": RING_WIDTH,
            "marker_label_color": other, "marker_label_outline_color": "none",
            "marker_arrow_color": fill, "marker_arrow_outline_color": other}


def make_decorate(look: Callable[[str | None, bool | None], dict[str, Any]]):
    """decorate for one railroad; look(the route's colour or None, toward the hub) -> styling keys."""

    def decorate(rec: dict[str, Any], obs: Obs, static: dict[str, Any] | None) -> None:
        rec.pop("position_jump", None)
        ex = (static or {}).get("extras") or {}
        info = (ex.get("trip") or {}).get(obs.trip_id or "")
        route = (ex.get("route") or {}).get(info[0]) if info else None
        code = (route[0] if route and route[0] else None) or obs.line
        if code:
            rec["marker_label"] = code
        name = route[2] if route and route[2] else (
            "%s-%s" % (short_name(info[7]), short_name(info[8])) if info and info[7] and info[8] else None)
        if obs.train:
            rec["line_name"] = "Train %s · %s" % (obs.train, name) if name else "Train %s" % obs.train
        rec["late_threshold_min"] = LATE_MIN
        rec["very_late_threshold_min"] = VERY_LATE_MIN
        delay = rec.get("delay_min")
        delay_s = delay * 60.0 if isinstance(delay, (int, float)) and not isinstance(delay, bool) else 0.0
        rec.update(look(route[1] if route else None, toward_hub(info, delay_s, clock())))
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

    return decorate


def short_name(station: str) -> str:
    """'Oslo lufthavn stasjon' -> 'Oslo lufthavn' (Entur's station names end in ' stasjon'; Vy's line names do not)."""
    return station[:-len(" stasjon")] if station.endswith(" stasjon") else station


def stops_from_updates(tu, static: dict[str, Any] | None, now: float) -> tuple[dict, dict]:
    """({trip: (next stop's name, estimated arrival epoch)}, {trip: delay seconds at it}) from Entur's trip updates and
    the timetable (Operator.stops_from_updates). MEASURED 2026-11-08 (bin\\no_flt_debug.txt): Entur's updates list
    every stop of the run from the first, passed ones included, with a delay and no clock time, so the generic
    next_stops (first update not behind the train) took the ORIGIN. As Live Track Intercity Rail does for Norway: the
    first stop whose departure (else arrival) plus its delay is still ahead (saw_livetrack's next_by_timetable), never
    the origin; the origin's delay counts for the stop after it."""
    ex = (static or {}).get("extras") or {}
    trips = ex.get("trip") or {}
    names = (static or {}).get("stops") or {}
    nxt_out: dict[str, tuple] = {}
    delays_out: dict[str, int] = {}
    for ent in getattr(tu, "entity", ()):
        if not ent.HasField("trip_update"):
            continue
        tid = ent.trip_update.trip.trip_id.strip()
        info = trips.get(tid)
        calls = info[9] if info and len(info) > 9 and isinstance(info[9], list) else None
        if not calls:
            continue
        base_s = now - service_seconds(now, info[5], info[6])
        rows = [(seq, sid, None if a is None else base_s + a, None if d is None else base_s + d)
                for seq, sid, a, d in calls]
        delays, skipped = update_delays(ent.trip_update)
        ahead = rows[1:] if len(rows) > 1 else rows
        known = dict(delays)
        if rows[0][0] in known and ahead[0][0] not in known:
            known[ahead[0][0]] = known[rows[0][0]]
        got = next_by_timetable(ahead, known, skipped, now)
        if got is None:
            continue
        seq, sid, delay, eta = got
        if names.get(sid):
            nxt_out[tid] = (names[sid], eta)
        if isinstance(delay, (int, float)) and not isinstance(delay, bool):
            delays_out[tid] = int(delay)
    return nxt_out, delays_out


def drop_finished(observations: list[Obs], static: dict[str, Any] | None, now: float) -> list[Obs]:
    """Observations without the trains whose run's last stop is FINISHED_AGE_S behind them and whose fix is that old
    too. Without the timetable, or a trip it does not know, nothing is dropped."""
    trips = ((static or {}).get("extras") or {}).get("trip") or {}
    out = []
    for o in observations:
        info = trips.get(o.trip_id or "")
        fixed = epoch(o.observed_at)
        old = fixed is not None and now - fixed > FINISHED_AGE_S
        if old and info and isinstance(info[6], (int, float)) \
                and service_seconds(now, info[5], info[6]) > info[6] + FINISHED_AGE_S:
            continue
        out.append(o)
    return out


def make_operator(*, op_id: str, name: str, short: str, codespace: str, default_colour: str, hubs: Iterable[str],
                  look: Callable[[str | None, bool | None], dict[str, Any]] | None = None,
                  route_keep: Callable[[dict[str, str]], bool] = keep_route,
                  rewrite: Callable[[bytes], bytes] | None = None, credit: str = "") -> Operator:
    """One Norwegian commuter railroad on Entur's shared client."""
    if look is None:
        def look(colour: str | None, toward: bool | None) -> dict[str, Any]:
            return line_look(colour or default_colour, toward)
    return Operator(
        id=op_id,
        name=name,
        short=short,
        regions=("NO",),
        # The config flow's check: one GET of the trip updates the shared client reads.
        positions_url=TRIP_UPDATES_URL % codespace,
        source=SOURCE_ENTUR,
        entur_consumer=COMMUTER,
        entur_codespace=codespace,
        entur_push=True,
        parse=parse,
        # The timetable from the client's own copy on disk (statics, raw_source); this URL names the dataset.
        static_url="https://storage.googleapis.com/marduk-production/outbound/gtfs/rb_%s-aggregated-gtfs.zip"
                   % codespace.lower(),
        static_window=True,
        static_route_keep=route_keep,
        static_rewrite=rewrite,
        static_max_bytes=192 * 1024 * 1024,
        static_timeout_s=600,
        static_extras=make_extras(hubs),
        decorate=make_decorate(look),
        obs_filter=drop_finished,
        stops_from_updates=stops_from_updates,
        off_rail_m=OFF_RAIL_M,
        narn=False,
        stall_m=STALL_M,
        attribution=ATTRIBUTION + credit + ". This integration is not sponsored by, affiliated with, or operated by "
                    + name + ".",
        terms_url=TERMS_URL,
    )
