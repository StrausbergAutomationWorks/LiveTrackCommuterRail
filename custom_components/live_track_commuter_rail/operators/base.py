"""What an operator adapter is. No Home Assistant imports.

! A CAPABILITY IS A PROPERTY OF THE SOURCE, NOT OF THE INTEGRATION
(05_SHARED_LESSONS.md B11). Every operator's GTFS-Realtime feed differs in
what it actually populates: Metra's bearing is real on a moving train and
reads 359.0 on parked equipment; NICTD's bearing is 0.0 on every vehicle.
Each adapter states ONLY what its own source really carries and leaves the
rest out (06_MAP_CONTRACT.md D0). Nothing downstream branches on which
operator it is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass(frozen=True)
class Obs:
    """One vehicle in one poll, as its adapter understood it."""

    vehicle_id: str
    lat: float
    lon: float
    # When this position was true: the vehicle's own GTFS-RT timestamp,
    # timezone-aware. None when the vehicle carried none - never the feed
    # header time, which says when the FEED was built (D2).
    observed_at: datetime | None
    in_service: bool
    # The train number a rider would recognise, when in service.
    train: str | None = None
    # The operator's own line id, e.g. "UP-W", or None.
    line: str | None = None
    # A course the SOURCE reports and that is trustworthy WHILE MOVING.
    # None where the source has no usable course. Used only when the vehicle
    # has just moved; at rest it is ignored (Metra reports 359.0 there).
    reported_course: float | None = None
    # The GTFS-RT trip_id while in service: what a TripUpdate is keyed by.
    # Never an identity (NICTD's is the bare train number, and repeats).
    trip_id: str | None = None


@dataclass(frozen=True)
class Operator:
    """One commuter railroad: where its feed is, and how to read it."""

    id: str                      # permanent: becomes the config entry's unique_id
    name: str                    # shown in the setup list
    short: str                   # entity names: "<short> unit <vehicle id>"
    regions: tuple[str, ...]     # region codes from REGIONS, for the setup UI
    positions_url: str
    parse: Callable[[Any], list[Obs]]
    attribution: str
    # Where a user reads the terms, and gets a key if one is needed. Linked,
    # never restated (05_SHARED_LESSONS.md B9).
    terms_url: str | None = None
    # Query parameter carrying the user's key, or None when no key is needed.
    key_param: str | None = None
    key_url: str | None = None
    trip_updates_url: str | None = None
    # TripUpdates -> {train number: delay in seconds}
    parse_delays: Callable[[Any], dict[str, int]] | None = None
    # The operator's GTFS static zip, for next-station names (schedule.py).
    # None: no next station is published.
    static_url: str | None = None
    # True where TripUpdates name a stop only by sequence, so the timetable's
    # stop_times are needed to know which station and when (NICTD).
    static_stop_times: bool = False
    # Obs -> marker styling keys (06_MAP_CONTRACT.md D4a), each only when set.
    styling: Callable[[Obs], dict[str, Any]] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def needs_key(self) -> bool:
        return self.key_param is not None


# Region codes and the label the setup list shows. ISO 3166-2 where one
# exists, so a new region's code is never a guess.
REGIONS: dict[str, str] = {
    "US-IL": "United States — Illinois",
    "US-IN": "United States — Indiana",
    "US-WI": "United States — Wisconsin",
}


def vehicle_time(v) -> datetime | None:
    """A GTFS-RT VehiclePosition's own timestamp, or None. Shared helper.

    ! HasField, never truthiness: proto2 returns a default for an unset field
    and that default is indistinguishable from a value (06 D3b-i; backlog 197
    found the same trap in current_status).
    """
    if v.HasField("timestamp") and int(v.timestamp) > 0:
        return datetime.fromtimestamp(int(v.timestamp), tz=timezone.utc)
    return None


def position_of(v) -> tuple[float, float] | None:
    """(lat, lon) to 6 decimals, or None when unset or the null island.

    GTFS-RT positions are float32. Promoted to Python floats they carry noise
    digits (41.860511779785156, seen on the box 2026-10-02 in previous_*). Six
    decimals is ~0.1 m, below anything a feed resolves; South Shore rounded
    the same way.
    """
    if not v.HasField("position"):
        return None
    lat = round(float(v.position.latitude), 6)
    lon = round(float(v.position.longitude), 6)
    if lat == 0.0 and lon == 0.0:
        return None
    return lat, lon
