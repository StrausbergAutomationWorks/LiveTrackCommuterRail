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

from saw_livetrack.gtfs.realtime import Obs, position_of, vehicle_time  # noqa: F401


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
