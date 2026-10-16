"""What the coordinator does to one poll around Fleet. No Home Assistant imports.

Each step is decided by a property of the operator's SOURCE (operators/base.py), never
by which operator it is.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from .operators import Obs

# GTFS-RT StopTimeUpdate.ScheduleRelationship SKIPPED.
SKIPPED = 1


def fresh_only(observations: Iterable[Obs], now: float,
               max_age_s: float | None) -> tuple[list[Obs], int]:
    """(the observations whose fix is at most max_age_s old at `now`, how many were
    refused). An observation with no fix time is kept: its age cannot be known.

    SE Queensland (SSOT 9.1, Lee 2026-10-15 20:09: "refuse anything older than 5
    minutes"): a train whose fix froze stays in the feed until the service day ends.
    MEASURED (20_Research/SEQ_CAPTURE1_ANALYSIS_20261015.md section 3): 14.8% of rows
    were over 8 minutes old; a fix 2-5 minutes old was followed by a fresh one 62% of
    the time, 5-8 minutes 15%, older 0.7%. A refused train is absent from the poll, so
    Fleet waits out its grace and then removes it.
    """
    obs = list(observations)
    if max_age_s is None:
        return obs, 0
    kept = [o for o in obs
            if o.observed_at is None or now - o.observed_at.timestamp() <= max_age_s]
    return kept, len(obs) - len(kept)


def drop_skipped(feed) -> int:
    """Remove SKIPPED stop updates from a TripUpdates feed, in place; how many.

    A skipped stop is not the train's next stop, and a stop update with a time is
    otherwise taken for one (saw_livetrack.gtfs.schedule.next_stops). MEASURED
    2026-10-15 on 50 SE Queensland trip-update bodies (bin\\seq_build_measure2.txt):
    646 of 106,026 stop updates SKIPPED, every one carrying a time.
    """
    if feed is None:
        return 0
    n = 0
    for ent in feed.entity:
        if not ent.HasField("trip_update"):
            continue
        updates = ent.trip_update.stop_time_update
        for i in range(len(updates) - 1, -1, -1):
            if updates[i].schedule_relationship == SKIPPED:
                del updates[i]
                n += 1
    return n


def unstall_stale(result: dict[str, Any], observations: Iterable[Obs], now: float,
                  max_age_s: float | None) -> int:
    """Drop `stalled` from every published record whose fix is at least max_age_s old
    at `now`, in place; how many. None: nothing.

    Finland (SSOT 8.1, Lee 2026-10-15: a fix 2 minutes old or more never counts as
    standing). MEASURED (bin\\fi_commuter_stale.txt, fi_commuter_stale2.txt): in service,
    fix age p50 4 s, p99 332 s; the stale fixes are lines P and I frozen at the two ends
    of the Ring Rail airport tunnel while the train is underground. A frozen fix does not
    move, so Fleet counts the train as standing, and a late one would pulse.
    """
    if max_age_s is None:
        return 0
    by_vid = {o.vehicle_id: o for o in observations}
    n = 0
    for vid, rec in (result.get("vehicles") or {}).items():
        obs = by_vid.get(vid)
        if (rec.get("stalled") and obs is not None and obs.observed_at is not None
                and now - obs.observed_at.timestamp() >= max_age_s):
            del rec["stalled"]
            n += 1
    return n


def apply_extras(result: dict[str, Any], extras: dict[str, dict[str, Any]] | None) -> None:
    """Add the adapter's keys for a vehicle to its published record, in place, over
    what the Fleet set (a Digitraffic operator's line name, which no GTFS route_id
    carries here, and vr_lahijunat's colour by place). In-service records only."""
    if not extras:
        return
    for vid, rec in (result.get("vehicles") or {}).items():
        keys = extras.get(vid)
        if keys and rec.get("in_service"):
            rec.update(keys)


def decorate_all(result: dict[str, Any], observations: Iterable[Obs],
                 static: dict[str, Any] | None,
                 decorate: Callable[[dict[str, Any], Obs, dict[str, Any] | None], None] | None
                 ) -> None:
    """The operator's decorate on every published record, in place, with the
    observation it came from."""
    if decorate is None:
        return
    by_vid = {o.vehicle_id: o for o in observations}
    for vid, rec in (result.get("vehicles") or {}).items():
        obs = by_vid.get(vid)
        if obs is not None:
            decorate(rec, obs, static)
