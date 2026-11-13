# Attribution

Live Track Commuter Rail reads each railroad's live feed at runtime, on your Home Assistant, with your own
key where the railroad asks for one. Nothing from a live feed is shipped in this repository. Every train it
draws carries its railroad's credit in its `attribution` attribute, worded as below. Each railroad's terms
are linked from the setup dialog and from the README's [Supported railroads](README.md#supported-railroads)
table; they bind you, as the person receiving the data.

This integration is not sponsored by, affiliated with, or operated by any of the railroads, agencies or
services named here.

## Live data and timetables, railroad by railroad

**Metra** (Chicago area). Data: Metra GTFS-Realtime, under Metra's licence agreement,
https://metra.com/gtfs-realtime-api-key-request-license-agreement, which each user accepts when requesting
a key. The agreement is linked, not restated here. "Metra" appears only as the name of the railroad a user
picks.

**South Shore Line (NICTD)**. Live data from NICTD / South Shore Line via ETA SPOT (mysouthshoreline.com).
The feed and its timetable are public files ETA SPOT publishes on NICTD's behalf, with no key, no
registration and no licence agreement.

**Queensland Rail Citytrain** (SE Queensland). Data: Translink, Queensland Government, CC BY 4.0,
https://translink.com.au/about-translink/open-data.

**VR lähijunat** (Finland). Data: Fintraffic / digitraffic.fi, CC BY 4.0,
https://www.digitraffic.fi/en/railway-traffic/. Fare zones: HSL, hsl.fi, CC BY 4.0 (the stations in
HSL's zones A to E, taken from HSL's timetable of 2026-10-16 and written into the code).

**Renfe Cercanías and Rodalies** (Spain, 15 networks). Data: Renfe (data.renfe.com), CC BY 4.0, modified,
https://data.renfe.com/.

**Vy, Go-Ahead Norge and Flytoget** (Norway). Contains data under the Norwegian licence for Open Government
data (NLOD) distributed by Entur, https://data.norge.no/nlod/en/2.0.

**SL Pendeltåg, Västtågen pendeltåg and Arlanda Express** (Sweden). Data: Trafikverket (trafikverket.se),
CC0, https://creativecommons.org/publicdomain/zero/1.0/. No credit is required; it is given anyway.

**Irish Rail** (Ireland). Data: Irish Rail (irishrail.ie). Irish Rail publishes no licence or terms for
its realtime service and provides the information as is. Timetable: National Transport Authority,
CC BY 4.0, https://www.transportforireland.ie/transitData/PT_Data.html, provided as is; the National
Transport Authority is not responsible for errors or inaccuracies in it.

**NS Sprinter** (the Netherlands). Data: NS (apiportal.ns.nl), with each user's own key; the NS API
portal, https://apiportal.ns.nl/, publishes no separate product terms. Timetable and delays: OVapi
(gtfs.ovapi.nl), CC0. Lines: NS SpoorKaart, downloaded by each installation at runtime and kept in its
own `.storage`, never shipped here.

**NSW TrainLink Intercity** (New South Wales). Data: Transport for NSW (opendata.transport.nsw.gov.au),
CC BY 4.0, https://opendata.transport.nsw.gov.au/datalicence.

**Adelaide Metro** (South Australia). Data: Adelaide Metro – Department for Infrastructure and Transport,
South Australia, CC BY 4.0, https://www.adelaidemetro.com.au/developer-info (the attribution the Government of
South Australia requests). The piping shrike emblem and Adelaide Metro's trademarks are not used.

**V/Line commuter** (Victoria). Data: Transport Victoria (opendata.transport.vic.gov.au), CC BY 4.0,
https://discover.data.vic.gov.au/dataset/gtfs-realtime.

## Data shipped in this repository

`custom_components/live_track_commuter_rail/rail/`:

* `metra.json.gz`, `nictd.json.gz`: track from the FRA North American Rail Network (US DOT, National
  Transportation Atlas Database), a US Government work in the public domain, cut by `tools/build_rail.py`.
* `vr_lahijunat_tracks.json.gz`: Source: Fintraffic / digitraffic.fi (infra-api), CC BY 4.0, modified:
  only the tracks commuter trains use (listed in `tools/fi_commuter_tracks.txt`), joined where they meet,
  split there and simplified, by `tools/build_tracks.py`.
* `flytoget_lines.json.gz`: Flytoget's lines cut from Vy's timetable shapes over the same track, by
  `tools/build_flytoget_lines.py`. Contains data under the Norwegian licence for Open Government data
  (NLOD) distributed by Entur; modified.
* `sweden_lines.json.gz`: each station pair's line, routed on OpenStreetMap's railway track by
  `tools/sweden_lines.py`. (c) OpenStreetMap contributors, Open Database License (ODbL) 1.0,
  https://opendatacommons.org/licenses/odbl/1-0/. The file's own `meta` says so.
* `sweden_ends.json`: the end cities' populations, from Statistics Sweden (SCB), CC0.

## The map card

`custom_components/live_track_commuter_rail/frontend/live-track-map-card.js` is a released build of
[LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) (MIT), committed byte for
byte. The notices for the packages bundled in it are in the file's first lines.

## The brand icon

`custom_components/live_track_commuter_rail/brand/icon.png` and `icon@2x.png` were drawn for
StrausbergAutomationWorks and are under the MIT licence in `LICENSE`.

## The code

MIT, in `LICENSE`.
