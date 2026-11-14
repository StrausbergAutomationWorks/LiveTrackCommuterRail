# Live Track Commuter Rail

[English](README.md) · **Suomi** · [Svenska](README.sv.md) · [Norsk](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md)

Lähijunat reaaliajassa Home Assistantin kartalla. Live Track Commuter Rail on
Home Assistant -integraatio (custom component, asennetaan Marketplacesta /
HACSista), joka näyttää valitsemiesi lähiliikennerautateiden jokaisen junan
reaaliajassa: missä juna on, sen numero ja linja, onko se myöhässä, seuraava
pysäkki ja milloin juna on siellä. Sijainnit tulevat kunkin rautatien omasta
avoimen datan syötteestä. Jokainen juna näkyy `geo_location`-entiteettinä ja
liikkuu syötteen päivittyessä.

## Suomessa: VR lähijunat

**VR:n ja HSL:n lähijunat** Helsingin seudulla. Data: Fintraffic /
digitraffic.fi, CC BY 4.0. Avainta tai tiliä ei tarvita.

* Merkissä on linjan kirjain. Se on HSL:n violetti, kun seuraava pysäkki on HSL:n
  vyöhykkeillä A–E, ja VR:n vihreä niiden ulkopuolella. R-juna on violetti
  Jokelaan asti ja vihreä Riihimäelle. Suunta vaihtaa värit: Helsingistä poispäin
  täytetty ympyrä ja valkoinen kirjain, Helsinkiin päin valkoinen ympyrä.
* Juna on myöhässä 4 minuutista (VR:n sääntö) ja paljon myöhässä 8 minuutista.
* Kehäradan lentoasematunnelissa I- ja P-junat eivät lähetä sijaintia. Siellä
  integraatio kuljettaa junaa raiteita pitkin itse, kunnes oikea sijainti palaa
  (`position_source: estimated`).
* Kahden sijainnin välillä karttakortti liu'uttaa junaa raiteita pitkin.
  Raideverkko toimitetaan integraation mukana (Fintraffic / digitraffic.fi,
  infra-api, CC BY 4.0, muokattu).

## Kaikki rautatiet

Metra ja South Shore Line (Chicago), Renfe Cercanías ja Rodalies (Espanja),
VR lähijunat (Suomi), Vy, Go-Ahead Norge ja Flytoget (Norja), SL Pendeltåg,
Västtågen ja Arlanda Express (Ruotsi), NS Sprinter (Alankomaat), Irish Rail
(Irlanti), Queensland Rail Citytrain, NSW TrainLink Intercity, V/Line, Adelaide Metro ja Perthin junat (Australia). Avaimet ja käyttöehdot: [taulukko englanninkielisessä
README:ssä](README.md#supported-railroads).

## Osa Live Trackia

Live Track on Home Assistantin moduulijärjestelmä. Jokainen moduuli seuraa yhtä
liikkuvaa asiaa, ja kaikki moduulit piirtävät samalle kartalle. Ne jakavat yhden
Python-kirjaston ([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
ja yhden karttakortin ([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)),
joten uusi moduuli ei lisää kyselyjä jaettuun lähteeseen, kuten Digitrafficiin.
Julkaistu: Live Track Commuter Rail,
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)
ja [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT).
Kehitteillä: Live Track Intercity Rail, Live Track Ships ja Live Track Weather.

## Vaatimukset

- Home Assistant 2026.11 tai uudempi.
- Suomen junille ei tarvita avainta.
- Home Assistant asentaa tarvittavat Python-paketit, kun integraatio latautuu
  ensimmäisen kerran.

## Asennus

### Marketplacesta

Integraatio ei ole vielä Marketplacen luettelossa. Lisää se linkillä:

1. **Settings > Marketplace** ja **Add from link**.
2. Kirjoita `StrausbergAutomationWorks/LiveTrackCommuterRail`. Jos tyyppiä
   kysytään, valitse **Integration**.
3. Asenna **Live Track Commuter Rail**.
4. Käynnistä Home Assistant uudelleen. Marketplace tarjoaa uudelleenkäynnistystä
   korjauksena kohdassa **Settings > System > Repairs**.

### Käsin

1. Lataa [uusimman julkaisun](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest)
   lähdekoodi.
2. Kopioi sen kansio `custom_components/live_track_commuter_rail` Home Assistantin
   asetushakemiston `custom_components`-kansioon.
3. Käynnistä Home Assistant uudelleen.

## Käyttöönotto

**Settings > Devices & services > Add integration > Live Track Commuter Rail**.
Valitse alue ja sitten rautatie. Asetusikkuna ja alueiden nimet näkyvät suomeksi, kun Home
Assistantin kieli on suomi. Valikkojen nimet yllä ovat englanninkielisen
käyttöliittymän mukaiset.

## Data ja lisenssi

Junat luetaan ajon aikana suoraan rautatien syötteestä; tämä repositorio ei
sisällä syötteiden dataa. Jokaisen junan `attribution`-määrite kertoo lähteen.
Mukana toimitettavat rata- ja linjatiedostot ja niiden lisenssit:
[ATTRIBUTION.md](ATTRIBUTION.md). Koodi: MIT.

Tämä integraatio ei ole minkään rautatien sponsoroima, sidoksissa siihen tai sen
ylläpitämä. Kaikki yksityiskohdat: [README englanniksi](README.md).

## Hakusanat

Home Assistant junat kartalla · lähijunat reaaliajassa · junien sijainti ·
VR lähijunat · HSL junat · Digitraffic · Fintraffic · junaseuranta ·
Helsinki lähijunat kartalla · HACS integraatio
