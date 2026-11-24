# Live Track Commuter Rail

[English](README.md) · **Suomi** · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md) · [Kaikki kielet](#kielet)

**Lähijunat Home Assistantiin, yhdelle kartalle.** Live Track Commuter Rail
näyttää valitsemiesi lähijunarautateiden jokaisen junan Home Assistantin
kartalla reaaliajassa: missä juna on, sen junanumeron tai linjan, onko se
myöhässä ja sen seuraavan aseman. Jokainen rautatie lisätään erikseen, sen
omista avoimista tiedoista.

> **Live Track Commuter Rail on yksi Live Trackin moduuli.** Live Track on
> joukko Home Assistant -integraatioita, jotka piirtävät kaiken liikkuvan, ja
> sään, jonka läpi se liikkuu, yhdelle yhteiselle kartalle: lentokoneet,
> laivat, junat ja sään. Asenna se yksinään tai muiden moduulien rinnalle
> ([luettelo alempana](#osa-live-trackia-muut-moduulit)).

> **Kasvaa, ja ideat ovat tervetulleita.** Live Track Commuter Rail kattaa
> tänään 31 rautatietä 8 maassa 3 mantereella, ja lisäämme rautateitä ja maita.
> Puuttuuko omasi? [Ehdota sitä](#auta-sitä-kasvamaan), tai lisää se itse:
> autamme sinua.

**Tila: 0.1.6, julkaistu.** Markkinapaikan luettelossa ([asenna se
alempana](#asenna-se-vaihe-vaiheelta)).

StrausbergAutomationWorksin alkuperäinen työ. Ei sidoksissa seuraaviin,
eivätkä ne ole hyväksyneet sitä: Metra, Northern Indiana Commuter
Transportation District (NICTD), ETA SPOT, Renfe, Fintraffic, HSL, VR, Entur,
Vy, Go-Ahead Norge, Flytoget, Trafikverket, SL, Västtågen, Arlanda Express,
Irish Rail, National Transport Authority (Irlanti), NS, OVapi, Translink,
Queensland Rail, Transport for NSW, Transport Victoria, V/Line, Adelaide
Metro, Länsi-Australian Public Transport Authority tai mikään muu rautatie.

---

## Sisällys

1. [Kaikki mitä se tekee](#kaikki-mitä-se-tekee)
2. [Missä se toimii](#missä-se-toimii)
3. [Osa Live Trackia: muut moduulit](#osa-live-trackia-muut-moduulit)
4. [Ennen kuin aloitat](#ennen-kuin-aloitat)
5. [Asenna se, vaihe vaiheelta](#asenna-se-vaihe-vaiheelta)
6. [Ota se käyttöön, vaihe vaiheelta](#ota-se-käyttöön-vaihe-vaiheelta)
7. [Ilmaiset avaimet, jotka tuovat lisää, vaihe vaiheelta](#ilmaiset-avaimet-jotka-tuovat-lisää-vaihe-vaiheelta)
8. [Lisää kartta kojelaudalle](#lisää-kartta-kojelaudalle)
9. [Käytä sitä automaatioissa](#käytä-sitä-automaatioissa)
10. [Kaikki kartalla, tarkemmin](#kaikki-kartalla-tarkemmin)
11. [Kaikki sen luomat entiteetit](#kaikki-sen-luomat-entiteetit)
12. [Mitä se lähettää ja lataa](#mitä-se-lähettää-ja-lataa)
13. [Auta sitä kasvamaan](#auta-sitä-kasvamaan)
14. [Kielet](#kielet)
15. [Tekijät ja lisenssit](#tekijät-ja-lisenssit)
16. [Hakusanat](#hakusanat)

---

## Kaikki mitä se tekee

### Kartalla, ilman asetuksia

Lisäät **rautatien**: valitset maan tai alueen ja sitten yhden sen
lähijunarautateistä. Kaikki alla oleva näkyy silloin sille rautatielle. Lisää
integraatio uudelleen jokaista muuta haluamaasi rautatietä varten.

| Mitä | Missä | Mistä |
|---|---|---|
| **Liikenteessä olevat junat**: yksi merkki junaa kohden, junanumerolla tai linjalla, rautatien omissa väreissä, käännettynä kulkusuuntaan | kaikki rautatiet | kunkin rautatien oma reaaliaikainen syöte |
| **Myöhästyminen**: juna näkyy myöhässä tai paljon myöhässä rautatien oman säännön mukaan, jos rautatie julkaisee sellaisen | kaikki rautatiet, jotka ilmoittavat myöhästymiset | kunkin rautatien syöte ja aikataulu |
| **Seuraava asema ja aika**: asema, jolla juna pysähtyy seuraavaksi, ja milloin se on siellä | kaikki rautatiet, joiden syöte tai aikataulu kertoo sen | kunkin rautatien syöte ja aikataulu |
| **Junat, jotka seuraavat rataa**: kahden sijainnin välillä juna liukuu rataa pitkin eikä suoraan | Alankomaat, Ruotsi, Suomi | integraation mukana tulevat tai sen lataamat ratatiedostot |
| **Kalusto, joka ei ole liikenteessä**: tyhjät junat varikoiden välillä, näkyvät liikkuessaan | rautatiet, joiden syöte ilmoittaa ne | kunkin rautatien syöte |
| **Kaksi laskuria rautatietä kohden**: liikenteessä olevat junat ja kalusto, joka ei ole liikenteessä | kaikki rautatiet | sama syöte |

### Oma ilmainen avain tai tili tuo lisää

| Ilmainen avain tai tili | Mitä se tuo |
|---|---|
| **Metran** avain | Metran junat (Chicagon seutu, Yhdysvallat) |
| **Trafikverketin** avain | SL Pendeltåg, Västtågenin pendeltåg ja Arlanda Express (Ruotsi) |
| **NS API -portaalin** avain | NS Sprinter -junat (Alankomaat) |
| **Transport for NSW Open Data** -avain | NSW TrainLink Intercity -junat (Uusi Etelä-Wales, Australia) |
| **Transport Victoria Open Data** -avain | V/Linen lähijunat (Victoria, Australia) |

Jokaisen saa muutamassa minuutissa: [vaihe vaiheelta alempana](#ilmaiset-avaimet-jotka-tuovat-lisää-vaihe-vaiheelta).
Muut 26 rautatietä eivät tarvitse avainta.

---

## Missä se toimii

| Alue | Mitä saat | Mistä | Tarvitsee |
|---|---|---|---|
| **Australia**: Etelä-Australia | Adelaide Metron junat: linjat Belair, Gawler, Outer Harbor ja Seaford | Adelaide Metro | ei mitään |
| **Australia**: Länsi-Australia | Perthin junat, kaikki yhdeksän linjaa, vain aikataulusta ([miksi](#perthin-junat-länsi-australia-australia)) | Länsi-Australian Public Transport Authority | ei mitään |
| **Australia**: Queensland | Queensland Rail Citytrain, Kaakkois-Queensland (Brisbane) | Translink | ei mitään |
| **Australia**: Uusi Etelä-Wales | NSW TrainLink Intercity: linjat Blue Mountains, Central Coast and Newcastle, Hunter, South Coast ja Southern Highlands Sydneystä | Transport for NSW | ilmainen avain |
| **Australia**: Victoria | V/Linen lähijunat: linjat Geelong, Ballarat, Bendigo, Seymour ja Traralgon | Transport Victoria | ilmainen avain |
| **Eurooppa**: Alankomaat | NS Sprinter -junat, koko maa | NS, OVapi | ilmainen avain |
| **Eurooppa**: Espanja | Renfe Cercanías ja Rodalies de Catalunya, 15 verkkoa: Madrid, Barcelona, Asturia, Sevilla, Cádiz, Málaga, Valencia, Murcia ja Alicante, Cartagena, Ferrol, León, Bilbao, San Sebastián, Kantabria, Zaragoza | Renfe | ei mitään |
| **Eurooppa**: Irlanti | Irish Railin lähijunat Dublinin ja Corkin ympärillä | Irish Rail, National Transport Authority | ei mitään |
| **Eurooppa**: Norja | Vyn L1, L2 ja L4 (Oslon seutu, Bergen), Go-Ahead Norgen L5 (Stavanger), Flytoget (Oslon lentoasema) | Entur | ei mitään |
| **Eurooppa**: Ruotsi | SL Pendeltåg (Tukholma), Västtågenin pendeltåg (Göteborg), Arlanda Express | Trafikverket | ilmainen avain |
| **Eurooppa**: Suomi | VR:n ja HSL:n lähijunat Helsingin seudulla | Fintraffic Digitraffic | ei mitään |
| **Pohjois-Amerikka**: Yhdysvallat | Metra (Chicagon seutu: Illinois, Wisconsin) | Metra | ilmainen avain |
| **Pohjois-Amerikka**: Yhdysvallat | South Shore Line (Chicagosta South Bendiin: Illinois, Indiana) | NICTD, ETA SPOTin kautta | ei mitään |

Eikö omasi ole luettelossa? [Kerro meille](#auta-sitä-kasvamaan). Jos joku
julkaisee tiedot avoimesti, katsomme, voimmeko lisätä ne.

⚠ **Juna on vain niin hyvä kuin sen rautatien syöte.** Jotkin rautatiet
sijoittavat junansa aikataulun mukaan eivätkä GPS:llä, jotkin ilmoittavat
junan vain muutaman minuutin välein olevilla opastimilla, ja jotkin syötteet
pysähtyvät tai jäätyvät hetkeksi. Kunkin rautatien rajoitukset ovat kohdassa
[Kaikki kartalla, tarkemmin](#kaikki-kartalla-tarkemmin).

⚠ **Tämä ei ole rautatien virallista tietoa.** Tarkista ennen matkaa
rautatien oma sovellus tai verkkosivu.

---

## Osa Live Trackia: muut moduulit

Live Track on joukko Home Assistant -integraatioita, yksi kutakin liikkuvaa
asiaa kohden, ja kaikki piirretään samalle karttakortille. Jokainen toimii
yksinään; yhdessä ne muodostavat yhden elävän kuvan. Niillä on yhteinen
karttakortti ja Python-kirjasto
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
joten uuden moduulin asentaminen ei lisää pyyntöjä lähteeseen, jota toinen jo
lukee.

| Moduuli | Mitä se tuo kartalle | Tila |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | lentokoneet yläpuolellasi ADS-B:n kautta, reiteillä ja tyyppikuvakkeilla | julkaistu |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | laivat ja veneet AIS:n kautta, lähelläsi tai missä tahansa | julkaistu |
| **Live Track Commuter Rail** | lähijunat Pohjois-Amerikassa, Euroopassa ja Australiassa (tämä moduuli) | julkaistu |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | kaukojunat Pohjois-Amerikassa, Euroopassa ja Australiassa | julkaistu |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | maahanmuutto- ja liittovaltion lainvalvontaviranomaisten lentokoneet ja alukset julkisista luetteloista | julkaistu |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | sää, myrskyt ja luonnonvaarat | julkaistu |
| Live Track Stations | lähtötaulut ja "nyt on lähdettävä" -ilmoitukset jokaiselle asemalle | suunnitteilla |
| Live Track Satellites | yläpuolelta kulkevat satelliitit | suunnitteilla |
| Live Track Freight Trains | tavara- ja työjunat siellä, missä rautatiet julkaisevat ne | suunnitteilla |
| Live Track Transit | kaupunkibussit, raitiovaunut, lautat ja metro | suunnitteilla |
| Live Track Intercity Buses | pika- ja aluebussit | suunnitteilla |
| Live Track Commuter Buses | työmatkabussit | suunnitteilla |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | yhteinen karttakortti, jolle jokainen moduuli piirtää | julkaistu, asennetaan jokaisen moduulin mukana |

Kaikki on ilmaista ja avointa lähdekoodia. Mitään ei pidätetä tukijoille.

---

## Ennen kuin aloitat

* **Home Assistant** 2026.11 tai uudempi.
* **Markkinapaikka** (HACS) Home Assistantissa, jotta asennus ja päivitys
  käyvät helposti. Ilman sitä voit kopioida tiedostot käsin.
* **Internetyhteys** Home Assistantille: jokainen juna tulee oman rautatiensä
  avoimesta syötteestä.
* **Valinnainen: auto-entities** Markkinapaikasta, jotta merkit saadaan
  kartalle (katso [Lisää kartta kojelaudalle](#lisää-kartta-kojelaudalle)).
* Ei mitään maksettavaa. 26 rautatietä 31:stä ei tarvitse
  tiliä; muut viisi tarvitsevat oman, ilmaisen avaimen
  ([yllä](#oma-ilmainen-avain-tai-tili-tuo-lisää)).
* Home Assistant asentaa itse tarvitsemansa Python-paketit (`saw-livetrack`,
  `gtfs-realtime-bindings` ja `tzdata`), kun integraatio ladataan
  ensimmäisen kerran.

---

## Asenna se, vaihe vaiheelta

### Markkinapaikasta (suositus)

1. Avaa Home Assistantissa **Asetukset → Markkinapaikka** (HACS).
2. Hae **Live Track Commuter Rail** ja avaa se.
3. Valitse **Lataa** (tai **Asenna**).
4. **Käynnistä Home Assistant uudelleen**: **Asetukset → Järjestelmä →
   Korjaukset** tarjoaa uudelleenkäynnistyksen, tai käytä **Asetukset →
   Järjestelmä → Käynnistä uudelleen**.

Jos haku ei löydä sitä, lisää se linkin kautta: valitse **Lisää linkistä** (tai
kolmen pisteen valikko → **Mukautetut tietovarastot**), kirjoita
`StrausbergAutomationWorks/LiveTrackCommuterRail`, valitse **Integraatio**, jos
tyyppiä kysytään, ja jatka sitten vaiheesta 3.

Sen jälkeen Markkinapaikka tarjoaa jokaisen uuden version päivityksenä.

### Käsin

1. Lataa [uusimman version](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest)
   lähdekoodi.
2. Kopioi sen kansio `custom_components/live_track_commuter_rail` Home
   Assistantin asetuskansion kansioon `custom_components` (luo
   `custom_components`, jos sitä ei ole).
3. Käynnistä Home Assistant uudelleen.

Kun päivität käsin, vaihda kansio uuden version kansioon ja käynnistä
uudelleen.

---

## Ota se käyttöön, vaihe vaiheelta

1. Avaa **Asetukset → Laitteet & palvelut**.
2. Valitse **Lisää integraatio** (oikealla alhaalla) ja hae **Live Track
   Commuter Rail**.
3. **Alue**: valitse rautatien maa, tai maa ja alue. Luettelossa on vain
   paikat, joissa on vähintään yksi rautatie. Valitse **Lähetä**.
4. **Rautatie**: valitse rautatie. Valitse **Lähetä**.
5. **API-avain**: vain Metralle, kolmelle ruotsalaiselle rautatielle, NS
   Sprinterille, NSW TrainLink Intercitylle ja V/Line commuterille. Liitä
   avaimesi ([näin saat sen](#ilmaiset-avaimet-jotka-tuovat-lisää-vaihe-vaiheelta))
   ja valitse **Lähetä**. Muut rautatiet ohittavat tämän vaiheen.

Siinä kaikki. Junat ilmestyvät minuutin kuluessa. Jos rautatien seuraavat
asemat tulevat aikataulusta, ne täydentyvät ensimmäisten minuuttien aikana,
kun aikataulu on ladattu. Jos haluat seurata toista rautatietä, lisää
integraatio uudelleen. Samaa rautatietä ei voi lisätä kahdesti.

### Muuta sitä, mitä se näyttää: asetukset

Avaa **Asetukset → Laitteet & palvelut → Live Track Commuter Rail →
Määrittele** (hammasratas) sen rautatien kohdalla, jota haluat muuttaa.
Jokainen asetus selkein sanoin:

| Asetus | Mitä se tekee | Oletus |
|---|---|---|
| **Päivitysväli** | kuinka usein rautatien syöte luetaan, 15–600 sekuntia. Useimmat syötteet päivittyvät noin 30 sekunnin välein, joten lyhyempi väli näyttää harvoin enemmän | 30 sekuntia |
| **Näytä seisova kalusto** | pois: kalusto, joka ei ole liikenteessä, näkyy vain liikkuessaan ja poistuu kartalta seistyään 10 minuuttia. Päällä: syötteen kaikki kalustoyksiköt näytetään, myös seisovat junat | pois |

---

## Ilmaiset avaimet, jotka tuovat lisää, vaihe vaiheelta

Viisi rautatietä pyytää jokaiselta käyttäjältä oman avaimen. Kaikki nämä
avaimet ovat ilmaisia, ja jokainen Live Track Commuter Railin asentaja hankkii
omansa. Liität avaimen, kun asetusvalintaikkuna pyytää sitä
([vaihe 5 yllä](#ota-se-käyttöön-vaihe-vaiheelta)). Vain avainta pyydetään: ei
salasanaa eikä salaisuutta. Avain tallennetaan Home Assistantiin integraation
kanssa, eikä sitä koskaan kirjoiteta lokiin. Jos rautatie hylkää sen
jatkuvasti, Home Assistant pyytää sinulta uuden.

### Metra (Chicagon seutu, Yhdysvallat)

1. Avaa <https://metra.com/developers> ja vieritä kohtaan **GTFS Realtime API
   Key Request Form**.
2. Täytä **First Name** (etunimi), **Last Name** (sukunimi), **Email Address**
   (sähköpostiosoite, kysytään kahdesti) ja **Purpose of Use** (käyttötarkoitus,
   esimerkiksi: Home Assistant).
3. Rastita **I have read and agree to the License Agreement.** (olen lukenut
   lisenssisopimuksen ja hyväksyn sen; sopimus on osoitteessa
   <https://metra.com/gtfs-realtime-api-key-request-license-agreement>) ja
   valitse **Submit**.
4. Liitä Metralta saamasi avain kenttään **API-avain**, kun lisäät Metran.

### Trafikverket (Ruotsi: SL Pendeltåg, Västtågen, Arlanda Express)

1. Avaa <https://data.trafikverket.se/oauth2/Account/register>.
2. Täytä **Email**, **Displayname** (näyttönimi), **Password** (salasana) ja
   **Confirm password**, rastita **Accept license and Agreement** ja valitse
   **Register**.
3. Avaa <https://data.trafikverket.se/get-started> ja valitse **Create key**
   kohdan **Create a key** alta. Kirjaudu luomallasi tilillä ja luo avain.
4. Liitä se kenttään **API-avain**, kun lisäät ruotsalaisen rautatien. Yksi
   avain riittää kaikille kolmelle.

### NS (Alankomaat)

1. Avaa <https://apiportal.ns.nl/>, valitse **Inloggen** (kirjaudu) ja sitten
   **Externe bezoeker** (ulkopuolinen vierailija).
2. Täytä lomake ja lähetä se. Sähköposti vahvistaa rekisteröinnin. Rajapintojen
   näkyminen portaalissa voi kestää enintään 5 minuuttia.
3. Avaa **Virtual Train API** -sivu (NS:n junien sijainnit). Avaa sen tuote
   kohdasta **Related Products**, anna tilaukselle nimi ja valitse
   **Subscribe**.
4. Kun NS on hyväksynyt tilauksen, avaimesi on profiilisivullasi. Liitä se
   kenttään **API-avain**, kun lisäät NS Sprinterin.

### Transport for NSW (Uusi Etelä-Wales, Australia)

1. Avaa <https://opendata.transport.nsw.gov.au/>, valitse **Register**, luo
   tili ja kirjaudu sisään.
2. Valitse profiilikuvakkeesi ja sitten **API Tokens**.
3. Kirjoita avaimelle nimi ja valitse **CREATE API TOKEN**. Kopioi avain heti:
   sivusto näyttää sen vain kerran.
4. Liitä se kenttään **API-avain**, kun lisäät NSW TrainLink Intercityn. Liitä
   pelkkä avain: Live Track Commuter Rail lisää sanan `apikey` itse.

### Transport Victoria (Victoria, Australia)

1. Avaa <https://opendata.transport.vic.gov.au/>, valitse **Login** ja sitten
   **Sign up**.
2. Anna tietosi ja valitse **Create Account**. Kirjoita saamasi sähköpostin
   koodi ja valitse **Confirm**.
3. Portaali vaatii puhelimeen todennussovelluksen: skannaa QR-koodi sillä,
   kirjoita sovelluksen koodi ja valitse **Confirm**. Kirjaudu sitten
   sähköpostiosoitteellasi, salasanallasi ja sovelluksen koodilla.
4. Valitse **My Account** → **Profile** → **API tokens**. Avaimesi on jo
   siellä. Liitä se kenttään **API-avain**, kun lisäät V/Line commuterin.

---

## Lisää kartta kojelaudalle

Kartta on [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
kortti, jolle jokainen Live Track -moduuli piirtää. **Se asennetaan Live Track
Commuter Railin mukana**: ei mitään ladattavaa, ei mitään kopioitavaa, ei
resurssia lisättäväksi.

1. Avaa kojelauta, valitse kynä (**Muokkaa käyttöliittymää**) ja sitten
   **Lisää kortti**.
2. Vieritä alas ja valitse **Manuaalinen**.
3. Liitä tämä ja valitse **Tallenna**:

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

Tämä tapa tarvitsee Markkinapaikasta [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
-kortin. Jos sinulla on muita Live Track -moduuleja, lisää yksi
`- domain: geo_location` -suodatin kullekin niiden lähteelle
(`live_track_intercity_rail`, `live_track_aircraft` ja niin edelleen).

**Ilman auto-entities-korttia:** LiveTrackMapCard voi valita itse, mitä se
näyttää, `entity_filter`-asetuksella. Liitä tämä sen sijaan; muuta ei tarvitse
asentaa:

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

Muut Live Track -moduulit lisätään `entity_filter`-asetukseen samalla tavalla:
yksi `- domain: geo_location` -sääntö lisää kutakin lähdettä kohden.

**Kartalla:**

* Jokainen juna on kiekko linjansa tai rautatiensä väreissä, junanumerolla tai
  linjalla. Useimmilla rautateillä värit vaihtuvat suunnan mukaan: täytetty
  suurimmasta kaupungista poispäin, valkoinen sitä kohti.
* Nuoli näyttää junan kulkusuunnan. Paikallaan seisova juna säilyttää viimeisen
  suuntansa.
* **Osoita** junaa nähdäksesi sen rautatien, numeron tai linjan ja missä se
  kulkee. **Napsauta** sitä nähdäksesi kaikki tiedot, myös seuraavan aseman ja
  myöhästymisen.

Jos kojelautojesi resurssit määritellään YAML:ssa
(`lovelace: resource_mode: yaml`), mitään ei voi rekisteröidä puolestasi:
silloin **Korjaukset**-kohdan ilmoitus kertoo tarkat rivit, jotka lisätään
tiedostoon `configuration.yaml`. Ne näyttävät tältä, paikkamerkkien tilalla
integraation oma osoite:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_commuter_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Jokaisessa Live Track -moduulissa on kortin kopio, ja se rekisteröi kortin,
kun Home Assistant käynnistyy. Yhdessä ne pitävät kohdassa **Asetukset →
Kojelaudat → Resurssit** täsmälleen yhden rivin: uusimman korttiversion, joka
millä tahansa niistä on mukana, ei koskaan vanhempaa. Korttiin, jonka olet
itse asentanut Markkinapaikasta, ei kosketa. Kun poistat tämän moduulin
viimeisen rautatien, rivi siirtyy toiselle Live Track -moduulille, tai se
poistetaan, jos muita ei ole. Jos integraation tiedostot poistetaan, kun sen
rautatiet ovat yhä käytössä, eikä muuta Live Track -moduulia ole asennettu,
poista rivi itse kohdassa **Asetukset → Kojelaudat → Resurssit**.

**Jos haluat asentaa kortin käsin**, noudata
[kortin README-tiedoston](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track)
ohjeita. Itse tekemääsi riviä, joka on kansiossa `/local/` tai missä tahansa
muussa osoitteessa olevalle kopiolle, ei koskaan muuteta eikä poisteta. Niin
kauan kuin se lataa kortin, jokainen Live Track -moduuli jättää kortin sille,
vaikka moduulissa olisi uudempi julkaisu, eikä mikään kohdassa **Korjaukset**
kerro siitä. Palataksesi moduulin kopioon poista rivisi kohdassa **Asetukset →
Kojelaudat → Resurssit** ja käynnistä Home Assistant uudelleen. Jos poistat
kopiosi tiedoston, poista myös sen rivi: niin kauan kuin rivi, jonka tiedosto on
poissa, on jäljellä, moduuli ei lisää omaa riviään.

Mikä tahansa muu karttakortti, joka näyttää `geo_location`-entiteettejä,
näyttää myös junat tavallisina merkkeinä.

---

## Käytä sitä automaatioissa

Kaikki ovat tavallisia Home Assistant -entiteettejä, joten automaatioeditori
toimii niiden kanssa ilman koodia.

**Ilmoitus puhelimeen, kun rautatiesi näyttää tuskin yhtään junaa** (syöte on
ehkä pysähtynyt, tai liikenteessä voi olla häiriö):

1. **Asetukset → Automaatiot & tilanteet → Lisää automaatio → Luo uusi
   automaatio**.
2. **Kun**: **Laukaisuehto** → **Entiteetti** → **Numeerinen tila ylitti
   kynnysarvon**. Valitse rautatien entiteetti **Trains in service** ja
   **Alle** `3`.
3. **Tee sitten**: **Lisää toiminto**, hae puhelimesi ilmoitustoiminto (siinä
   on puhelimesi nimi) ja kirjoita viesti, esimerkiksi:

   ```text
   Tuskin yhtään junaa kartalla: tarkista rautatien oma sovellus
   ```

4. **Tallenna**.

**Muita ideoita:** valo, joka syttyy, kun juna on alle 1 km:n (0,6 mailin)
päässä kodistasi Helsingissä (Suomi), merkkien etäisyyden perusteella;
kojelaudan laskuri Metran liikenteessä olevista junista aamuruuhkassa
(Chicago, Yhdysvallat); viesti, kun päivän ensimmäinen juna kulkee
Brisbanessa (Australia), kun **Trains in service** nousee yli nollan.

---

## Kaikki kartalla, tarkemmin

### Junat ja kalusto, joka ei ole liikenteessä

Jokainen juna on yksi merkki. Sen tila on sen etäisyys kodistasi
kilometreinä. Merkki ilmestyy, kun rautatien syöte ilmoittaa junan, ja
poistuu, kun juna poistuu syötteestä (3 minuutin kuluttua, jotta lyhyt katkos
syötteessä ei poista sitä).

* **Liikenteessä olevalla junalla** on junanumero tai linja sen mukaan, miten
  rautatie ne numeroi (kukin rautatie alla kertoo kumpi).
* **Kalustolla, joka ei ole liikenteessä,** on `NIS` ja yksikkönumero, jotta
  yksikkönumeroa ei koskaan luulla junanumeroksi. Se näkyy vain liikkuessaan
  ja poistuu kartalta seistyään 10 minuuttia. Ota **Näytä seisova kalusto**
  käyttöön nähdäksesi syötteen kaikki kalustoyksiköt.
* **Kahden sijainnin välillä** karttakortti siirtää merkin todellisesta
  sijainnista seuraavaan. Viimeisen todellisen sijainnin jälkeen ei keksitä
  mitään.
* **Sijainti, joka ei ole radalla, hylätään.** Radan ulkopuolelle ilmoitettu
  juna näytetään viimeisessä radalla olleessa sijainnissaan enintään 10
  minuuttia, ja sitten se piilotetaan, kunnes se palaa. Junaa, joka nähdään
  ensimmäisen kerran radan ulkopuolella, ei näytetä.
* **Myöhässä ja paljon myöhässä**: jos rautatie julkaisee oman säännön
  myöhässä olevalle junalle, integraatio käyttää sitä ja kertoo sen alla.

Jokaisella junalla: `marker_label`, `observed_at` (milloin sijainti piti
paikkansa), `course_deg` (liikkuessa), `next_stop` ja `arrival_estimated_at`
(kun tiedossa), `delay_min`, `stalled`, `attribution` sekä kahden sijainnin
välillä `previous_latitude`, `previous_longitude`, `previous_observed_at` ja
`segment_duration_s`. Sijainnilla, jonka integraatio on arvioinut eikä
rautatie ilmoittanut, on `position_source: estimated`.

### Adelaide Metro (Etelä-Australia, Australia)

Adelaide Metron avoimesta syötteestä, jossa ovat myös sen raitiovaunut ja
bussit (niitä ei piirretä tässä). Sijainnit ovat GPS-sijainteja junan omalla
suunnalla. Adelaide ei julkaise junanumeroa, joten nimiö on Adelaide Metron
käyttämän reittikoodin kolme ensimmäistä kirjainta (SEA, FLN, GAW, BEL, OUT ja
niin edelleen); osoitettaessa näkyvä ruutu antaa koko koodin ("SEAFRD to
Seaford · railcar 4006"). Värit ovat linjakartan: Belair vihreä, Seaford ja
Flinders oranssi, Gawler punainen, Outer Harbor, Port Dock ja Grange sininen;
täytetty keskustasta poispäin, valkoinen kohti Adelaide Railway Stationia.
Yli 5 minuuttia vanha sijainti, tai yli 1 km:n päässä kaikista Adelaiden
rautatiereiteistä oleva, hylätään. Myöhässä 5 minuutista (Adelaide Metron oma
sääntö), paljon myöhässä 10 minuutista.

### Perthin junat (Länsi-Australia, Australia)

⚠ **Perth ei julkaise reaaliaikaisia sijainteja.** Jokainen juna piirretään
Länsi-Australian Public Transport Authorityn aikataulusta: sijoitettuna
reitilleen suunniteltujen aikojen mukaan, merkittynä arvioksi, ilman
myöhästymistä. Aikataulu tarkistetaan kerran päivässä. Nimiö on linjan kolme
ensimmäistä kirjainta (MAN, YAN, ARM, FRE, MID, ELL, AIR, THO; STA Stadium
Specialille); osoitettaessa näkyvä ruutu kertoo "Mandurah Line · Perth
Underground–Mandurah". Värit ovat linjakartan: täytetty Perthistä poispäin,
valkoinen Perthiä kohti.

### Queensland Rail Citytrain (Queensland, Australia)

Translinkin avoimesta syötteestä. ⚠ Sijainnit ovat kiinteitä pisteitä
radalla, eivät GPS:ää, ilman nopeutta ja suuntaa; nuoli seuraa junan reittiä
aikataulussa. Yli 5 minuuttia vanha sijainti hylätään, koska syöte pitää
junan, jonka sijainti on jäätynyt, liikennepäivän loppuun asti. Nimiö on
linjan T-numero Translinkin linjaväreissä, käännettynä etelään kulkeville
junille, ja tähti ylimääräisille vuoroille, joilla ei ole T-numeroa. Myöhässä
4 minuutista, Gold Coast-, Rosewood- ja Sunshine Coast -linjoilla 6
minuutista (Queensland Railin oma sääntö).

### NSW TrainLink Intercity (Uusi Etelä-Wales, Australia)

Transport for NSW:n NSW TrainLink- ja Sydney Trains -syötteistä omalla
avaimellasi. Vuoro, joka on molemmissa syötteissä, on yksi merkki. Nimiö on
linjakoodi (BMT, CCN, HUN, SCO, SHL); vuoro ja sen päätepisteet näkyvät
osoitettaessa näkyvässä ruudussa ("Train KN56 · Bomaderry–Kiama"). Linjan väri
aikataulusta, täytetty Sydney Centralista poispäin ja käännetty sitä kohti.
Tyhjät junat ovat `NIS` ja vuoronsa, harmaina. Seuraava asema on asema, ei
koskaan raide. ⚠ Yli 10 minuuttia vanhaa sijaintia ei piirretä, ja juna
poistetaan, kun sen vuoro on päättynyt. Myöhässä 6 minuutista (Transport for
NSW:n Intercity-mittari), paljon myöhässä 12 minuutista.

### V/Line commuter (Victoria, Australia)

Transport Victorian V/Line-syötteestä omalla avaimellasi. Nimiö on
linjakoodi (GEL, BAT, BGO, SER, TRN); junanumero ja linja näkyvät
osoitettaessa näkyvässä ruudussa ("Train 8037 · Bendigo - Melbourne via
Gisborne"). Kaikki linjat ovat V/Linen violettia: täytetty Melbournesta
poispäin, valkoinen Southern Crossia kohti. ⚠ V/Linen sijainnit seuraavat
aikataulua enemmän kuin junaa: vuoro poistuu syötteestä noin minuutin
suunnitellun saapumisensa jälkeen, missä juna sitten onkin, ja sijainnit
jäätyvät keskiyön tienoilla. Siksi juna säilyttää viimeisen sijaintinsa
enintään 10 minuuttia ja poistuu sitten kartalta, ja myöhässä oleva juna voi
kadota ennen viimeistä asemaansa. Myöhässä 6 minuutista (V/Linen sääntö
lähijunille), paljon myöhässä 12 minuutista.

### NS Sprinter (Alankomaat)

NS:n kalustotiedoista omalla avaimellasi. Nimiö on junanumero; osoitettaessa
näkyvä ruutu kertoo "Sprinter 6632 · Dordrecht–Arnhem Centraal". NS:n keltainen
NS:n sinisellä renkaalla. Tämä on täällä ainoa syöte, joka ilmoittaa junan
oman nopeuden ja suunnan, ja molemmat välitetään (`speed_kmh`, `course_deg`).
Seuraava asema ja myöhästyminen tulevat OVapin aikataulusta. Rata on NS:n
SpoorKaart, joka ladataan kerran päivässä; juna liukuu sitä pitkin kahden
sijainnin välillä, ja yli 1 km:n päässä siitä oleva sijainti hylätään.
Myöhässä 3 minuutista (NS:n oma määritelmä), paljon myöhässä 10 minuutista.

### Renfe Cercanías ja Rodalies (Espanja)

Renfen avoimesta syötteestä, kukin 15 verkosta omana kohtanaan. Nimiö on linja
(C5, R2N) linjan omassa värissä Renfen aikataulusta. Junanumero ja linjan nimi
näkyvät osoitettaessa näkyvässä ruudussa. ⚠ Renfe sijoittaa junansa niiden
reitille eikä GPS:llä, joten ne seisovat ja sitten hyppäävät. Juna liikkuu
vain eteenpäin omaa linjaansa: sijainti sen vierestä, taaksepäin sitä pitkin
tai mahdottoman nopea hylätään, ja viimeinen hyvä säilytetään enintään 10
minuuttia. Junaa sanotaan pysähtyneeksi vasta 6 minuutin jälkeen samassa
paikassa. Renfe ei julkaise sääntöä myöhässä olevalle junalle, joten
karttakortin omat rajat ovat käytössä.

### Irish Rail (Irlanti)

Irish Railin reaaliaikaisesta palvelusta, National Transport Authorityn
aikataululla reittejä ja asemia varten. ⚠ Irish Rail ilmoittaa junan vain,
kun se ohittaa muutaman minuutin välein olevia opastimia, joten jokainen juna
piirretään aikataulustaan ja viimeisimmästä myöhästymisestään siirrettynä
reittiään pitkin; Corkin junat, joita Irish Rail ei seuraa, tulevat vain
aikataulusta. Nimiö on junanumero ilman kirjainta (P508 näyttää 508). Väri on
linjan väri Transport for Irelandin linjakartalla, käännettynä Dublinia tai
Corkia kohti. Myöhässä 5 minuutista (Irish Railin oma sääntö), paljon
myöhässä 10 minuutista.

### Vy, Go-Ahead Norge ja Flytoget (Norja)

Enturista, kukin rautatie omana kohtanaan. Nimiö on linjakoodi (L1, L2, L4,
L5, FLY1, FLY2); junanumero ja linjan nimi näkyvät osoitettaessa näkyvässä
ruudussa. L-linjalla on aikataulun väri, täytetty Oslo S:stä poispäin (L4:llä
Bergenistä, L5:llä Stavangerista) ja käännetty sitä kohti. Flytoget on harmaa
oranssilla renkaalla Oslon lentoasemaa kohti ja oranssi harmaalla renkaalla
sieltä poispäin. Entur ei julkaise nopeutta eikä suuntaa, joten nuoli seuraa
junan linjaa. Oslon pitkissä tunneleissa juna, jonka sijainnit lakkaavat
tulemasta, siirretään linjaansa pitkin, kunnes ne palaavat. Myöhässä 4
minuutista, paljon myöhässä 8 minuutista.

### SL Pendeltåg, Västtågen ja Arlanda Express (Ruotsi)

Trafikverketistä omalla ilmaisella avaimellasi (yksi avain kaikille
kolmelle). Nimiö on junanumero; tuotemerkki, numero ja pääteasemat näkyvät
osoitettaessa näkyvässä ruudussa. SL Pendeltåg on vaaleanpunainen, Västtågen
vaaleansininen, Arlanda Express keltainen; kukin kääntää värinsä kohti
Stockholm C:tä (pendeltågille Stockholm City) tai, vuorolla, joka ei pysähdy
kummallakaan, kohti suurempaa päätekaupunkiaan. Kahden sijainnin välillä juna
liukuu vuoronsa linjaa pitkin, ja yli 1 km:n päässä siitä oleva sijainti
hylätään. Myöhässä 3 minuutista SL Pendeltågilla (Region Stockholmin sääntö),
paljon myöhässä 6 minuutista; myöhässä 6 ja paljon myöhässä 12 minuutista
kahdella muulla (Trafikverketin sääntö).

### VR:n ja HSL:n lähijunat (Suomi)

Fintrafficin Digitrafficista. Juna on vuoro: junanumero ja lähtöpäivä. Nimiö
on linjatunnus, väritettynä niin kuin HSL:n kartat ja asemakyltit värittävät
linjat: HSL:n violetti, kun seuraava asema on HSL:n vyöhykkeillä A–E, VR:n
vihreä niiden ulkopuolella. Helsingistä poispäin kulkeva juna on täytetty
kiekko; Helsinkiä kohti kulkeva on valkoinen. Juna näytetään ensimmäiseltä
asemaltaan viimeiselle asemalleen, ja sitten se poistetaan. V-linjan vuorot
ilman matkustajia näytetään `NIS`-merkinnällä liikkuessaan. Kahden sijainnin
välillä juna liukuu rataa pitkin. I- ja P-junat eivät ilmoita sijaintia
Kehäradan lentoasematunnelissa, joten siellä integraatio siirtää junaa rataa
pitkin sen aikataulun mukaan, kunnes todellinen sijainti palaa. Myöhässä 4
minuutista (VR:n sääntö), paljon myöhässä 8 minuutista. Yli 10 minuuttia
vanha sijainti hylätään.

### Metra ja South Shore Line (Yhdysvallat)

Metra omasta syötteestään omalla avaimellasi; South Shore Line syötteestä,
jonka ETA SPOT julkaisee NICTD:lle, ilman avainta. Nimiö on junanumero. Metra
kertoo seuraavan aseman ja ajan. South Shore Linen syöte antaa vain
pysäkkinumeron ja myöhästymisen, joten aikataulu antaa aseman ja ajan. Yli
300 m:n päässä kaikista North American Rail Networkin (Yhdysvallat) raiteista,
tai rautatien omasta reitistä, oleva sijainti hylätään. ⚠ Joinakin päivinä
Metran syöte on liittänyt vain harvat junistaan vuoroon; muut näkyvät silloin
`NIS`-merkinnällä tai eivät lainkaan, ja kartta näyttää hiljaiselta päivältä.
Laskuri **Trains in service** näyttää tällaiset päivät jälkikäteen.

---

## Kaikki sen luomat entiteetit

Kullekin rautatielle:

| Entiteetti | Mikä se on |
|---|---|
| `sensor.<rautatie>_trains_in_service` | **Trains in service**: kuinka monta liikenteessä olevaa junaa rautatien syöte nyt ilmoittaa. Metralle: `sensor.metra_chicago_area_trains_in_service` |
| `sensor.<rautatie>_vehicles_not_in_service` | **Vehicles not in service**: kuinka monta kalustoyksikköä, jotka eivät ole liikenteessä, syöte ilmoittaa |
| `geo_location.<rautatie>_unit_…` | yksi junaa tai kalustoyksikköä kohden (`geo_location.metra_unit_8426`); se tulee ja menee junan mukana. Jokaisella on `source: live_track_commuter_rail`, ja sen tila on sen etäisyys kodistasi kilometreinä |

Entiteettien nimet ovat englanniksi, oli Home Assistantisi kieli mikä
tahansa.

Jokaisella rautatiellä on tunnettu kalusto. Merkin entiteettitunnus tulee
rautatiestä ja kalustoyksikön numerosta syötteessä, ei koskaan nimiöstä, joten
sama yksikkö saa saman entiteettitunnuksen joka kerta, kun se ilmestyy:
`geo_location.metra_unit_8426` on aina Metran vaunu 8426. Merkki poistetaan,
kun yksikkö poistuu syötteestä, tai 10 minuutin seisomisen jälkeen, kun
**Näytä seisova kalusto** on pois päältä. Merkeillä ei ole yksilöllistä
tunnusta, kuten ei millään Live Trackin karttamerkillä, joten niitä ei voi
nimetä uudelleen, piilottaa eikä liittää alueeseen käyttöliittymässä. Kahdella
sensorilla on yksilöllinen tunnus, ja ne voi nimetä uudelleen.

Attribuutit, jotka muuttuvat jokaisella päivityskerralla, merkkien sijainnit
ja ajat, tallentuvat Home Assistantin historiaan kuten minkä tahansa
entiteetin. Kahdella sensorilla ei ole attribuutteja, joten niiden
säilyttäminen maksaa vähän, ja ne kertovat, kuinka monta junaa päivän aikana
kulki. Jos haluat pitää merkit historian ulkopuolella, lisää tämä tiedostoon
`configuration.yaml` ja käynnistä uudelleen:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_unit_*
```

Jos tiedostossasi `configuration.yaml` on jo `recorder:`-osio, lisää vain malli
`geo_location.*_unit_*` kohtien `exclude:` ja `entity_globs:` alle. Malli
osuu vain tämän moduulin junamerkkeihin. Karttakortilla, joka on asetettu
piirtämään historiaa, ei sitten ole jälkeä piirrettävänä.

---

## Mitä se lähettää ja lataa

**Sijainnistasi.** Ei mitään. Kotisi sijaintia käytetään vain Home
Assistantisi sisällä, jokaisen junan etäisyyden laskemiseen. Avaimesi, jos
rautatie tarvitsee sellaisen, lähetetään vain sille rautatielle. Mitään muuta
sinusta ei lähetetä minnekään. Jokainen palvelu näkee internetosoitteesi,
kuten mikä tahansa verkkosivu.

**Kuinka paljon.** Jokainen reaaliaikainen syöte luetaan jokaisella
päivityskerralla, oletuksena 30 sekunnin välein (**Päivitysväli**, 15–600
sekuntia), tai harvemmin, jos taulukko niin kertoo. Kun useampi Live Track
-moduuli lukee samaa syötettä, yksi yhteinen asiakas lukee sen kerran
kaikille. Mitattu 19. marraskuuta 2026 klo 02.20–02.40 UTC:

| Rautatie | Reaaliaikainen syöte, yksi lukukerta | Aikataulu |
|---|---|---|
| Adelaide Metro (Australia) | 298 kt | 20 Mt, kun Adelaide Metro julkaisee uuden version |
| Perthin junat (Australia) | ei mitään: Perth ei julkaise reaaliaikaista syötettä | 28 Mt, kun se muuttuu, tarkistetaan päivittäin |
| Queensland Rail Citytrain (Australia) | 141 kt | 42 Mt, joka päivä |
| NSW TrainLink Intercity (Australia) | 402 kt neljästä syötteestä, enintään kerran 55 sekunnissa | 51 Mt (kaksi aikataulua), kun se muuttuu, tarkistetaan päivittäin |
| V/Line commuter (Australia) | 14 kt | 59 Mt, kun se muuttuu, tarkistetaan päivittäin |
| NS Sprinter (Alankomaat) | 1,2 kt; myöhästymiset OVapilta, 1,6 Mt, 5 minuutin välein ja vain kun ne muuttuvat | OVapin aikataulu, 274 Mt, enintään kerran viikossa ja vain kun se muuttuu; NS:n ratakartta, 1,3 Mt, joka päivä |
| Renfe Cercanías ja Rodalies (Espanja) | yksi syöte kaikille 15 verkolle: 26 tavua, yöllä, kun junia ei kulje | 16 Mt, joka päivä |
| Irish Rail (Irlanti) | 0,2 kt, enintään kerran 55 sekunnissa | 6,6 Mt, kun se muuttuu, tarkistetaan päivittäin; asemaluettelo, 18 kt, kerran viikossa |
| Vy, Go-Ahead Norge, Flytoget (Norja) | Vy 497 kt, Go-Ahead Norge 7 kt, Flytoget 233 kt | Vy 67 Mt, Go-Ahead Norge 20 Mt, Flytoget 0,6 Mt, kun se muuttuu, tarkistetaan päivittäin |
| SL Pendeltåg, Västtågen, Arlanda Express (Ruotsi) | 3,7 kt ensimmäisellä kerralla, sitten noin 2 kt muutoksia | ei mitään; asemaluettelo, 0,15 Mt, joka päivä |
| VR:n ja HSL:n lähijunat (Suomi) | 1,1 kt pakattuna sijainneille sekä päivän junien muutokset kerran minuutissa | ei tiedostona: päivän junat tulevat reaaliaikaisten tietojen mukana |
| Metra (Yhdysvallat) | 18 kt | 0,4 Mt, joka päivä |
| South Shore Line (Yhdysvallat) | alle 1 kt | 0,14 Mt, joka päivä |

⚠ Mittaushetkellä Australiassa oli päivä, Yhdysvalloissa ilta ja Euroopassa
yö. Reaaliaikainen syöte on pienimmillään yöllä: päivällä eurooppalaiset
syötteet ovat suurempia kuin taulukossa.

**Virheen jälkeen.** Viimeiset hyvät sijainnit näytetään vielä kahden
epäonnistuneen lukukerran ajan; sitten junat merkitään saavuttamattomiksi,
kunnes syöte vastaa. Aikataulua, jota ei saada ladattua, yritetään uudelleen
tunnin kuluttua, ja nykyinen kopiosi pysyy käytössä. Jos rautatie hylkää
avaimesi jatkuvasti, Home Assistant pyytää uuden.

**Levyllä.** Aikataulut säilytetään Home Assistantin kansiossa `.storage`
nimillä, jotka alkavat `saw_`, jaettuina muiden samaa rautatietä lukevien Live
Track -moduulien kanssa: ne, joiden kohdalla lukee "kun se muuttuu", sellaisina
kuin ne ladattiin, muut pienempänä otteena. Jos poistat Live Track Commuter
Railin eikä mikään muu Live Track -moduuli käytä niitä, voit poistaa ne käsin.

---

## Auta sitä kasvamaan

Live Track Commuter Rail kasvaa yhä. Lisäämme rautateitä ja maita sitä mukaa
kuin löydämme niitä, ja haluamme tietää, mitä toivoisit seuraavaksi.

### Ehdota jotain

Puuttuuko maasi tai rautatiesi? Onko jokin väärin tai vaikea ymmärtää? Kerro
meille tavalla, joka on sinulle helpoin:

* [**Täytä lyhyt lomake**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=fi.yml)
  suomeksi. Tarvitset ilmaisen GitHub-tilin.
* **Lähetä sähköpostia** osoitteeseen
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Tiliä ei tarvita.

Kummin tahansa, auttaa, jos kerrot meille:

* mitä haluaisit nähdä, ja missä päin maailmaa;
* linkin paikkaan, jossa tiedot julkaistaan, jos tiedät sellaisen (avoimen
  datan sivu, julkinen syöte, palvelun verkkosivu): ei pakollista, mutta
  auttaa;
* Home Assistantisi kielen, jos ongelma koskee sanamuotoa tai käännöstä.

Kirjoita englanniksi tai omalla kielelläsi, kumpi on sinulle helpompaa.

### Lisää se itse, meidän avullamme

Jos haluat lisätä jotain itse, autamme sinua ensimmäisestä kysymyksestä
valmiiseen julkaisuun asti. Sinun ei tarvitse olla kehittäjä aloittaaksesi:

* **Käännös.** Asetusvalintaikkunan sanat ovat lyhyt lista lauseita yhdessä
  tekstitiedostossa. Näytämme, mikä tiedosto ja mitkä rivit.
* **Uusi rautatie.** Kerro meille, missä tiedot julkaistaan. Voimme kirjoittaa
  koodin yhdessä tai käydä omasi läpi.
* **Testaaminen siellä, missä asut.** Asenna se, katso omaa osaasi kartasta
  ja kerro, mikä on oikein ja mikä ei.
* **Korjaus tähän README-tiedostoon.** Jos jokin vaihe ei vastannut sitä,
  mitä näit, kerro meille, mitä näit.

[**Kerro meille, mitä sinulla on mielessä**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=fi.yml)
tai kirjoita osoitteeseen
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
niin vastaamme seuraavilla vaiheilla.

---

## Kielet

Tämä README: [English](README.md), **Suomi**, [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), [Español](README.es.md),
[Nederlands](README.nl.md), [Gaeilge](README.ga.md). Jokainen käännetty
README on täydellinen. Yksikään ei ole vielä ollut äidinkielisen lukijan
tarkistettavana. Jos suomi on äidinkielesi, kerro meille, luetaanko tämä README
sujuvasti: katso [Auta sitä kasvamaan](#auta-sitä-kasvamaan).

Asetusvalintaikkuna ja asetukset näkyvät Home Assistantisi kielellä, kun se
on jokin näistä: English, Suomi, Svenska, Norsk bokmål, Español, Nederlands,
Gaeilge. Muilla kielillä ne näkyvät englanniksi.

Löysitkö virheen käännöksestä, tai tarvitsetko toisen kielen? Kerro meille
osoitteessa <https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues>,
tai [käännä se meidän avullamme](#lisää-se-itse-meidän-avullamme).

---

## Tekijät ja lisenssit

Jokainen rautatie luetaan ajon aikana, Home Assistantisi toimesta, sen omasta
julkaistusta syötteestä; mitään reaaliaikaisesta syötteestä ei ole tässä
tietovarastossa. Jokainen juna mainitsee lähteensä attribuutissa
`attribution`. Kunkin rautatien ehdot sitovat sinua tietojen vastaanottajana.

* **Metra** (Yhdysvallat): GTFS-Realtime,
  [Metran lisenssisopimuksen](https://metra.com/gtfs-realtime-api-key-request-license-agreement)
  mukaisesti, jonka hyväksyt pyytäessäsi avainta.
* **South Shore Line** (NICTD, Yhdysvallat): julkinen syöte ja aikataulu,
  jotka ETA SPOT julkaisee NICTD:lle, ilman avainta ja ilman
  lisenssisopimusta.
* **Translink** (Queenslandin hallitus, Australia): tiedot lisenssillä
  CC BY 4.0 ([avoin data](https://translink.com.au/about-translink/open-data)).
* **Fintraffic / digitraffic.fi** (Suomi): tiedot lisenssillä CC BY 4.0.
  **HSL** (Suomi): vyöhykkeet, CC BY 4.0.
* **Renfe** (Espanja): tiedot lisenssillä CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)), muokattu.
* **Entur** (Norja): tiedot Norjan julkisen sektorin avoimen datan
  lisenssillä ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)), Enturin
  jakamina.
* **Trafikverket** (Ruotsi): tiedot lisenssillä [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irlanti): reaaliaikaiset tiedot; Irish Rail ei julkaise
  ehtoja. Aikataulu: [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irlanti), CC BY 4.0.
* **NS** (Alankomaat): kalustotiedot omalla avaimellasi
  [NS API -portaalista](https://apiportal.ns.nl/). Aikataulu ja myöhästymiset:
  [OVapi](https://gtfs.ovapi.nl), CC0.
* **Transport for NSW** (Australia): tiedot lisenssillä CC BY 4.0
  ([datalisenssi](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australia): tiedot lisenssillä CC BY 4.0
  ([avoin data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Adelaide Metro**, Department for Infrastructure and Transport, South
  Australia: tiedot lisenssillä CC BY 4.0 ([kehittäjätiedot](https://www.adelaidemetro.com.au/developer-info)).
* **Länsi-Australian Public Transport Authority**: aikataulutiedot saatavilla
  maksutta osoitteesta www.transperth.wa.gov.au
  ([paikkatietojen saatavuus](https://www.transperth.wa.gov.au/About/Spatial-Data-Access)).
* **Ratatiedostot kansiossa `rail/`**: North American Rail Network
  (Yhdysvaltain liikenneministeriö), vapaasti käytettävissä (public domain);
  Fintrafficin rataverkko, CC BY 4.0, muokattu; Flytogetin linjat Enturin
  tiedoista, NLOD 2.0, muokattu; Ruotsin linjat reititettynä OpenStreetMapin
  päälle, (c) OpenStreetMapin tekijät, ODbL 1.0; kaupunkien väkiluvut Ruotsin
  tilastokeskukselta (SCB), CC0. Mitä on muutettu, kerrotaan tiedostossa
  [ATTRIBUTION.md](ATTRIBUTION.md).
* **Karttakortti** on [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, kopio nathan-gsin [ha-map-cardista](https://github.com/nathan-gs/ha-map-card),
  MIT. Sen karttatiilet ja niiden tekijätiedot ovat sen README-tiedostossa.

Mikään näistä organisaatioista ei ole tehnyt tai hyväksynyt tätä
integraatiota.

**Koodi**: MIT, tiedostossa [LICENSE](LICENSE).

**Kehittäjille:** jokainen rautatie on yksi sovitin kansiossa
`custom_components/live_track_commuter_rail/operators/`; kansion `rail/`
ratatiedostot rakennetaan uudelleen kansion `tools/` skripteillä
(`build_rail.py`, `build_tracks.py`, `build_flytoget_lines.py`,
`sweden_lines.py`). Testit ajetaan komennolla
`python -m unittest discover -s tests`.

---

## Hakusanat

Home Assistant junat · lähijunat kartalla · junat reaaliajassa · junakartta ·
lähijunat · HSL · VR · Digitraffic · Fintraffic · pendeltåg · Vy · Flytoget ·
NS · Sprinter · Renfe Cercanías · Rodalies · Irish Rail · Metra · South Shore
Line · Queensland Rail · Translink · NSW TrainLink · V/Line · Adelaide Metro ·
Perthin junat · GTFS-Realtime · geo_location · karttakortti · Lovelace · HACS ·
Markkinapaikka · Live Track · LiveTrack · StrausbergAutomationWorks

---

**Kunnioitus.** StrausbergAutomationWorks tunnustaa kaikkien tämän kartan
kattamien maiden ja vesien alkuperäiskansat kaikkialla maailmassa ja osoittaa
kunnioitusta niiden vanhimmille, menneille ja nykyisille.
