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
    "last_seen",
    "previous_latitude",
    "previous_longitude",
    "previous_observed_at",
    "segment_duration_s",
    "course_deg",
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
)


def to_attributes(rec: dict[str, Any], operator_id: str) -> dict[str, Any]:
    """extra_state_attributes for one vehicle.

    Never emitted, on purpose:
      heading_deg          no feed here reports which way a train FACES (D2)
      speed_kmh            no feed here reports a speed (D3b-i)
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
