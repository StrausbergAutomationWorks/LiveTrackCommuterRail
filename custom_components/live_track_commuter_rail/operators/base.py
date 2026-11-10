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

from ..const import OFF_RAIL_M

# Where an operator's positions come from. GTFS-Realtime: positions_url is a feed,
# parse(feed) reads it. Digitraffic: the shared Fintraffic client
# (saw_livetrack.digitraffic_rail, one poller per Home Assistant), parse(records)
# reads this integration's records and parse_stops their timetables.
SOURCE_GTFS_RT = "gtfs_rt"
SOURCE_DIGITRAFFIC = "digitraffic"
# Renfe (Spain): the shared Renfe client (saw_livetrack.renfe, one poller per Home
# Assistant) hands over a positions feed and a trip-updates feed already cut to this
# integration's consumer; parse(feed) reads the positions as for GTFS_RT.
SOURCE_RENFE = "renfe"
# Entur (Norway, SSOT 12): the shared Entur client (saw_livetrack.entur, one poller per Home Assistant per codespace)
# hands over a positions feed and a trip-updates feed already cut to this integration's consumer and the operator's
# codespace; parse(feed) reads the positions as for GTFS_RT.
SOURCE_ENTUR = "entur"
# Trafikverket (Sweden, SSOT 14): the shared Trafikverket client (saw_livetrack.trafikverket, one poller per Home
# Assistant) hands over this operator's runs, each a fix and the calls of the trip it is on; parse(runs) reads them,
# as Digitraffic's records. Keyed: the user's key lives in the entry and the client sends it in the request BODY.
SOURCE_TRAFIKVERKET = "trafikverket"


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
    # Keep only these GTFS route_types before distilling the timetable (statics.py,
    # gtfs_filter). None: the whole zip. SE Queensland's zip is every mode.
    static_route_types: tuple[str, ...] | None = None
    # The largest timetable download accepted, in bytes.
    static_max_bytes: int = 20 * 1024 * 1024
    # Seconds a timetable download may take (Renfe's 16 MB took 36 s, SSOT 10).
    static_timeout_s: float = 60
    # True: cut the timetable to the trips running the day before, on and after today
    # before distilling (gtfs_filter.keep_service_window; Renfe's zip holds the whole
    # season, 1.8 M stop times). False: by route_type only, as before.
    static_window: bool = False
    # With static_window: keep only routes whose route_id starts with one of these
    # (Renfe: the network code). None: every route.
    static_route_prefixes: tuple[str, ...] | None = None
    # (the timetable zip, as cut; the distilled timetable; {shape_id: [line index,
    # reversed]}) -> extra keys kept with the timetable under "extras", for decorate.
    static_extras: Callable[[Any, dict[str, Any], dict[str, list[int]]], dict[str, Any]] | None = None
    # A fix older than this at the poll is refused (poll.fresh_only). None: no limit.
    max_fix_age_s: float | None = None
    # On rail: within this of NARN track or of the railroad's own shapes (rail.RailCheck).
    off_rail_m: float = OFF_RAIL_M
    # True where the FRA North American Rail Network covers the railroad (US only), so
    # rail/<id>.json.gz ships with the integration. False: its own shapes alone.
    narn: bool = True
    # (record, the Obs it came from, the distilled timetable or None) -> None: adjusts
    # one record Fleet published, in place (poll.decorate_all). None: nothing.
    decorate: Callable[[dict[str, Any], Obs, dict[str, Any] | None], None] | None = None
    # Fleet's stall_m: farther than this from every stop, a train is stalled after
    # REST_S standing, else after PLATFORM_HOLD_S. None: Fleet's own (300 m).
    stall_m: float | None = None
    # SOURCE_GTFS_RT or SOURCE_DIGITRAFFIC (above).
    source: str = SOURCE_GTFS_RT
    # Digitraffic: the consumer this operator registers with the shared client
    # ("commuter"; saw_livetrack.digitraffic_rail.CONSUMERS).
    digitraffic_consumer: str | None = None
    # Renfe: the consumer this operator registers with the shared Renfe client
    # ("commuter"; saw_livetrack.renfe.CONSUMERS).
    renfe_consumer: str | None = None
    # Entur: the consumer ("commuter") and codespace ("VYG", "GOA", "FLT") this operator registers with the shared
    # Entur client (saw_livetrack.entur.CONSUMERS, CODESPACES).
    entur_consumer: str | None = None
    entur_codespace: str | None = None
    # Entur: trains pushed through Oslo's tunnels where their fixes freeze (entur_push.py, D3d).
    entur_push: bool = False
    # Trafikverket: the (consumer, brand) claim this operator registers with the shared client ("commuter";
    # saw_livetrack.trafikverket.CONSUMERS, BRANDS).
    trafikverket_consumer: str | None = None
    trafikverket_brand: str | None = None
    # With static_window: keep only the routes this accepts (a routes.txt row as a dict; Norway's L lines). None:
    # every route.
    static_route_keep: Callable[[dict[str, str]], bool] | None = None
    # The cut timetable zip -> the zip distilled (Flytoget: its straight shapes replaced by the shipped line). None:
    # as cut.
    static_rewrite: Callable[[bytes], bytes] | None = None
    # (observations, the distilled timetable or None, now) -> the observations kept, after fresh_only (Norway: a
    # finished run's train still in the feed). None: all.
    obs_filter: Callable[[list[Obs], dict[str, Any] | None, float], list[Obs]] | None = None
    # (trip updates, the distilled timetable or None, now) -> (next_stops {trip: (name, eta)}, trip_delays {trip:
    # seconds}), in place of saw_livetrack's next_stops and stop_delays (Norway: Entur's updates list every stop with
    # delays only, so the generic rule took the origin). None: the generic rule.
    stops_from_updates: Callable[[Any, dict[str, Any] | None, float], tuple[dict, dict]] | None = None
    # A feed of trip updates -> this operator's own, before anything reads them (Renfe:
    # one feed for every network; the timetable check must count its own trips). None:
    # the feed as fetched.
    filter_trip_updates: Callable[[Any], Any] | None = None
    # Refuse a fix off the trip's own shape, back along it or too fast forward, and point
    # the arrow the way the trip's stops run (plausible.py; Renfe, whose feed bounces).
    plausible: bool = False
    # The vehicle ids whose fix in this feed is a placeholder, not a position (Renfe:
    # INCOMING_AT rows sit at or past the next stop); plausible.py holds them.
    untrusted_fixes: Callable[[Any], set] | None = None
    # Digitraffic: (records, the distilled timetable or None, now) -> (next_stops
    # {trip: (name, eta)}, trip_delays {trip: seconds}, extras {vehicle: keys added
    # to its published record, poll.apply_extras}).
    parse_stops: Callable[[Any, dict[str, Any] | None, float],
                          tuple[dict, dict, dict]] | None = None
    # Headers for the timetable download besides the User-Agent (Digitraffic asks
    # callers to identify themselves). None: none.
    static_headers: dict[str, str] | None = None
    # A fix at least this old at the poll never counts as standing: `stalled` is
    # dropped (poll.unstall_stale; Finland's Ring Rail tunnel, SSOT 8.1). None: off.
    stand_max_fix_age_s: float | None = None
    # Tunnels its trains are pushed through where their fixes stop, as the map
    # contract's along-route estimate (tunnel.TunnelPush, D3d; Finland's Lentoasema
    # tunnel, SSOT 8.3). Needs the railroad's track network. Empty: none.
    tunnels: tuple[Any, ...] = ()
    # Digitraffic: records -> {vehicle: {station code: tunnel.StopClock}} for the trains
    # in service on a tunnel's line. None: no clocks, so nothing is pushed.
    tunnel_clocks: Callable[[Any], dict[str, dict[str, Any]]] | None = None
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
    "AU-QLD": "Australia — Queensland",
    "FI": "Finland",
    "ES-AN": "Spain — Andalusia",
    "ES-AR": "Spain — Aragon",
    "ES-AS": "Spain — Asturias",
    "ES-CB": "Spain — Cantabria",
    "ES-CL": "Spain — Castile and León",
    "ES-CT": "Spain — Catalonia",
    "ES-GA": "Spain — Galicia",
    "ES-MC": "Spain — Murcia",
    "ES-MD": "Spain — Madrid",
    "ES-PV": "Spain — Basque Country",
    "ES-VC": "Spain — Valencian Community",
    "NO": "Norway",
    "SE": "Sweden",
}
