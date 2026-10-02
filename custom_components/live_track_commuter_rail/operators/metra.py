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


def _train(v) -> str | None:
    label = (v.vehicle.label or "").strip()
    if label:
        return label
    # Fallback only; the label was set on every routed vehicle measured.
    # trip_id looks like "UP-NW_UNW601_V3_C" -> "601".
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
        ))
    return out


METRA = Operator(
    id="metra",
    name="Metra (Chicago area)",
    short="Metra",
    regions=("US-IL", "US-WI"),
    positions_url="https://gtfspublic.metrarr.com/gtfs/public/positions",
    parse=parse,
    attribution=(
        "Data: Metra GTFS-Realtime. This integration is not sponsored by, "
        "affiliated with, or operated by Metra."
    ),
    terms_url="https://metra.com/gtfs-realtime-api-key-request-license-agreement",
    key_param="api_token",
    key_url="https://metra.com/developers",
)
