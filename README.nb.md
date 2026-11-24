# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · **Norsk bokmål** · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md) · [Alle språk](#språk)

**Lokaltog for Home Assistant, på ett kart.** Live Track Commuter Rail viser
hvert tog på lokaltogbanene du velger på Home Assistant-kartet ditt, i sanntid:
hvor det er, tognummeret eller linjen, om det er forsinket, og neste stasjon.
Hver bane legges til for seg, fra banens egne åpne data.

> **Live Track Commuter Rail er en modul i Live Track**, en familie av Home
> Assistant-integrasjoner som tegner alt som beveger seg, og været det beveger
> seg gjennom, på ett felles kart: fly, skip, tog og vær. Installer den alene,
> eller ved siden av de andre modulene
> ([liste nedenfor](#en-del-av-live-track-de-andre-modulene)).

> **Vokser, og åpen for ideer.** Live Track Commuter Rail dekker i dag 31 baner
> i 8 land på 3 kontinenter, og vi legger til flere baner og land. Mangler din?
> [Foreslå den](#hjelp-den-å-vokse), eller legg den til selv: vi hjelper deg.

**Status: 0.1.6, utgitt.** I katalogen til Marketplace ([installer den
nedenfor](#installer-den-trinn-for-trinn)).

Originalt arbeid av StrausbergAutomationWorks. Ikke tilknyttet, eller
godkjent av, Metra, Northern Indiana Commuter Transportation District
(NICTD), ETA SPOT, Renfe, Fintraffic, HSL, VR, Entur, Vy, Go-Ahead Norge,
Flytoget, Trafikverket, SL, Västtågen, Arlanda Express, Irish Rail, National
Transport Authority (Irland), NS, OVapi, Translink, Queensland Rail,
Transport for NSW, Transport Victoria, V/Line, Adelaide Metro, Public
Transport Authority i Vest-Australia eller noen annen bane.

---

## Innhold

1. [Alt den gjør](#alt-den-gjør)
2. [Hvor den virker](#hvor-den-virker)
3. [En del av Live Track: de andre modulene](#en-del-av-live-track-de-andre-modulene)
4. [Før du begynner](#før-du-begynner)
5. [Installer den, trinn for trinn](#installer-den-trinn-for-trinn)
6. [Sett den opp, trinn for trinn](#sett-den-opp-trinn-for-trinn)
7. [Gratis nøkler som slår på mer, trinn for trinn](#gratis-nøkler-som-slår-på-mer-trinn-for-trinn)
8. [Sett kartet på et dashbord](#sett-kartet-på-et-dashbord)
9. [Bruk den i automasjoner](#bruk-den-i-automasjoner)
10. [Alt på kartet, i detalj](#alt-på-kartet-i-detalj)
11. [Alle entitetene den lager](#alle-entitetene-den-lager)
12. [Hva den sender og laster ned](#hva-den-sender-og-laster-ned)
13. [Hjelp den å vokse](#hjelp-den-å-vokse)
14. [Språk](#språk)
15. [Kreditering og lisenser](#kreditering-og-lisenser)
16. [Søkeord](#søkeord)

---

## Alt den gjør

### På kartet, uten noe å sette opp

Du legger til en **bane**: du velger et land eller en region, og så en av
lokaltogbanene der. Alt nedenfor vises da for den banen. Legg til
integrasjonen på nytt for hver annen bane du vil ha.

| Hva | Hvor | Fra |
|---|---|---|
| **Tog i trafikk**: én markør per tog, med tognummer eller linje, i banens egne farger, vendt i retningen toget kjører | alle baner | hver banes egen sanntidsstrøm |
| **Forsinkelse**: et tog vises som forsinket eller svært forsinket etter banens egen regel, der banen publiserer en | alle baner som melder forsinkelser | hver banes strøm og rutetabell |
| **Neste stasjon og tid**: stasjonen toget stopper på neste gang, og når det ventes dit | alle baner der strømmen eller rutetabellen sier det | hver banes strøm og rutetabell |
| **Tog som følger sporet**: mellom to posisjoner glir toget langs linjen, ikke rett over | Finland, Nederland, Sverige | sporfiler som følger med integrasjonen eller som den laster ned |
| **Materiell som ikke er i trafikk**: tomme tog mellom hensettingsområder, vist mens de beveger seg | baner der strømmen melder dem | hver banes strøm |
| **To tellere per bane**: tog i trafikk, og kjøretøy som ikke er i trafikk | alle baner | samme strøm |

### Slått på med din egen gratis nøkkel eller konto

| Gratis nøkkel eller konto | Hva den legger til |
|---|---|
| Nøkkel fra **Metra** | Metras tog (Chicago-området, USA) |
| Nøkkel fra **Trafikverket** | SL Pendeltåg, Västtågens pendeltåg og Arlanda Express (Sverige) |
| Nøkkel fra **NS API-portal** | NS Sprinter-tog (Nederland) |
| Nøkkel fra **Transport for NSW Open Data** | NSW TrainLink Intercity-tog (New South Wales, Australia) |
| Nøkkel fra **Transport Victoria Open Data** | V/Lines lokaltog (Victoria, Australia) |

Hver tar noen minutter å skaffe: [trinn for trinn nedenfor](#gratis-nøkler-som-slår-på-mer-trinn-for-trinn).
De andre 26 banene trenger ingen nøkkel.

---

## Hvor den virker

| Region | Hva du får | Fra | Trenger |
|---|---|---|---|
| **Australia**: New South Wales | NSW TrainLink Intercity: linjene Blue Mountains, Central Coast and Newcastle, Hunter, South Coast og Southern Highlands fra Sydney | Transport for NSW | en gratis nøkkel |
| **Australia**: Queensland | Queensland Rail Citytrain, sørøstlige Queensland (Brisbane) | Translink | ingenting |
| **Australia**: Sør-Australia | Adelaide Metros tog: linjene Belair, Gawler, Outer Harbor og Seaford | Adelaide Metro | ingenting |
| **Australia**: Vest-Australia | Perths tog, alle ni linjer, bare fra rutetabellen ([hvorfor](#perths-tog-vest-australia-australia)) | Public Transport Authority i Vest-Australia | ingenting |
| **Australia**: Victoria | V/Lines lokaltog: linjene Geelong, Ballarat, Bendigo, Seymour og Traralgon | Transport Victoria | en gratis nøkkel |
| **Europa**: Finland | VRs og HSLs lokaltog rundt Helsingfors | Fintraffic Digitraffic | ingenting |
| **Europa**: Irland | Irish Rails lokaltog rundt Dublin og Cork | Irish Rail, National Transport Authority | ingenting |
| **Europa**: Nederland | NS Sprinter-tog, hele landet | NS, OVapi | en gratis nøkkel |
| **Europa**: Norge | Vys L1, L2 og L4 (Oslo-området, Bergen), Go-Ahead Norges L5 (Stavanger), Flytoget (Oslo lufthavn) | Entur | ingenting |
| **Europa**: Spania | Renfe Cercanías og Rodalies de Catalunya, 15 nett: Madrid, Barcelona, Asturias, Sevilla, Cádiz, Málaga, Valencia, Murcia og Alicante, Cartagena, Ferrol, León, Bilbao, San Sebastián, Cantabria, Zaragoza | Renfe | ingenting |
| **Europa**: Sverige | SL Pendeltåg (Stockholm), Västtågens pendeltåg (Göteborg), Arlanda Express | Trafikverket | en gratis nøkkel |
| **Nord-Amerika**: USA | Metra (Chicago-området: Illinois, Wisconsin) | Metra | en gratis nøkkel |
| **Nord-Amerika**: USA | South Shore Line (Chicago til South Bend: Illinois, Indiana) | NICTD, via ETA SPOT | ingenting |

Står den ikke på listen? [Si fra](#hjelp-den-å-vokse). Der noen publiserer
dataene åpent, ser vi på om vi kan legge dem til.

⚠ **Et tog er bare så godt som banens strøm.** Noen baner plasserer togene
etter rutetabellen i stedet for med GPS, noen melder et tog bare ved signaler
noen minutter fra hverandre, og noen strømmer stopper eller fryser en stund.
Hver banes begrensninger står under [Alt på kartet, i detalj](#alt-på-kartet-i-detalj).

⚠ **Det er ikke banens offisielle informasjon.** Sjekk banens egen app eller
nettside før du reiser.

---

## En del av Live Track: de andre modulene

Live Track er et sett Home Assistant-integrasjoner, én for hver slags ting som
beveger seg, alle tegnet på det samme kartkortet. Hver virker alene; sammen
blir de ett levende bilde. De deler kartkortet og et Python-bibliotek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
så å installere én til legger ingen forespørsler til en kilde som en annen
allerede leser.

| Modul | Hva den viser på kartet | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | fly over deg via ADS-B, med ruter og typeikoner | utgitt |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | skip og båter via AIS, nær deg eller hvor som helst | utgitt |
| **Live Track Commuter Rail** | lokaltog i Nord-Amerika, Europa og Australia (denne modulen) | utgitt |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity- og fjerntog i Nord-Amerika, Europa og Australia | utgitt |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | fly og fartøy brukt av immigrasjons- og føderale politimyndigheter, fra offentlige lister | utgitt |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | vær, stormer og naturfarer | utgitt |
| Live Track Stations | avgangstavler og "på tide å gå"-varsler for hver stasjon | planlagt |
| Live Track Satellites | satellitter som passerer over deg | planlagt |
| Live Track Freight Trains | godstog og arbeidstog der jernbaner publiserer dem | planlagt |
| Live Track Transit | bybusser, trikker, ferger og T-bane | planlagt |
| Live Track Intercity Buses | ekspress- og regionbusser | planlagt |
| Live Track Commuter Buses | pendlerbusser | planlagt |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | det felles kartkortet hver modul tegner på | utgitt, installeres med hver modul |

Alt er gratis og åpen kildekode. Ingenting holdes tilbake for sponsorer.

---

## Før du begynner

* **Home Assistant** 2026.11 eller nyere.
* **Marketplace** (HACS) i Home Assistant, for å installere og oppdatere den
  på den enkle måten. Uten den kan du kopiere filene for hånd.
* **Internettilgang** for Home Assistant: hvert tog kommer fra banens egen
  åpne strøm.
* **Valgfritt: auto-entities** fra Marketplace, for å få markørene på kartet
  (se [Sett kartet på et dashbord](#sett-kartet-på-et-dashbord)).
* Ingenting å betale. 26 av de 31 banene trenger ingen
  konto; de andre fem trenger en egen, gratis nøkkel
  ([ovenfor](#slått-på-med-din-egen-gratis-nøkkel-eller-konto)).
* Home Assistant installerer selv Python-pakkene den trenger (`saw-livetrack`,
  `gtfs-realtime-bindings` og `tzdata`) første gang integrasjonen lastes.

---

## Installer den, trinn for trinn

### Fra Marketplace (anbefalt)

1. Åpne **Innstillinger → Marketplace** (HACS) i Home Assistant.
2. Søk etter **Live Track Commuter Rail** og åpne den.
3. Velg **Last ned** (eller **Installer**).
4. **Start Home Assistant på nytt**: **Innstillinger → System →
   Reparasjoner** tilbyr omstarten, eller bruk **Innstillinger → System →
   Omstart**.

Hvis søket ikke finner den, legg den til via lenken: velg **Legg til fra lenke**
(eller menyen med tre prikker → **Egendefinerte kodelager**), skriv inn
`StrausbergAutomationWorks/LiveTrackCommuterRail`, velg **Integrasjon** hvis du
blir spurt om typen, og fortsett deretter fra trinn 3.

Deretter tilbyr Marketplace hver nye versjon som en oppdatering.

### For hånd

1. Last ned kildekoden for
   [den nyeste versjonen](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Kopier mappen `custom_components/live_track_commuter_rail` inn i mappen
   `custom_components` i konfigurasjonsmappen til Home Assistant (lag
   `custom_components` hvis den ikke finnes).
3. Start Home Assistant på nytt.

For å oppdatere for hånd bytter du ut mappen med den nye versjonens og starter
på nytt.

---

## Sett den opp, trinn for trinn

1. Åpne **Innstillinger → Enheter og tjenester**.
2. Velg **Legg til integrasjon** (nede til høyre) og søk etter **Live Track
   Commuter Rail**.
3. **Region**: velg banens land, eller land og region. Bare steder med minst
   én bane står på listen. Velg **Send inn**.
4. **Bane**: velg banen. Velg **Send inn**.
5. **API-nøkkel**: bare for Metra, de tre svenske banene, NS Sprinter, NSW
   TrainLink Intercity og V/Line commuter. Lim inn nøkkelen din
   ([slik får du en](#gratis-nøkler-som-slår-på-mer-trinn-for-trinn)) og velg
   **Send inn**. De andre banene hopper over dette trinnet.

Det er alt. Togene vises innen et minutt. Der en banes neste stasjoner kommer
fra rutetabellen, fylles de inn i løpet av de første minuttene, når
rutetabellen er lastet ned. For å følge én bane til legger du til
integrasjonen på nytt. Samme bane to ganger blir avvist.

### Endre hva den viser: alternativene

Åpne **Innstillinger → Enheter og tjenester → Live Track Commuter Rail →
Konfigurer** (tannhjulet) på banen du vil endre. Hvert alternativ, med enkle
ord:

| Alternativ | Hva det gjør | Standard |
|---|---|---|
| **Oppdateringsintervall** | hvor ofte banens strøm leses, 15 til 600 sekunder. De fleste strømmer oppdateres omtrent hvert 30. sekund, så et kortere intervall viser sjelden mer | 30 sekunder |
| **Vis hensatt materiell** | av: materiell som ikke er i trafikk, vises bare mens det beveger seg, og forsvinner fra kartet etter 10 minutter i ro. På: alt materiell i strømmen vises, også hensatte tog | av |

---

## Gratis nøkler som slår på mer, trinn for trinn

Fem baner ber hver bruker om en egen nøkkel. Alle disse nøklene er gratis, og
alle som installerer Live Track Commuter Rail, skaffer sin egen. Du limer inn
nøkkelen når oppsettdialogen ber om den
([trinn 5 ovenfor](#sett-den-opp-trinn-for-trinn)). Bare nøkkelen
etterspørres: ikke noe passord og ingen hemmelighet. Nøkkelen lagres i Home
Assistant sammen med integrasjonen og skrives aldri til loggen. Hvis banen
fortsetter å avvise den, ber Home Assistant deg om en ny.

### Metra (Chicago-området, USA)

1. Åpne <https://metra.com/developers> og bla ned til **GTFS Realtime API Key
   Request Form**.
2. Fyll ut **First Name** (fornavn), **Last Name** (etternavn), **Email
   Address** (e-postadresse, spørres om to ganger) og **Purpose of Use**
   (bruk, for eksempel: Home Assistant).
3. Kryss av for **I have read and agree to the License Agreement.** (jeg har
   lest og godtar lisensavtalen, som står på
   <https://metra.com/gtfs-realtime-api-key-request-license-agreement>) og
   velg **Submit**.
4. Lim inn nøkkelen du får fra Metra, i **API-nøkkel** når du legger til
   Metra.

### Trafikverket (Sverige: SL Pendeltåg, Västtågen, Arlanda Express)

1. Åpne <https://data.trafikverket.se/oauth2/Account/register>.
2. Fyll ut **Email**, **Displayname** (visningsnavn), **Password** (passord)
   og **Confirm password**, kryss av for **Accept license and Agreement**, og
   velg **Register**.
3. Åpne <https://data.trafikverket.se/get-started> og velg **Create key**,
   under **Create a key**. Logg inn med kontoen du laget, og lag nøkkelen.
4. Lim den inn i **API-nøkkel** når du legger til en svensk bane. Én nøkkel
   gjelder for alle tre.

### NS (Nederland)

1. Åpne <https://apiportal.ns.nl/>, velg **Inloggen** (logg inn) og så
   **Externe bezoeker** (ekstern besøkende).
2. Fyll ut skjemaet og send det. En e-post bekrefter registreringen. Det kan
   ta opptil 5 minutter før API-ene vises i portalen.
3. Åpne siden til **Virtual Train API** (NS sine togposisjoner). Åpne
   produktet under **Related Products**, gi abonnementet ditt et navn, og
   velg **Subscribe**.
4. Når NS har godkjent abonnementet, står nøkkelen på profilsiden din. Lim
   den inn i **API-nøkkel** når du legger til NS Sprinter.

### Transport for NSW (New South Wales, Australia)

1. Åpne <https://opendata.transport.nsw.gov.au/>, velg **Register**, lag en
   konto og logg inn.
2. Velg profilikonet ditt og så **API Tokens**.
3. Skriv et navn på nøkkelen og velg **CREATE API TOKEN**. Kopier nøkkelen
   med en gang: nettstedet viser den bare én gang.
4. Lim den inn i **API-nøkkel** når du legger til NSW TrainLink Intercity.
   Lim inn bare nøkkelen: Live Track Commuter Rail legger selv til ordet
   `apikey`.

### Transport Victoria (Victoria, Australia)

1. Åpne <https://opendata.transport.vic.gov.au/>, velg **Login** og så
   **Sign up**.
2. Skriv inn opplysningene dine og velg **Create Account**. Skriv inn koden
   fra e-posten du får, og velg **Confirm**.
3. Portalen krever en autentiseringsapp på telefonen: skann QR-koden med den,
   skriv inn koden fra appen og velg **Confirm**. Logg så inn med
   e-postadressen, passordet og koden fra appen.
4. Velg **My Account** → **Profile** → **API tokens**. Nøkkelen din ligger
   der allerede. Lim den inn i **API-nøkkel** når du legger til V/Line
   commuter.

---

## Sett kartet på et dashbord

Kartet er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
kortet alle Live Track-moduler tegner på. **Det installeres med Live Track
Commuter Rail**: ingenting å laste ned, ingenting å kopiere, ingen ressurs å
legge til.

1. Åpne et dashbord, velg blyanten (**Rediger dashbord**) og så **Legg til
   kort**.
2. Bla helt ned og velg **Manuell**.
3. Lim inn dette og velg **Lagre**:

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

Denne formen trenger [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
fra Marketplace. Har du andre Live Track-moduler installert, legger du til ett
`- domain: geo_location`-filter til for hver av kildene deres
(`live_track_intercity_rail`, `live_track_aircraft` og så videre).

**Uten auto-entities:** LiveTrackMapCard kan selv velge hva det viser, med
`entity_filter`. Lim inn dette i stedet; ingenting mer må installeres:

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

Andre Live Track-moduler legges i `entity_filter` på samme måte: én regel
`- domain: geo_location` til for hver kilde.

**På kartet:**

* Hvert tog er en skive i linjens eller banens farger, med tognummer eller
  linje. På de fleste baner bytter fargene plass med retningen: fylt ut fra
  den største byen, hvit mot den.
* En pil viser retningen toget kjører. Et tog som står stille, beholder sin
  siste retning.
* **Pek** på et tog for å se bane, nummer eller linje, og hvor det kjører.
  **Klikk** på det for alle detaljene, også neste stasjon og forsinkelsen.

Hvis ressursene til dashbordene dine er satt i YAML
(`lovelace: resource_mode: yaml`), kan ingenting registreres for deg: en sak
under **Reparasjoner** gir da nøyaktig de linjene som skal legges til i
`configuration.yaml`. De ser slik ut, med integrasjonens egen adresse i
stedet for plassholderne:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_commuter_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Hver Live Track-modul har med seg en kopi av kortet og registrerer den når
Home Assistant starter. Sammen holder de nøyaktig én rad i **Innstillinger →
Dashbord → Ressurser**: den nyeste kortversjonen noen av dem har med seg,
aldri en eldre. Et kort du selv har installert via Marketplace, blir ikke
rørt. Når du fjerner den siste banen i denne modulen, går raden over til en
annen Live Track-modul, eller fjernes hvis ingen er igjen. Hvis
integrasjonens filer fjernes mens banene fortsatt er satt opp, og ingen annen
Live Track-modul er installert, fjerner du selv raden under **Innstillinger →
Dashbord → Ressurser**.

**For å installere kortet for hånd i stedet** følger du trinnene i
[kortets README](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
En rad du selv har laget for en kopi under `/local/` eller på en annen adresse,
blir aldri endret eller fjernet. Så lenge den laster kortet, overlater hver Live
Track-modul kortet til den, også når en modul har en nyere versjon, og ingenting
under **Reparasjoner** sier fra om det. For å gå tilbake til modulens kopi
fjerner du raden din under **Innstillinger → Dashbord → Ressurser** og starter
Home Assistant på nytt. Hvis du sletter filen til kopien din, fjerner du også
raden: så lenge en rad med en fil som er borte, står igjen, legger modulen ikke
til en egen rad.

Alle andre kartkort som viser `geo_location`-entiteter, viser også togene,
som vanlige markører.

---

## Bruk den i automasjoner

Alt er vanlige Home Assistant-entiteter, så automasjonsredigeringen virker med
dem, uten kode.

**Et varsel på telefonen når banen din nesten ikke viser noen tog** (strømmen
kan ha stoppet, eller trafikken kan være forstyrret):

1. **Innstillinger → Automasjoner og scener → Opprett automasjon → Opprett ny
   automasjon**.
2. **Når**: **Legg til utløser** → **Entitet** → **Numerisk tilstand krysset
   terskel**. Velg banens entitet **Trains in service**, og **Under** `3`.
3. **Så gjør**: **Legg til handling**, søk etter telefonens varslingshandling
   (den har telefonens navn), og skriv en melding, for eksempel:

   ```text
   Nesten ingen tog på kartet: sjekk banens egen app
   ```

4. **Lagre**.

**Flere ideer:** en lampe som slås på når et tog er innen 1 km (0,6 engelske
mil) fra hjemmet ditt i Oslo (Norge), ut fra markørenes avstand; en teller på
dashbordet for Metras tog i trafikk i morgenrushet (Chicago, USA); en melding
når dagens første tog går i Brisbane (Australia), når **Trains in service**
stiger over 0.

---

## Alt på kartet, i detalj

### Tog, og materiell som ikke er i trafikk

Hvert tog er én markør. Tilstanden er avstanden til hjemmet ditt, i
kilometer. Markøren vises når banens strøm melder toget, og fjernes når toget
forsvinner fra strømmen (etter 3 minutter, så et kort brudd i strømmen ikke
fjerner den).

* **Et tog i trafikk** har tognummeret eller linjen sin, slik banen nummererer
  dem (hver bane nedenfor sier hvilken).
* **Materiell som ikke er i trafikk** har `NIS` og enhetsnummeret, så et
  enhetsnummer aldri forveksles med et tognummer. Det vises bare mens det
  beveger seg, og forsvinner fra kartet etter 10 minutter i ro. Slå på **Vis
  hensatt materiell** for å se alt materiell i strømmen.
* **Mellom to posisjoner** flytter kartkortet markøren fra én virkelig
  posisjon til den neste. Ingenting diktes opp etter den siste virkelige
  posisjonen.
* **En posisjon som ikke ligger på et spor, avvises.** Et tog som meldes
  utenfor sporene, vises på sin siste posisjon som lå på dem, i høyst 10
  minutter, og skjules så til det er tilbake. Et tog som først ses utenfor
  sporene, vises ikke.
* **Forsinket og svært forsinket**: der banen publiserer en egen regel for et
  forsinket tog, bruker integrasjonen den, og sier det nedenfor.

På hvert tog: `marker_label`, `observed_at` (når posisjonen var riktig),
`course_deg` (mens det beveger seg), `next_stop` og `arrival_estimated_at`
(der de er kjent), `delay_min`, `stalled`, `attribution` og, mellom to
posisjoner, `previous_latitude`, `previous_longitude`, `previous_observed_at`
og `segment_duration_s`. En posisjon integrasjonen har anslått, i stedet for
en banen meldte, har `position_source: estimated`.

### NSW TrainLink Intercity (New South Wales, Australia)

Fra strømmene til NSW TrainLink og Sydney Trains hos Transport for NSW, med
din egen nøkkel. En avgang som står i begge strømmene, er én markør. Etiketten
er linjekoden (BMT, CCN, HUN, SCO, SHL); avgangen og endepunktene står i
boksen som vises når du peker ("Train KN56 · Bomaderry–Kiama"). Linjens farge
fra rutetabellen, fylt ut fra Sydney Central og snudd mot den. Tomme tog er
`NIS` og avgangen, i grått. Neste stasjon er en stasjon, aldri et spor. ⚠ En
posisjon som er eldre enn 10 minutter, tegnes ikke, og et tog fjernes når
avgangen er over. Forsinket fra 6 minutter (Transport for NSWs mål for
Intercity), svært forsinket fra 12.

### Queensland Rail Citytrain (Queensland, Australia)

Fra Translinks åpne strøm. ⚠ Posisjonene er faste punkter på sporet, ikke
GPS, uten fart og uten retning; pilen følger togets rute i rutetabellen. En
posisjon som er eldre enn 5 minutter, avvises, fordi strømmen beholder et tog
med frosset posisjon til trafikkdøgnet er slutt. Etiketten er linjens
T-nummer i Translinks linjefarger, snudd for tog sørover, og en stjerne for
ekstratog uten T-nummer. Forsinket fra 4 minutter, 6 på linjene Gold Coast,
Rosewood og Sunshine Coast (Queensland Rails egen regel).

### Adelaide Metro (Sør-Australia, Australia)

Fra Adelaide Metros åpne strøm, som også har trikkene og bussene deres (ikke
tegnet her). Posisjonene er GPS, med togets egen retning. Adelaide publiserer
ikke noe tognummer, så etiketten er de tre første bokstavene i rutekoden
Adelaide Metro bruker (SEA, FLN, GAW, BEL, OUT og så videre); boksen som vises
når du peker, gir hele koden ("SEAFRD to Seaford · railcar 4006"). Fargene er
linjekartets: Belair grønn, Seaford og Flinders oransje, Gawler rød, Outer
Harbor, Port Dock og Grange blå; fylt ut fra sentrum, hvit mot Adelaide
Railway Station. En posisjon som er eldre enn 5 minutter, eller mer enn 1 km
fra alle jernbanelinjer i Adelaide, avvises. Forsinket fra 5 minutter
(Adelaide Metros egen regel), svært forsinket fra 10.

### Perths tog (Vest-Australia, Australia)

⚠ **Perth publiserer ingen sanntidsposisjoner.** Hvert tog tegnes fra
rutetabellen til Public Transport Authority i Vest-Australia: plassert langs
ruten etter de planlagte tidene, merket som et anslag, uten forsinkelse.
Rutetabellen sjekkes én gang om dagen. Etiketten er de tre første bokstavene
i linjen (MAN, YAN, ARM, FRE, MID, ELL, AIR, THO; STA for en Stadium
Special); boksen som vises når du peker, sier "Mandurah Line · Perth
Underground–Mandurah". Fargene er linjekartets: fylt ut fra Perth, hvit mot
Perth.

### V/Line commuter (Victoria, Australia)

Fra V/Line-strømmen til Transport Victoria, med din egen nøkkel. Etiketten er
linjekoden (GEL, BAT, BGO, SER, TRN); tognummer og linje står i boksen som
vises når du peker ("Train 8037 · Bendigo - Melbourne via Gisborne"). Alle
linjer er V/Line-lilla: fylt ut fra Melbourne, hvit mot Southern Cross.
⚠ V/Lines posisjoner følger rutetabellen mer enn toget: en avgang forsvinner
fra strømmen omtrent et minutt etter planlagt ankomst, uansett hvor toget er,
og posisjonene fryser rundt midnatt. Derfor beholder et tog sin siste posisjon
i høyst 10 minutter og forlater så kartet, og et forsinket tog kan forsvinne
før siste stasjon. Forsinket fra 6 minutter (V/Lines regel for lokaltog),
svært forsinket fra 12.

### VRs og HSLs lokaltog (Finland)

Fra Fintraffics Digitraffic. Et tog er en avgang: tognummeret og dagen det
gikk. Etiketten er linjebokstaven, farget slik HSLs kart og stasjonsskilt
farger linjene: HSL-lilla mens neste stasjon ligger i HSLs takstsoner A til
E, VR-grønn utenfor dem. Et tog på vei fra Helsingfors er en fylt skive; et på
vei mot Helsingfors er hvitt. Et tog vises fra første stasjon til siste
stasjon, og fjernes så. Avganger på linje V uten passasjerer vises som `NIS`
mens de beveger seg. Mellom to posisjoner glir et tog langs sporene. Linjene I
og P gir ingen posisjon i Ringbanens tunnel ved Helsingfors lufthavn, så der
flytter integrasjonen toget langs sporene etter rutetabellen til en virkelig
posisjon kommer tilbake. Forsinket fra 4 minutter (VRs regel), svært forsinket
fra 8. En posisjon som er eldre enn 10 minutter, avvises.

### Irish Rail (Irland)

Fra Irish Rails sanntidstjeneste, med rutetabellen til National Transport
Authority for ruter og stasjoner. ⚠ Irish Rail melder et tog bare når det
passerer signaler noen minutter fra hverandre, så hvert tog tegnes fra
rutetabellen og sin siste forsinkelse, flyttet langs ruten; togene i Cork, som
Irish Rail ikke følger, kommer bare fra rutetabellen. Etiketten er tognummeret
uten bokstaven (P508 viser 508). Fargen er linjens på linjekartet til
Transport for Ireland, snudd mot Dublin eller Cork. Forsinket fra 5 minutter
(Irish Rails egen regel), svært forsinket fra 10.

### NS Sprinter (Nederland)

Fra NS sine kjøretøydata, med din egen nøkkel. Etiketten er tognummeret;
boksen som vises når du peker, sier "Sprinter 6632 · Dordrecht–Arnhem
Centraal". NS-gul med en NS-blå ring. Dette er den eneste strømmen her som
melder togets egen fart og retning, og begge sendes videre (`speed_kmh`,
`course_deg`). Neste stasjon og forsinkelsen kommer fra rutetabellen til
OVapi. Sporet er NS SpoorKaart, lastet ned én gang om dagen; et tog glir
langs det mellom to posisjoner, og en posisjon mer enn 1 km fra det avvises.
Forsinket fra 3 minutter (NS sin egen definisjon), svært forsinket fra 10.

### Vy, Go-Ahead Norge og Flytoget (Norge)

Fra Entur, hver bane i sin egen oppføring. Etiketten er linjekoden (L1, L2,
L4, L5, FLY1, FLY2); tognummer og linjenavn står i boksen som vises når du
peker. En L-linje har fargen sin fra rutetabellen, fylt ut fra Oslo S (Bergen
på L4, Stavanger på L5) og snudd mot den. Flytoget er grått med en oransje
ring mot Oslo lufthavn, og oransje med en grå ring derfra. Entur publiserer
verken fart eller retning, så pilen følger togets linje. I Oslos lange tunneler
flyttes et tog som slutter å sende posisjoner langs linjen til de kommer
tilbake. Forsinket fra 4 minutter, svært forsinket fra 8.

### Renfe Cercanías og Rodalies (Spania)

Fra Renfes åpne strøm, hvert av de 15 nettene i sin egen oppføring.
Etiketten er linjen (C5, R2N) i linjens egen farge fra Renfes rutetabell.
Tognummer og linjenavn står i boksen som vises når du peker. ⚠ Renfe
plasserer togene på ruten i stedet for med GPS, så de står stille og hopper
så. Et tog beveger seg bare framover langs sin egen linje: en posisjon ved
siden av den, bakover langs den eller umulig rask avvises, og den siste gode
beholdes i høyst 10 minutter. Et tog kalles stillestående først etter 6
minutter på samme sted. Renfe publiserer ingen regel for et forsinket tog, så
kartkortets egne terskler gjelder.

### SL Pendeltåg, Västtågen og Arlanda Express (Sverige)

Fra Trafikverket, med din egen gratis nøkkel (én nøkkel for alle tre).
Etiketten er tognummeret; merke, nummer og endestasjoner står i boksen som
vises når du peker. SL Pendeltåg er rosa, Västtågen lyseblå, Arlanda Express
gul; hver bytter farger mot Stockholm C (Stockholm City for pendeltågen) eller,
på en avgang som ikke stopper på noen av dem, mot den største endebyen.
Mellom to posisjoner glir et tog langs avgangens linje, og en posisjon mer enn
1 km fra den avvises. Forsinket fra 3 minutter på SL Pendeltåg (Region
Stockholms regel), svært forsinket fra 6; forsinket fra 6 og svært forsinket
fra 12 på de to andre (Trafikverkets regel).

### Metra og South Shore Line (USA)

Metra fra sin egen strøm, med din egen nøkkel; South Shore Line fra strømmen
ETA SPOT publiserer for NICTD, uten nøkkel. Etiketten er tognummeret. Metra
oppgir neste stasjon og tiden. Strømmen til South Shore Line gir bare et
stoppnummer og en forsinkelse, så rutetabellen gir stasjonen og tiden. En
posisjon mer enn 300 m fra alle spor i North American Rail Network (USA),
eller fra banens egen rute, avvises. ⚠ Noen dager har Metras strøm knyttet
bare få av togene sine til en avgang; resten vises da som `NIS` eller ikke i
det hele tatt, og kartet ser ut som en rolig dag. Telleren **Trains in
service** viser slike dager i ettertid.

---

## Alle entitetene den lager

For hver bane:

| Entitet | Hva det er |
|---|---|
| `sensor.<bane>_trains_in_service` | **Trains in service**: hvor mange tog i trafikk banens strøm melder nå. For Metra: `sensor.metra_chicago_area_trains_in_service` |
| `sensor.<bane>_vehicles_not_in_service` | **Vehicles not in service**: hvor mange kjøretøy som ikke er i trafikk strømmen melder |
| `geo_location.<bane>_unit_…` | én per tog eller kjøretøy (`geo_location.metra_unit_8426`); den kommer og går med toget. Hver har `source: live_track_commuter_rail`, og tilstanden er avstanden til hjemmet ditt i kilometer |

Navnene på entitetene er på engelsk, uansett språk i Home Assistant.

Hver bane har en kjent materiellflåte. En markørs entitets-ID kommer fra banen
og kjøretøyets nummer i strømmen, aldri fra etiketten, så samme kjøretøy får
samme entitets-ID hver gang det dukker opp: `geo_location.metra_unit_8426` er
alltid Metras vogn 8426. Markøren fjernes når kjøretøyet forsvinner fra
strømmen, eller etter 10 minutter hensatt mens **Vis hensatt materiell** er
av. Markørene har ingen unik ID, slik ingen kartmarkør i Live Track har, så de
kan ikke gis nytt navn, skjules eller få et område i grensesnittet. De to
sensorene har en unik ID og kan gis nytt navn.

Attributter som endres ved hver oppdatering, markørenes posisjoner og tider,
lagres i Home Assistants historikk, som for alle entiteter. De to sensorene
har ingen attributter, så de koster lite å ta vare på, og de er oversikten
over hvor mange tog som gikk en dag. For å holde markørene utenfor
historikken legger du dette til i `configuration.yaml`, og starter på nytt:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_unit_*
```

Hvis `configuration.yaml` allerede har en `recorder:`-seksjon, legger du bare
til mønsteret `geo_location.*_unit_*`, under `exclude:` og `entity_globs:`.
Mønsteret treffer bare togmarkørene til denne modulen. Et kartkort som er satt
til å tegne historikk, har da ikke noe spor å tegne.

---

## Hva den sender og laster ned

**Om posisjonen din.** Ingenting. Hjemmets posisjon brukes bare inne i Home
Assistant, for å gi avstanden til hvert tog. Nøkkelen din, der en bane trenger
en, sendes bare til den banen. Ingenting annet om deg sendes noe sted. Hver
tjeneste ser internettadressen din, slik alle nettsteder gjør.

**Hvor mye.** Hver sanntidsstrøm leses ved hver oppdatering, hvert 30. sekund
som standard (**Oppdateringsintervall**, 15 til 600 sekunder), eller sjeldnere
der tabellen sier det. Der flere Live Track-moduler leser samme strøm, leser
én felles klient den én gang for alle. Målt 19. november 2026, 02:20 til
02:40 UTC:

| Bane | Sanntidsstrøm, én lesing | Rutetabell |
|---|---|---|
| NSW TrainLink Intercity (Australia) | 402 KB fra fire strømmer, høyst én gang per 55 sekunder | 51 MB (to rutetabeller), når den endres, sjekket daglig |
| Queensland Rail Citytrain (Australia) | 141 KB | 42 MB, hver dag |
| Adelaide Metro (Australia) | 298 KB | 20 MB, når Adelaide Metro publiserer en ny versjon |
| Perths tog (Australia) | ingen: Perth publiserer ingen sanntidsstrøm | 28 MB, når den endres, sjekket daglig |
| V/Line commuter (Australia) | 14 KB | 59 MB, når den endres, sjekket daglig |
| VRs og HSLs lokaltog (Finland) | 1,1 KB komprimert for posisjonene, pluss endringene i dagens tog én gang i minuttet | ingen fil: dagens tog kommer med sanntidsdataene |
| Irish Rail (Irland) | 0,2 KB, høyst én gang per 55 sekunder | 6,6 MB, når den endres, sjekket daglig; stasjonslisten, 18 KB, én gang i uken |
| NS Sprinter (Nederland) | 1,2 KB; forsinkelser fra OVapi, 1,6 MB, hvert 5. minutt og bare når de endres | rutetabellen til OVapi, 274 MB, høyst én gang i uken og bare når den endres; sporkartet til NS, 1,3 MB, hver dag |
| Vy, Go-Ahead Norge, Flytoget (Norge) | Vy 497 KB, Go-Ahead Norge 7 KB, Flytoget 233 KB | Vy 67 MB, Go-Ahead Norge 20 MB, Flytoget 0,6 MB, når den endres, sjekket daglig |
| Renfe Cercanías og Rodalies (Spania) | én strøm for alle de 15 nettene: 26 byte, om natten når ingen tog går | 16 MB, hver dag |
| SL Pendeltåg, Västtågen, Arlanda Express (Sverige) | 3,7 KB første gang, så omtrent 2 KB endringer | ingen; stasjonslisten, 0,15 MB, hver dag |
| Metra (USA) | 18 KB | 0,4 MB, hver dag |
| South Shore Line (USA) | under 1 KB | 0,14 MB, hver dag |

⚠ Da dette ble målt, var det dag i Australia, kveld i USA og natt i Europa.
En sanntidsstrøm er minst om natten: om dagen er de europeiske strømmene
større enn tabellen viser.

**Etter en feil.** De siste gode posisjonene vises i to mislykkede lesinger
til; så merkes togene som utilgjengelige til strømmen svarer. En rutetabell
som ikke lar seg laste ned, prøves igjen en time senere, og kopien du har,
brukes videre. Hvis banen fortsetter å avvise nøkkelen din, ber Home
Assistant om en ny.

**På disken.** Rutetabellene lagres i Home Assistants mappe `.storage` under
navn som begynner med `saw_`, delt med de andre Live Track-modulene som leser
samme bane: de som er merket "når den endres" slik de ble lastet ned, de
andre som et mindre utdrag. Hvis du fjerner Live Track Commuter Rail og ingen
annen Live Track-modul bruker dem, kan du slette dem for hånd.

---

## Hjelp den å vokse

Live Track Commuter Rail vokser fortsatt. Vi legger til baner og land når vi
finner dem, og vi vil vite hva du ønsker deg neste gang.

### Foreslå noe

Mangler landet eller banen din? Er noe feil, eller vanskelig å forstå? Si fra
på den måten som er enklest for deg:

* [**Fyll ut et kort skjema**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=nb.yml)
  på norsk. Du trenger en gratis GitHub-konto.
* **Send en e-post** til
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Ingen konto nødvendig.

Uansett hjelper det om du forteller oss:

* hva du vil se, og hvor i verden;
* en lenke til hvor dataene publiseres, hvis du kjenner til en (en side med
  åpne data, en offentlig strøm, en tjenestes nettsted): ikke nødvendig, men
  det hjelper;
* språket i Home Assistant, hvis problemet er ordlyden eller en
  oversettelse.

Skriv på engelsk eller på ditt eget språk, det som er enklest for deg.

### Legg det til selv, med vår hjelp

Hvis du vil legge til noe selv, hjelper vi deg, fra det første spørsmålet til
den ferdige versjonen. Du trenger ikke være utvikler for å begynne:

* **En oversettelse.** Ordene i oppsettdialogen er en kort liste med fraser i
  én tekstfil. Vi viser deg hvilken fil og hvilke linjer.
* **En ny bane.** Fortell oss hvor dataene publiseres. Vi kan skrive koden
  sammen, eller se over din.
* **Testing der du bor.** Installer den, se på din del av kartet, og fortell
  oss hva som stemmer og hva som ikke gjør det.
* **En rettelse av denne README-filen.** Hvis et trinn ikke stemte med det du
  så, fortell oss hva du så.

[**Fortell oss hva du har i tankene**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=nb.yml)
eller skriv til
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
så svarer vi med de neste trinnene.

---

## Språk

Denne README-filen: [English](README.md), [Suomi](README.fi.md),
[Svenska](README.sv.md), **Norsk bokmål**, [Español](README.es.md),
[Nederlands](README.nl.md), [Gaeilge](README.ga.md). Hver oversatte
README-fil er fullstendig. Ingen er ennå lest av noen med språket som
morsmål. Er norsk morsmålet ditt, si gjerne fra om denne README-filen leses
godt: se [Hjelp den å vokse](#hjelp-den-å-vokse).

Oppsettdialogen og alternativene vises på språket i Home Assistant når det er
ett av disse: English, Suomi, Svenska, Norsk bokmål, Español, Nederlands,
Gaeilge. Alle andre språk viser engelsk.

Funnet en feil i en oversettelse, eller trenger du et annet språk? Si fra på
<https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues>,
eller [oversett med vår hjelp](#legg-det-til-selv-med-vår-hjelp).

---

## Kreditering og lisenser

Hver bane leses mens integrasjonen kjører, av Home Assistant, fra banens egen
publiserte strøm; ingenting fra en sanntidsstrøm ligger i dette kodelageret.
Hvert tog oppgir kilden sin i attributtet `attribution`. Hver banes vilkår
gjelder deg, som den som mottar dataene.

* **Metra** (USA): GTFS-Realtime, under
  [Metras lisensavtale](https://metra.com/gtfs-realtime-api-key-request-license-agreement),
  som du godtar når du ber om en nøkkel.
* **South Shore Line** (NICTD, USA): åpen strøm og rutetabell som ETA SPOT
  publiserer for NICTD, uten nøkkel og uten lisensavtale.
* **Translink** (Queenslands regjering, Australia): data under CC BY 4.0
  ([åpne data](https://translink.com.au/about-translink/open-data)).
* **Fintraffic / digitraffic.fi** (Finland): data under CC BY 4.0. **HSL**
  (Finland): takstsoner, CC BY 4.0.
* **Renfe** (Spania): data under CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)), bearbeidet.
* **Entur** (Norge): data under Norsk lisens for offentlige data
  ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)), distribuert av Entur.
* **Trafikverket** (Sverige): data under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irland): sanntidsdata; Irish Rail publiserer ingen vilkår.
  Rutetabell fra [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irland), CC BY 4.0.
* **NS** (Nederland): kjøretøydata, med din egen nøkkel, fra
  [NS API-portal](https://apiportal.ns.nl/). Rutetabell og forsinkelser fra
  [OVapi](https://gtfs.ovapi.nl), CC0.
* **Transport for NSW** (Australia): data under CC BY 4.0
  ([datalisens](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australia): data under CC BY 4.0
  ([åpne data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Adelaide Metro**, Department for Infrastructure and Transport, South
  Australia: data under CC BY 4.0 ([informasjon for utviklere](https://www.adelaidemetro.com.au/developer-info)).
* **Public Transport Authority i Vest-Australia**: rutetabelldata tilgjengelig
  gratis fra www.transperth.wa.gov.au
  ([tilgang til geodata](https://www.transperth.wa.gov.au/About/Spatial-Data-Access)).
* **Sporfiler i `rail/`**: North American Rail Network (USAs
  samferdselsdepartement), allemannseie; Fintraffics spornett, CC BY 4.0,
  bearbeidet; Flytogets linjer fra Enturs data, NLOD 2.0, bearbeidet; de
  svenske linjene lagt på OpenStreetMap, (c) OpenStreetMap-bidragsytere, ODbL
  1.0; byenes folketall fra Statistiska centralbyrån (Sverige), CC0. Hva som
  er endret, står i [ATTRIBUTION.md](ATTRIBUTION.md).
* **Kartkortet** er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, en kopi av [ha-map-card](https://github.com/nathan-gs/ha-map-card) av
  nathan-gs, MIT. Kartflisene og krediteringen deres står i README-filen der.

Ingen av disse organisasjonene har laget eller godkjent denne integrasjonen.

**Kode**: MIT, i [LICENSE](LICENSE).

**For utviklere:** hver bane er én adapter i
`custom_components/live_track_commuter_rail/operators/`; sporfilene i `rail/`
bygges på nytt med skriptene i `tools/` (`build_rail.py`, `build_tracks.py`,
`build_flytoget_lines.py`, `sweden_lines.py`). Testene kjøres med
`python -m unittest discover -s tests`.

---

## Søkeord

Home Assistant tog · tog i sanntid · togkart · lokaltog · Vy · Flytoget ·
Go-Ahead Norge · Jærbanen · Entur · tog på kartet · pendeltåg · SL ·
lähijunat · HSL · VR · NS · Sprinter · Renfe Cercanías · Rodalies · Irish
Rail · Metra · South Shore Line · Queensland Rail · Translink · NSW
TrainLink · V/Line · Adelaide Metro · Perths tog · GTFS-Realtime ·
geo_location · kartkort · Lovelace · HACS · Marketplace · Live Track ·
LiveTrack · StrausbergAutomationWorks

---

**Anerkjennelse.** StrausbergAutomationWorks anerkjenner urfolkene i alle land
og farvann som dette kartet dekker, over hele verden, og viser respekt for deres
eldste, før og nå.
