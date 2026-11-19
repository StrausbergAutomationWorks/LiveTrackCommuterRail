# Live Track Commuter Rail

**English** · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md) · [All languages](#languages)

**Commuter trains for Home Assistant, on one map.** Live Track Commuter Rail
puts every train of the commuter railroads you choose on your Home Assistant
map, live: where it is, its train number or line, whether it is late, and its
next stop. Each railroad is added on its own, from its own open data.

> **Live Track Commuter Rail is one module of Live Track**, a family of Home
> Assistant integrations that draw everything that moves, and the weather it
> moves through, on one shared map: aircraft, ships, trains and weather.
> Install it on its own, or beside the other modules
> ([list below](#part-of-live-track-the-other-modules)).

> **Growing, and open to ideas.** Live Track Commuter Rail covers 31 railroads
> in 8 countries on 3 continents today, and we are adding more railroads and
> countries. Is yours missing? [Suggest it](#help-it-grow), or add it
> yourself: we will help you do it.

**Status: 0.1.4, released.** Added to the Marketplace by link
([below](#install-it-step-by-step)); it is not in the Marketplace's catalog
yet.

Original work by StrausbergAutomationWorks. Not affiliated with, or endorsed
by, Metra, the Northern Indiana Commuter Transportation District (NICTD),
ETA SPOT, Renfe, Fintraffic, HSL, VR, Entur, Vy, Go-Ahead Norge, Flytoget,
Trafikverket, SL, Västtågen, Arlanda Express, Irish Rail, the National
Transport Authority (Ireland), NS, OVapi, Translink, Queensland Rail,
Transport for NSW, Transport Victoria, V/Line, Adelaide Metro, the Public
Transport Authority of Western Australia, or any other railroad.

---

## Contents

1. [Everything it does](#everything-it-does)
2. [Where it works](#where-it-works)
3. [Part of Live Track: the other modules](#part-of-live-track-the-other-modules)
4. [Before you start](#before-you-start)
5. [Install it, step by step](#install-it-step-by-step)
6. [Set it up, step by step](#set-it-up-step-by-step)
7. [Free keys that switch on more, step by step](#free-keys-that-switch-on-more-step-by-step)
8. [Put the map on a dashboard](#put-the-map-on-a-dashboard)
9. [Use it in automations](#use-it-in-automations)
10. [Everything on the map, in detail](#everything-on-the-map-in-detail)
11. [All the entities it creates](#all-the-entities-it-creates)
12. [What it sends and downloads](#what-it-sends-and-downloads)
13. [Help it grow](#help-it-grow)
14. [Languages](#languages)
15. [Credits and licences](#credits-and-licences)
16. [Keywords](#keywords)

---

## Everything it does

### On the map, with nothing to set up

You add a **railroad**: you choose a country or region, then one of its
commuter railroads. Everything below then appears for that railroad. Add the
integration again for each other railroad you want.

| What | Where | From |
|---|---|---|
| **Trains in service**: one marker per train, labelled with its train number or its line, in the railroad's own colours, turned to the direction it runs | every railroad | each railroad's own live feed |
| **Lateness**: a train shows as late or very late by the railroad's own rule, where the railroad publishes one | every railroad that reports delays | each railroad's own feed and timetable |
| **Next stop and its time**: the station a train calls at next, and when it is expected there | every railroad whose feed or timetable says so | each railroad's own feed and timetable |
| **Trains that follow the tracks**: between two positions a train slides along the line, not straight across | Finland, the Netherlands, Sweden | track files shipped with the integration or downloaded by it |
| **Equipment not in service**: empty trains moving between yards, shown while they move | railroads whose feeds report them | each railroad's own feed |
| **Two counts per railroad**: trains in service, and vehicles not in service | every railroad | the same feed |

### Switched on by your own free key or account

| Free key or account | What it adds |
|---|---|
| **Metra** key | Metra's trains (Chicago area, United States) |
| **Trafikverket** key | SL Pendeltåg, Västtågen's pendeltåg and Arlanda Express (Sweden) |
| **NS API portal** key | NS Sprinter trains (the Netherlands) |
| **Transport for NSW Open Data** key | NSW TrainLink Intercity trains (New South Wales, Australia) |
| **Transport Victoria Open Data** key | V/Line's commuter trains (Victoria, Australia) |

Each takes a few minutes to get: [step by step below](#free-keys-that-switch-on-more-step-by-step).
The other 26 railroads need no key.

---

## Where it works

| Region | What you get | From | Needs |
|---|---|---|---|
| **Australia**: New South Wales | NSW TrainLink Intercity: the Blue Mountains, Central Coast and Newcastle, Hunter, South Coast and Southern Highlands lines out of Sydney | Transport for NSW | a free key |
| **Australia**: Queensland | Queensland Rail Citytrain, South East Queensland (Brisbane) | Translink | nothing |
| **Australia**: South Australia | Adelaide Metro's trains: the Belair, Gawler, Outer Harbor and Seaford lines | Adelaide Metro | nothing |
| **Australia**: Victoria | V/Line's commuter trains: the Geelong, Ballarat, Bendigo, Seymour and Traralgon lines | Transport Victoria | a free key |
| **Australia**: Western Australia | Perth's trains, all nine lines, from the timetable only ([why](#perths-trains-western-australia-australia)) | Public Transport Authority of Western Australia | nothing |
| **Europe**: Finland | VR and HSL commuter trains around Helsinki | Fintraffic Digitraffic | nothing |
| **Europe**: Ireland | Irish Rail's commuter trains around Dublin and Cork | Irish Rail, National Transport Authority | nothing |
| **Europe**: Netherlands | NS Sprinter trains, the whole country | NS, OVapi | a free key |
| **Europe**: Norway | Vy's L1, L2 and L4 (Oslo area, Bergen), Go-Ahead Norge's L5 (Stavanger), Flytoget (Oslo Airport) | Entur | nothing |
| **Europe**: Spain | Renfe Cercanías and Rodalies de Catalunya, 15 networks: Madrid, Barcelona, Asturias, Sevilla, Cádiz, Málaga, Valencia, Murcia and Alicante, Cartagena, Ferrol, León, Bilbao, San Sebastián, Cantabria, Zaragoza | Renfe | nothing |
| **Europe**: Sweden | SL Pendeltåg (Stockholm), Västtågen's pendeltåg (Göteborg), Arlanda Express | Trafikverket | a free key |
| **North America**: United States | Metra (Chicago area: Illinois, Wisconsin) | Metra | a free key |
| **North America**: United States | South Shore Line (Chicago to South Bend: Illinois, Indiana) | NICTD, by way of ETA SPOT | nothing |

Not on the list? [Tell us](#help-it-grow). Where someone publishes the data
openly, we will look at adding it.

⚠ **A train is only as good as its railroad's feed.** Some railroads place
their trains on the timetable rather than by GPS, some report a train only at
signals a few minutes apart, and some feeds stop or freeze for a time. Each
railroad's limits are under [Everything on the map, in detail](#everything-on-the-map-in-detail).

⚠ **It is not the railroad's official information.** Before you travel, check
the railroad's own app or website.

---

## Part of Live Track: the other modules

Live Track is a set of Home Assistant integrations, one per kind of moving
thing, all drawn on the same map card. Each works on its own; together they
make one live picture. They share the map card and a Python library
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
so installing another one adds no requests to a source another already reads.

| Module | What it puts on the map | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aircraft overhead from ADS-B, with routes and type icons | released |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | ships and boats from AIS, near you or anywhere | released |
| **Live Track Commuter Rail** | commuter trains in North America, Europe and Australia (this module) | released |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity and long-distance trains in North America, Europe and Australia | released |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | immigration and federal law-enforcement aircraft and vessels, from public lists | released |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | weather, storms and natural hazards | released |
| Live Track Stations | departure boards and "time to leave" alerts for every station | planned |
| Live Track Satellites | satellites passing overhead | planned |
| Live Track Freight Trains | freight and work trains where railways publish them | planned |
| Live Track Transit | city buses, trams, ferries and metro | planned |
| Live Track Intercity Buses | intercity and regional coaches | planned |
| Live Track Commuter Buses | commuter buses | planned |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | the shared map card every module draws on | released, installed with each module |

Everything is free and open source. Nothing is held back for sponsors.

---

## Before you start

* **Home Assistant** 2026.11 or later.
* **The Marketplace** (HACS) in your Home Assistant, to install and update it
  the easy way. Without it you can copy the files by hand.
* **Internet access** for Home Assistant: every train comes from the
  railroad's own public feed.
* **Optional: auto-entities** from the Marketplace, to put the markers on the
  map (see [Put the map on a dashboard](#put-the-map-on-a-dashboard)).
* Nothing to pay. 26 of the 31 railroads need no
  account; the other five need a free key of your own ([above](#switched-on-by-your-own-free-key-or-account)).
* Home Assistant installs the Python packages it needs (`saw-livetrack`,
  `gtfs-realtime-bindings` and `tzdata`) by itself the first time the
  integration loads.

---

## Install it, step by step

### From the Marketplace (recommended)

Live Track Commuter Rail is not in the Marketplace's catalog yet. Add it by
its link:

1. In Home Assistant, open **Settings → Marketplace** (HACS).
2. Choose **Add from link** (or the three-dot menu → **Custom repositories**).
3. Enter `StrausbergAutomationWorks/LiveTrackCommuterRail`. If asked for the
   type, choose **Integration**.
4. Find **Live Track Commuter Rail** in the list and choose **Download** or
   **Install**.
5. **Restart Home Assistant**: **Settings → System → Repairs** offers the
   restart, or use **Settings → System → Restart**.

The Marketplace then offers each new release as an update.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Copy its `custom_components/live_track_commuter_rail` folder into the
   `custom_components` folder of your Home Assistant configuration folder
   (create `custom_components` if it is not there).
3. Restart Home Assistant.

To update by hand, replace the folder with the new release's and restart.

---

## Set it up, step by step

1. Open **Settings → Devices & services**.
2. Choose **Add integration** (bottom right) and search for **Live Track
   Commuter Rail**.
3. **Region**: choose the country, or the country and region, of the railroad.
   Only places with at least one railroad are listed. Choose **Submit**.
4. **Railroad**: choose the railroad. Choose **Submit**.
5. **API key**: only for Metra, the three Swedish railroads, NS Sprinter, NSW
   TrainLink Intercity and V/Line commuter. Paste your key
   ([how to get one](#free-keys-that-switch-on-more-step-by-step)) and choose
   **Submit**. The other railroads skip this step.

That is all. The trains appear within a minute. Where a railroad's next stops
come from its timetable, they fill in over the first minutes, once the
timetable has downloaded. To watch another railroad, add the integration
again. The same railroad twice is refused.

### Change what it shows: the options

Open **Settings → Devices & services → Live Track Commuter Rail → Configure**
(the cog) on the railroad you want to change. Every option, in plain words:

| Option | What it does | Default |
|---|---|---|
| **Poll interval** | how often the railroad's feed is read, 15 to 600 seconds. Most feeds refresh about every 30 seconds, so a shorter interval rarely shows more | 30 seconds |
| **Show parked equipment** | off: equipment not in service appears only while it moves, and leaves the map after 10 minutes standing. On: every vehicle in the feed is shown, parked trains included | off |

---

## Free keys that switch on more, step by step

Five railroads ask each user for their own key. Every one of these keys is
free, and each person who installs Live Track Commuter Rail gets their own.
You paste the key when the setup dialog asks for it
([step 5 above](#set-it-up-step-by-step)). Only the key is asked for: no
password and no secret. The key is stored in Home Assistant with the
integration and is never written to the log. If the railroad keeps refusing
it, Home Assistant asks you for a new one.

### Metra (Chicago area, United States)

1. Open <https://metra.com/developers> and scroll down to **GTFS Realtime API
   Key Request Form**.
2. Fill in **First Name**, **Last Name**, **Email Address** (it is asked
   twice) and **Purpose of Use** (for example: Home Assistant).
3. Tick **I have read and agree to the License Agreement.** (the agreement is
   at <https://metra.com/gtfs-realtime-api-key-request-license-agreement>)
   and choose **Submit**.
4. Paste the key you receive from Metra into **API key** when you add Metra.

### Trafikverket (Sweden: SL Pendeltåg, Västtågen, Arlanda Express)

1. Open <https://data.trafikverket.se/oauth2/Account/register>.
2. Fill in **Email**, **Displayname**, **Password** and **Confirm password**,
   tick **Accept license and Agreement**, and choose **Register**.
3. Open <https://data.trafikverket.se/get-started> and choose **Create key**,
   under **Create a key**. Sign in with the account you made, and create the
   key.
4. Paste it into **API key** when you add a Swedish railroad. One key serves
   all three.

### NS (the Netherlands)

1. Open <https://apiportal.ns.nl/>, choose **Inloggen** (sign in), then
   **Externe bezoeker** (external visitor).
2. Fill in the form and send it. An email confirms the registration. The APIs
   can take up to 5 minutes to appear in the portal.
3. Open the page of the **Virtual Train API** (NS's train positions). Under
   **Related Products**, open its product, give your subscription a name, and
   choose **Subscribe**.
4. When NS has approved the subscription, your key is on your profile page.
   Paste it into **API key** when you add NS Sprinter.

### Transport for NSW (New South Wales, Australia)

1. Open <https://opendata.transport.nsw.gov.au/>, choose **Register**, create
   an account, and log in.
2. Choose your user profile icon, then **API Tokens**.
3. Type a name for the key and choose **CREATE API TOKEN**. Copy the key at
   once: the site shows it only once.
4. Paste it into **API key** when you add NSW TrainLink Intercity. Paste the
   key alone: Live Track Commuter Rail adds the word `apikey` itself.

### Transport Victoria (Victoria, Australia)

1. Open <https://opendata.transport.vic.gov.au/>, choose **Login**, then
   **Sign up**.
2. Enter your details and choose **Create Account**. Enter the code from the
   email you receive and choose **Confirm**.
3. The portal asks for an authenticator app on your phone: scan the QR code
   with it, enter the app's code and choose **Confirm**. Then sign in with
   your email, your password and the app's code.
4. Choose **My Account** → **Profile** → **API tokens**. Your key is already
   there. Paste it into **API key** when you add V/Line commuter.

---

## Put the map on a dashboard

The map is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
the card every Live Track module draws on. **It is installed with Live Track
Commuter Rail**: nothing to download, nothing to copy, no resource to add.

1. Open a dashboard, choose the pencil (**Edit dashboard**), then **Add card**.
2. Scroll to the bottom and choose **Manual**.
3. Paste this, and choose **Save**:

```yaml
type: custom:auto-entities
card:
  type: custom:live-track-map-card
filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_commuter_rail
      options:
        display: attribute
        attribute: marker_label
        position_transition: auto
  exclude:
    - state: unavailable
```

The markers need [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
from the Marketplace. With other Live Track modules installed, add one more
`- domain: geo_location` filter for each of their sources
(`live_track_intercity_rail`, `live_track_aircraft` and so on).

**On the map:**

* Each train is a disc in its line's or railroad's colours, labelled with its
  train number or line. On most railroads the colours swap with the
  direction: filled leaving the main city, white toward it.
* An arrow shows the direction the train runs. A train standing still keeps
  its last direction.
* **Point at** a train to see its railroad, number or line, and where it runs.
  **Click** it for all its details, its next stop and its delay included.

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you: a **Repairs** issue then gives the exact
lines to add to `configuration.yaml`. They look like this, with the
integration's own address in place of the placeholders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_commuter_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Every Live Track module carries a copy of the card and registers it when Home
Assistant starts. Together they keep exactly one row in **Settings →
Dashboards → Resources**: the newest card version any of them carries, never
an older one. A card you installed yourself through the Marketplace is left
alone. When you remove this module's last railroad, the row passes to another
Live Track module, or is removed if none is left. If the integration's files
are removed while its railroads are still set up, and no other Live Track
module is installed, remove the row yourself in **Settings → Dashboards →
Resources**.

**To install the card by hand instead**, follow the steps in the
[card's README](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
A row you made yourself for a copy under `/local/` is pointed at this
module's copy only when this module's copy is a newer release.

Any other map card that shows `geo_location` entities shows the trains too,
as plain markers.

---

## Use it in automations

Everything is an ordinary Home Assistant entity, so the automation editor
works with it, no code needed.

**A phone notification when your railroad shows almost no trains** (the
feed may have stopped, or service may be disrupted):

1. **Settings → Automations & scenes → Create automation → Create new
   automation**.
2. **When**: **Add trigger** → **Entity** → **Numeric state crossed
   threshold**. Choose the railroad's **Trains in service** entity, and
   **Below** `3`.
3. **Then do**: **Add action**, search for your phone's notification action
   (it carries your phone's name), and enter a message, for example:

   ```text
   Almost no trains on the map: check the railroad's own app
   ```

4. **Save**.

**Other ideas:** a light that turns on when a train is within 1 km (0.6 miles)
of your home in Stockholm (Sweden), from the markers' distance; a
dashboard count of Metra trains in service at the morning peak (Chicago,
United States); a message when the first train of the day runs in Brisbane
(Australia), from **Trains in service** rising above 0.

---

## Everything on the map, in detail

### Trains, and equipment not in service

Each train is one marker. Its state is its distance from your home, in
kilometres. The marker appears when the railroad's feed reports the train and
is removed when the train leaves the feed (after 3 minutes, so a short gap in
the feed does not remove it).

* **A train in service** is labelled with its train number or its line, as
  the railroad numbers them (each railroad below says which).
* **Equipment not in service** is labelled `NIS` and its unit number, so a
  unit number is never mistaken for a train number. It is shown only while it
  moves, and leaves the map after 10 minutes standing. Turn on **Show parked
  equipment** to see every vehicle in the feed.
* **Between two positions** the map card moves the marker from one real
  position to the next. Nothing is invented past the last real position.
* **A position that is not on a railway is refused.** A train reported away
  from the tracks is shown at its last position that was on them, for up to
  10 minutes, then hidden until it is back. A train first seen away from the
  tracks is not shown.
* **Late and very late**: where the railroad publishes its own rule for a
  late train, the integration uses it, and says so below.

On each train: `marker_label`, `observed_at` (when its position was true),
`course_deg` (while it moves), `next_stop` and `arrival_estimated_at` (where
known), `delay_min`, `stalled`, `attribution`, and, between two positions,
`previous_latitude`, `previous_longitude`, `previous_observed_at` and
`segment_duration_s`. A position the integration estimated, rather than one
the railroad reported, carries `position_source: estimated`.

### NSW TrainLink Intercity (New South Wales, Australia)

From Transport for NSW's NSW TrainLink and Sydney Trains feeds, with your own
key. A run in both feeds is one marker. The label is the line code (BMT, CCN,
HUN, SCO, SHL); the run and its ends are in the hover box ("Train KN56 ·
Bomaderry–Kiama"). The line's timetable colour, filled leaving Sydney Central
and swapped going to it. Empty trains are `NIS` and their run, in grey. The
next stop is a station, never a platform. ⚠ A position more than 10 minutes
old is not drawn, and a train is removed when its run is over. Late from 6
minutes (Transport for NSW's Intercity measure), very late from 12.

### Queensland Rail Citytrain (Queensland, Australia)

From Translink's open feed. ⚠ Positions are fixed points on the track, not
GPS, with no speed and no direction; the arrow follows the train's route in
the timetable. A position more than 5 minutes old is refused, because the feed
keeps a train whose position froze until the end of the service day. The
label is the line's T number in Translink's line colours, swapped for trains
heading south, and a star for special runs with no T number. Late from 4
minutes, 6 on the Gold Coast, Rosewood and Sunshine Coast lines (Queensland
Rail's own rule).

### Adelaide Metro (South Australia, Australia)

From Adelaide Metro's open feed, which also carries its trams and buses (not
drawn here). Positions are GPS, with the train's own direction. Adelaide
publishes no train number, so the label is the first three letters of the
route code Adelaide Metro uses (SEA, FLN, GAW, BEL, OUT and so on); the hover
box gives the full code ("SEAFRD to Seaford · railcar 4006"). The colours are
the rail network map's: Belair green, Seaford and Flinders orange, Gawler red,
Outer Harbor, Port Dock and Grange blue; filled leaving the City, white toward
Adelaide Railway Station. A position more than 5 minutes old, or more than
1 km from every Adelaide rail route, is refused. Late from 5 minutes (Adelaide
Metro's own rule), very late from 10.

### V/Line commuter (Victoria, Australia)

From Transport Victoria's V/Line feed, with your own key. The label is the
line code (GEL, BAT, BGO, SER, TRN); the train number and line are in the
hover box ("Train 8037 · Bendigo - Melbourne via Gisborne"). Every line is
V/Line purple: filled leaving Melbourne, white toward Southern Cross. ⚠ V/Line's
positions follow the timetable more than the train: a trip leaves the feed
about a minute after its scheduled arrival wherever the train is, and positions
freeze around midnight. So a train keeps its last position for up to 10
minutes and then leaves the map, and a late train can disappear before its
last station. Late from 6 minutes (V/Line's rule for commuter services), very
late from 12.

### Perth's trains (Western Australia, Australia)

⚠ **Perth publishes no live positions.** Every train is drawn from the
timetable of the Public Transport Authority of Western Australia: placed along
its route by its scheduled times, marked as an estimate, with no delay. The
timetable is checked once a day. The label is the line's first three letters
(MAN, YAN, ARM, FRE, MID, ELL, AIR, THO; STA for a Stadium Special); the hover
box reads "Mandurah Line · Perth Underground–Mandurah". The colours are the
network map's: filled leaving Perth, white toward it.

### VR and HSL commuter trains (Finland)

From Fintraffic's Digitraffic. A train is a run: its train number and the day
it started. The label is the line letter, coloured as HSL's maps and station
signs colour the lines: HSL purple while the next stop is in HSL's fare zones
A to E, VR green outside them. A train heading away from Helsinki is a filled
disc; one heading toward it is white. A train is shown from its first station
to its last stop, then removed. Line V runs that carry no passengers are shown
as `NIS` while they move. Between two positions a train slides along the
tracks. Lines I and P report no position in the Ring Rail tunnel at Helsinki
Airport, so there the integration moves the train along the tracks by its
timetable until a real position comes back. Late from 4 minutes (VR's rule),
very late from 8. A position over 10 minutes old is refused.

### Irish Rail (Ireland)

From Irish Rail's live service, with the National Transport Authority's
timetable for routes and stations. ⚠ Irish Rail reports a train only as it
passes signals a few minutes apart, so each train is drawn from its timetable
and its latest delay, moved along its route; Cork's trains, which Irish Rail
does not track, come from the timetable alone. The label is the train number
without its letter (P508 shows 508). The colour is the line's on Transport for
Ireland's network map, swapped toward Dublin or Cork. Late from 5 minutes
(Irish Rail's own rule), very late from 10.

### NS Sprinter (the Netherlands)

From NS's vehicle data, with your own key. The label is the train number; the
hover box reads "Sprinter 6632 · Dordrecht–Arnhem Centraal". NS yellow with an
NS blue ring. This is the one feed here that reports a train's own speed and
direction, and both are passed on (`speed_kmh`, `course_deg`). The next stop
and the delay come from OVapi's timetable. The track is NS's SpoorKaart,
downloaded once a day; a train slides along it between positions, and a
position more than 1 km from it is refused. Late from 3 minutes (NS's own
definition), very late from 10.

### Vy, Go-Ahead Norge and Flytoget (Norway)

From Entur, each railroad its own entry. The label is the line code (L1, L2,
L4, L5, FLY1, FLY2); the train number and line name are in the hover box. An L
line wears its timetable colour, filled leaving Oslo S (Bergen on L4,
Stavanger on L5) and swapped toward it. Flytoget is grey with an orange ring
toward Oslo Airport, and orange with a grey ring leaving it. Entur publishes no
speed and no direction, so the arrow follows the train's line. In Oslo's long
tunnels a train whose positions stop is moved along its line until they come
back. Late from 4 minutes, very late from 8.

### Renfe Cercanías and Rodalies (Spain)

From Renfe's open feed, each of the 15 networks its own entry. The label is
the line (C5, R2N) in the line's own colour from Renfe's timetable. The train
number and line name are in the hover box. ⚠ Renfe places its trains on their
route rather than by GPS, so they stand, then jump. A train moves only forward
along its own line: a position off it, back along it or impossibly fast is
refused, and the last good one kept for up to 10 minutes. A train is called
stalled only after 6 minutes in one place. Renfe publishes no rule for a late
train, so the map card's own thresholds apply.

### SL Pendeltåg, Västtågen and Arlanda Express (Sweden)

From Trafikverket, with your own free key (one key for all three). The label
is the train number; the brand, number and end stations are in the hover box.
SL Pendeltåg is pink, Västtågen light blue, Arlanda Express yellow; each swaps
its colours toward Stockholm C (Stockholm City for the pendeltåg) or, on a trip
that calls at neither, toward its larger end city. Between two positions a
train slides along its trip's line, and a position more than 1 km from it is
refused. Late from 3 minutes on SL Pendeltåg (Region Stockholm's rule), very
late from 6; late from 6 and very late from 12 on the other two
(Trafikverket's rule).

### Metra and the South Shore Line (United States)

Metra from its own feed, with your own key; the South Shore Line from the feed
ETA SPOT publishes for NICTD, with no key. The label is the train number. Metra
names the next stop and its time. The South Shore Line's feed gives only a stop
number and a delay, so its timetable supplies the station and the time. A
position more than 300 m from any railway in the North American Rail Network
(United States), or from the railroad's own route, is refused. ⚠ Metra's feed
has, on some days, attributed few of its trains to a trip; the rest then show
as `NIS` or not at all, and the map looks like a quiet day. The
**Trains in service** count shows such days afterwards.

---

## All the entities it creates

For each railroad:

| Entity | What it is |
|---|---|
| `sensor.<railroad>_trains_in_service` | **Trains in service**: how many trains in service the railroad's feed reports now. For Metra: `sensor.metra_chicago_area_trains_in_service` |
| `sensor.<railroad>_vehicles_not_in_service` | **Vehicles not in service**: how many vehicles the feed reports that are not in service |
| `geo_location.<railroad>_unit_…` | one per train or vehicle (`geo_location.metra_unit_8426`); it comes and goes with the train. Each carries `source: live_track_commuter_rail`, and its state is its distance from your home in kilometres |

Each railroad runs a known fleet. A marker's entity ID comes from the railroad
and the vehicle's number in the feed, never from its label, so the same
vehicle gets the same entity ID each time it appears:
`geo_location.metra_unit_8426` is always Metra's railcar 8426. The marker is
removed when the vehicle leaves the feed, or after 10 minutes parked while
**Show parked equipment** is off. The markers have no unique ID, as no Live
Track map marker has, so they cannot be renamed, hidden or given an area in
the interface. The two sensors have a unique ID and can be renamed.

Attributes that change at every poll, the markers' positions and times, are
recorded in Home Assistant's history, as for any entity. The two sensors have
no attributes, so they cost little to keep, and they are the record of how
many trains ran on a day. To keep the markers out of history, add this to
`configuration.yaml`, then restart:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_unit_*
```

If your `configuration.yaml` already has a `recorder:` section, add only the
pattern `geo_location.*_unit_*` to it, under `exclude:` and `entity_globs:`.
The pattern matches this module's train markers only. A map card set to draw
history then has no trail to draw.

---

## What it sends and downloads

**About your location.** Nothing. Your home's position is used only inside
your Home Assistant, to give each train's distance. Your key, where a railroad
needs one, is sent only to that railroad. Nothing else about you is sent
anywhere. Each service sees your internet address, as any website does.

**How much.** Each live feed is read at each poll, every 30 seconds by default
(**Poll interval**, 15 to 600 seconds), or less often where the table says so.
Where several Live Track modules read the same feed, one shared client reads
it once for all of them. Measured on 19 November 2026, 02:20 to 02:40 UTC:

| Railroad | Live feed, one read | Timetable |
|---|---|---|
| NSW TrainLink Intercity (Australia) | 402 KB from four feeds, at most once every 55 seconds | 51 MB (two timetables), when changed, checked daily |
| Queensland Rail Citytrain (Australia) | 141 KB | 42 MB, every day |
| Adelaide Metro (Australia) | 298 KB | 20 MB, when Adelaide Metro publishes a new version |
| V/Line commuter (Australia) | 14 KB | 59 MB, when changed, checked daily |
| Perth's trains (Australia) | none: Perth publishes no live feed | 28 MB, when changed, checked daily |
| VR and HSL commuter trains (Finland) | 1.1 KB compressed for the positions, plus the changes to the day's trains once a minute | none as a file: the day's trains come with the live data |
| Irish Rail (Ireland) | 0.2 KB, at most once every 55 seconds | 6.6 MB, when changed, checked daily; the station list, 18 KB, once a week |
| NS Sprinter (the Netherlands) | 1.2 KB; delays from OVapi, 1.6 MB, every 5 minutes and only when changed | OVapi's timetable, 274 MB, at most once a week and only when changed; NS's track map, 1.3 MB, every day |
| Vy, Go-Ahead Norge, Flytoget (Norway) | Vy 497 KB, Go-Ahead Norge 7 KB, Flytoget 233 KB | Vy 67 MB, Go-Ahead Norge 20 MB, Flytoget 0.6 MB, when changed, checked daily |
| Renfe Cercanías and Rodalies (Spain) | one feed for all 15 networks: 26 bytes, at night with no trains running | 16 MB, every day |
| SL Pendeltåg, Västtågen, Arlanda Express (Sweden) | 3.7 KB the first time, then about 2 KB of changes | none; the station list, 0.15 MB, every day |
| Metra (United States) | 18 KB | 0.4 MB, every day |
| South Shore Line (United States) | under 1 KB | 0.14 MB, every day |

⚠ When this was measured it was day in Australia, evening in the United
States and night in Europe. A live feed is at its smallest at night: in the
day the European feeds are larger than the table shows.

**After an error.** The last good positions are shown for two more failed
reads; then the trains are marked unavailable until the feed answers. A
timetable that fails to download is tried again an hour later, and the copy
you have stays in use. If the railroad keeps refusing your key, Home
Assistant asks for a new one.

**On disk.** The timetables are kept in Home Assistant's `.storage` folder
under names beginning `saw_`, shared with the other Live Track modules that
read the same railroad: those marked "when changed" as downloaded, the others
as a smaller extract. If you remove Live Track Commuter Rail and no other Live
Track module uses them, you can delete them by hand.

---

## Help it grow

Live Track Commuter Rail is still growing. We add railroads and countries as
we find them, and we want to know what you would like next.

### Suggest something

Is your country or railroad missing? Is something wrong, or hard to
understand? Tell us whichever way is easier for you:

* [**Fill in a short form**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=en.yml)
  in English. You need a free GitHub account.
* **Write an email** to
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No account needed.

Either way, it helps to tell us:

* what you would like to see, and where in the world;
* a link to where the data is published, if you know one (an open-data page,
  a public feed, a service's website): not needed, but it helps;
* your Home Assistant language, if the problem is the wording or a
  translation.

Write in English or in your own language, whichever is easier for you.

### Add it yourself, with our help

If you would like to add something yourself, we will help you do it, from
the first question to the finished release. You do not need to be a
developer to start:

* **A translation.** The words in the setup dialog are a short list of
  phrases in one text file. We will show you which file and which lines.
* **A new railroad.** Tell us where the data is published. We can write the
  code together, or look over yours.
* **Testing where you live.** Install it, look at your part of the map, and
  tell us what is right and what is not.
* **A fix to this README.** If a step did not match what you saw, tell us
  what you saw.

[**Tell us what you have in mind**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=en.yml)
or write to
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
and we will reply with the next steps.

---

## Languages

This README: **English**, [Suomi](README.fi.md), [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), [Español](README.es.md),
[Nederlands](README.nl.md), [Gaeilge](README.ga.md). Each translated README
is complete. None has yet been read by a native speaker. If one of these
languages is yours, please tell us whether its README reads well: see
[Help it grow](#help-it-grow).

The setup dialog and the options appear in your Home Assistant language when
it is one of these: English, Suomi, Svenska, Norsk bokmål, Español,
Nederlands, Gaeilge. Any other language shows English.

Found a mistake in a translation, or need another language? Tell us at
<https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues>, or
[translate it with our help](#add-it-yourself-with-our-help).

---

## Credits and licences

Every railroad is read at runtime, by your Home Assistant, from its own
published feed; nothing from a live feed is in this repository. Each train
credits its source in its `attribution` attribute. Each railroad's terms bind
you, as the person receiving its data.

* **Metra** (United States): GTFS-Realtime, under
  [Metra's licence agreement](https://metra.com/gtfs-realtime-api-key-request-license-agreement),
  which you accept when you ask for a key.
* **South Shore Line** (NICTD, United States): public feed and timetable
  published for NICTD by ETA SPOT, with no key and no licence agreement.
* **Translink** (Queensland Government, Australia): data under CC BY 4.0
  ([open data](https://translink.com.au/about-translink/open-data)).
* **Fintraffic / digitraffic.fi** (Finland): data under CC BY 4.0. **HSL**
  (Finland): fare zones, CC BY 4.0.
* **Renfe** (Spain): data under CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)), modified.
* **Entur** (Norway): data under the Norwegian licence for Open Government
  data ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)), distributed by Entur.
* **Trafikverket** (Sweden): data under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Ireland): live data; Irish Rail publishes no terms. Timetable
  from the [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Ireland), CC BY 4.0.
* **NS** (the Netherlands): vehicle data, with your own key, from the
  [NS API portal](https://apiportal.ns.nl/). Timetable and delays from
  [OVapi](https://gtfs.ovapi.nl), CC0.
* **Transport for NSW** (Australia): data under CC BY 4.0
  ([data licence](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australia): data under CC BY 4.0
  ([open data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Adelaide Metro**, Department for Infrastructure and Transport, South
  Australia: data under CC BY 4.0 ([developer information](https://www.adelaidemetro.com.au/developer-info)).
* **Public Transport Authority of Western Australia**: timetable data
  available free of charge from www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access)).
* **Track files shipped in `rail/`**: the North American Rail Network (United
  States Department of Transportation), public domain; Fintraffic's track
  network, CC BY 4.0, modified; Flytoget's lines from Entur's data, NLOD 2.0,
  modified; Sweden's lines routed on OpenStreetMap, (c) OpenStreetMap
  contributors, ODbL 1.0; Statistics Sweden's city populations, CC0. What was
  changed is listed in [ATTRIBUTION.md](ATTRIBUTION.md).
* **The map card** is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, a copy of [ha-map-card](https://github.com/nathan-gs/ha-map-card) by
  nathan-gs, MIT. Its map tiles and their credits are in its README.

None of these organisations made or endorsed this integration.

**Code**: MIT, in [LICENSE](LICENSE).

**For developers:** each railroad is one adapter in
`custom_components/live_track_commuter_rail/operators/`; the track files in
`rail/` are rebuilt with the scripts in `tools/` (`build_rail.py`,
`build_tracks.py`, `build_flytoget_lines.py`, `sweden_lines.py`). The tests run
with `python -m unittest discover -s tests`.

---

## Keywords

Home Assistant trains · Home Assistant train tracker · live train map ·
commuter rail · suburban rail · regional rail · GTFS-Realtime · Metra ·
South Shore Line · Renfe Cercanías · Rodalies · trenes en tiempo real ·
lähijunat · junat kartalla · HSL · VR · pendeltåg · tåg i realtid · Vy ·
Flytoget · tog i sanntid · NS · Sprinter · treinen live · Irish Rail ·
traenacha beo · Queensland Rail · Translink · NSW TrainLink · V/Line ·
Adelaide Metro · Perth trains · geo_location · map card · Lovelace · HACS ·
Marketplace · Live Track · LiveTrack · StrausbergAutomationWorks

---

**Acknowledgement.** StrausbergAutomationWorks acknowledges the Indigenous
peoples of every land and water on this map, all over the world, and pays its
respect to their Elders, past and present.
