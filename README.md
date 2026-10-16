# Live Track Commuter Rail

Live commuter trains on your Home Assistant map. Pick the railroad you want to
watch; every train it reports appears as a `geo_location` entity and moves as
the railroad's live feed updates. Add more railroads one at a time.

This integration is not sponsored by, affiliated with, or operated by any of
the railroads it reads. It is original work, MIT-licensed.

## Supported railroads

| Railroad | Area | Key needed | Terms |
|---|---|---|---|
| Metra | Chicago area (Illinois, Wisconsin) | Yes, your own: request one at [metra.com/developers](https://metra.com/developers) | [Metra's GTFS-Realtime licence](https://metra.com/gtfs-realtime-api-key-request-license-agreement) |
| South Shore Line (NICTD) | Chicago to South Bend (Illinois, Indiana) | No | Public feed published for NICTD by ETA SPOT |
| Queensland Rail Citytrain | SE Queensland (Australia) | No | [Translink open data](https://translink.com.au/about-translink/open-data); data CC BY 4.0, credit Translink |
| VR lähijunat (VR and HSL commuter trains) | Finland | No | [Fintraffic Digitraffic](https://www.digitraffic.fi/en/railway-traffic/); data CC BY 4.0, credit Fintraffic / digitraffic.fi |

Read each railroad's terms before you use its data; they bind you, as the
person receiving it.

## Setup

Settings → Devices & services → Add integration → **Live Track Commuter Rail**.
Choose a region, then a railroad, then enter your key if that railroad needs
one. The key is stored by Home Assistant with the integration and is never
written to the log; if the railroad later refuses it, Home Assistant asks for
a new one.

Options: the poll interval (default 30 s), and whether to show parked
equipment.

## What appears

* **One `geo_location` entity per vehicle**, named `<railroad> unit <unit
  number>`. Its state is the distance from your home in km.
* `marker_label` is the **train number** for a train in service and
  **`NIS <unit>`** for equipment that is not in service, so a unit number is
  never mistaken for a train number.
* **Equipment not in service** is shown only while it moves, and leaves the
  map after 10 minutes standing. Turn on *Show parked equipment* to see every
  vehicle in the feed.
* Each entity carries `observed_at` (when its position was true) and, between
  two observed positions, `previous_latitude`, `previous_longitude`,
  `previous_observed_at` and `segment_duration_s`, so a map card can move the
  marker between real fixes. Nothing is extrapolated: no feed here reports a
  speed.
* `course_deg` while the train moves; at rest it is left out, and
  `icon_rotation_deg` with `icon_rotation_basis: held` keeps the last
  direction for the marker's arrow.
* `next_stop` (the station's name) and `arrival_estimated_at` (when it is
  expected, ISO 8601 UTC) on a train in service whose next station the
  railroad's feed can resolve; absent otherwise. Metra's feed names the stop
  and its time; South Shore's gives only a stop number and a delay, so the
  railroad's published timetable supplies the station and the scheduled time.
  The timetable is downloaded once a day (no key) and cached in
  `.storage/saw_gtfs_<railroad>.json`.
* **A position that is not on any railway is refused.** A train in service
  reported more than 300 m from track (any railway in the FRA North American
  Rail Network, or the railroad's own published route) is shown at its last
  position that was,
  for up to 10 minutes, then hidden until it is back on track; `observed_at`
  says how old the shown position is. A train first seen off track is not
  shown. The track is the FRA North American Rail Network (US DOT, NTAD), a US
  Government work in the public domain, shipped with the integration in
  `rail/` and rebuilt with `tools/build_rail.py`; the railroad's own route comes
  from the timetable the integration already downloads. Nothing is refused until
  that timetable has loaded.
* **SE Queensland** reports no speed and no bearing, and its positions are fixed
  points on the track, not GPS. A position more than 5 minutes old is refused
  (Translink's feed keeps a train whose position froze until the service day
  ends), as is one more than 1 km from every rail line in Translink's own
  timetable (there is no FRA network outside the US). The marker carries the
  line's T number in Translink's line colours, swapped for trains heading
  south, and a star for the special runs that have no T number; the arrow
  follows the train's own route in the timetable. A train is late from 4
  minutes, 6 on the Gold Coast, Rosewood and Sunshine Coast lines, Queensland
  Rail's own rule (`late_threshold_min`). Translink's timetable covers every
  mode; only its trains are kept.
* **Finland** comes from Fintraffic's Digitraffic rail service through one poller
  shared with the other Live Track rail integrations (`saw-livetrack`), so
  installing more of them costs Digitraffic no extra requests. A train is a run:
  `<train number>-<day of its departure date>`. The marker carries the line
  letter, coloured by where the train is, as HSL's own maps and station signs
  colour the lines: HSL purple while its next stop is in HSL's fare area (zones
  A to E, from HSL's open data, CC BY 4.0), VR green outside it. An R train is
  purple to Jokela and green on to Riihimäki; G, M and O, which are not HSL
  lines, are always green. A train is shown from its first station
  until its last commercial stop, then removed. Line V runs that carry no one
  are shown as `NIS <number>` while they move. A train is late from 4 minutes
  (VR's rule, more than 3) and very late from 8. Positions under the Ring Rail
  airport tunnel freeze until the train comes out: a position 2 minutes old or
  more never marks a train as stalled, and one over 10 minutes old is refused.
  Off track is more than 1 km from every commuter line in Digitraffic's own
  timetable.
* Two count sensors per railroad: **Trains in service** and **Vehicles not in
  service**.

## Map card

Any map card that shows `geo_location` entities works. With
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities), filter
on `domain: geo_location` and `attributes: {source: live_track_commuter_rail}`,
and use `marker_label` as the displayed attribute.
