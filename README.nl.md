# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk](README.nb.md) · [Español](README.es.md) · **Nederlands** · [Gaeilge](README.ga.md)

Treinen live op je Home Assistant-kaart. Live Track Commuter Rail is een Home
Assistant-integratie (custom component, te installeren via de Marketplace /
HACS) die elke trein toont van de spoorwegen die je kiest, in realtime: waar de
trein is, het treinnummer en de lijn, of hij vertraging heeft, de volgende
halte en wanneer hij daar verwacht wordt. De posities komen uit de open data
van elke vervoerder. Elke trein is een `geo_location`-entiteit en beweegt mee
als de bron wordt bijgewerkt.

## In Nederland: NS Sprinter

**NS Sprinter**, de stoptreinen van NS. Data: NS ([apiportal.ns.nl](https://apiportal.ns.nl/)),
met je eigen sleutel: maak een account aan op het NS API-portaal. Dienstregeling
en vertragingen: OVapi (gtfs.ovapi.nl), CC0. Het spoor: NS SpoorKaart, dat de
integratie zelf dagelijks ophaalt; tussen twee posities schuift een trein over
het spoor van SpoorKaart. Een positie meer dan 1 km van het spoor wordt
geweigerd.

* Het label is het treinnummer; bij aanwijzen staat er bijvoorbeeld
  "Sprinter 6632 · Dordrecht–Arnhem Centraal". NS-geel met een NS-blauwe rand.
* NS meldt zelf de snelheid en de rijrichting van de trein; beide worden
  doorgegeven. De positie heeft geen tijd, dus `observed_at` is de eerste
  ophaalronde die haar zag.
* Te laat vanaf 3 minuten (de definitie van NS), flink te laat vanaf 10.

## Alle spoorwegen

Metra en South Shore Line (Chicago), Renfe Cercanías en Rodalies (Spanje),
VR lähijunat (Finland), Vy, Go-Ahead Norge en Flytoget (Noorwegen), SL
Pendeltåg, Västtågen en Arlanda Express (Zweden), NS Sprinter (Nederland), Irish
Rail (Ierland), Queensland Rail Citytrain, NSW TrainLink Intercity, V/Line en Adelaide Metro (Australië). Sleutels en voorwaarden: [de tabel in de Engelse
README](README.md#supported-railroads).

## Onderdeel van Live Track

Live Track is een systeem van modules voor Home Assistant. Elke module volgt één
soort ding dat beweegt, en alle modules tekenen op dezelfde kaart. Ze delen één
Python-bibliotheek ([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
en één dashboardkaart voor de kaart ([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)),
dus een extra module stuurt geen extra verzoeken naar een gedeelde bron zoals
NS. Uitgebracht: Live Track Commuter Rail,
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)
en [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT).
In ontwikkeling: Live Track Intercity Rail, Live Track Ships en Live Track
Weather.

## Vereisten

- Home Assistant 2026.11 of nieuwer.
- Een eigen sleutel van het NS API-portaal.
- Home Assistant installeert de benodigde Python-pakketten de eerste keer dat de
  integratie laadt.

## Installatie

### Via de Marketplace

De integratie staat nog niet in de catalogus van de Marketplace. Voeg hem toe
via een link:

1. **Settings > Marketplace** en **Add from link**.
2. Vul `StrausbergAutomationWorks/LiveTrackCommuterRail` in. Kies
   **Integration** als om het type wordt gevraagd.
3. Installeer **Live Track Commuter Rail**.
4. Herstart Home Assistant. De Marketplace biedt de herstart aan als reparatie
   onder **Settings > System > Repairs**.

### Handmatig

1. Download de broncode van de [laatste
   release](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Kopieer de map `custom_components/live_track_commuter_rail` naar de map
   `custom_components` in de configuratiemap van Home Assistant.
3. Herstart Home Assistant.

## Instellen

**Settings > Devices & services > Add integration > Live Track Commuter Rail**.
Kies de regio, dan de spoorweg, en vul je sleutel in. Het venster en de namen van de regio's verschijnen in het
Nederlands als Home Assistant op Nederlands staat. De menunamen hierboven zijn
die van de Engelse interface.

## Data en licentie

De treinen worden tijdens het draaien rechtstreeks uit de bron van elke
vervoerder gelezen; deze repository bevat geen data uit die bronnen. Het
attribuut `attribution` van elke trein noemt de bron. De spoor- en lijnbestanden
die worden meegeleverd en hun licenties: [ATTRIBUTION.md](ATTRIBUTION.md).
Code: MIT.

Deze integratie wordt niet gesponsord door, is niet verbonden aan en wordt niet
beheerd door een van de vervoerders. Alle details: [README in het
Engels](README.md).

## Zoektermen

Home Assistant treinen op de kaart · treinen live · treinposities · NS Sprinter ·
NS API · OVapi · SpoorKaart · treinkaart · GTFS-Realtime · HACS-integratie
