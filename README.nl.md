# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Español](README.es.md) · **Nederlands** · [Gaeilge](README.ga.md) · [Alle talen](#talen)

**Forensentreinen voor Home Assistant, op één kaart.** Live Track Commuter
Rail zet elke trein van de forensenspoorwegen die je kiest live op je Home
Assistant-kaart: waar hij is, zijn treinnummer of lijn, of hij vertraging
heeft, en zijn volgende halte. Elke spoorweg voeg je apart toe, uit zijn eigen
open data.

> **Live Track Commuter Rail is een module van Live Track**, een familie Home
> Assistant-integraties die alles wat beweegt, en het weer waar het doorheen
> beweegt, op één gedeelde kaart tekenen: vliegtuigen, schepen, treinen en
> weer. Installeer het los, of naast de andere modules
> ([lijst hieronder](#onderdeel-van-live-track-de-andere-modules)).

> **Groeiend, en open voor ideeën.** Live Track Commuter Rail dekt vandaag 31
> spoorwegen in 8 landen op 3 continenten, en we voegen meer spoorwegen en
> landen toe. Ontbreekt de jouwe? [Stel hem voor](#help-het-groeien), of voeg
> hem zelf toe: we helpen je daarbij.

**Status: 0.1.6, uitgebracht.** In de catalogus van de Marktplaats ([installeer
het hieronder](#installeren-stap-voor-stap)).

Origineel werk van StrausbergAutomationWorks. Niet verbonden aan, of
onderschreven door, Metra, het Northern Indiana Commuter Transportation
District (NICTD), ETA SPOT, Renfe, Fintraffic, HSL, VR, Entur, Vy, Go-Ahead
Norge, Flytoget, Trafikverket, SL, Västtågen, Arlanda Express, Irish Rail, de
National Transport Authority (Ierland), NS, OVapi, Translink, Queensland Rail,
Transport for NSW, Transport Victoria, V/Line, Adelaide Metro, de Public
Transport Authority van West-Australië, of enige andere spoorweg.

---

## Inhoud

1. [Alles wat het doet](#alles-wat-het-doet)
2. [Waar het werkt](#waar-het-werkt)
3. [Onderdeel van Live Track: de andere modules](#onderdeel-van-live-track-de-andere-modules)
4. [Voordat je begint](#voordat-je-begint)
5. [Installeren, stap voor stap](#installeren-stap-voor-stap)
6. [Instellen, stap voor stap](#instellen-stap-voor-stap)
7. [Gratis sleutels die meer aanzetten, stap voor stap](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap)
8. [De kaart op een dashboard zetten](#de-kaart-op-een-dashboard-zetten)
9. [Gebruiken in automatiseringen](#gebruiken-in-automatiseringen)
10. [Alles op de kaart, in detail](#alles-op-de-kaart-in-detail)
11. [Alle entiteiten die het aanmaakt](#alle-entiteiten-die-het-aanmaakt)
12. [Wat het verstuurt en downloadt](#wat-het-verstuurt-en-downloadt)
13. [Help het groeien](#help-het-groeien)
14. [Talen](#talen)
15. [Bronvermelding en licenties](#bronvermelding-en-licenties)
16. [Trefwoorden](#trefwoorden)

---

## Alles wat het doet

### Op de kaart, zonder iets in te stellen

Je voegt een **spoorweg** toe: je kiest een land of regio, en dan een van zijn
forensenspoorwegen. Alles hieronder verschijnt dan voor die spoorweg. Voeg de
integratie opnieuw toe voor elke andere spoorweg die je wilt.

| Wat | Waar | Van |
|---|---|---|
| **Treinen in dienst**: één marker per trein, met zijn treinnummer of zijn lijn, in de eigen kleuren van de spoorweg, gedraaid in de richting waarin hij rijdt | elke spoorweg | de eigen livefeed van elke spoorweg |
| **Vertraging**: een trein staat als vertraagd of sterk vertraagd volgens de eigen regel van de spoorweg, waar de spoorweg er een publiceert | elke spoorweg die vertragingen meldt | de feed en dienstregeling van elke spoorweg |
| **Volgende halte en tijd**: het station waar de trein hierna stopt, en wanneer hij daar wordt verwacht | elke spoorweg waarvan de feed of dienstregeling dat zegt | de feed en dienstregeling van elke spoorweg |
| **Treinen die het spoor volgen**: tussen twee posities glijdt een trein langs de lijn, niet in een rechte lijn | Finland, Nederland, Zweden | spoorbestanden die met de integratie meekomen of die zij downloadt |
| **Materieel buiten dienst**: lege treinen tussen opstelterreinen, getoond zolang ze rijden | spoorwegen waarvan de feed ze meldt | de feed van elke spoorweg |
| **Twee tellingen per spoorweg**: treinen in dienst, en voertuigen buiten dienst | elke spoorweg | dezelfde feed |

### Aangezet met je eigen gratis sleutel of account

| Gratis sleutel of account | Wat het toevoegt |
|---|---|
| **Metra**-sleutel | de treinen van Metra (omgeving Chicago, Verenigde Staten) |
| **Trafikverket**-sleutel | SL Pendeltåg, de pendeltåg van Västtågen en Arlanda Express (Zweden) |
| Sleutel van het **NS API-portaal** | NS Sprinters (Nederland) |
| Sleutel van **Transport for NSW Open Data** | NSW TrainLink Intercity-treinen (New South Wales, Australië) |
| Sleutel van **Transport Victoria Open Data** | de forensentreinen van V/Line (Victoria, Australië) |

Elk is in een paar minuten te krijgen: [stap voor stap hieronder](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap).
De andere 26 spoorwegen hebben geen sleutel nodig.

---

## Waar het werkt

| Regio | Wat je krijgt | Van | Nodig |
|---|---|---|---|
| **Australië**: New South Wales | NSW TrainLink Intercity: de lijnen Blue Mountains, Central Coast and Newcastle, Hunter, South Coast en Southern Highlands vanuit Sydney | Transport for NSW | een gratis sleutel |
| **Australië**: Queensland | Queensland Rail Citytrain, Zuidoost-Queensland (Brisbane) | Translink | niets |
| **Australië**: Victoria | de forensentreinen van V/Line: de lijnen Geelong, Ballarat, Bendigo, Seymour en Traralgon | Transport Victoria | een gratis sleutel |
| **Australië**: West-Australië | de treinen van Perth, alle negen lijnen, alleen uit de dienstregeling ([waarom](#treinen-van-perth-west-australië-australië)) | Public Transport Authority van West-Australië | niets |
| **Australië**: Zuid-Australië | de treinen van Adelaide Metro: de lijnen Belair, Gawler, Outer Harbor en Seaford | Adelaide Metro | niets |
| **Europa**: Finland | de forensentreinen van VR en HSL rond Helsinki | Fintraffic Digitraffic | niets |
| **Europa**: Ierland | de forensentreinen van Irish Rail rond Dublin en Cork | Irish Rail, National Transport Authority | niets |
| **Europa**: Nederland | NS Sprinters, het hele land | NS, OVapi | een gratis sleutel |
| **Europa**: Noorwegen | de lijnen L1, L2 en L4 van Vy (omgeving Oslo, Bergen), L5 van Go-Ahead Norge (Stavanger), Flytoget (luchthaven Oslo) | Entur | niets |
| **Europa**: Spanje | Renfe Cercanías en Rodalies de Catalunya, 15 netten: Madrid, Barcelona, Asturië, Sevilla, Cádiz, Málaga, Valencia, Murcia en Alicante, Cartagena, Ferrol, León, Bilbao, San Sebastián, Cantabrië, Zaragoza | Renfe | niets |
| **Europa**: Zweden | SL Pendeltåg (Stockholm), de pendeltåg van Västtågen (Göteborg), Arlanda Express | Trafikverket | een gratis sleutel |
| **Noord-Amerika**: Verenigde Staten | Metra (omgeving Chicago: Illinois, Wisconsin) | Metra | een gratis sleutel |
| **Noord-Amerika**: Verenigde Staten | South Shore Line (Chicago naar South Bend: Illinois, Indiana) | NICTD, via ETA SPOT | niets |

Staat het er niet bij? [Laat het ons weten](#help-het-groeien). Waar iemand de
gegevens openlijk publiceert, kijken we of we ze kunnen toevoegen.

⚠ **Een trein is zo goed als de feed van zijn spoorweg.** Sommige spoorwegen
plaatsen hun treinen volgens de dienstregeling in plaats van met gps, andere
melden een trein alleen bij seinen die een paar minuten uit elkaar liggen, en
sommige feeds stoppen of bevriezen een tijdje. De beperkingen van elke
spoorweg staan onder [Alles op de kaart, in detail](#alles-op-de-kaart-in-detail).

⚠ **Het is niet de officiële informatie van de spoorweg.** Kijk voor je reist
in de eigen app of op de website van de spoorweg.

---

## Onderdeel van Live Track: de andere modules

Live Track is een reeks Home Assistant-integraties, één per soort bewegend
ding, allemaal getekend op dezelfde kaart. Elke werkt op zichzelf; samen
vormen ze één live beeld. Ze delen de kaart en een Python-bibliotheek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
dus een extra module installeren voegt geen verzoeken toe aan een bron die een
andere al leest.

| Module | Wat het op de kaart zet | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | vliegtuigen boven je via ADS-B, met routes en typesymbolen | uitgebracht |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | schepen en boten via AIS, bij jou in de buurt of overal | uitgebracht |
| **Live Track Commuter Rail** | forensentreinen in Noord-Amerika, Europa en Australië (deze module) | uitgebracht |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity- en langeafstandstreinen in Noord-Amerika, Europa en Australië | uitgebracht |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | vliegtuigen en schepen van immigratie- en federale ordediensten, uit openbare lijsten | uitgebracht |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | weer, stormen en natuurgevaren | uitgebracht |
| Live Track Stations | vertrekborden en "tijd om te gaan"-meldingen voor elk station | gepland |
| Live Track Satellites | satellieten die over je heen trekken | gepland |
| Live Track Freight Trains | goederen- en werktreinen waar spoorwegen ze publiceren | gepland |
| Live Track Transit | stadsbussen, trams, veerboten en metro | gepland |
| Live Track Intercity Buses | intercity- en streekbussen | gepland |
| Live Track Commuter Buses | forensenbussen | gepland |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | de gedeelde kaart waarop elke module tekent | uitgebracht, met elke module geïnstalleerd |

Alles is gratis en open source. Niets wordt achtergehouden voor sponsors.

---

## Voordat je begint

* **Home Assistant** 2026.11 of nieuwer.
* **De Marktplaats** (HACS) in je Home Assistant, om het op de makkelijke
  manier te installeren en bij te werken. Zonder kun je de bestanden met de
  hand kopiëren.
* **Internettoegang** voor Home Assistant: elke trein komt uit de openbare
  feed van zijn eigen spoorweg.
* Niets te betalen. 26 van de 31 spoorwegen hebben geen
  account nodig; de andere vijf hebben een eigen, gratis sleutel nodig
  ([hierboven](#aangezet-met-je-eigen-gratis-sleutel-of-account)).
* Home Assistant installeert de Python-pakketten die het nodig heeft
  (`saw-livetrack`, `gtfs-realtime-bindings` en `tzdata`) zelf, de eerste keer
  dat de integratie laadt.

---

## Installeren, stap voor stap

### Via de Marktplaats (aanbevolen)

1. Open in Home Assistant **Instellingen → Marktplaats** (HACS).
2. Zoek **Live Track Commuter Rail** en open het.
3. Kies **Download** (of **Installeren**).
4. **Herstart Home Assistant**: **Instellingen → Systeem → Reparaties** biedt
   de herstart aan, of gebruik **Instellingen → Systeem → Herstart**.

Vindt de zoekfunctie het niet, voeg het dan toe via de koppeling: kies **Via
koppeling toevoegen** (of het menu met de drie puntjes → **Aangepaste
repositories**), voer `StrausbergAutomationWorks/LiveTrackCommuterRail` in, kies
**Integratie** als om het type wordt gevraagd en ga daarna verder bij stap 3.

Daarna biedt de Marktplaats elke nieuwe release als update aan.

### Met de hand

1. Download de broncode van de
   [laatste release](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Kopieer de map `custom_components/live_track_commuter_rail` naar de map
   `custom_components` in de configuratiemap van je Home Assistant (maak
   `custom_components` aan als die er niet is).
3. Herstart Home Assistant.

Om met de hand bij te werken, vervang je de map door die van de nieuwe release
en herstart je.

---

## Instellen, stap voor stap

1. Open **Instellingen → Apparaten en diensten**.
2. Kies **Voeg integratie toe** (rechtsonder) en zoek naar **Live Track
   Commuter Rail**.
3. **Regio**: kies het land, of het land en de regio, van de spoorweg. Alleen
   plaatsen met ten minste één spoorweg staan erin. Kies **Verzend**.
4. **Spoorweg**: kies de spoorweg. Kies **Verzend**.
5. **API-sleutel**: alleen voor Metra, de drie Zweedse spoorwegen, NS
   Sprinter, NSW TrainLink Intercity en V/Line commuter. Plak je sleutel
   ([zo krijg je er een](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap))
   en kies **Verzend**. De andere spoorwegen slaan deze stap over.

Dat is alles. De treinen verschijnen binnen een minuut. Waar de volgende
haltes van een spoorweg uit de dienstregeling komen, vullen ze zich in de
eerste minuten aan, zodra de dienstregeling is gedownload. Om nog een spoorweg
te volgen, voeg je de integratie opnieuw toe. Dezelfde spoorweg twee keer
wordt geweigerd.

### Wat het toont veranderen: de opties

Open **Instellingen → Apparaten en diensten → Live Track Commuter Rail →
Configureer** (het tandwiel) bij de spoorweg die je wilt veranderen. Elke
optie, in gewone woorden:

| Optie | Wat het doet | Standaard |
|---|---|---|
| **Ophaalinterval** | hoe vaak de feed van de spoorweg wordt gelezen, 15 tot 600 seconden. De meeste feeds worden ongeveer elke 30 seconden bijgewerkt, dus een korter interval toont zelden meer | 30 seconden |
| **Geparkeerd materieel tonen** | uit: materieel buiten dienst verschijnt alleen zolang het rijdt, en verdwijnt van de kaart na 10 minuten stilstand. Aan: elk voertuig in de feed wordt getoond, ook geparkeerde treinen | uit |

---

## Gratis sleutels die meer aanzetten, stap voor stap

Vijf spoorwegen vragen elke gebruiker om een eigen sleutel. Al deze sleutels
zijn gratis, en iedereen die Live Track Commuter Rail installeert, krijgt zijn
eigen sleutel. Je plakt de sleutel als de instellingsdialoog erom vraagt
([stap 5 hierboven](#instellen-stap-voor-stap)). Alleen de sleutel wordt
gevraagd: geen wachtwoord en geen geheim. De sleutel wordt in Home Assistant
bij de integratie bewaard en nooit in het logboek geschreven. Als de spoorweg
hem blijft weigeren, vraagt Home Assistant je om een nieuwe.

### Metra (omgeving Chicago, Verenigde Staten)

1. Open <https://metra.com/developers> en scrol omlaag naar **GTFS Realtime
   API Key Request Form**.
2. Vul **First Name** (voornaam), **Last Name** (achternaam), **Email
   Address** (e-mailadres, wordt twee keer gevraagd) en **Purpose of Use**
   (gebruik, bijvoorbeeld: Home Assistant) in.
3. Vink **I have read and agree to the License Agreement.** aan (ik heb de
   licentieovereenkomst gelezen en ga akkoord; die staat op
   <https://metra.com/gtfs-realtime-api-key-request-license-agreement>) en
   kies **Submit**.
4. Plak de sleutel die je van Metra krijgt in **API-sleutel** als je Metra
   toevoegt.

### Trafikverket (Zweden: SL Pendeltåg, Västtågen, Arlanda Express)

1. Open <https://data.trafikverket.se/oauth2/Account/register>.
2. Vul **Email**, **Displayname** (weergavenaam), **Password** (wachtwoord)
   en **Confirm password** in, vink **Accept license and Agreement** aan en
   kies **Register**.
3. Open <https://data.trafikverket.se/get-started> en kies **Create key**,
   onder **Create a key**. Log in met het account dat je hebt gemaakt en maak
   de sleutel aan.
4. Plak hem in **API-sleutel** als je een Zweedse spoorweg toevoegt. Eén
   sleutel geldt voor alle drie.

### NS (Nederland)

1. Open <https://apiportal.ns.nl/>, kies **Inloggen** en dan **Externe
   bezoeker**.
2. Vul het formulier in en verstuur het. Een e-mail bevestigt de registratie.
   Het kan tot 5 minuten duren voordat de API's in het portaal verschijnen.
3. Open de pagina van de **Virtual Train API** (de treinposities van NS).
   Open onder **Related Products** het product, geef je abonnement een naam
   en kies **Subscribe**.
4. Als NS het abonnement heeft goedgekeurd, staat je sleutel op je
   profielpagina. Plak hem in **API-sleutel** als je NS Sprinter toevoegt.

### Transport for NSW (New South Wales, Australië)

1. Open <https://opendata.transport.nsw.gov.au/>, kies **Register**, maak een
   account aan en log in.
2. Kies het pictogram van je gebruikersprofiel en dan **API Tokens**.
3. Typ een naam voor de sleutel en kies **CREATE API TOKEN**. Kopieer de
   sleutel meteen: de site toont hem maar één keer.
4. Plak hem in **API-sleutel** als je NSW TrainLink Intercity toevoegt. Plak
   alleen de sleutel: Live Track Commuter Rail zet het woord `apikey` er zelf
   voor.

### Transport Victoria (Victoria, Australië)

1. Open <https://opendata.transport.vic.gov.au/>, kies **Login** en dan
   **Sign up**.
2. Voer je gegevens in en kies **Create Account**. Voer de code uit de e-mail
   in die je krijgt en kies **Confirm**.
3. Het portaal vraagt om een authenticator-app op je telefoon: scan er de
   QR-code mee, voer de code van de app in en kies **Confirm**. Log daarna in
   met je e-mailadres, je wachtwoord en de code van de app.
4. Kies **My Account** → **Profile** → **API tokens**. Je sleutel staat er
   al. Plak hem in **API-sleutel** als je V/Line commuter toevoegt.

---

## De kaart op een dashboard zetten

De kaart is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
de kaart waarop elke Live Track-module tekent. **Hij wordt met Live Track
Commuter Rail geïnstalleerd**: niets te downloaden, niets te kopiëren, geen
bron toe te voegen.

1. Open een dashboard, kies het potlood (**Wijzig dashboard**) en dan **Voeg
   kaart toe**.
2. Scrol naar beneden en kies **Handmatig**.
3. Plak dit en kies **Bewaar**:

```yaml
type: custom:live-track-map-card
entity_filter:
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

Andere Live Track-modules gaan op dezelfde manier in `entity_filter`: nog een
regel `- domain: geo_location` voor elke bron.

**Op de kaart:**

* Elke trein is een schijf in de kleuren van zijn lijn of spoorweg, met zijn
  treinnummer of lijn. Bij de meeste spoorwegen wisselen de kleuren met de
  richting: gevuld bij vertrek uit de hoofdstad of grootste stad, wit ernaartoe.
* Een pijl toont de richting waarin de trein rijdt. Een stilstaande trein
  houdt zijn laatste richting.
* **Wijs** een trein **aan** om zijn spoorweg, nummer of lijn te zien, en
  waar hij rijdt. **Klik** erop voor al zijn gegevens, ook zijn volgende
  halte en zijn vertraging.

Als de bronnen van je dashboards in YAML zijn ingesteld
(`lovelace: resource_mode: yaml`), kan er niets voor je worden geregistreerd:
een melding onder **Reparaties** geeft dan de precieze regels om aan
`configuration.yaml` toe te voegen. Ze zien er zo uit, met het eigen adres van
de integratie in plaats van de plaatshouders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_commuter_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Elke Live Track-module heeft een kopie van de kaart bij zich en registreert
die als Home Assistant start. Samen houden ze precies één regel aan in
**Instellingen → Dashboards → Bronnen**: de nieuwste kaartversie die een van
hen meebrengt, nooit een oudere. Een kaart die je zelf via de Marktplaats hebt
geïnstalleerd, blijft onaangeroerd. Als je de laatste spoorweg van deze module
verwijdert, gaat de regel over naar een andere Live Track-module, of wordt hij
verwijderd als er geen meer is. Als de bestanden van de integratie worden
verwijderd terwijl haar spoorwegen nog zijn ingesteld, en er geen andere Live
Track-module is geïnstalleerd, verwijder de regel dan zelf in **Instellingen →
Dashboards → Bronnen**.

**Om de kaart in plaats daarvan met de hand te installeren**, volg je de
stappen in de [README van de kaart](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
Een regel die je zelf hebt gemaakt, voor een kopie onder `/local/` of op een
ander adres, wordt nooit gewijzigd of verwijderd. Zolang die de kaart laadt,
laat elke Live Track-module de kaart eraan over, ook als een module een nieuwere
release heeft, en niets in **Reparaties** meldt dat. Om terug te gaan naar de
kopie van de module, verwijder je je regel in **Instellingen → Dashboards →
Bronnen** en herstart je Home Assistant. Verwijder je het bestand van je kopie,
verwijder dan ook de regel: zolang een regel waarvan het bestand weg is blijft
staan, voegt de module geen eigen regel toe.

Elke andere kaart die `geo_location`-entiteiten toont, toont de treinen ook,
als gewone markers.

---

## Gebruiken in automatiseringen

Alles is een gewone Home Assistant-entiteit, dus de automatiseringseditor
werkt ermee, zonder code.

**Een melding op je telefoon als je spoorweg bijna geen treinen toont** (de
feed kan gestopt zijn, of de dienst kan verstoord zijn):

1. **Instellingen → Automatiseringen en scènes → Maak automatisering aan →
   Voeg automatisering toe**.
2. **Wanneer**: **Voeg trigger toe** → **Entiteit** → **Numerieke status
   heeft drempelwaarde overschreden**. Kies de entiteit **Trains in service**
   van de spoorweg, en **Onder** `3`.
3. **Doe dan**: **Voeg actie toe**, zoek de meldingsactie van je telefoon (die
   draagt de naam van je telefoon) en voer een bericht in, bijvoorbeeld:

   ```text
   Bijna geen treinen op de kaart: kijk in de app van de spoorweg
   ```

4. **Bewaar**.

**Andere ideeën:** een lamp die aangaat als een trein binnen 1 km (0,6 mijl)
van je huis in Utrecht (Nederland) is, uit de afstand van de markers; een
telling op het dashboard van de Metra-treinen in dienst in de ochtendspits
(Chicago, Verenigde Staten); een bericht als de eerste trein van de dag rijdt
in Brisbane (Australië), zodra **Trains in service** boven 0 komt.

---

## Alles op de kaart, in detail

### Treinen, en materieel buiten dienst

Elke trein is één marker. Zijn status is zijn afstand tot je huis, in
kilometers. De marker verschijnt als de feed van de spoorweg de trein meldt,
en wordt verwijderd als de trein uit de feed verdwijnt (na 3 minuten, zodat
een korte onderbreking van de feed hem niet verwijdert).

* **Een trein in dienst** draagt zijn treinnummer of zijn lijn, zoals de
  spoorweg die nummert (elke spoorweg hieronder zegt welke).
* **Materieel buiten dienst** draagt `NIS` en zijn eenheidsnummer, zodat een
  eenheidsnummer nooit voor een treinnummer wordt aangezien. Het wordt alleen
  getoond zolang het rijdt, en verdwijnt van de kaart na 10 minuten
  stilstand. Zet **Geparkeerd materieel tonen** aan om elk voertuig in de feed
  te zien.
* **Tussen twee posities** beweegt de kaart de marker van de ene echte
  positie naar de volgende. Voorbij de laatste echte positie wordt niets
  verzonnen.
* **Een positie die niet op het spoor ligt, wordt geweigerd.** Een trein die
  naast het spoor wordt gemeld, wordt getoond op zijn laatste positie die wel
  op het spoor lag, hoogstens 10 minuten, en daarna verborgen tot hij terug
  is. Een trein die voor het eerst naast het spoor wordt gezien, wordt niet
  getoond.
* **Vertraagd en sterk vertraagd**: waar de spoorweg een eigen regel voor een
  vertraagde trein publiceert, gebruikt de integratie die, en zegt dat
  hieronder.

Op elke trein: `marker_label`, `observed_at` (wanneer zijn positie klopte),
`course_deg` (zolang hij rijdt), `next_stop` en `arrival_estimated_at` (waar
bekend), `delay_min`, `stalled`, `attribution`, en, tussen twee posities,
`previous_latitude`, `previous_longitude`, `previous_observed_at` en
`segment_duration_s`. Een positie die de integratie heeft geschat, in plaats
van een die de spoorweg meldde, draagt `position_source: estimated`.

### NSW TrainLink Intercity (New South Wales, Australië)

Uit de feeds van NSW TrainLink en Sydney Trains van Transport for NSW, met je
eigen sleutel. Een rit die in beide feeds staat, is één marker. Het label is
de lijncode (BMT, CCN, HUN, SCO, SHL); de rit en zijn eindpunten staan in het
hoverblok ("Train KN56 · Bomaderry–Kiama"). De kleur van de lijn uit de
dienstregeling, gevuld bij vertrek uit Sydney Central en omgekeerd ernaartoe.
Lege treinen zijn `NIS` en hun rit, in grijs. De volgende halte is een
station, nooit een perron. ⚠ Een positie van meer dan 10 minuten oud wordt
niet getekend, en een trein wordt verwijderd als zijn rit voorbij is.
Vertraagd vanaf 6 minuten (de Intercity-maatstaf van Transport for NSW),
sterk vertraagd vanaf 12.

### Queensland Rail Citytrain (Queensland, Australië)

Uit de open feed van Translink. ⚠ De posities zijn vaste punten op het spoor,
geen gps, zonder snelheid en zonder richting; de pijl volgt de route van de
trein in de dienstregeling. Een positie van meer dan 5 minuten oud wordt
geweigerd, omdat de feed een trein waarvan de positie bevroor tot het einde
van de dienstdag vasthoudt. Het label is het T-nummer van de lijn in de
lijnkleuren van Translink, omgekeerd voor treinen naar het zuiden, en een ster
voor extra ritten zonder T-nummer. Vertraagd vanaf 4 minuten, 6 op de lijnen
Gold Coast, Rosewood en Sunshine Coast (de eigen regel van Queensland Rail).

### V/Line commuter (Victoria, Australië)

Uit de V/Line-feed van Transport Victoria, met je eigen sleutel. Het label is
de lijncode (GEL, BAT, BGO, SER, TRN); treinnummer en lijn staan in het
hoverblok ("Train 8037 · Bendigo - Melbourne via Gisborne"). Elke lijn is
V/Line-paars: gevuld bij vertrek uit Melbourne, wit richting Southern Cross.
⚠ De posities van V/Line volgen meer de dienstregeling dan de trein: een rit
verdwijnt ongeveer een minuut na zijn geplande aankomst uit de feed, waar de
trein ook is, en posities bevriezen rond middernacht. Daarom houdt een trein
zijn laatste positie hoogstens 10 minuten en verlaat dan de kaart, en kan een
vertraagde trein verdwijnen voor zijn laatste station. Vertraagd vanaf 6
minuten (de regel van V/Line voor forensendiensten), sterk vertraagd vanaf
12.

### Treinen van Perth (West-Australië, Australië)

⚠ **Perth publiceert geen liveposities.** Elke trein wordt getekend uit de
dienstregeling van de Public Transport Authority van West-Australië: langs
zijn route geplaatst volgens zijn geplande tijden, gemarkeerd als schatting,
zonder vertraging. De dienstregeling wordt eens per dag gecontroleerd. Het
label is de eerste drie letters van de lijn (MAN, YAN, ARM, FRE, MID, ELL,
AIR, THO; STA voor een Stadium Special); het hoverblok zegt "Mandurah Line ·
Perth Underground–Mandurah". De kleuren zijn die van de netkaart: gevuld bij
vertrek uit Perth, wit ernaartoe.

### Adelaide Metro (Zuid-Australië, Australië)

Uit de open feed van Adelaide Metro, die ook zijn trams en bussen bevat (hier
niet getekend). De posities zijn gps, met de eigen richting van de trein.
Adelaide publiceert geen treinnummer, dus het label is de eerste drie letters
van de routecode die Adelaide Metro gebruikt (SEA, FLN, GAW, BEL, OUT
enzovoort); het hoverblok geeft de volledige code ("SEAFRD to Seaford ·
railcar 4006"). De kleuren zijn die van de netkaart: Belair groen, Seaford en
Flinders oranje, Gawler rood, Outer Harbor, Port Dock en Grange blauw; gevuld
bij vertrek uit het centrum, wit richting Adelaide Railway Station. Een
positie van meer dan 5 minuten oud, of meer dan 1 km van elke spoorroute van
Adelaide, wordt geweigerd. Vertraagd vanaf 5 minuten (de eigen regel van
Adelaide Metro), sterk vertraagd vanaf 10.

### Forensentreinen van VR en HSL (Finland)

Uit Digitraffic van Fintraffic. Een trein is een rit: zijn treinnummer en de
dag waarop hij vertrok. Het label is de lijnletter, gekleurd zoals de kaarten
en stationsborden van HSL de lijnen kleuren: HSL-paars zolang de volgende
halte in de tariefzones A tot E van HSL ligt, VR-groen daarbuiten. Een trein
die van Helsinki wegrijdt, is een gevulde schijf; een die ernaartoe rijdt, is
wit. Een trein wordt getoond van zijn eerste station tot zijn laatste halte,
en dan verwijderd. Ritten van lijn V zonder reizigers worden als `NIS`
getoond zolang ze rijden. Tussen twee posities glijdt een trein langs het
spoor. De lijnen I en P geven geen positie in de Ring Rail-tunnel bij de
luchthaven van Helsinki, dus daar beweegt de integratie de trein zelf langs
het spoor volgens zijn dienstregeling, tot er weer een echte positie komt.
Vertraagd vanaf 4 minuten (de regel van VR), sterk vertraagd vanaf 8. Een
positie van meer dan 10 minuten oud wordt geweigerd.

### Irish Rail (Ierland)

Uit de livedienst van Irish Rail, met de dienstregeling van de National
Transport Authority voor routes en stations. ⚠ Irish Rail meldt een trein
alleen als hij seinen passeert die een paar minuten uit elkaar liggen, dus
elke trein wordt getekend uit zijn dienstregeling en zijn laatste vertraging,
langs zijn route bewogen; de treinen van Cork, die Irish Rail niet volgt,
komen alleen uit de dienstregeling. Het label is het treinnummer zonder letter
(P508 toont 508). De kleur is die van de lijn op de netkaart van Transport for
Ireland, omgekeerd richting Dublin of Cork. Vertraagd vanaf 5 minuten (de
eigen regel van Irish Rail), sterk vertraagd vanaf 10.

### NS Sprinter (Nederland)

Uit de voertuiggegevens van NS, met je eigen sleutel. Het label is het
treinnummer; het hoverblok zegt "Sprinter 6632 · Dordrecht–Arnhem Centraal".
NS-geel met een NS-blauwe ring. Dit is de enige feed hier die de eigen
snelheid en richting van de trein meldt, en beide worden doorgegeven
(`speed_kmh`, `course_deg`). De volgende halte en de vertraging komen uit de
dienstregeling van OVapi. Het spoor is de SpoorKaart van NS, eens per dag
gedownload; een trein glijdt er tussen twee posities langs, en een positie
meer dan 1 km ervandaan wordt geweigerd. Vertraagd vanaf 3 minuten (de eigen
definitie van NS), sterk vertraagd vanaf 10.

### Vy, Go-Ahead Norge en Flytoget (Noorwegen)

Uit Entur, elke spoorweg een eigen item. Het label is de lijncode (L1, L2, L4,
L5, FLY1, FLY2); treinnummer en lijnnaam staan in het hoverblok. Een L-lijn
draagt zijn kleur uit de dienstregeling, gevuld bij vertrek uit Oslo S
(Bergen op L4, Stavanger op L5) en omgekeerd ernaartoe. Flytoget is grijs met
een oranje ring richting luchthaven Oslo, en oranje met een grijze ring bij
vertrek ervandaan. Entur publiceert geen snelheid en geen richting, dus de
pijl volgt de lijn van de trein. In de lange tunnels van Oslo wordt een trein
waarvan de posities wegvallen langs zijn lijn bewogen tot ze terugkomen.
Vertraagd vanaf 4 minuten, sterk vertraagd vanaf 8.

### Renfe Cercanías en Rodalies (Spanje)

Uit de open feed van Renfe, elk van de 15 netten een eigen item. Het label is
de lijn (C5, R2N) in de eigen kleur van de lijn uit de dienstregeling van
Renfe. Treinnummer en lijnnaam staan in het hoverblok. ⚠ Renfe plaatst zijn
treinen op hun route in plaats van met gps, dus ze staan stil en springen
dan. Een trein gaat alleen vooruit langs zijn eigen lijn: een positie ernaast,
terug langs de lijn of onmogelijk snel wordt geweigerd, en de laatste goede
hoogstens 10 minuten vastgehouden. Een trein heet pas stilgevallen na 6
minuten op één plek. Renfe publiceert geen regel voor een vertraagde trein,
dus gelden de eigen drempels van de kaart.

### SL Pendeltåg, Västtågen en Arlanda Express (Zweden)

Uit Trafikverket, met je eigen gratis sleutel (één sleutel voor alle drie).
Het label is het treinnummer; merk, nummer en eindstations staan in het
hoverblok. SL Pendeltåg is roze, Västtågen lichtblauw, Arlanda Express geel;
elk keert zijn kleuren om richting Stockholm C (Stockholm City voor de
pendeltåg) of, bij een rit die geen van beide aandoet, richting de grootste
eindstad. Tussen twee posities glijdt een trein langs de lijn van zijn rit,
en een positie meer dan 1 km ervandaan wordt geweigerd. Vertraagd vanaf 3
minuten op SL Pendeltåg (de regel van Region Stockholm), sterk vertraagd
vanaf 6; vertraagd vanaf 6 en sterk vertraagd vanaf 12 op de andere twee (de
regel van Trafikverket).

### Metra en de South Shore Line (Verenigde Staten)

Metra uit zijn eigen feed, met je eigen sleutel; de South Shore Line uit de
feed die ETA SPOT voor NICTD publiceert, zonder sleutel. Het label is het
treinnummer. Metra noemt de volgende halte en de tijd. De feed van de South
Shore Line geeft alleen een haltenummer en een vertraging, dus de
dienstregeling levert het station en de tijd. Een positie meer dan 300 m van
elk spoor van het North American Rail Network (Verenigde Staten), of van de
eigen route van de spoorweg, wordt geweigerd. ⚠ Op sommige dagen heeft de feed
van Metra maar weinig van zijn treinen aan een rit gekoppeld; de rest staat
dan als `NIS` of helemaal niet op de kaart, en de kaart lijkt een rustige
dag. De telling **Trains in service** laat zulke dagen achteraf zien.

---

## Alle entiteiten die het aanmaakt

Per spoorweg:

| Entiteit | Wat het is |
|---|---|
| `sensor.<spoorweg>_trains_in_service` | **Trains in service**: hoeveel treinen in dienst de feed van de spoorweg nu meldt. Voor Metra: `sensor.metra_chicago_area_trains_in_service` |
| `sensor.<spoorweg>_vehicles_not_in_service` | **Vehicles not in service**: hoeveel voertuigen buiten dienst de feed meldt |
| `geo_location.<spoorweg>_unit_…` | één per trein of voertuig (`geo_location.metra_unit_8426`); hij komt en gaat met de trein. Elk draagt `source: live_track_commuter_rail`, en zijn status is zijn afstand tot je huis in kilometers |

De namen van de entiteiten zijn Engels, in welke taal je Home Assistant ook
staat.

Elke spoorweg heeft een bekend wagenpark. De entiteit-ID van een marker komt
van de spoorweg en het nummer van het voertuig in de feed, nooit van het
label, dus hetzelfde voertuig krijgt elke keer dat het verschijnt dezelfde
entiteit-ID: `geo_location.metra_unit_8426` is altijd rijtuig 8426 van Metra.
De marker wordt verwijderd als het voertuig uit de feed verdwijnt, of na 10
minuten geparkeerd terwijl **Geparkeerd materieel tonen** uit staat. De
markers hebben geen unieke ID, net als geen enkele Live Track-kaartmarker,
dus je kunt ze in de interface niet hernoemen, verbergen of aan een ruimte
toewijzen. De twee sensoren hebben een unieke ID en kun je hernoemen.

Attributen die bij elke ophaalbeurt veranderen, de posities en tijden van de
markers, worden in de geschiedenis van Home Assistant opgeslagen, zoals bij
elke entiteit. De twee sensoren hebben geen attributen, dus ze bewaren kost
weinig, en ze zijn de registratie van hoeveel treinen er op een dag reden.
Om de markers buiten de geschiedenis te houden, zet je dit in
`configuration.yaml` en herstart je:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_unit_*
```

Heeft je `configuration.yaml` al een `recorder:`-sectie, voeg dan alleen het
patroon `geo_location.*_unit_*` toe, onder `exclude:` en `entity_globs:`. Het
patroon past alleen op de treinmarkers van deze module. Een kaart die is
ingesteld om de geschiedenis te tekenen, heeft dan geen spoor meer om te
tekenen.

---

## Wat het verstuurt en downloadt

**Over je locatie.** Niets. De positie van je huis wordt alleen binnen je Home
Assistant gebruikt, om de afstand van elke trein te geven. Je sleutel, waar
een spoorweg er een nodig heeft, gaat alleen naar die spoorweg. Verder wordt
niets over jou ergens heen gestuurd. Elke dienst ziet je internetadres, zoals
elke website.

**Hoeveel.** Elke livefeed wordt bij elke ophaalbeurt gelezen, standaard elke
30 seconden (**Ophaalinterval**, 15 tot 600 seconden), of minder vaak waar de
tabel dat zegt. Waar meerdere Live Track-modules dezelfde feed lezen, leest
één gedeelde client hem één keer voor allemaal. Gemeten op 19 november 2026,
van 02:20 tot 02:40 UTC:

| Spoorweg | Livefeed, één leesbeurt | Dienstregeling |
|---|---|---|
| NSW TrainLink Intercity (Australië) | 402 KB uit vier feeds, hoogstens één keer per 55 seconden | 51 MB (twee dienstregelingen), als die verandert, dagelijks gecontroleerd |
| Queensland Rail Citytrain (Australië) | 141 KB | 42 MB, elke dag |
| V/Line commuter (Australië) | 14 KB | 59 MB, als die verandert, dagelijks gecontroleerd |
| Treinen van Perth (Australië) | geen: Perth publiceert geen livefeed | 28 MB, als die verandert, dagelijks gecontroleerd |
| Adelaide Metro (Australië) | 298 KB | 20 MB, als Adelaide Metro een nieuwe versie publiceert |
| Forensentreinen van VR en HSL (Finland) | 1,1 KB gecomprimeerd voor de posities, plus de wijzigingen in de treinen van de dag één keer per minuut | geen bestand: de treinen van de dag komen met de livegegevens mee |
| Irish Rail (Ierland) | 0,2 KB, hoogstens één keer per 55 seconden | 6,6 MB, als die verandert, dagelijks gecontroleerd; de stationslijst, 18 KB, één keer per week |
| NS Sprinter (Nederland) | 1,2 KB; vertragingen van OVapi, 1,6 MB, elke 5 minuten en alleen als ze veranderen | de dienstregeling van OVapi, 274 MB, hoogstens één keer per week en alleen als die verandert; de spoorkaart van NS, 1,3 MB, elke dag |
| Vy, Go-Ahead Norge, Flytoget (Noorwegen) | Vy 497 KB, Go-Ahead Norge 7 KB, Flytoget 233 KB | Vy 67 MB, Go-Ahead Norge 20 MB, Flytoget 0,6 MB, als die verandert, dagelijks gecontroleerd |
| Renfe Cercanías en Rodalies (Spanje) | één feed voor alle 15 netten: 26 bytes, 's nachts zonder rijdende treinen | 16 MB, elke dag |
| SL Pendeltåg, Västtågen, Arlanda Express (Zweden) | 3,7 KB de eerste keer, daarna ongeveer 2 KB aan wijzigingen | geen; de stationslijst, 0,15 MB, elke dag |
| Metra (Verenigde Staten) | 18 KB | 0,4 MB, elke dag |
| South Shore Line (Verenigde Staten) | minder dan 1 KB | 0,14 MB, elke dag |

⚠ Toen dit werd gemeten, was het dag in Australië, avond in de Verenigde
Staten en nacht in Europa. Een livefeed is 's nachts het kleinst: overdag
zijn de Europese feeds groter dan de tabel laat zien.

**Na een fout.** De laatste goede posities blijven nog twee mislukte
leesbeurten staan; daarna worden de treinen als niet beschikbaar gemarkeerd
tot de feed weer antwoordt. Een dienstregeling die niet kan worden
gedownload, wordt een uur later opnieuw geprobeerd, en je huidige kopie
blijft in gebruik. Als de spoorweg je sleutel blijft weigeren, vraagt Home
Assistant om een nieuwe.

**Op schijf.** De dienstregelingen worden bewaard in de map `.storage` van
Home Assistant, onder namen die met `saw_` beginnen, gedeeld met de andere
Live Track-modules die dezelfde spoorweg lezen: die met "als die verandert"
zoals ze zijn gedownload, de andere als een kleiner uittreksel. Als je Live
Track Commuter Rail verwijdert en geen andere Live Track-module ze gebruikt,
kun je ze met de hand wissen.

---

## Help het groeien

Live Track Commuter Rail groeit nog. We voegen spoorwegen en landen toe zodra
we ze vinden, en we willen weten wat je hierna zou willen.

### Iets voorstellen

Ontbreekt je land of je spoorweg? Klopt er iets niet, of is iets moeilijk te
begrijpen? Laat het ons weten op de manier die voor jou het makkelijkst is:

* [**Vul een kort formulier in**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=nl.yml)
  in het Nederlands. Je hebt een gratis GitHub-account nodig.
* **Stuur een e-mail** naar
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Geen account nodig.

Hoe dan ook, het helpt als je ons vertelt:

* wat je graag zou zien, en waar ter wereld;
* een link naar waar de gegevens worden gepubliceerd, als je die kent (een
  open-datapagina, een openbare feed, de website van een dienst): niet nodig,
  maar het helpt;
* de taal van je Home Assistant, als het probleem de formulering of een
  vertaling is.

Schrijf in het Engels of in je eigen taal, wat voor jou het makkelijkst is.

### Zelf iets toevoegen, met onze hulp

Wil je zelf iets toevoegen, dan helpen we je daarbij, van de eerste vraag tot
de afgeronde release. Je hoeft geen ontwikkelaar te zijn om te beginnen:

* **Een vertaling.** De teksten in de instellingsdialoog zijn een korte lijst
  zinnen in één tekstbestand. We laten je zien welk bestand en welke regels.
* **Een nieuwe spoorweg.** Vertel ons waar de gegevens worden gepubliceerd.
  We kunnen de code samen schrijven, of de jouwe nakijken.
* **Testen waar je woont.** Installeer het, bekijk jouw deel van de kaart, en
  vertel ons wat klopt en wat niet.
* **Een verbetering van deze README.** Als een stap niet overeenkwam met wat
  je zag, vertel ons wat je zag.

[**Vertel ons wat je in gedachten hebt**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=nl.yml)
of schrijf naar
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
en we antwoorden met de volgende stappen.

---

## Talen

Deze README: [English](README.md), [Suomi](README.fi.md),
[Svenska](README.sv.md), [Norsk bokmål](README.nb.md),
[Español](README.es.md), **Nederlands**, [Gaeilge](README.ga.md). Elke
vertaalde README is volledig. Geen enkele is nog door een moedertaalspreker
gelezen. Is Nederlands je moedertaal, laat ons dan weten of deze README goed
leest: zie [Help het groeien](#help-het-groeien).

De instellingsdialoog en de opties verschijnen in de taal van je Home
Assistant als die een van deze is: English, Suomi, Svenska, Norsk bokmål,
Español, Nederlands, Gaeilge. Elke andere taal toont Engels.

Een fout in een vertaling gevonden, of een andere taal nodig? Laat het ons
weten op <https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues>,
of [vertaal het met onze hulp](#zelf-iets-toevoegen-met-onze-hulp).

---

## Bronvermelding en licenties

Elke spoorweg wordt tijdens het draaien gelezen, door je Home Assistant, uit
zijn eigen gepubliceerde feed; niets uit een livefeed staat in deze
repository. Elke trein vermeldt zijn bron in zijn attribuut `attribution`. De
voorwaarden van elke spoorweg binden jou, als ontvanger van zijn gegevens.

* **Metra** (Verenigde Staten): GTFS-Realtime, onder de
  [licentieovereenkomst van Metra](https://metra.com/gtfs-realtime-api-key-request-license-agreement),
  die je aanvaardt als je een sleutel aanvraagt.
* **South Shore Line** (NICTD, Verenigde Staten): openbare feed en
  dienstregeling die ETA SPOT voor NICTD publiceert, zonder sleutel en zonder
  licentieovereenkomst.
* **Translink** (regering van Queensland, Australië): gegevens onder CC BY 4.0
  ([open data](https://translink.com.au/about-translink/open-data)).
* **Fintraffic / digitraffic.fi** (Finland): gegevens onder CC BY 4.0. **HSL**
  (Finland): tariefzones, CC BY 4.0.
* **Renfe** (Spanje): gegevens onder CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)), bewerkt.
* **Entur** (Noorwegen): gegevens onder de Noorse licentie voor open
  overheidsgegevens ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)),
  verspreid door Entur.
* **Trafikverket** (Zweden): gegevens onder [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Ierland): livegegevens; Irish Rail publiceert geen
  voorwaarden. Dienstregeling van de
  [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Ierland), CC BY 4.0.
* **NS** (Nederland): voertuiggegevens, met je eigen sleutel, uit het
  [NS API-portaal](https://apiportal.ns.nl/). Dienstregeling en vertragingen
  van [OVapi](https://gtfs.ovapi.nl), CC0.
* **Transport for NSW** (Australië): gegevens onder CC BY 4.0
  ([gegevenslicentie](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australië): gegevens onder CC BY 4.0
  ([open data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Adelaide Metro**, Department for Infrastructure and Transport, South
  Australia: gegevens onder CC BY 4.0 ([informatie voor ontwikkelaars](https://www.adelaidemetro.com.au/developer-info)).
* **Public Transport Authority van West-Australië**: dienstregelingsgegevens
  gratis beschikbaar via www.transperth.wa.gov.au
  ([toegang tot ruimtelijke gegevens](https://www.transperth.wa.gov.au/About/Spatial-Data-Access)).
* **Spoorbestanden in `rail/`**: het North American Rail Network (ministerie
  van Transport van de Verenigde Staten), publiek domein; het spoornet van
  Fintraffic, CC BY 4.0, bewerkt; de lijnen van Flytoget uit gegevens van
  Entur, NLOD 2.0, bewerkt; de Zweedse lijnen gerouteerd op OpenStreetMap,
  (c) OpenStreetMap-bijdragers, ODbL 1.0; de inwonertallen van steden van
  Statistics Sweden, CC0. Wat is veranderd, staat in [ATTRIBUTION.md](ATTRIBUTION.md).
* **De kaart** is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, een kopie van [ha-map-card](https://github.com/nathan-gs/ha-map-card)
  door nathan-gs, MIT. De kaarttegels en hun bronvermelding staan in de
  README ervan.

Geen van deze organisaties heeft deze integratie gemaakt of onderschreven.

**Code**: MIT, in [LICENSE](LICENSE).

**Voor ontwikkelaars:** elke spoorweg is één adapter in
`custom_components/live_track_commuter_rail/operators/`; de spoorbestanden in
`rail/` worden opnieuw gebouwd met de scripts in `tools/` (`build_rail.py`,
`build_tracks.py`, `build_flytoget_lines.py`, `sweden_lines.py`). De tests
draaien met `python -m unittest discover -s tests`.

---

## Trefwoorden

Home Assistant treinen · treinen live volgen · live treinkaart ·
forensentreinen · NS treinen live · Sprinter · treinkaart · treinposities ·
GTFS-Realtime · Metra · South Shore Line · Renfe Cercanías · Rodalies ·
lähijunat · HSL · VR · pendeltåg · Vy · Flytoget · Irish Rail · Queensland
Rail · Translink · NSW TrainLink · V/Line · Adelaide Metro · treinen Perth ·
geo_location · map card · Lovelace · HACS · Marktplaats · Live Track ·
LiveTrack · StrausbergAutomationWorks

---

**Erkenning.** StrausbergAutomationWorks erkent de inheemse volken van alle
landen en wateren op deze kaart, overal ter wereld, en betuigt zijn respect aan
hun Elders, van vroeger en nu.
