"""Metra (Northeast Illinois Regional Commuter Railroad). No HA imports.

What this feed carries, measured (Live Track Commuter Rail SSOT section 4):

* vehicle.id      set on every vehicle, unique, stable across pulls. Identity.
* trip block      present ONLY on vehicles in revenue service. 79-172 vehicles
                  carry none at any hour; they are equipment moves, deadheads
                  and parked consists, and none of them stops at stations.
* vehicle.label   the TRAIN NUMBER on routed vehicles; never set otherwise.
                  ! Train numbers are not unique (two 703s ran at once on ME
                  and RI) and collide with equipment numbers (unrouted 1253
                  beside BNSF train 1253), so neither is ever an identity, and
                  a non-revenue vehicle is labelled "NIS <unit>" (06 D8).
* bearing         real and continuous on a MOVING vehicle; 359.0 on most of
                  the parked fleet (128 of 154 at 02:31). Course of travel,
                  never heading (06 D2). Used only right after a move.
* speed           NOT SET on any vehicle. No speed, not a speed of zero, so no
                  max_extrapolation_s ever (06 D3b-i).
* timestamp       set on every vehicle; when the position was true.
* current_status  absent. Do not read it: proto2 defaults it to IN_TRANSIT_TO
                  and the default looks like data (backlog 197).

Licence (SSOT section 5a, read 2026-10-02; linked, not restated): each user
accepts it to get their own key. Clause 1 asks for the not-affiliated
statement below; clause 2 for the time the data was last updated, which every
entity carries as observed_at.
"""

from __future__ import annotations

import re

from .base import Obs, Operator, position_of, vehicle_time

_TRAIN_IN_TRIP = re.compile(r"_[A-Z]*?(\d+)_")

# --- Marker styling, decided by Lee 2026-10-02 (06_MAP_CONTRACT.md D4a) -----
# FILL: Metra's own line colour, `route_color` in its GTFS static routes.txt,
# read 2026-10-02 (bin\ltcr_metra_colors.txt; schedule zip kept in
# bin\metra_gtfs\). Re-check when Metra republishes the static feed.
LINE_COLOR = {
    "BNSF": "#29C233",
    "HC": "#550E0C",
    "MD-N": "#CC5500",
    "MD-W": "#F1AD0E",
    "ME": "#EB5C00",
    "NCS": "#9785BC",
    "RI": "#E02400",
    "SWS": "#0042A8",
    "UP-N": "#008000",
    "UP-NW": "#FFE600",
    "UP-W": "#FE8D81",
}
# HALO (the ring round the disc) and the DIRECTION ARROW's fill: Metra blue,
# with the arrow outlined in white, on every Metra marker.
METRA_BLUE = "#0054A4"
WHITE = "#FFFFFF"
# ! ONE EXCEPTION, Lee's: SWS's own fill #0042A8 is too close to the blue
# halo to separate from it, so its halo is white. Still recognisable: blue
# and white are Metra's colours, and SWS riders know their line is blue.
RING_COLOR_FOR = {"SWS": WHITE}
# Equipment NOT in service carries no route, so no line colour: Lee
# 2026-10-02, it is filled grey (the halo and arrow stay Metra blue). The
# exact grey was not specified; #808080 is a neutral mid grey, chosen here.
NOT_IN_SERVICE_FILL = "#808080"
# HALO WIDTH, Metra only (Lee 2026-10-02: thicker on Metra without changing
# anyone else's). Emitted per entity, so the card's 1 px default stands for
# every other source (06_MAP_CONTRACT.md D4a rule 6b: a JSON number 0.5-4,
# CSS px). 2, not 1.5: a browser floors a border to whole DEVICE pixels, so
# 1.5 draws 1 px on a 1x screen and would look unchanged there. Must stay an
# int or float, never a bool (Python's True is an int and reaches the card as
# JSON true, which it rejects).
RING_WIDTH = 2


def styling(obs: Obs) -> dict[str, str | int]:
    """Marker keys for one Metra vehicle (D4a rule 2 form, rule 3 omission).

    Halo and arrow go on every Metra marker. Fill: the line's colour when in
    service; grey when not in service. An in-service train on a line missing
    from the table gets no fill key, and the card draws its own (D4a rule 3).
    Label colours are not set: the card's defaults apply.
    """
    out = {
        "marker_ring_color": RING_COLOR_FOR.get(obs.line or "", METRA_BLUE),
        "marker_ring_width": RING_WIDTH,
        "marker_arrow_color": METRA_BLUE,
        "marker_arrow_outline_color": WHITE,
    }
    fill = LINE_COLOR.get(obs.line or "") if obs.in_service else NOT_IN_SERVICE_FILL
    if fill is not None:
        out["marker_color"] = fill
    return out


def _train(v) -> str | None:
    label = (v.vehicle.label or "").strip()
    if label:
        return label
    # Fallback only; the label was set on every routed vehicle measured.
    # trip_id looks like "UP-NW_UNW601_V3_C" -> "601"; after Metra's 2026 GTFS
    # change "BNSF_1200_8_2009_5682524" -> "1200": the first _digits_ run, either way.
    m = _TRAIN_IN_TRIP.search(v.trip.trip_id or "")
    return m.group(1) if m else None


def parse(feed) -> list[Obs]:
    out: list[Obs] = []
    for ent in feed.entity:
        if not ent.HasField("vehicle"):
            continue
        v = ent.vehicle
        vid = (v.vehicle.id or "").strip()
        pos = position_of(v)
        if not vid or pos is None:
            continue
        route = (v.trip.route_id or "").strip() if v.HasField("trip") else ""
        in_service = bool(route)
        course = None
        if v.position.HasField("bearing"):
            course = float(v.position.bearing) % 360.0
        out.append(Obs(
            vehicle_id=vid,
            lat=pos[0],
            lon=pos[1],
            observed_at=vehicle_time(v),
            in_service=in_service,
            train=_train(v) if in_service else None,
            line=route or None,
            reported_course=course,
            trip_id=((v.trip.trip_id or "").strip() or None) if in_service else None,
        ))
    return out


METRA = Operator(
    id="metra",
    name="Metra (Chicago area)",
    short="Metra",
    regions=("US-IL", "US-WI"),
    positions_url="https://gtfspublic.metrarr.com/gtfs/public/positions",
    # Next stop by stop_id with an absolute arrival time: 36 of 46 trains in
    # service, 2026-10-02 19:45 (bin\ltcr_eta_probe.txt). Same key.
    trip_updates_url="https://gtfspublic.metrarr.com/gtfs/public/tripupdates",
    # Public, no key. Read for station names and coordinates, line names, and the
    # scheduled times behind delay_min (saw_livetrack.gtfs.distill), by header
    # name; trip, service and shape ids are joined as opaque strings, never
    # parsed, so Metra's 2026 GTFS static change needs nothing here (SSOT 7.9).
    static_url="https://schedules.metrarail.com/gtfs/schedule.zip",
    parse=parse,
    styling=styling,
    attribution=(
        "Data: Metra GTFS-Realtime. This integration is not sponsored by, "
        "affiliated with, or operated by Metra."
    ),
    terms_url="https://metra.com/gtfs-realtime-api-key-request-license-agreement",
    key_param="api_token",
    key_url="https://metra.com/developers",
)
