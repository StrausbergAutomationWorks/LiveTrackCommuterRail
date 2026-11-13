# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · **Svenska** · [Norsk](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md)

Pendeltåg och närtåg i realtid på din Home Assistant-karta. Live Track Commuter
Rail är en Home Assistant-integration (custom component, installeras via
Marketplace / HACS) som visar varje tåg på de pendeltågsbanor du väljer, i
realtid: var tåget är, dess tågnummer och linje, om det är försenat, nästa
station och när det väntas dit. Positionerna kommer från varje järnvägs egen
öppna datakälla. Varje tåg blir en `geo_location`-entitet och flyttas när
källan uppdateras.

## I Sverige: SL Pendeltåg, Västtågen och Arlanda Express

**SL Pendeltåg** (Stockholmsområdet, till Uppsala, Bålsta, Gnesta och
Nynäshamn), **Västtågens pendeltåg** (Göteborg till Kungsbacka, Älvängen, Floda
och Alingsås) och **Arlanda Express** (Stockholm C till Arlanda). Data:
Trafikverket (trafikverket.se), CC0. Du behöver en egen, kostnadsfri nyckel:
registrera dig på [data.trafikverket.se](https://data.trafikverket.se/oauth2/Account/register).
En nyckel räcker för alla svenska banor.

* Markören bär tågnumret; varumärke, nummer och ändstationer syns när du håller
  över den. SL Pendeltåg är rosa, Västtågen ljusblå och Arlanda Express gul;
  färgerna byts mot Stockholm C (Stockholm City för pendeltågen).
* SL Pendeltåg är försenat från 3 minuter och mycket försenat från 6; de andra
  två från 6 och 12 minuter (Trafikverkets regel).
* Sverige publicerar inga linjeformer, så linjen mellan varje stationspar följer
  med integrationen, dragen på OpenStreetMaps spår ((c) OpenStreetMap
  contributors, ODbL 1.0). Ett tåg glider längs sin linje mellan positionerna.

## I Finland: VR:s och HSL:s närtåg

**VR lähijunat**, närtågen i Helsingforsregionen. Data: Fintraffic /
digitraffic.fi, CC BY 4.0. Ingen nyckel behövs. Markören bär linjebokstaven, i
HSL:s lila inom HSL:s zoner A–E och i VR:s gröna utanför dem. Försenat från 4
minuter, mycket försenat från 8. I Ringbanans flygplatstunnel, där linjerna I
och P inte rapporterar någon position, flyttar integrationen själv tåget längs
spåret tills en riktig position kommer tillbaka.

## Alla banor

Metra och South Shore Line (Chicago), Renfe Cercanías och Rodalies (Spanien),
VR lähijunat (Finland), Vy, Go-Ahead Norge och Flytoget (Norge), SL Pendeltåg,
Västtågen och Arlanda Express (Sverige), NS Sprinter (Nederländerna), Irish
Rail (Irland), Queensland Rail Citytrain, NSW TrainLink Intercity, V/Line och Adelaide Metro (Australien). Nycklar och villkor: [tabellen i den engelska
README-filen](README.md#supported-railroads).

## En del av Live Track

Live Track är ett system av moduler för Home Assistant. Varje modul följer en
sorts sak som rör sig, och alla moduler ritar på samma karta. De delar ett
Python-bibliotek ([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
och ett kartkort ([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)),
så en modul till lägger inte till frågor mot en delad källa som Trafikverket.
Släppta: Live Track Commuter Rail,
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)
och [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT).
Under utveckling: Live Track Intercity Rail, Live Track Ships och Live Track
Weather.

## Krav

- Home Assistant 2026.11 eller senare.
- För svenska banor: Trafikverkets kostnadsfria nyckel (ovan). Finland behöver
  ingen.
- Home Assistant installerar de Python-paket som behövs första gången
  integrationen laddas.

## Installation

### Från Marketplace

Integrationen finns inte i Marketplace-katalogen än. Lägg till den via länk:

1. **Settings > Marketplace** och **Add from link**.
2. Ange `StrausbergAutomationWorks/LiveTrackCommuterRail`. Välj
   **Integration** om typen efterfrågas.
3. Installera **Live Track Commuter Rail**.
4. Starta om Home Assistant. Marketplace erbjuder omstarten som en reparation
   under **Settings > System > Repairs**.

### För hand

1. Ladda ner källkoden för [den senaste
   versionen](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Kopiera mappen `custom_components/live_track_commuter_rail` till mappen
   `custom_components` i Home Assistants konfigurationskatalog.
3. Starta om Home Assistant.

## Inställning

**Settings > Devices & services > Add integration > Live Track Commuter Rail**.
Välj region, sedan bana, och ange nyckeln om banan kräver en. Dialogen och regionernas namn visas på svenska när Home
Assistant är inställt på svenska. Menynamnen ovan är det engelska
gränssnittets.

## Data och licens

Tågen läses vid körning direkt från varje banas källa; inget från källorna finns
i det här repot. Varje tågs attribut `attribution` anger källan. De spår- och
linjefiler som följer med, och deras licenser: [ATTRIBUTION.md](ATTRIBUTION.md).
Kod: MIT.

Integrationen är inte sponsrad av, ansluten till eller driven av någon av
banorna. Alla detaljer: [README på engelska](README.md).

## Sökord

Home Assistant tåg på kartan · pendeltåg i realtid · tågpositioner · SL
Pendeltåg karta · Västtågen · Arlanda Express · Trafikverket API · närtåg
Helsingfors · VR · HSL · HACS-integration
