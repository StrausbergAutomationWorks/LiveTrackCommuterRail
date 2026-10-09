"""Constants for Live Track Commuter Rail. No Home Assistant imports."""

DOMAIN = "live_track_commuter_rail"

# Config entry keys. One config entry per operator; the entry's unique_id is
# the operator id, so the same railroad cannot be added twice and no two
# entries ever publish the same vehicle (06_MAP_CONTRACT.md D1).
CONF_OPERATOR = "operator"
CONF_REGION = "region"
CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SHOW_PARKED = "show_parked_equipment"

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 15
MAX_SCAN_INTERVAL = 600
DEFAULT_SHOW_PARKED = False

USER_AGENT = (
    "LiveTrackCommuterRail/0.1.0 "
    "(+https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail)"
)
REQUEST_TIMEOUT = 20  # seconds

# Ride out this many consecutive failed fetches by serving the last good
# result, so one network blip does not blank every marker. Carried over from
# Live Track South Shore, where 9 transient failures were logged in one day
# against a feed that otherwise answered 40 of 40 requests.
MAX_TRANSIENT_FAILURES = 2

# --- Motion (06_MAP_CONTRACT.md D8) -------------------------------------
# Moved / not moved. A parked vehicle's reported position wanders: Brightline
# p50 2 m, max 29 m; Metra's parked fleet max 37 m over 120 s. 50 m is above
# both, and it is the same threshold saw_livetrack's FixTracker uses to tell a
# new fix from the same one seen again.
JITTER_M = 50.0

# A vehicle that is NOT in service is shown from its first displacement over
# JITTER_M until it has been still this long. D8: appear on the first move,
# disappear only after sustained stillness, never on the first quiet sample.
# A crawl through a signal must not blink a train off the map. ~10 min is
# backlog 198's figure; a choice, not a measurement.
HOLD_S = 600

# A vehicle that has not moved for this long is AT REST: course_deg is
# omitted (D3c-iii) and the arrow is held (D4). A choice, not a measurement:
# long enough that a feed which updates positions less often than we poll
# does not make the course flicker, short enough that a train standing at a
# platform stops claiming a direction of travel within a couple of polls.
REST_S = 90

# A vehicle missing from the feed keeps its entity this long (unavailable
# meanwhile) before the entity is removed. Brightline measured trains leaving
# the feed and coming back 65 s later while still running.
GRACE_S = 180

# Longest gap still published as one segment. Longer means the vehicle stood,
# or dropped out and came back, and a straight slide across that gap would be
# invention. Carried over from Live Track South Shore.
MAX_SEGMENT_S = 600

# The shared map's layer name (06_MAP_CONTRACT.md D10). Every vehicle here is
# a train, non-revenue moves included (D8). The card owns the number.
MAP_LAYER = "rail"

# --- Is the cached timetable the realtime feed's? (Metra GTFS change) ----
# Metra's Developer Change Notice (received 2026-10-08): every trip_id is
# renamed in both feeds at its cutover, and a timetable refreshed once a day
# can sit on the wrong side of it for hours, losing every Metra delay with no
# error. MEASURED on the 40 recorded polls of 2026-10-03: the right timetable
# knows 739 of 739 Metra and 191 of 191 NICTD trip references; the wrong one
# knows 0 of 739 (bin\saw_mgc_prove.txt). Any share between is a clear
# answer; half is the choice. Below 5 trips (overnight) nothing is decided.
COVERAGE_MIN_TRIPS = 5
COVERAGE_MIN_SHARE = 0.5

# --- Off rail (Lee 2026-10-08; SSOT 7.10) --------------------------------
# A train in service whose position is farther than this from every railway
# in rail/<operator>.json.gz is refused (saw_livetrack Fleet's on_rail).
# MEASURED 2026-10-08 against FRA NARN track: every real Metra and NICTD fix
# in 9,109 lay within 210 m (RI 705 near Joliet; Millennium Station's
# underground platforms 144 m); the bad unit (8426, UP-N 835) never came
# closer than 374 m (bin\ltcr_offshape_narn.txt, ltcr_rail_size.txt).
OFF_RAIL_M = 300.0
