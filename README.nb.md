# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · **Norsk** · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md)

Lokaltog i sanntid på Home Assistant-kartet ditt. Live Track Commuter Rail er en
Home Assistant-integrasjon (custom component, installeres fra Marketplace /
HACS) som viser hvert tog på lokaltogbanene du velger, i sanntid: hvor toget er,
tognummer og linje, om det er forsinket, neste stasjon og når det er ventet dit.
Posisjonene kommer fra hver jernbanes egen åpne datakilde. Hvert tog blir en
`geo_location`-entitet og flytter seg når kilden oppdateres.

## I Norge: Vy, Go-Ahead Norge og Flytoget

**Vy** (L1, L2 og L4: Oslo-området og Bergen), **Go-Ahead Norge** (L5 Jærbanen,
Stavanger–Egersund) og **Flytoget** (FLY1 og FLY2: Drammen og Stabekk til Oslo
lufthavn). Inneholder data under Norsk lisens for offentlige data (NLOD 2.0)
distribuert av Entur. Ingen nøkkel trengs.

* Markøren viser linjekoden (L1, FLY1); tognummer og linjenavn står i
  hover-boksen. En L-linje har rutetabellens farge, fylt med hvit ring fra Oslo S
  (Bergen på L4, Stavanger på L5) og omvendt mot den. Flytoget er grått med
  oransje ring mot Oslo lufthavn og oransje med grå ring fra den.
* Forsinket fra 4 minutter, svært forsinket fra 8.
* Entur publiserer verken fart eller retning, så pilen følger togets egen linje.
* I Oslos lange tunneler (Oslotunnelen, Lysaker–Sandvika, Sandvika–Asker,
  Romeriksporten, Lieråsen, Follobanen) flyttes et tog som slutter å sende
  posisjon langs linjen til der posisjonene kommer tilbake
  (`position_source: estimated`).
* Flytogets egen rutetabell tegner rette streker mellom stasjonene, så linjen
  følger med integrasjonen, kuttet fra Vys rutetabellformer over samme spor
  (data NLOD 2.0, distribuert av Entur; bearbeidet).

## Alle baner

Metra og South Shore Line (Chicago), Renfe Cercanías og Rodalies (Spania),
VR lähijunat (Finland), Vy, Go-Ahead Norge og Flytoget (Norge), SL Pendeltåg,
Västtågen og Arlanda Express (Sverige), NS Sprinter (Nederland), Irish Rail
(Irland), Queensland Rail Citytrain, NSW TrainLink Intercity, V/Line, Adelaide Metro og Perths tog (Australia). Nøkler og vilkår: [tabellen i den engelske
README-filen](README.md#supported-railroads).

## En del av Live Track

Live Track er et system av moduler for Home Assistant. Hver modul følger én type
ting som beveger seg, og alle modulene tegner på det samme kartet. De deler ett
Python-bibliotek ([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
og ett kartkort ([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)),
så en modul til gir ikke flere forespørsler mot en delt kilde som Entur.
Utgitt: Live Track Commuter Rail,
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)
og [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT).
Under utvikling: Live Track Intercity Rail (som tegner Norges F-, RE-, RX- og
R-linjer), Live Track Ships og Live Track Weather.

## Krav

- Home Assistant 2026.11 eller nyere.
- Ingen nøkkel for de norske banene.
- Home Assistant installerer Python-pakkene som trengs første gang integrasjonen
  lastes.

## Installasjon

### Fra Marketplace

Integrasjonen står ikke i Marketplace-katalogen ennå. Legg den til med lenke:

1. **Settings > Marketplace** og **Add from link**.
2. Skriv `StrausbergAutomationWorks/LiveTrackCommuterRail`. Velg
   **Integration** hvis typen etterspørres.
3. Installer **Live Track Commuter Rail**.
4. Start Home Assistant på nytt. Marketplace tilbyr omstarten som en reparasjon
   under **Settings > System > Repairs**.

### For hånd

1. Last ned kildekoden til [siste
   utgivelse](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Kopier mappen `custom_components/live_track_commuter_rail` til mappen
   `custom_components` i Home Assistants konfigurasjonskatalog.
3. Start Home Assistant på nytt.

## Oppsett

**Settings > Devices & services > Add integration > Live Track Commuter Rail**.
Velg region og så bane. Dialogen og regionnavnene vises på norsk når Home Assistant er
satt til norsk bokmål. Menynavnene over er fra det engelske grensesnittet.

## Data og lisens

Togene leses mens integrasjonen kjører, direkte fra banens kilde; ingenting fra
kildene ligger i dette repoet. Attributtet `attribution` på hvert tog oppgir
kilden. Spor- og linjefilene som følger med, og lisensene deres:
[ATTRIBUTION.md](ATTRIBUTION.md). Kode: MIT.

Integrasjonen er ikke sponset av, tilknyttet eller drevet av noen av banene.
Alle detaljer: [README på engelsk](README.md).

## Søkeord

Home Assistant tog på kartet · tog i sanntid · togposisjoner · Vy lokaltog ·
Flytoget · Go-Ahead Norge · Jærbanen · Entur API · Oslo lokaltog kart ·
HACS-integrasjon
