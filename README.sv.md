# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · **Svenska** · [Norsk bokmål](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md) · [Alla språk](#språk)

**Pendeltåg för Home Assistant, på en karta.** Live Track Commuter Rail visar
varje tåg på de pendeltågsbanor du väljer på din Home Assistant-karta, i
realtid: var det är, dess tågnummer eller linje, om det är försenat och dess
nästa station. Varje bana läggs till för sig, från bananas egna öppna data.

> **Live Track Commuter Rail är en modul i Live Track**, en familj av Home
> Assistant-integrationer som ritar allt som rör sig, och vädret det rör sig
> genom, på en gemensam karta: flygplan, fartyg, tåg och väder. Installera den
> ensam, eller bredvid de andra modulerna
> ([lista nedan](#en-del-av-live-track-de-andra-modulerna)).

> **Växer, och öppen för idéer.** Live Track Commuter Rail täcker i dag 31
> banor i 8 länder på 3 kontinenter, och vi lägger till fler banor och länder.
> Saknas din? [Föreslå den](#hjälp-den-att-växa), eller lägg till den själv:
> vi hjälper dig.

**Status: 0.1.4, utgiven.** Läggs till i Marknadsplatsen via sin länk
([nedan](#installera-den-steg-för-steg)); den finns ännu inte i
Marknadsplatsens katalog.

Originalarbete av StrausbergAutomationWorks. Inte knuten till, eller godkänd
av, Metra, Northern Indiana Commuter Transportation District (NICTD), ETA
SPOT, Renfe, Fintraffic, HSL, VR, Entur, Vy, Go-Ahead Norge, Flytoget,
Trafikverket, SL, Västtågen, Arlanda Express, Irish Rail, National Transport
Authority (Irland), NS, OVapi, Translink, Queensland Rail, Transport for NSW,
Transport Victoria, V/Line, Adelaide Metro, Public Transport Authority i
Västaustralien eller någon annan bana.

---

## Innehåll

1. [Allt den gör](#allt-den-gör)
2. [Var den fungerar](#var-den-fungerar)
3. [En del av Live Track: de andra modulerna](#en-del-av-live-track-de-andra-modulerna)
4. [Innan du börjar](#innan-du-börjar)
5. [Installera den, steg för steg](#installera-den-steg-för-steg)
6. [Ställ in den, steg för steg](#ställ-in-den-steg-för-steg)
7. [Gratis nycklar som slår på mer, steg för steg](#gratis-nycklar-som-slår-på-mer-steg-för-steg)
8. [Lägg kartan på en kontrollpanel](#lägg-kartan-på-en-kontrollpanel)
9. [Använd den i automatiseringar](#använd-den-i-automatiseringar)
10. [Allt på kartan, i detalj](#allt-på-kartan-i-detalj)
11. [Alla entiteter den skapar](#alla-entiteter-den-skapar)
12. [Vad den skickar och laddar ner](#vad-den-skickar-och-laddar-ner)
13. [Hjälp den att växa](#hjälp-den-att-växa)
14. [Språk](#språk)
15. [Tack och licenser](#tack-och-licenser)
16. [Sökord](#sökord)

---

## Allt den gör

### På kartan, utan något att ställa in

Du lägger till en **bana**: du väljer ett land eller en region, och sedan en
av dess pendeltågsbanor. Allt nedan visas då för den banan. Lägg till
integrationen igen för varje annan bana du vill ha.

| Vad | Var | Från |
|---|---|---|
| **Tåg i trafik**: en markör per tåg, med tågnummer eller linje, i banans egna färger, vänd åt det håll tåget går | alla banor | varje banas eget realtidsflöde |
| **Förseningar**: ett tåg visas som försenat eller mycket försenat enligt banans egen regel, där banan publicerar en | alla banor som rapporterar förseningar | varje banas flöde och tidtabell |
| **Nästa station och tid**: stationen där tåget stannar härnäst, och när det väntas dit | alla banor vars flöde eller tidtabell anger det | varje banas flöde och tidtabell |
| **Tåg som följer spåret**: mellan två positioner glider tåget längs linjen, inte rakt över | Finland, Nederländerna, Sverige | spårfiler som följer med integrationen eller som den laddar ner |
| **Fordon som inte är i trafik**: tomma tåg mellan depåer, visade medan de rör sig | banor vars flöden rapporterar dem | varje banas flöde |
| **Två räknare per bana**: tåg i trafik och fordon som inte är i trafik | alla banor | samma flöde |

### Påslaget med din egen gratis nyckel eller ditt eget konto

| Gratis nyckel eller konto | Vad den lägger till |
|---|---|
| Nyckel från **Metra** | Metras tåg (Chicagoområdet, USA) |
| Nyckel från **Trafikverket** | SL Pendeltåg, Västtågens pendeltåg och Arlanda Express (Sverige) |
| Nyckel från **NS API-portal** | NS Sprinter-tåg (Nederländerna) |
| Nyckel från **Transport for NSW Open Data** | NSW TrainLink Intercity-tåg (New South Wales, Australien) |
| Nyckel från **Transport Victoria Open Data** | V/Lines pendeltåg (Victoria, Australien) |

Var och en tar några minuter att skaffa: [steg för steg nedan](#gratis-nycklar-som-slår-på-mer-steg-för-steg).
De andra 26 banorna behöver ingen nyckel.

---

## Var den fungerar

| Region | Vad du får | Från | Behöver |
|---|---|---|---|
| **Australien**: New South Wales | NSW TrainLink Intercity: linjerna Blue Mountains, Central Coast and Newcastle, Hunter, South Coast och Southern Highlands från Sydney | Transport for NSW | en gratis nyckel |
| **Australien**: Queensland | Queensland Rail Citytrain, sydöstra Queensland (Brisbane) | Translink | ingenting |
| **Australien**: South Australia | Adelaide Metros tåg: linjerna Belair, Gawler, Outer Harbor och Seaford | Adelaide Metro | ingenting |
| **Australien**: Victoria | V/Lines pendeltåg: linjerna Geelong, Ballarat, Bendigo, Seymour och Traralgon | Transport Victoria | en gratis nyckel |
| **Australien**: Västaustralien | Perths tåg, alla nio linjer, endast från tidtabellen ([varför](#perths-tåg-västaustralien-australien)) | Public Transport Authority i Västaustralien | ingenting |
| **Europa**: Finland | VR:s och HSL:s närtåg runt Helsingfors | Fintraffic Digitraffic | ingenting |
| **Europa**: Irland | Irish Rails pendeltåg runt Dublin och Cork | Irish Rail, National Transport Authority | ingenting |
| **Europa**: Nederländerna | NS Sprinter-tåg, hela landet | NS, OVapi | en gratis nyckel |
| **Europa**: Norge | Vys L1, L2 och L4 (Osloområdet, Bergen), Go-Ahead Norges L5 (Stavanger), Flytoget (Oslo flygplats) | Entur | ingenting |
| **Europa**: Spanien | Renfe Cercanías och Rodalies de Catalunya, 15 nät: Madrid, Barcelona, Asturien, Sevilla, Cádiz, Málaga, Valencia, Murcia och Alicante, Cartagena, Ferrol, León, Bilbao, San Sebastián, Kantabrien, Zaragoza | Renfe | ingenting |
| **Europa**: Sverige | SL Pendeltåg (Stockholm), Västtågens pendeltåg (Göteborg), Arlanda Express | Trafikverket | en gratis nyckel |
| **Nordamerika**: USA | Metra (Chicagoområdet: Illinois, Wisconsin) | Metra | en gratis nyckel |
| **Nordamerika**: USA | South Shore Line (Chicago till South Bend: Illinois, Indiana) | NICTD, via ETA SPOT | ingenting |

Finns den inte med? [Säg till](#hjälp-den-att-växa). Där någon publicerar
data öppet ser vi på om vi kan lägga till den.

⚠ **Ett tåg är bara så bra som banans flöde.** Vissa banor placerar sina tåg
efter tidtabellen i stället för med GPS, vissa rapporterar ett tåg bara vid
signaler några minuter isär, och vissa flöden stannar eller fryser en tid.
Varje banas begränsningar står under [Allt på kartan, i detalj](#allt-på-kartan-i-detalj).

⚠ **Det är inte banans officiella information.** Titta i banans egen app
eller på dess webbplats innan du reser.

---

## En del av Live Track: de andra modulerna

Live Track är en uppsättning Home Assistant-integrationer, en för varje sorts
sak som rör sig, alla ritade på samma kartkort. Var och en fungerar ensam;
tillsammans blir de en levande bild. De delar kartkortet och ett
Python-bibliotek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
så att installera en till lägger inga förfrågningar till en källa som en annan
redan läser.

| Modul | Vad den visar på kartan | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | flygplan ovanför dig via ADS-B, med rutter och typikoner | utgiven |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | fartyg och båtar via AIS, nära dig eller var som helst | utgiven |
| **Live Track Commuter Rail** | pendeltåg i Nordamerika, Europa och Australien (den här modulen) | utgiven |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity- och fjärrtåg i Nordamerika, Europa och Australien | utgiven |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | flygplan och fartyg som används av immigrations- och federala polismyndigheter, från offentliga listor | utgiven |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | väder, stormar och naturrisker | utgiven |
| Live Track Stations | avgångstavlor och "dags att gå"-aviseringar för varje station | planerad |
| Live Track Satellites | satelliter som passerar ovanför | planerad |
| Live Track Freight Trains | godståg och arbetståg där järnvägar publicerar dem | planerad |
| Live Track Transit | stadsbussar, spårvagnar, färjor och tunnelbana | planerad |
| Live Track Intercity Buses | fjärr- och regionbussar | planerad |
| Live Track Commuter Buses | pendelbussar | planerad |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | det gemensamma kartkortet som varje modul ritar på | utgivet, installeras med varje modul |

Allt är gratis och öppen källkod. Inget hålls tillbaka för sponsorer.

---

## Innan du börjar

* **Home Assistant** 2026.11 eller senare.
* **Marknadsplatsen** (HACS) i din Home Assistant, för att installera och
  uppdatera den på det enkla sättet. Utan den kan du kopiera filerna för hand.
* **Internetåtkomst** för Home Assistant: varje tåg kommer från banans eget
  öppna flöde.
* **Valfritt: auto-entities** från Marknadsplatsen, för att få markörerna på
  kartan (se [Lägg kartan på en kontrollpanel](#lägg-kartan-på-en-kontrollpanel)).
* Inget att betala. 26 av de 31 banorna behöver
  inget konto; de andra fem behöver en egen, gratis nyckel
  ([ovan](#påslaget-med-din-egen-gratis-nyckel-eller-ditt-eget-konto)).
* Home Assistant installerar själv de Python-paket som behövs
  (`saw-livetrack`, `gtfs-realtime-bindings` och `tzdata`) första gången
  integrationen läses in.

---

## Installera den, steg för steg

### Från Marknadsplatsen (rekommenderas)

Live Track Commuter Rail finns ännu inte i Marknadsplatsens katalog. Lägg
till den via sin länk:

1. Öppna **Inställningar → Marknadsplatsen** (HACS) i Home Assistant.
2. Välj **Lägg till från länk** (eller menyn med tre punkter → **Anpassade
   förråd**).
3. Ange `StrausbergAutomationWorks/LiveTrackCommuterRail`. Om du får frågan om
   typ, välj **Integration**.
4. Leta upp **Live Track Commuter Rail** i listan och välj **Ladda ner** eller
   **Installera**.
5. **Starta om Home Assistant**: **Inställningar → System → Lagningar**
   erbjuder omstarten, eller använd **Inställningar → System → Starta om**.

Sedan erbjuder Marknadsplatsen varje ny version som en uppdatering.

### För hand

1. Ladda ner källkoden för
   [den senaste versionen](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Kopiera dess mapp `custom_components/live_track_commuter_rail` till mappen
   `custom_components` i Home Assistants konfigurationsmapp (skapa
   `custom_components` om den inte finns).
3. Starta om Home Assistant.

För att uppdatera för hand byter du ut mappen mot den nya versionens och
startar om.

---

## Ställ in den, steg för steg

1. Öppna **Inställningar → Enheter och tjänster**.
2. Välj **Lägg till integration** (nere till höger) och sök efter **Live
   Track Commuter Rail**.
3. **Region**: välj banans land, eller land och region. Bara platser med minst
   en bana finns med. Välj **Bekräfta**.
4. **Bana**: välj banan. Välj **Bekräfta**.
5. **API-nyckel**: bara för Metra, de tre svenska banorna, NS Sprinter, NSW
   TrainLink Intercity och V/Line commuter. Klistra in din nyckel
   ([så får du en](#gratis-nycklar-som-slår-på-mer-steg-för-steg)) och välj
   **Bekräfta**. De andra banorna hoppar över det här steget.

Det är allt. Tågen visas inom en minut. Där en banas nästa stationer kommer
från tidtabellen fylls de i under de första minuterna, när tidtabellen har
laddats ner. För att följa en till bana lägger du till integrationen igen.
Samma bana två gånger nekas.

### Ändra vad den visar: alternativen

Öppna **Inställningar → Enheter och tjänster → Live Track Commuter Rail →
Konfigurera** (kugghjulet) på den bana du vill ändra. Varje alternativ, med
enkla ord:

| Alternativ | Vad det gör | Standard |
|---|---|---|
| **Uppdateringsintervall** | hur ofta banans flöde läses, 15 till 600 sekunder. De flesta flöden uppdateras ungefär var 30:e sekund, så ett kortare intervall visar sällan mer | 30 sekunder |
| **Visa uppställda fordon** | av: fordon som inte är i trafik visas bara medan de rör sig och försvinner från kartan efter 10 minuter stillastående. På: alla fordon i flödet visas, även uppställda tåg | av |

---

## Gratis nycklar som slår på mer, steg för steg

Fem banor ber varje användare om en egen nyckel. Alla dessa nycklar är
gratis, och varje person som installerar Live Track Commuter Rail skaffar sin
egen. Du klistrar in nyckeln när inställningsdialogen ber om den
([steg 5 ovan](#ställ-in-den-steg-för-steg)). Bara nyckeln efterfrågas: inget
lösenord och ingen hemlighet. Nyckeln sparas i Home Assistant med
integrationen och skrivs aldrig i loggen. Om banan fortsätter att neka den
ber Home Assistant dig om en ny.

### Metra (Chicagoområdet, USA)

1. Öppna <https://metra.com/developers> och bläddra ner till **GTFS Realtime
   API Key Request Form**.
2. Fyll i **First Name** (förnamn), **Last Name** (efternamn), **Email
   Address** (e-postadress, efterfrågas två gånger) och **Purpose of Use**
   (användning, till exempel: Home Assistant).
3. Kryssa i **I have read and agree to the License Agreement.** (jag har läst
   och godtar licensavtalet, som finns på
   <https://metra.com/gtfs-realtime-api-key-request-license-agreement>) och
   välj **Submit**.
4. Klistra in nyckeln du får från Metra i **API-nyckel** när du lägger till
   Metra.

### Trafikverket (Sverige: SL Pendeltåg, Västtågen, Arlanda Express)

1. Öppna <https://data.trafikverket.se/oauth2/Account/register>.
2. Fyll i **Email**, **Displayname** (visningsnamn), **Password** (lösenord)
   och **Confirm password**, kryssa i **Accept license and Agreement** och
   välj **Register**.
3. Öppna <https://data.trafikverket.se/get-started> och välj **Create key**,
   under **Create a key**. Logga in med kontot du skapade och skapa nyckeln.
4. Klistra in den i **API-nyckel** när du lägger till en svensk bana. En
   nyckel räcker för alla tre.

### NS (Nederländerna)

1. Öppna <https://apiportal.ns.nl/>, välj **Inloggen** (logga in) och sedan
   **Externe bezoeker** (extern besökare).
2. Fyll i formuläret och skicka det. Ett e-postmeddelande bekräftar
   registreringen. Det kan ta upp till 5 minuter innan API:erna visas i
   portalen.
3. Öppna sidan för **Virtual Train API** (NS tågpositioner). Öppna dess
   produkt under **Related Products**, ge ditt abonnemang ett namn och välj
   **Subscribe**.
4. När NS har godkänt abonnemanget finns din nyckel på din profilsida.
   Klistra in den i **API-nyckel** när du lägger till NS Sprinter.

### Transport for NSW (New South Wales, Australien)

1. Öppna <https://opendata.transport.nsw.gov.au/>, välj **Register**, skapa
   ett konto och logga in.
2. Välj din profilikon och sedan **API Tokens**.
3. Skriv ett namn för nyckeln och välj **CREATE API TOKEN**. Kopiera nyckeln
   direkt: webbplatsen visar den bara en gång.
4. Klistra in den i **API-nyckel** när du lägger till NSW TrainLink
   Intercity. Klistra in bara nyckeln: Live Track Commuter Rail lägger själv
   till ordet `apikey`.

### Transport Victoria (Victoria, Australien)

1. Öppna <https://opendata.transport.vic.gov.au/>, välj **Login** och sedan
   **Sign up**.
2. Fyll i dina uppgifter och välj **Create Account**. Skriv in koden från
   e-postmeddelandet du får och välj **Confirm**.
3. Portalen kräver en autentiseringsapp i telefonen: skanna QR-koden med
   den, skriv in appens kod och välj **Confirm**. Logga sedan in med din
   e-postadress, ditt lösenord och appens kod.
4. Välj **My Account** → **Profile** → **API tokens**. Din nyckel finns redan
   där. Klistra in den i **API-nyckel** när du lägger till V/Line commuter.

---

## Lägg kartan på en kontrollpanel

Kartan är [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
kortet som alla Live Track-moduler ritar på. **Det installeras med Live Track
Commuter Rail**: inget att ladda ner, inget att kopiera, ingen resurs att
lägga till.

1. Öppna en kontrollpanel, välj pennan (**Redigera kontrollpanel**) och sedan
   **Lägg till kort**.
2. Bläddra längst ner och välj **Manuell**.
3. Klistra in detta och välj **Spara**:

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

Markörerna behöver [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
från Marknadsplatsen. Har du andra Live Track-moduler installerade lägger du
till ett `- domain: geo_location`-filter till för var och en av deras källor
(`live_track_intercity_rail`, `live_track_aircraft` och så vidare).

**På kartan:**

* Varje tåg är en skiva i linjens eller banans färger, med tågnummer eller
  linje. På de flesta banor byter färgerna plats med riktningen: fylld från
  den största staden, vit mot den.
* En pil visar åt vilket håll tåget går. Ett stillastående tåg behåller sin
  senaste riktning.
* **Peka** på ett tåg för att se bana, nummer eller linje, och var det går.
  **Klicka** på det för alla detaljer, även nästa station och förseningen.

Om dina kontrollpanelers resurser anges i YAML
(`lovelace: resource_mode: yaml`) kan inget registreras åt dig: ett ärende
under **Lagningar** ger då exakt de rader som ska läggas till i
`configuration.yaml`. De ser ut så här, med integrationens egen adress i
stället för platshållarna:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_commuter_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Varje Live Track-modul har med sig en kopia av kortet och registrerar den när
Home Assistant startar. Tillsammans håller de exakt en rad i **Inställningar →
Kontrollpaneler → Resurser**: den nyaste kortversionen som någon av dem har
med sig, aldrig en äldre. Ett kort som du själv har installerat via
Marknadsplatsen lämnas orört. När du tar bort den här modulens sista bana går
raden över till en annan Live Track-modul, eller tas bort om ingen finns
kvar. Om integrationens filer tas bort medan dess banor fortfarande är
inställda, och ingen annan Live Track-modul är installerad, tar du själv bort
raden under **Inställningar → Kontrollpaneler → Resurser**.

**För att i stället installera kortet för hand** följer du stegen i
[kortets README](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
En rad som du själv har skapat för en kopia under `/local/` pekas om till den
här modulens kopia bara när den kopian är en nyare version.

Varje annat kartkort som visar `geo_location`-entiteter visar också tågen,
som vanliga markörer.

---

## Använd den i automatiseringar

Allt är vanliga Home Assistant-entiteter, så automatiseringsredigeraren
fungerar med dem, utan kod.

**En avisering i telefonen när din bana nästan inte visar några tåg** (flödet
kan ha stannat, eller trafiken kan vara störd):

1. **Inställningar → Automatiseringar och scener → Skapa automatisering →
   Skapa ny automatisering**.
2. **När**: **Lägg till utlösare** → **Entitet** → **Numeriskt tillstånd
   passerat tröskelvärde**. Välj banans entitet **Trains in service** och
   **Under** `3`.
3. **Gör då**: **Lägg till åtgärd**, sök efter telefonens aviseringsåtgärd
   (den har telefonens namn) och skriv ett meddelande, till exempel:

   ```text
   Nästan inga tåg på kartan: titta i banans egen app
   ```

4. **Spara**.

**Fler idéer:** en lampa som tänds när ett tåg är inom 1 km (0,6 engelska
mil) från ditt hem i Stockholm (Sverige), från markörernas avstånd; en räknare
på kontrollpanelen för Metras tåg i trafik i morgonrusningen (Chicago, USA);
ett meddelande när dagens första tåg går i Brisbane (Australien), när
**Trains in service** stiger över 0.

---

## Allt på kartan, i detalj

### Tåg, och fordon som inte är i trafik

Varje tåg är en markör. Dess tillstånd är avståndet till ditt hem, i
kilometer. Markören visas när banans flöde rapporterar tåget och tas bort när
tåget lämnar flödet (efter 3 minuter, så att ett kort avbrott i flödet inte
tar bort den).

* **Ett tåg i trafik** har sitt tågnummer eller sin linje, så som banan
  numrerar dem (varje bana nedan säger vilket).
* **Fordon som inte är i trafik** har `NIS` och sitt fordonsnummer, så att
  ett fordonsnummer aldrig misstas för ett tågnummer. De visas bara medan de
  rör sig och försvinner från kartan efter 10 minuter stillastående. Slå på
  **Visa uppställda fordon** för att se alla fordon i flödet.
* **Mellan två positioner** flyttar kartkortet markören från en verklig
  position till nästa. Inget hittas på efter den senaste verkliga positionen.
* **En position som inte ligger på ett spår nekas.** Ett tåg som rapporteras
  utanför spåren visas på sin senaste position som låg på dem, i högst 10
  minuter, och döljs sedan tills det är tillbaka. Ett tåg som först ses
  utanför spåren visas inte.
* **Försenat och mycket försenat**: där banan publicerar en egen regel för
  ett försenat tåg använder integrationen den, och säger det nedan.

På varje tåg: `marker_label`, `observed_at` (när positionen var sann),
`course_deg` (medan det rör sig), `next_stop` och `arrival_estimated_at` (där
de är kända), `delay_min`, `stalled`, `attribution` och, mellan två
positioner, `previous_latitude`, `previous_longitude`, `previous_observed_at`
och `segment_duration_s`. En position som integrationen har uppskattat, i
stället för en som banan rapporterade, har `position_source: estimated`.

### NSW TrainLink Intercity (New South Wales, Australien)

Från Transport for NSW:s flöden för NSW TrainLink och Sydney Trains, med din
egen nyckel. En tur som finns i båda flödena är en markör. Etiketten är
linjekoden (BMT, CCN, HUN, SCO, SHL); turen och dess ändpunkter står i
rutan som visas när du pekar ("Train KN56 · Bomaderry–Kiama"). Linjens färg
från tidtabellen, fylld från Sydney Central och omvänd mot den. Tomma tåg är
`NIS` och sin tur, i grått. Nästa station är en station, aldrig ett spår. ⚠ En
position som är äldre än 10 minuter ritas inte, och ett tåg tas bort när dess
tur är slut. Försenat från 6 minuter (Transport for NSW:s mått för Intercity),
mycket försenat från 12.

### Queensland Rail Citytrain (Queensland, Australien)

Från Translinks öppna flöde. ⚠ Positionerna är fasta punkter på spåret, inte
GPS, utan hastighet och riktning; pilen följer tågets rutt i tidtabellen. En
position som är äldre än 5 minuter nekas, eftersom flödet behåller ett tåg
vars position har frusit tills trafikdygnet är slut. Etiketten är linjens
T-nummer i Translinks linjefärger, omvända för tåg söderut, och en stjärna för
extratåg utan T-nummer. Försenat från 4 minuter, 6 på linjerna Gold Coast,
Rosewood och Sunshine Coast (Queensland Rails egen regel).

### Adelaide Metro (South Australia, Australien)

Från Adelaide Metros öppna flöde, som också har dess spårvagnar och bussar
(ritas inte här). Positionerna är GPS, med tågets egen riktning. Adelaide
publicerar inget tågnummer, så etiketten är de tre första bokstäverna i den
linjekod Adelaide Metro använder (SEA, FLN, GAW, BEL, OUT och så vidare);
rutan som visas när du pekar ger hela koden ("SEAFRD to Seaford · railcar
4006"). Färgerna är linjenätskartans: Belair grön, Seaford och Flinders
orange, Gawler röd, Outer Harbor, Port Dock och Grange blå; fylld från city,
vit mot Adelaide Railway Station. En position som är äldre än 5 minuter, eller
mer än 1 km från varje järnvägslinje i Adelaide, nekas. Försenat från 5
minuter (Adelaide Metros egen regel), mycket försenat från 10.

### V/Line commuter (Victoria, Australien)

Från Transport Victorias V/Line-flöde, med din egen nyckel. Etiketten är
linjekoden (GEL, BAT, BGO, SER, TRN); tågnummer och linje står i rutan som
visas när du pekar ("Train 8037 · Bendigo - Melbourne via Gisborne"). Alla
linjer är V/Line-lila: fylld från Melbourne, vit mot Southern Cross. ⚠ V/Lines
positioner följer tidtabellen mer än tåget: en tur lämnar flödet ungefär en
minut efter sin planerade ankomst var tåget än är, och positionerna fryser
runt midnatt. Därför behåller ett tåg sin senaste position i högst 10 minuter
och lämnar sedan kartan, och ett försenat tåg kan försvinna före sin sista
station. Försenat från 6 minuter (V/Lines regel för pendeltåg), mycket
försenat från 12.

### Perths tåg (Västaustralien, Australien)

⚠ **Perth publicerar inga positioner i realtid.** Varje tåg ritas från
tidtabellen från Public Transport Authority i Västaustralien: placerat längs
sin rutt efter sina planerade tider, markerat som en uppskattning, utan
försening. Tidtabellen kontrolleras en gång om dagen. Etiketten är linjens tre
första bokstäver (MAN, YAN, ARM, FRE, MID, ELL, AIR, THO; STA för en Stadium
Special); rutan som visas när du pekar säger "Mandurah Line · Perth
Underground–Mandurah". Färgerna är linjenätskartans: fylld från Perth, vit
mot Perth.

### VR:s och HSL:s närtåg (Finland)

Från Fintraffics Digitraffic. Ett tåg är en tur: tågnumret och dagen det
avgick. Etiketten är linjebokstaven, färgad så som HSL:s kartor och
stationsskyltar färgar linjerna: HSL-lila medan nästa station ligger i HSL:s
taxezoner A till E, VR-grön utanför dem. Ett tåg på väg från Helsingfors är en
fylld skiva; ett på väg mot Helsingfors är vitt. Ett tåg visas från sin första
station till sin sista station och tas sedan bort. Turer på linje V utan
resenärer visas som `NIS` medan de rör sig. Mellan två positioner glider ett
tåg längs spåren. Linjerna I och P ger ingen position i Ringbanans tunnel vid
Helsingfors flygplats, så där flyttar integrationen tåget längs spåren efter
dess tidtabell tills en verklig position kommer tillbaka. Försenat från 4
minuter (VR:s regel), mycket försenat från 8. En position som är äldre än 10
minuter nekas.

### Irish Rail (Irland)

Från Irish Rails realtidstjänst, med National Transport Authoritys tidtabell
för rutter och stationer. ⚠ Irish Rail rapporterar ett tåg bara när det
passerar signaler några minuter isär, så varje tåg ritas från sin tidtabell
och sin senaste försening, flyttat längs sin rutt; Corks tåg, som Irish Rail
inte följer, kommer bara från tidtabellen. Etiketten är tågnumret utan sin
bokstav (P508 visar 508). Färgen är linjens på Transport for Irelands
linjenätskarta, omvänd mot Dublin eller Cork. Försenat från 5 minuter (Irish
Rails egen regel), mycket försenat från 10.

### NS Sprinter (Nederländerna)

Från NS fordonsdata, med din egen nyckel. Etiketten är tågnumret; rutan som
visas när du pekar säger "Sprinter 6632 · Dordrecht–Arnhem Centraal". NS-gul
med en NS-blå ring. Det här är det enda flödet här som rapporterar tågets egen
hastighet och riktning, och båda förs vidare (`speed_kmh`, `course_deg`).
Nästa station och förseningen kommer från OVapis tidtabell. Spåret är NS
SpoorKaart, nedladdad en gång om dagen; ett tåg glider längs den mellan två
positioner, och en position mer än 1 km från den nekas. Försenat från 3
minuter (NS egen definition), mycket försenat från 10.

### Vy, Go-Ahead Norge och Flytoget (Norge)

Från Entur, varje bana i sin egen post. Etiketten är linjekoden (L1, L2, L4,
L5, FLY1, FLY2); tågnummer och linjenamn står i rutan som visas när du pekar.
En L-linje har sin färg från tidtabellen, fylld från Oslo S (Bergen på L4,
Stavanger på L5) och omvänd mot den. Flytoget är grått med en orange ring mot
Oslo flygplats och orange med en grå ring därifrån. Entur publicerar varken
hastighet eller riktning, så pilen följer tågets linje. I Oslos långa
tunnlar flyttas ett tåg vars positioner upphör längs sin linje tills de kommer
tillbaka. Försenat från 4 minuter, mycket försenat från 8.

### Renfe Cercanías och Rodalies (Spanien)

Från Renfes öppna flöde, vart och ett av de 15 näten i sin egen post.
Etiketten är linjen (C5, R2N) i linjens egen färg från Renfes tidtabell.
Tågnummer och linjenamn står i rutan som visas när du pekar. ⚠ Renfe placerar
sina tåg på deras rutt i stället för med GPS, så de står still och hoppar
sedan. Ett tåg rör sig bara framåt längs sin egen linje: en position bredvid
den, bakåt längs den eller omöjligt snabb nekas, och den senaste goda behålls
i högst 10 minuter. Ett tåg kallas stillastående först efter 6 minuter på
samma ställe. Renfe publicerar ingen regel för ett försenat tåg, så
kartkortets egna gränser gäller.

### SL Pendeltåg, Västtågen och Arlanda Express (Sverige)

Från Trafikverket, med din egen gratis nyckel (en nyckel för alla tre).
Etiketten är tågnumret; varumärke, nummer och ändstationer står i rutan som
visas när du pekar. SL Pendeltåg är rosa, Västtågen ljusblå, Arlanda Express
gul; var och en byter färger mot Stockholm C (Stockholm City för pendeltågen)
eller, på en tur som inte stannar vid någon av dem, mot den större ändstaden.
Mellan två positioner glider ett tåg längs turens linje, och en position mer
än 1 km från den nekas. Försenat från 3 minuter på SL Pendeltåg (Region
Stockholms regel), mycket försenat från 6; försenat från 6 och mycket
försenat från 12 på de andra två (Trafikverkets regel).

### Metra och South Shore Line (USA)

Metra från sitt eget flöde, med din egen nyckel; South Shore Line från det
flöde som ETA SPOT publicerar för NICTD, utan nyckel. Etiketten är
tågnumret. Metra anger nästa station och tiden. South Shore Lines flöde ger
bara ett stationsnummer och en försening, så tidtabellen ger stationen och
tiden. En position mer än 300 m från alla spår i North American Rail Network
(USA), eller från banans egen rutt, nekas. ⚠ Vissa dagar har Metras flöde
kopplat bara få av sina tåg till en tur; resten visas då som `NIS` eller inte
alls, och kartan ser ut som en lugn dag. Räknaren **Trains in service** visar
sådana dagar i efterhand.

---

## Alla entiteter den skapar

För varje bana:

| Entitet | Vad det är |
|---|---|
| `sensor.<bana>_trains_in_service` | **Trains in service**: hur många tåg i trafik banans flöde rapporterar nu. För Metra: `sensor.metra_chicago_area_trains_in_service` |
| `sensor.<bana>_vehicles_not_in_service` | **Vehicles not in service**: hur många fordon som inte är i trafik flödet rapporterar |
| `geo_location.<bana>_unit_…` | en per tåg eller fordon (`geo_location.metra_unit_8426`); den kommer och går med tåget. Var och en har `source: live_track_commuter_rail`, och tillståndet är avståndet till ditt hem i kilometer |

Entiteternas namn är på engelska, oavsett språk i din Home Assistant.

Varje bana har en känd fordonsflotta. En markörs entitets-ID kommer från
banan och fordonets nummer i flödet, aldrig från etiketten, så samma fordon
får samma entitets-ID varje gång det dyker upp:
`geo_location.metra_unit_8426` är alltid Metras vagn 8426. Markören tas bort
när fordonet lämnar flödet, eller efter 10 minuter uppställt medan **Visa
uppställda fordon** är av. Markörerna har inget unikt ID, som ingen
kartmarkör i Live Track har, så de kan inte döpas om, döljas eller ges ett
område i gränssnittet. De två sensorerna har ett unikt ID och kan döpas om.

Attribut som ändras vid varje uppdatering, markörernas positioner och tider,
sparas i Home Assistants historik, som för alla entiteter. De två sensorerna
har inga attribut, så de kostar lite att spara, och de är uppgiften om hur
många tåg som gick en viss dag. För att hålla markörerna utanför historiken
lägger du till detta i `configuration.yaml` och startar om:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_unit_*
```

Om din `configuration.yaml` redan har en `recorder:`-sektion lägger du bara
till mönstret `geo_location.*_unit_*`, under `exclude:` och `entity_globs:`.
Mönstret matchar bara den här modulens tågmarkörer. Ett kartkort som är
inställt på att rita historik har då inget spår att rita.

---

## Vad den skickar och laddar ner

**Om din plats.** Ingenting. Ditt hems position används bara inne i din Home
Assistant, för att ge varje tågs avstånd. Din nyckel, där en bana behöver en,
skickas bara till den banan. Inget annat om dig skickas någonstans. Varje
tjänst ser din internetadress, som alla webbplatser gör.

**Hur mycket.** Varje realtidsflöde läses vid varje uppdatering, var 30:e
sekund som standard (**Uppdateringsintervall**, 15 till 600 sekunder), eller
mer sällan där tabellen säger det. Där flera Live Track-moduler läser samma
flöde läser en gemensam klient det en gång för alla. Mätt den 19 november
2026, 02:20 till 02:40 UTC:

| Bana | Realtidsflöde, en läsning | Tidtabell |
|---|---|---|
| NSW TrainLink Intercity (Australien) | 402 KB från fyra flöden, högst en gång per 55 sekunder | 51 MB (två tidtabeller), när den ändras, kontrolleras dagligen |
| Queensland Rail Citytrain (Australien) | 141 KB | 42 MB, varje dag |
| Adelaide Metro (Australien) | 298 KB | 20 MB, när Adelaide Metro publicerar en ny version |
| V/Line commuter (Australien) | 14 KB | 59 MB, när den ändras, kontrolleras dagligen |
| Perths tåg (Australien) | inget: Perth publicerar inget realtidsflöde | 28 MB, när den ändras, kontrolleras dagligen |
| VR:s och HSL:s närtåg (Finland) | 1,1 KB komprimerat för positionerna, plus ändringarna i dagens tåg en gång i minuten | ingen fil: dagens tåg kommer med realtidsdata |
| Irish Rail (Irland) | 0,2 KB, högst en gång per 55 sekunder | 6,6 MB, när den ändras, kontrolleras dagligen; stationslistan, 18 KB, en gång i veckan |
| NS Sprinter (Nederländerna) | 1,2 KB; förseningar från OVapi, 1,6 MB, var 5:e minut och bara när de ändras | OVapis tidtabell, 274 MB, högst en gång i veckan och bara när den ändras; NS spårkarta, 1,3 MB, varje dag |
| Vy, Go-Ahead Norge, Flytoget (Norge) | Vy 497 KB, Go-Ahead Norge 7 KB, Flytoget 233 KB | Vy 67 MB, Go-Ahead Norge 20 MB, Flytoget 0,6 MB, när den ändras, kontrolleras dagligen |
| Renfe Cercanías och Rodalies (Spanien) | ett flöde för alla 15 näten: 26 byte, på natten när inga tåg går | 16 MB, varje dag |
| SL Pendeltåg, Västtågen, Arlanda Express (Sverige) | 3,7 KB första gången, sedan ungefär 2 KB ändringar | ingen; stationslistan, 0,15 MB, varje dag |
| Metra (USA) | 18 KB | 0,4 MB, varje dag |
| South Shore Line (USA) | under 1 KB | 0,14 MB, varje dag |

⚠ När detta mättes var det dag i Australien, kväll i USA och natt i Europa.
Ett realtidsflöde är som minst på natten: på dagen är de europeiska flödena
större än tabellen visar.

**Efter ett fel.** De senaste goda positionerna visas i två misslyckade
läsningar till; sedan markeras tågen som otillgängliga tills flödet svarar.
En tidtabell som inte går att ladda ner försöks igen en timme senare, och den
kopia du har används vidare. Om banan fortsätter att neka din nyckel ber Home
Assistant om en ny.

**På disken.** Tidtabellerna sparas i Home Assistants mapp `.storage` under
namn som börjar med `saw_`, delade med de andra Live Track-moduler som läser
samma bana: de som är märkta "när den ändras" som de laddades ner, de andra
som ett mindre utdrag. Om du tar bort Live Track Commuter Rail och ingen
annan Live Track-modul använder dem kan du radera dem för hand.

---

## Hjälp den att växa

Live Track Commuter Rail växer fortfarande. Vi lägger till banor och länder
när vi hittar dem, och vi vill veta vad du vill ha härnäst.

### Föreslå något

Saknas ditt land eller din bana? Är något fel, eller svårt att förstå? Säg
till på det sätt som är enklast för dig:

* [**Fyll i ett kort formulär**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=sv.yml)
  på svenska. Du behöver ett gratis GitHub-konto.
* **Skicka e-post** till
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Inget konto behövs.

Hur du än gör hjälper det om du berättar:

* vad du vill se, och var i världen;
* en länk till var data publiceras, om du känner till en (en sida med öppna
  data, ett öppet flöde, en tjänsts webbplats): inte nödvändigt, men det
  hjälper;
* språket i din Home Assistant, om problemet är formuleringen eller en
  översättning.

Skriv på engelska eller på ditt eget språk, det som är enklast för dig.

### Lägg till det själv, med vår hjälp

Om du vill lägga till något själv hjälper vi dig, från den första frågan till
den färdiga versionen. Du behöver inte vara utvecklare för att börja:

* **En översättning.** Orden i inställningsdialogen är en kort lista med
  fraser i en textfil. Vi visar vilken fil och vilka rader.
* **En ny bana.** Berätta var data publiceras. Vi kan skriva koden
  tillsammans, eller gå igenom din.
* **Testa där du bor.** Installera den, titta på din del av kartan och säg
  vad som stämmer och vad som inte gör det.
* **En rättelse av den här README-filen.** Om ett steg inte stämde med det du
  såg, berätta vad du såg.

[**Berätta vad du har i tankarna**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=sv.yml)
eller skriv till
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
så svarar vi med nästa steg.

---

## Språk

Den här README-filen: [English](README.md), [Suomi](README.fi.md),
**Svenska**, [Norsk bokmål](README.nb.md), [Español](README.es.md),
[Nederlands](README.nl.md), [Gaeilge](README.ga.md). Varje översatt
README-fil är fullständig. Ingen har ännu lästs av någon med språket som
modersmål. Är svenska ditt modersmål, säg gärna om den här README-filen läses
bra: se [Hjälp den att växa](#hjälp-den-att-växa).

Inställningsdialogen och alternativen visas på din Home Assistants språk när
det är något av dessa: English, Suomi, Svenska, Norsk bokmål, Español,
Nederlands, Gaeilge. Alla andra språk visar engelska.

Hittat ett fel i en översättning, eller behöver du ett annat språk? Säg till
på <https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues>,
eller [översätt med vår hjälp](#lägg-till-det-själv-med-vår-hjälp).

---

## Tack och licenser

Varje bana läses medan integrationen körs, av din Home Assistant, från banans
eget publicerade flöde; inget från ett realtidsflöde finns i det här
förrådet. Varje tåg anger sin källa i attributet `attribution`. Varje banas
villkor gäller dig, som den som tar emot dess data.

* **Metra** (USA): GTFS-Realtime, enligt
  [Metras licensavtal](https://metra.com/gtfs-realtime-api-key-request-license-agreement),
  som du godtar när du ber om en nyckel.
* **South Shore Line** (NICTD, USA): öppet flöde och tidtabell som ETA SPOT
  publicerar för NICTD, utan nyckel och utan licensavtal.
* **Translink** (Queenslands regering, Australien): data under CC BY 4.0
  ([öppna data](https://translink.com.au/about-translink/open-data)).
* **Fintraffic / digitraffic.fi** (Finland): data under CC BY 4.0. **HSL**
  (Finland): taxezoner, CC BY 4.0.
* **Renfe** (Spanien): data under CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)), bearbetade.
* **Entur** (Norge): data under den norska licensen för öppna offentliga data
  ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)), distribuerade av Entur.
* **Trafikverket** (Sverige): data under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irland): realtidsdata; Irish Rail publicerar inga villkor.
  Tidtabell från [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irland), CC BY 4.0.
* **NS** (Nederländerna): fordonsdata, med din egen nyckel, från
  [NS API-portal](https://apiportal.ns.nl/). Tidtabell och förseningar från
  [OVapi](https://gtfs.ovapi.nl), CC0.
* **Transport for NSW** (Australien): data under CC BY 4.0
  ([datalicens](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australien): data under CC BY 4.0
  ([öppna data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Adelaide Metro**, Department for Infrastructure and Transport, South
  Australia: data under CC BY 4.0 ([information för utvecklare](https://www.adelaidemetro.com.au/developer-info)).
* **Public Transport Authority i Västaustralien**: tidtabellsdata tillgängliga
  utan kostnad från www.transperth.wa.gov.au
  ([tillgång till geodata](https://www.transperth.wa.gov.au/About/Spatial-Data-Access)).
* **Spårfiler i `rail/`**: North American Rail Network (USA:s
  transportdepartement), allmän egendom; Fintraffics spårnät, CC BY 4.0,
  bearbetat; Flytogets linjer från Enturs data, NLOD 2.0, bearbetade; de
  svenska linjerna dragna på OpenStreetMap, (c) OpenStreetMaps bidragsgivare,
  ODbL 1.0; städernas befolkning från Statistiska centralbyrån, CC0. Vad som
  har ändrats står i [ATTRIBUTION.md](ATTRIBUTION.md).
* **Kartkortet** är [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, en kopia av [ha-map-card](https://github.com/nathan-gs/ha-map-card) av
  nathan-gs, MIT. Kartplattorna och deras källor står i dess README.

Ingen av dessa organisationer har gjort eller godkänt den här integrationen.

**Kod**: MIT, i [LICENSE](LICENSE).

**För utvecklare:** varje bana är en adapter i
`custom_components/live_track_commuter_rail/operators/`; spårfilerna i
`rail/` byggs om med skripten i `tools/` (`build_rail.py`, `build_tracks.py`,
`build_flytoget_lines.py`, `sweden_lines.py`). Testerna körs med
`python -m unittest discover -s tests`.

---

## Sökord

Home Assistant tåg · pendeltåg i realtid · tåg på kartan · tåg i realtid ·
tågkarta · SL Pendeltåg · Västtågen · Arlanda Express · Trafikverket ·
närtåg · lähijunat · HSL · VR · Vy · Flytoget · tog i sanntid · NS ·
Sprinter · Renfe Cercanías · Rodalies · Irish Rail · Metra · South Shore
Line · Queensland Rail · Translink · NSW TrainLink · V/Line · Adelaide Metro ·
Perths tåg · GTFS-Realtime · geo_location · kartkort · Lovelace · HACS ·
Marknadsplatsen · Live Track · LiveTrack · StrausbergAutomationWorks

---

**Erkännande.** StrausbergAutomationWorks erkänner urfolken i alla de länder och
vatten som den här kartan täcker, över hela världen, och visar sin respekt för
deras äldste, förr och nu.
