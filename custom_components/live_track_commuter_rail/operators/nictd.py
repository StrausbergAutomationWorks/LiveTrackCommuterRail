"""NICTD South Shore Line. No HA imports.

Carried over from Live Track South Shore (south_shore_tracker), which this
operator replaces (SSOT section 0, Lee 2026-10-02). The feed is GTFS-RT but
non-standard, verified against the live feed 2026-08-23 and since:

* route_id   ALWAYS EMPTY. NICTD runs one railroad; never filter on route.
* trip_id    the bare train number ("515"), not a GTFS trip id.
* label      the train number on the controlling unit; "NIS" (Not In
             Service) on every trailing unit of a consist and on non-revenue
             moves. Every unit transmits its own position.
             ! The line comes from trip_id, never the label: a Monon train
             laying over reported label "NIS" with trip_id "1601".
* vehicle.id set and unique on every unit, trailing units included. trip_id
             is NOT unique (two NIS units both reported trip 509). Identity.
* bearing    present on every vehicle and ALWAYS exactly 0.0 (06 D3b-ii), so
             no reported course: direction comes from two observed fixes.
* speed      never set.

Published as plain S3 objects by ETA SPOT on NICTD's behalf: no key, no
licence agreement, no registration.
"""

from __future__ import annotations

from .base import Obs, Operator, position_of, vehicle_time

LAKESHORE = "lakeshore"
MONON = "monon"

# Colours are this operator's own decision (06_MAP_CONTRACT.md D4a), set by
# Lee 2026-09-20 for Live Track South Shore and carried over unchanged:
# Lakeshore fill orange with dark-red text, Monon the reverse; labels outlined
# in the marker's own fill; arrows outlined in the OTHER line's colour.
MARKER_COLOR = {LAKESHORE: "#EF8322", MONON: "#7F281F"}
LABEL_COLOR = {LAKESHORE: "#7F281F", MONON: "#EF8322"}
LABEL_OUTLINE_COLOR = {LAKESHORE: "#EF8322", MONON: "#7F281F"}
ARROW_OUTLINE_COLOR = {LAKESHORE: "#7F281F", MONON: "#EF8322"}


def line_of(trip_id: str | None) -> str | None:
    """'monon', 'lakeshore', or None when the trip id is not a train number.

    From NICTD's April 2026 timetable, all 139 trains, 0 misses: Monon is
    300-399 or 1000 and above; Lakeshore every other number. NICTD's
    numbering, not a published rule: re-check it with each new timetable.
    """
    s = (trip_id or "").strip()
    if not s.isdigit():
        return None
    n = int(s)
    return MONON if (n >= 1000 or 300 <= n <= 399) else LAKESHORE


def styling(obs: Obs) -> dict[str, str]:
    """Every colour key for the unit's line; {} when it has none (D4a rule 3)."""
    line = obs.line
    if line not in MARKER_COLOR:
        return {}
    return {
        "marker_color": MARKER_COLOR[line],
        "marker_label_color": LABEL_COLOR[line],
        "marker_label_outline_color": LABEL_OUTLINE_COLOR[line],
        "marker_arrow_outline_color": ARROW_OUTLINE_COLOR[line],
    }


def parse(feed) -> list[Obs]:
    out: list[Obs] = []
    for ent in feed.entity:
        if not ent.HasField("vehicle"):
            continue
        v = ent.vehicle
        label = (v.vehicle.label or "").strip()
        trip = (v.trip.trip_id or "").strip()
        # Fall back to the feed entity id, which is "vehicle_position_<id>".
        vid = (v.vehicle.id or "").strip() or (ent.id or "").strip()
        pos = position_of(v)
        # As south_shore_tracker did: a unit with neither a trip nor a label
        # is skipped, and only an explicit "NIS" label marks it out of service.
        if not vid or pos is None or not (trip or label):
            continue
        in_service = label.upper() != "NIS"
        out.append(Obs(
            vehicle_id=vid,
            lat=pos[0],
            lon=pos[1],
            observed_at=vehicle_time(v),
            in_service=in_service,
            train=(trip or label) if in_service else None,
            line=line_of(trip),
            reported_course=None,
        ))
    return out


def parse_delays(feed) -> dict[str, int]:
    """{train number: delay in seconds} at the soonest upcoming stop.

    Only delay and stop_sequence are published - no stop_id, no absolute
    times - so the soonest stop is the best "how late is it now".
    """
    delays: dict[str, int] = {}
    for ent in feed.entity:
        if not ent.HasField("trip_update"):
            continue
        tu = ent.trip_update
        train = (tu.trip.trip_id or "").strip()
        if not train:
            continue
        best = None
        for stu in tu.stop_time_update:
            if stu.HasField("arrival") and stu.arrival.HasField("delay"):
                if best is None or stu.stop_sequence < best[0]:
                    best = (stu.stop_sequence, int(stu.arrival.delay))
        if best is not None:
            delays[train] = best[1]
    return delays


NICTD = Operator(
    id="nictd",
    name="South Shore Line (NICTD)",
    short="NICTD",
    regions=("US-IL", "US-IN"),
    positions_url=(
        "https://s3.amazonaws.com/etatransit.gtfs/"
        "southshore.etaspot.net/position_updates.pb"
    ),
    trip_updates_url=(
        "https://s3.amazonaws.com/etatransit.gtfs/"
        "southshore.etaspot.net/trip_updates.pb"
    ),
    parse=parse,
    parse_delays=parse_delays,
    styling=styling,
    attribution=(
        "Live data from NICTD / South Shore Line via ETA SPOT "
        "(mysouthshoreline.com)"
    ),
)
