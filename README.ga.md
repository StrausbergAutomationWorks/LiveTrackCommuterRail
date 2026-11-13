# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · **Gaeilge**

Traenacha comaitéireachta beo ar do léarscáil Home Assistant. Is comhtháthú
Home Assistant é Live Track Commuter Rail (custom component, a shuiteáiltear ón
Marketplace / HACS) a thaispeánann gach traein ar na línte comaitéireachta a
roghnaíonn tú, i bhfíor-am: cá bhfuil an traein, a huimhir agus a líne, an
bhfuil moill uirthi, an chéad stad eile agus cathain a bheidh sí ann. Tagann na
suíomhanna ó shonraí oscailte gach oibreora. Is aonán `geo_location` gach traein,
agus bogann sí de réir mar a nuashonraítear an fhoinse.

## In Éirinn: Iarnród Éireann

**Irish Rail / Iarnród Éireann**, na seirbhísí comaitéireachta timpeall ar
Bhaile Átha Cliath agus Corcaigh. Sonraí: Irish Rail (irishrail.ie); ní
fhoilsíonn Irish Rail ceadúnas ná téarmaí dá sheirbhís bheo. Amchlár: an tÚdarás
Náisiúnta Iompair, CC BY 4.0, "mar atá"; níl an tÚdarás freagrach as earráidí
ann. Níl eochair ag teastáil.

## Na hiarnróid go léir

Metra agus South Shore Line (Chicago), Renfe Cercanías agus Rodalies (an
Spáinn), VR lähijunat (an Fhionlainn), Vy, Go-Ahead Norge agus Flytoget (an
Iorua), SL Pendeltåg, Västtågen agus Arlanda Express (an tSualainn), NS Sprinter
(an Ísiltír), Irish Rail (Éire), Queensland Rail Citytrain, NSW TrainLink
Intercity agus V/Line (an Astráil). Eochracha agus téarmaí: [an tábla sa README
Béarla](README.md#supported-railroads).

## Cuid de Live Track

Is córas modúl do Home Assistant é Live Track. Leanann gach modúl cineál amháin
ruda a bhogann, agus tarraingíonn na modúil go léir ar an léarscáil chéanna.
Roinneann siad leabharlann Python amháin
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
agus cárta léarscáile amháin
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)),
mar sin ní chuireann modúl eile iarratais bhreise ar fhoinse roinnte. Eisithe:
Live Track Commuter Rail,
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)
agus [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT).
Á bhforbairt: Live Track Intercity Rail, Live Track Ships agus Live Track
Weather.

## Riachtanais

- Home Assistant 2026.11 nó níos déanaí.
- Níl eochair ag teastáil do Irish Rail.
- Suiteálann Home Assistant na pacáistí Python a theastaíonn an chéad uair a
  luchtaítear an comhtháthú.

## Suiteáil

### Ón Marketplace

Níl an comhtháthú i gcatalóg an Marketplace fós. Cuir leis é le nasc:

1. **Settings > Marketplace** agus **Add from link**.
2. Scríobh `StrausbergAutomationWorks/LiveTrackCommuterRail`. Má iarrtar an
   cineál, roghnaigh **Integration**.
3. Suiteáil **Live Track Commuter Rail**.
4. Atosaigh Home Assistant. Tairgeann an Marketplace an t-atosú mar dheisiúchán
   faoi **Settings > System > Repairs**.

### De láimh

1. Íoslódáil cód foinse [an eisiúna is
   déanaí](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Cóipeáil an fillteán `custom_components/live_track_commuter_rail` isteach
   san fhillteán `custom_components` i gcomhadlann chumraíochta Home Assistant.
3. Atosaigh Home Assistant.

## Socrú

**Settings > Devices & services > Add integration > Live Track Commuter Rail**.
Roghnaigh réigiún agus ansin iarnród. Tá an dialóg i mBéarla faoi láthair, agus
is ainmneacha an chomhéadain Bhéarla iad ainmneacha na roghchlár thuas.

## Sonraí agus ceadúnas

Léitear na traenacha ó fhoinse gach oibreora fad atá an comhtháthú ag rith; níl
aon sonraí ó na foinsí sin sa stór seo. Insíonn tréith `attribution` gach traenach
cad é a foinse. Na comhaid iarnróid agus líne a thagann leis, agus a gceadúnais:
[ATTRIBUTION.md](ATTRIBUTION.md). Cód: MIT.

Níl an comhtháthú seo urraithe ag aon oibreoir, ná cleamhnaithe le haon cheann
acu, ná á oibriú acu. Gach mionsonra: [an README i mBéarla](README.md).

## Téarmaí cuardaigh

Home Assistant traenacha ar an léarscáil · traenacha beo · Iarnród Éireann ·
Irish Rail live trains · traenacha Bhaile Átha Cliath · Cork commuter trains ·
GTFS-Realtime · comhtháthú HACS
