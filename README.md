# Live Track Commuter Rail

**English** · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md)

Live commuter trains on your Home Assistant map. Live Track Commuter Rail is a
Home Assistant integration (a custom component, installed through the
Marketplace / HACS) that shows every train of the commuter railroads you pick,
in real time: where each train is, its train number and line, whether it is
late, its next stop and when it is due there. Positions come from each
railroad's own open data feed (GTFS-Realtime or the railroad's live API); every
train appears as a `geo_location` entity and moves as the feed updates. Add
more railroads one at a time.

Railroads today: **Metra** and the **South Shore Line** (Chicago),
**Renfe Cercanías** and **Rodalies de Catalunya** (Madrid, Barcelona, Valencia,
Sevilla, Bilbao and ten more Spanish networks), **VR and HSL commuter trains**
(Helsinki, Finland), **Vy**, **Go-Ahead Norge** and **Flytoget** (Oslo, Bergen,
Stavanger), **SL Pendeltåg**, **Västtågen** and **Arlanda Express** (Stockholm,
Göteborg), **NS Sprinter** (the Netherlands), **Irish Rail** (Dublin, Cork),
**Queensland Rail Citytrain** (Brisbane), **NSW TrainLink Intercity** (Sydney)
and **V/Line** (Melbourne, Geelong, Ballarat, Bendigo).

## Part of Live Track

Live Track is a system of modules for Home Assistant. Each module tracks one
kind of thing that moves, and every module draws on the same map, so trains,
aircraft and more share one live picture. The modules share one Python library,
[saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)
(on PyPI), and one map card,
[LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard).
Where two modules read the same source, one shared client serves both, so
installing another module does not add requests to that source. Install only
the modules you want; each works on its own.

| Module | What it tracks | Status |
|---|---|---|
| **Live Track Commuter Rail** (this one) | commuter trains | released |
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aircraft around your home, with routes and type icons (ADS-B) | released |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | immigration and federal law-enforcement aircraft and vessels | released |
| Live Track Intercity Rail | intercity and long-distance trains in North America, Europe and Australia (Amtrak, Brightline, VIA Rail, VR and more) | in development |
| Live Track Ships | ships and boats (AIS) | in development |
| Live Track Weather | weather warnings and tropical cyclones | in development |

This integration is not sponsored by, affiliated with, or operated by any of
the railroads it reads. It is original work, MIT-licensed.

## Status

**0.1.1.** It runs live on its development instance with every railroad
below. New in 0.1.1: the setup dialog in Finnish, Swedish, Norwegian Bokmål,
Spanish, Dutch and Irish, and "What appears" for every railroad.

## Requirements

- Home Assistant 2026.11 or later.
- A key of your own for Metra, the Swedish railroads (Trafikverket), NS,
  NSW TrainLink Intercity (Transport for NSW) and V/Line (Transport Victoria);
  where to get each is in the table below. The other railroads need none.
- Home Assistant installs the Python packages it needs (`saw-livetrack`,
  `gtfs-realtime-bindings` and `tzdata`) the first time the integration loads.

## Installation

### From the Marketplace

Live Track Commuter Rail is not in the Marketplace catalog yet. Add it by its
link:

1. Go to **Settings > Marketplace** and select **Add from link**.
2. Enter `StrausbergAutomationWorks/LiveTrackCommuterRail`. If asked for the
   type, choose **Integration**.
3. Install **Live Track Commuter Rail**.
4. Restart Home Assistant. The Marketplace offers the restart as a repair under
   **Settings > System > Repairs**.

The Marketplace then offers each new release as an update.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Copy its `custom_components/live_track_commuter_rail` folder into the
   `custom_components` folder of your Home Assistant configuration directory
   (create that folder if it is not there), so the path ends in
   `custom_components/live_track_commuter_rail/manifest.json`.
3. Restart Home Assistant.

To update by hand, replace the folder with the new release's and restart.

## Supported railroads

