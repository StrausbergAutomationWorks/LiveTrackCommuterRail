"""Moved to saw_livetrack.gtfs.schedule (backlog 274). timetable_stale is ours."""
from saw_livetrack.gtfs.schedule import (  # noqa: F401
    AHEAD_S, PAST_S, STATIC_VERSION, distill, iso_utc, line_name, next_stops,
    trip_coverage)

from .const import COVERAGE_MIN_SHARE, COVERAGE_MIN_TRIPS


def timetable_stale(hit: int, total: int) -> bool:
    """True when the cached timetable knows too few of the realtime feed's
    trips (saw_livetrack.gtfs.trip_coverage) to be the one the feed runs on.
    Fewer than COVERAGE_MIN_TRIPS trips says nothing either way."""
    return total >= COVERAGE_MIN_TRIPS and hit < total * COVERAGE_MIN_SHARE
