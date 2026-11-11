"""Vehicle record -> geo_location attributes. The ONE place that mapping lives.

No Home Assistant imports. An ALLOWLIST, so a key added to a record somewhere
else cannot reach the map by accident, and a key missing here is visible in
one place (06_MAP_CONTRACT.md: an integration must not emit a name from the
contract meaning something else).
"""

from __future__ import annotations

from typing import Any

from .const import MAP_LAYER

# Copied when present. Absent stays absent: never None, never a sentinel (D0).
PASSTHROUGH = (
    "train",
    "line",
    "line_name",
    "observed_at",
    # The observed_at rule under D2: "first_seen" where the source gives no fix time and observed_at is the poll
    # that first saw the position (NS, SSOT 15). Absent when the source gave the time.
    "observed_at_source",
    "last_seen",
    "previous_latitude",
    "previous_longitude",
    "previous_observed_at",
    "segment_duration_s",
    # D3c-v: the way along the tracks from the last fix (tracknet; Finland, SSOT 8.3).
    "track_path",
    # D3d: "estimated" when the position was pushed along the tracks where the fixes
    # stop (tunnel.py; Finland's airport tunnel, SSOT 8.3), with the fix it came from;
    # "observed" on the operator's other trains in service.
    "position_source",
    "fix_latitude",
    "fix_longitude",
    "course_deg",
    # D2: the speed the SOURCE reported, km/h. Only NS here reports one (SSOT 15).
    "speed_kmh",
    "icon_rotation_deg",
    "icon_rotation_basis",
    "position_jump",
    "stalled",
    "delay_min",
    "next_stop",
    "arrival_estimated_at",
    "marker_color",
    "marker_label_color",
    "marker_label_outline_color",
    "marker_arrow_color",
    "marker_arrow_outline_color",
    "marker_ring_color",
    "marker_ring_width",
    # D4a-inner-ring: Irish Rail's Western and South Western band (SSOT 13).
    "marker_inner_ring_color",
    "marker_inner_ring_width",
    "marker_symbol",
    "marker_symbol_outline_color",
    "late_threshold_min",
    "very_late_threshold_min",
)


def to_attributes(rec: dict[str, Any], operator_id: str) -> dict[str, Any]:
    """extra_state_attributes for one vehicle.

    Never emitted, on purpose:
      heading_deg          no feed here reports which way a train FACES (D2)
      speed_kmh            except where the feed reports one (NS, SSOT 15); never derived (D3b-i)
      max_extrapolation_s  fails D3b condition 1 on every operator so far
      object_ids           a vehicle or trip id is none of D11's keys
      z_index_offset       retired; map_layer replaces it (D10)
    """
    attrs: dict[str, Any] = {
        "identity": rec["vehicle_id"],
        "marker_label": rec["marker_label"],
        "vehicle_id": rec["vehicle_id"],
        "in_service": rec["in_service"],
        "operator": operator_id,
        "map_layer": MAP_LAYER,
    }
    for key in PASSTHROUGH:
        value = rec.get(key)
        if value is not None:
            attrs[key] = value
    return attrs