| Railroad | Area | Key needed | Terms |
|---|---|---|---|
| Metra | Chicago area (Illinois, Wisconsin) | Yes, your own: request one at [metra.com/developers](https://metra.com/developers) | [Metra's GTFS-Realtime licence](https://metra.com/gtfs-realtime-api-key-request-license-agreement) |
| South Shore Line (NICTD) | Chicago to South Bend (Illinois, Indiana) | No | Public feed published for NICTD by ETA SPOT |
| Queensland Rail Citytrain | SE Queensland (Australia) | No | [Translink open data](https://translink.com.au/about-translink/open-data); data CC BY 4.0, credit Translink |
| VR lähijunat (VR and HSL commuter trains) | Finland | No | [Fintraffic Digitraffic](https://www.digitraffic.fi/en/railway-traffic/); data CC BY 4.0, credit Fintraffic / digitraffic.fi |
| Vy (L1, L2, L4) | Norway: Oslo area, Bergen | No | [Entur open data](https://developer.entur.org); data under the [NLOD 2.0](https://data.norge.no/nlod/en/2.0), distributed by Entur |
| Go-Ahead Norge (L5 Jærbanen) | Norway: Stavanger to Egersund | No | as Vy |
| Flytoget (FLY1, FLY2) | Norway: Drammen and Stabekk to Oslo Airport | No | as Vy |
| SL Pendeltåg | Sweden: Stockholm area, to Uppsala, Bålsta, Gnesta and Nynäshamn | Yes, your own, free: register at [data.trafikverket.se](https://data.trafikverket.se/oauth2/Account/register) | [Trafikverket open data](https://data.trafikverket.se); data [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Västtågen pendeltåg | Sweden: Göteborg to Kungsbacka, Älvängen, Floda and Alingsås | Yes, as SL Pendeltåg (one key serves every Swedish railroad) | as SL Pendeltåg |
| Arlanda Express | Sweden: Stockholm C to Arlanda Airport | Yes, as SL Pendeltåg | as SL Pendeltåg |
| Renfe Cercanías and Rodalies (15 networks) | Spain: Madrid, Barcelona (Rodalies), Asturias, Sevilla, Cádiz, Málaga, Valencia, Murcia/Alicante, Cartagena, Ferrol, León, Bilbao, San Sebastián, Cantabria, Zaragoza | No | [Renfe open data](https://data.renfe.com/); data CC BY 4.0, credit Renfe |
| Irish Rail | Ireland: commuter services around Dublin and Cork | No | Irish Rail publishes no terms; timetable from the [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html), CC BY 4.0 |
| NS Sprinter | the Netherlands | Yes, your own: [NS API portal](https://apiportal.ns.nl/) | the NS API portal; timetable and delays from [OVapi](https://gtfs.ovapi.nl), CC0 |
| NSW TrainLink Intercity | Australia: New South Wales, the Intercity lines out of Sydney | Yes, your own: [Transport for NSW Open Data](https://opendata.transport.nsw.gov.au/) | [Transport for NSW data licence](https://opendata.transport.nsw.gov.au/datalicence); data CC BY 4.0 |
| V/Line commuter | Australia: Victoria, the Geelong, Ballarat, Bendigo, Seymour and Traralgon lines | Yes, your own: [Transport Victoria Open Data](https://opendata.transport.vic.gov.au/) | [Transport Victoria open data](https://discover.data.vic.gov.au/dataset/gtfs-realtime); data CC BY 4.0 |

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

The dialog, and the names of the regions in it, are in English, Finnish,
Swedish, Norwegian Bokmål, Spanish, Dutch and Irish; Home Assistant shows the
one that matches your language.

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
  lines, are always green. Direction swaps the colours: a train heading away
  from Helsinki is the filled disc with a white letter, one heading toward it a
  white disc with the letter and ring in the line's colour. VR numbers its
  trains by direction (odd away from Helsinki, even toward); the ring lines I
  and P turn toward Helsinki at the airport. A train is shown from its first station
  until its last commercial stop, then removed. Line V runs that carry no one
  are shown as `NIS <number>` while they move. A train is late from 4 minutes
  (VR's rule, more than 3) and very late from 8. Lines I and P report no
  position in the Ring Rail airport tunnel, so there the integration moves the
  train along the tracks itself: from the portal to Lentoasema and Aviapolis,
  standing at each until its live departure estimate, then out past the far
  portal to where the quickest trains reappear, until a real position takes
  over. Such a position is marked `position_source: estimated`, with the last
  real one in `fix_latitude` / `fix_longitude`. A position 2 minutes old or
  more never marks a train as stalled, and one over 10 minutes old is refused.
  Between two positions the map card slides a train along the tracks rather
  than in a straight line (`track_path`): the track network ships with the
  integration in `rail/vr_lahijunat_tracks.json.gz`, built with
  `tools/build_tracks.py` from Fintraffic's infra-api tracks (Source:
  Fintraffic / digitraffic.fi, CC BY 4.0; modified: only the tracks commuter
  trains use, joined where they meet, split there and simplified). A move
  with no way along the tracks, or one faster than 200 km/h, slides straight
  as before.
  Off track is more than 1 km from every commuter line in Digitraffic's own
  timetable.
* **Norway** (Vy, Go-Ahead Norge, Flytoget), from Entur through one client shared
  with Live Track Intercity Rail, which draws Norway's F, RE, RX and R lines:
  the label is the line code (L1, FLY1), the train number and the line's name
  are in the hover box. An L line wears its timetable colour, filled with a
  white ring leaving Oslo S (Bergen on L4, Stavanger on L5) and swapped going
  to it. Flytoget is grey with an orange ring going to Oslo Airport and orange
  with a grey ring leaving it. Late from 4 minutes, very late from 8. Entur
  publishes no speed and no heading, so the arrow follows the train's own
  line. In Oslo's long tunnels (Oslotunnelen, Lysaker-Sandvika,
  Sandvika-Asker, Romeriksporten, Lieråsen, Follobanen) a train whose position
  stops coming is moved along its line to where positions come back, in the
  quickest time measured, as `position_source: estimated`. Flytoget's own
  timetable draws straight lines between stations, so its line ships in
  `rail/flytoget_lines.json.gz`, cut from Vy's timetable shapes over the same
  track by `tools/build_flytoget_lines.py` (data NLOD 2.0, distributed by
  Entur; modified).
* **Sweden** (SL Pendeltåg, Västtågen's pendeltåg, Arlanda Express), from
  Trafikverket's open API through one client shared with Live Track Intercity
  Rail, which draws Sweden's other trains; each user brings Trafikverket's free
  key. A train is a run, `<train number>-<day of its date>`, labelled with its
  train number; the brand, number and end stations are in the hover box. SL
  Pendeltåg is pink with a white ring and number, Västtågen light blue with a
  dark blue ring and number, Arlanda Express yellow with black; each swaps its
  colours going toward Stockholm C (Stockholm City for the pendeltåg) or, on a
  trip that calls at neither, its larger end city. Late from 3 minutes on SL
  Pendeltåg (Region Stockholm counts a pendeltåg punctual within 3 minutes),
  very late from 6; late from 6 and very late from 12 on the other two
  (Trafikverket's rule). Sweden publishes no route shapes, so each station
  pair's line ships in `rail/sweden_lines.json.gz`, routed once on
  OpenStreetMap's track by `tools/sweden_lines.py` ((c) OpenStreetMap
  contributors, ODbL 1.0); a train slides along its trip's line between
  positions, and a position more than 1 km from it is refused.
  `rail/sweden_ends.json` holds the end cities' populations (Statistics
  Sweden, CC0).
* **Spain** (Renfe Cercanías and Rodalies; each of the 15 networks is its own
  entry), from Renfe's one open GTFS-Realtime feed through one client shared
  with the other Live Track integrations that read it. A train is a trip. The
  label is its line (C5, R2N) in the route's own colour from Renfe's timetable,
  white with a dark outline as Renfe draws it; a white line gets a thin black
  ring. The train number and the line's name are in the hover box. Renfe places
  its trains on the trip's route rather than by GPS, so they stand and then
  jump: no speed is derived, the arrow follows the trip's route where the train
  is, and a train is called stalled only after 6 minutes in one place. Each
  train moves only forward along its own line: a position more than 150 m off
  it, more than 100 m back along it or faster than 200 km/h is refused and the
  last good one held for up to 10 minutes (six refused positions that agree
  are taken). A position more than 1 km from every route of the network is
  refused. Renfe publishes no on-time rule, so no lateness thresholds are sent
  and the card's defaults apply.
* **Ireland** (Irish Rail's Commuter trains around Dublin and Cork, one entry),
  from Irish Rail's live service through one client shared with Live Track
  Intercity Rail, with the National Transport Authority's timetable for the
  routes and stations. Irish Rail reports a train only as it passes signalling
  points a few minutes apart, so each train is drawn from its timetable and its
  latest reported delay, moved along its trip's route; Cork's trains, which
  Irish Rail does not track, come from the timetable alone. The label is the
  train number without its letter (P508 shows 508); the hover box reads
  "Irish Rail P508 · Maynooth–Dublin Connolly". The disc is the line's colour
  from Transport for Ireland's network map: Northern blue and Cork purple-grey
  with a white ring and number, Western yellow and South Western orange with a
  pale or dark-orange band inside a black ring and a black number. The colours
  swap toward the hub, Dublin or Cork (Kent); a train crossing the city flips
  to leaving once it passes Connolly, Heuston or Kent. Late from 5 minutes
  (Irish Rail's own rule), very late from 10.
* **The Netherlands** (NS Sprinter, one entry), from NS's vehicle feed with your
  own key, through one client shared with Live Track Intercity Rail, which
  draws NS's Intercity and regional trains. The label is the train number;
  the hover box reads "Sprinter 6632 · Dordrecht–Arnhem Centraal". NS yellow
  with an NS blue ring. This is the one feed here that reports a train's own
  speed and heading, and both are passed on (`speed_kmh`, `course_deg`). It
  gives no time for a position, so `observed_at` is the poll that first saw it
  (`observed_at_source: first_seen`). The next stop and the delay come from
  OVapi's timetable (CC0); the track is NS's SpoorKaart, downloaded daily, and
  a train slides along it between positions; a position more than 1 km from it
  is refused. Late from 3 minutes (NS's own definition), very late from 10.
* **New South Wales** (NSW TrainLink Intercity: the Blue Mountains, Central
  Coast and Newcastle, Hunter, South Coast and Southern Highlands lines, one
  entry), from Transport for NSW's NSW TrainLink and Sydney Trains feeds with
  your own key, through one client shared with Live Track Intercity Rail. A run
  in both feeds is one marker. The label is the line code (BMT, CCN, HUN, SCO,
  SHL); the run and its ends are in the hover box ("Train KN56 ·
  Bomaderry–Kiama"). The line's timetable colour, filled with a white ring
  leaving Sydney Central and swapped going to it. Empty trains are
  `NIS <run>` in grey. The next stop is a station, never a platform. The arrow
  follows the trip's route. A position more than 10 minutes old is not drawn,
  and a train is removed when its run is over (its last stop plus its latest
  delay). Late from 6 minutes (Transport for NSW's Intercity measure), very
  late from 12.
* **Victoria** (V/Line commuter: the Geelong, Ballarat, Bendigo, Seymour and
  Traralgon lines, one entry), from Transport Victoria's V/Line feed with your
  own key, through one client shared with Live Track Intercity Rail, which
  draws V/Line's long-distance trains. The label is the line code (GEL, BAT,
  BGO, SER, TRN); the train number and line are in the hover box ("Train 8037 ·
  Bendigo - Melbourne via Gisborne"). Every line is V/Line purple: leaving
  Melbourne a purple disc with a white ring and label, toward Southern Cross a
  white disc with a purple ring and label. V/Line's positions follow the
  timetable more than the train: a trip leaves the feed about a minute after
  its scheduled arrival wherever the train is, and positions freeze around
  midnight. So a train keeps its last position for up to 10 minutes and then
  leaves the map, and a late train can disappear before its terminal. A jump
  faster than 70 m/s is refused. Late from 6 minutes (V/Line's rule for
  commuter services), very late from 12. The arrow follows the trip's route.
* Two count sensors per railroad: **Trains in service** and **Vehicles not in
  service**.

## Map card

Trains are drawn by [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
the card every Live Track integration renders on. Any map card that shows
`geo_location` entities also works.

**The card is installed with the integration.** This integration carries a
released copy of the card, serves it, and registers it as a dashboard resource
when Home Assistant starts; there is nothing to download or copy into `www`.
Every Live Track integration does the same, and they keep exactly one resource
row between them: the highest card version any of them carries, never a
downgrade. A card you installed through HACS is left alone. Removing the last
railroad of this integration hands the row to another Live Track integration,
or removes it if none is left. See the card's README, section
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you. A Repairs issue then gives the exact line to
add; it looks like this, with the integration's own address in place of the
placeholders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_commuter_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

If the integration's files are removed (through HACS, say) while its railroads
are still set up, and no other Live Track integration is installed, nothing is
left to tidy the row: remove it in Settings > Dashboards > Resources. To
install the card by hand instead, follow the card's README; the resource row
of a hand-installed copy under `/local/` is pointed at an integration's copy
only when that copy is a newer release.

Give the card the trains with
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities), filtering
on `domain: geo_location` and `attributes: {source: live_track_commuter_rail}`,
and use `marker_label` as the displayed attribute.

## Data sources

Every railroad is read at runtime, from its own published feed, by your Home
Assistant; nothing from a live feed is in this repository. The table above
links each railroad's terms, and each train credits its source in its
`attribution` attribute. What the repository does ship (track and line files in
`rail/`, built from the FRA's North American Rail Network, Fintraffic,
Entur and OpenStreetMap) and the credit each owes are listed in
[`ATTRIBUTION.md`](ATTRIBUTION.md). By installing this integration you use
these services, and their terms apply to you.

## Licence

Code: MIT, see `LICENSE`. The files in `rail/` keep their sources' licences
(public domain, CC BY 4.0, NLOD 2.0, ODbL 1.0, CC0), and the bundled map card
its own; see [`ATTRIBUTION.md`](ATTRIBUTION.md).

## Search terms

Home Assistant train tracker · live train map · real-time train positions ·
commuter rail · regional rail · suburban rail · GTFS-Realtime · HACS
integration · Metra tracker · South Shore Line tracker · Renfe Cercanías en
tiempo real · Rodalies en temps real · trenes en el mapa · lähijunat kartalla ·
junat reaaliajassa · HSL · pendeltåg i realtid · tåg på kartan · tog i
sanntid · Vy · Flytoget · NS treinen live · Sprinter · treinkaart · Irish Rail
live trains · traenacha beo · Queensland Rail · Translink · NSW TrainLink ·
Transport for NSW · V/Line · Transport Victoria
