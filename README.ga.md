# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · **Gaeilge** · [Gach teanga](#teangacha)

**Traenacha comaitéara do Home Assistant, ar léarscáil amháin.** Cuireann Live
Track Commuter Rail gach traein de na hiarnróid chomaitéara a roghnaíonn tú ar
do léarscáil Home Assistant, beo: cá bhfuil sí, a huimhir traenach nó a líne,
an bhfuil moill uirthi, agus a céad stad eile. Cuirtear gach iarnród leis ar
leith, óna shonraí oscailte féin.

> **Is modúl de Live Track é Live Track Commuter Rail**, teaghlach de
> chomhtháthuithe Home Assistant a tharraingíonn gach rud a ghluaiseann, agus
> an aimsir a ghluaiseann sé tríd, ar léarscáil chomhroinnte amháin:
> aerárthaí, longa, traenacha agus aimsir. Suiteáil leis féin é, nó in éineacht
> leis na modúil eile ([liosta thíos](#cuid-de-live-track-na-modúil-eile)).

> **Ag fás, agus oscailte do smaointe.** Clúdaíonn Live Track Commuter Rail 31
> iarnród in 8 dtír ar 3 mhór-roinn inniu, agus táimid ag cur tuilleadh
> iarnród agus tíortha leis. An bhfuil d'iarnród féin in easnamh?
> [Mol é](#cuidigh-leis-fás), nó cuir leis tú féin é: cabhróimid leat.

**Stádas: 0.1.4, eisithe.** Cuirtear leis an Margadh é trína nasc
([thíos](#suiteáil-é-céim-ar-chéim)); níl sé i gcatalóg an Mhargaidh fós.

Saothar bunaidh le StrausbergAutomationWorks. Níl baint aige le Metra,
Northern Indiana Commuter Transportation District (NICTD), ETA SPOT, Renfe,
Fintraffic, HSL, VR, Entur, Vy, Go-Ahead Norge, Flytoget, Trafikverket, SL,
Västtågen, Arlanda Express, Iarnród Éireann (Irish Rail), an tÚdarás
Náisiúnta Iompair (Éire), NS, OVapi, Translink, Queensland Rail, Transport
for NSW, Transport Victoria, V/Line, Adelaide Metro, Public Transport
Authority Iarthar na hAstráile, ná le haon iarnród eile, agus níor fhormhuinigh
siad é.

---

## Clár ábhair

1. [Gach rud a dhéanann sé](#gach-rud-a-dhéanann-sé)
2. [Cá n-oibríonn sé](#cá-n-oibríonn-sé)
3. [Cuid de Live Track: na modúil eile](#cuid-de-live-track-na-modúil-eile)
4. [Sula dtosaíonn tú](#sula-dtosaíonn-tú)
5. [Suiteáil é, céim ar chéim](#suiteáil-é-céim-ar-chéim)
6. [Socraigh é, céim ar chéim](#socraigh-é-céim-ar-chéim)
7. [Eochracha saor in aisce a chuireann tuilleadh ar siúl, céim ar chéim](#eochracha-saor-in-aisce-a-chuireann-tuilleadh-ar-siúl-céim-ar-chéim)
8. [Cuir an léarscáil ar phainéal](#cuir-an-léarscáil-ar-phainéal)
9. [Úsáid é in uathoibrithe](#úsáid-é-in-uathoibrithe)
10. [Gach rud ar an léarscáil, go mion](#gach-rud-ar-an-léarscáil-go-mion)
11. [Na haonáin go léir a chruthaíonn sé](#na-haonáin-go-léir-a-chruthaíonn-sé)
12. [Cad a sheolann sé agus a íoslódálann sé](#cad-a-sheolann-sé-agus-a-íoslódálann-sé)
13. [Cuidigh leis fás](#cuidigh-leis-fás)
14. [Teangacha](#teangacha)
15. [Creidiúintí agus ceadúnais](#creidiúintí-agus-ceadúnais)
16. [Eochairfhocail](#eochairfhocail)

---

## Gach rud a dhéanann sé

### Ar an léarscáil, gan aon rud le socrú

Cuireann tú **iarnród** leis: roghnaíonn tú tír nó réigiún, agus ansin ceann
dá iarnróid chomaitéara. Ansin feictear gach rud thíos don iarnród sin. Cuir
an comhtháthú leis arís do gach iarnród eile atá uait.

| Cad | Cá háit | Ó |
|---|---|---|
| **Traenacha i seirbhís**: marcóir amháin in aghaidh na traenach, lena huimhir traenach nó a líne, i ndathanna an iarnróid féin, casta sa treo ina bhfuil sí ag dul | gach iarnród | foinse bheo gach iarnróid |
| **Moill**: taispeántar traein mar mhoillithe nó an-mhoillithe de réir riail an iarnróid féin, nuair a fhoilsíonn an t-iarnród riail | gach iarnród a thuairiscíonn moill | foinse agus clár ama gach iarnróid |
| **An chéad stad eile agus a am**: an stáisiún ag a stopfaidh an traein ina dhiaidh seo, agus cathain a bheidh sí ann | gach iarnród a luann a fhoinse nó a chlár ama é | foinse agus clár ama gach iarnróid |
| **Traenacha a leanann an rian**: idir dhá shuíomh sleamhnaíonn traein feadh na líne, ní díreach trasna | An Fhionlainn, An Ísiltír, An tSualainn | comhaid riain a thagann leis an gcomhtháthú nó a íoslódálann sé |
| **Feithiclí nach bhfuil i seirbhís**: traenacha folmha ag dul idir clóis, a thaispeántar fad atá siad ag gluaiseacht | iarnróid a dtuairiscíonn a bhfoinsí iad | foinse gach iarnróid |
| **Dhá chomhaireamh in aghaidh an iarnróid**: traenacha i seirbhís, agus feithiclí nach bhfuil i seirbhís | gach iarnród | an fhoinse chéanna |

### Le heochair nó cuntas saor in aisce de do chuid féin

| Eochair nó cuntas saor in aisce | Cad a chuireann sé leis |
|---|---|
| Eochair **Metra** | traenacha Metra (ceantar Chicago, Stáit Aontaithe Mheiriceá) |
| Eochair **Trafikverket** | SL Pendeltåg, pendeltåg Västtågen agus Arlanda Express (An tSualainn) |
| Eochair **thairseach API NS** | traenacha NS Sprinter (An Ísiltír) |
| Eochair **Transport for NSW Open Data** | traenacha NSW TrainLink Intercity (New South Wales, An Astráil) |
| Eochair **Transport Victoria Open Data** | traenacha comaitéara V/Line (Victoria, An Astráil) |

Tógann gach ceann acu cúpla nóiméad le fáil: [céim ar chéim thíos](#eochracha-saor-in-aisce-a-chuireann-tuilleadh-ar-siúl-céim-ar-chéim).
Níl eochair de dhíth ar an 26 iarnród eile.

---

## Cá n-oibríonn sé

| Réigiún | Cad a fhaigheann tú | Ó | Riachtanach |
|---|---|---|---|
| **An Astráil**: An Astráil Theas | traenacha Adelaide Metro: na línte Belair, Gawler, Outer Harbor agus Seaford | Adelaide Metro | faic |
| **An Astráil**: Iarthar na hAstráile | traenacha Perth, na naoi líne ar fad, ón gclár ama amháin ([cén fáth](#traenacha-perth-iarthar-na-hastráile-an-astráil)) | Public Transport Authority Iarthar na hAstráile | faic |
| **An Astráil**: New South Wales | NSW TrainLink Intercity: na línte Blue Mountains, Central Coast and Newcastle, Hunter, South Coast agus Southern Highlands ó Sydney | Transport for NSW | eochair saor in aisce |
| **An Astráil**: Queensland | Queensland Rail Citytrain, oirdheisceart Queensland (Brisbane) | Translink | faic |
| **An Astráil**: Victoria | traenacha comaitéara V/Line: na línte Geelong, Ballarat, Bendigo, Seymour agus Traralgon | Transport Victoria | eochair saor in aisce |
| **An Eoraip**: Éire | traenacha comaitéara Iarnród Éireann timpeall Bhaile Átha Cliath agus Chorcaí | Iarnród Éireann, an tÚdarás Náisiúnta Iompair | faic |
| **An Eoraip**: An Fhionlainn | traenacha comaitéara VR agus HSL timpeall Heilsincí | Fintraffic Digitraffic | faic |
| **An Eoraip**: An Iorua | L1, L2 agus L4 Vy (ceantar Oslo, Bergen), L5 Go-Ahead Norge (Stavanger), Flytoget (aerfort Oslo) | Entur | faic |
| **An Eoraip**: An Ísiltír | traenacha NS Sprinter, an tír ar fad | NS, OVapi | eochair saor in aisce |
| **An Eoraip**: An Spáinn | Renfe Cercanías agus Rodalies de Catalunya, 15 líonra: Maidrid, Barcelona, Asturias, Sevilla, Cádiz, Málaga, Valencia, Murcia agus Alicante, Cartagena, Ferrol, León, Bilbao, San Sebastián, Cantabria, Zaragoza | Renfe | faic |
| **An Eoraip**: An tSualainn | SL Pendeltåg (Stócólm), pendeltåg Västtågen (Göteborg), Arlanda Express | Trafikverket | eochair saor in aisce |
| **Meiriceá Thuaidh**: Stáit Aontaithe Mheiriceá | Metra (ceantar Chicago: Illinois, Wisconsin) | Metra | eochair saor in aisce |
| **Meiriceá Thuaidh**: Stáit Aontaithe Mheiriceá | South Shore Line (Chicago go South Bend: Illinois, Indiana) | NICTD, trí ETA SPOT | faic |

Níl sé ar an liosta? [Inis dúinn](#cuidigh-leis-fás). Nuair a fhoilsíonn duine
éigin na sonraí go hoscailte, féachfaimid an féidir iad a chur leis.

⚠ **Níl traein níos fearr ná foinse a hiarnróid.** Cuireann iarnróid áirithe
a dtraenacha de réir an chláir ama seachas le GPS, ní thuairiscíonn cuid eile
traein ach ag comharthaí atá cúpla nóiméad óna chéile, agus stopann nó reonn
foinsí áirithe ar feadh tamaill. Tá teorainneacha gach iarnróid faoi
[Gach rud ar an léarscáil, go mion](#gach-rud-ar-an-léarscáil-go-mion).

⚠ **Ní hé seo eolas oifigiúil an iarnróid.** Sula dtaistealaíonn tú, féach ar
aip nó ar shuíomh gréasáin an iarnróid féin.

---

## Cuid de Live Track: na modúil eile

Is sraith de chomhtháthuithe Home Assistant é Live Track, ceann amháin do gach
cineál ruda a ghluaiseann, iad ar fad tarraingthe ar an gcárta léarscáile
céanna. Oibríonn gach ceann leis féin; le chéile déanann siad pictiúr beo
amháin. Roinneann siad an cárta léarscáile agus leabharlann Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
mar sin ní chuireann modúl eile a shuiteáil iarratais le foinse atá á léamh ag
modúl eile cheana.

| Modúl | Cad a chuireann sé ar an léarscáil | Stádas |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aerárthaí os do chionn ó ADS-B, le bealaí agus deilbhíní de réir cineáil | eisithe |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | longa agus báid ó AIS, in aice leat nó áit ar bith | eisithe |
| **Live Track Commuter Rail** | traenacha comaitéara i Meiriceá Thuaidh, san Eoraip agus san Astráil (an modúl seo) | eisithe |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | traenacha idirchathrach agus fadachair i Meiriceá Thuaidh, san Eoraip agus san Astráil | eisithe |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aerárthaí agus soithí inimirce agus forfheidhmithe dlí cónaidhme, ó liostaí poiblí | eisithe |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | aimsir, stoirmeacha agus guaiseacha nádúrtha | eisithe |
| Live Track Stations | cláir imeachta agus foláirimh "am imeacht" do gach stáisiún | beartaithe |
| Live Track Satellites | satailítí ag dul thar bráid os do chionn | beartaithe |
| Live Track Freight Trains | traenacha lastais agus oibre nuair a fhoilsíonn iarnróid iad | beartaithe |
| Live Track Transit | busanna cathrach, tramanna, báid farantóireachta agus meitreo | beartaithe |
| Live Track Intercity Buses | cóistí idirchathrach agus réigiúnacha | beartaithe |
| Live Track Commuter Buses | busanna comaitéara | beartaithe |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | an cárta léarscáile comhroinnte a dtarraingíonn gach modúl air | eisithe, suiteáilte le gach modúl |

Tá gach rud saor in aisce agus foinse oscailte. Ní choinnítear aon rud siar do
lucht urraíochta.

---

## Sula dtosaíonn tú

* **Home Assistant** 2026.11 nó níos déanaí.
* **An Margadh** (HACS) i do Home Assistant, chun é a shuiteáil agus a
  nuashonrú ar an mbealach éasca. Gan é is féidir leat na comhaid a chóipeáil
  de láimh.
* **Rochtain ar an idirlíon** do Home Assistant: tagann gach traein ó fhoinse
  phoiblí a hiarnróid féin.
* **Roghnach: auto-entities** ón Margadh, chun na marcóirí a chur ar an
  léarscáil (féach [Cuir an léarscáil ar phainéal](#cuir-an-léarscáil-ar-phainéal)).
* Faic le híoc. Níl cuntas de dhíth ar 26
  den 31 iarnród; teastaíonn eochair saor in aisce dá gcuid féin ón gcúig cinn eile
  ([thuas](#le-heochair-nó-cuntas-saor-in-aisce-de-do-chuid-féin)).
* Suiteálann Home Assistant féin na pacáistí Python atá de dhíth air
  (`saw-livetrack`, `gtfs-realtime-bindings` agus `tzdata`) an chéad uair a
  luchtaítear an comhtháthú.

---

## Suiteáil é, céim ar chéim

### Ón Margadh (molta)

Níl Live Track Commuter Rail i gcatalóg an Mhargaidh fós. Cuir leis é trína
nasc:

1. I Home Assistant, oscail **Socruithe → Margadh** (HACS).
2. Roghnaigh **Cuir leis ón nasc** (nó an roghchlár trí phonc → **Stórtha
   saincheaptha**).
3. Iontráil `StrausbergAutomationWorks/LiveTrackCommuterRail`. Má iarrtar an
   cineál, roghnaigh **Comhtháthú**.
4. Aimsigh **Live Track Commuter Rail** sa liosta agus roghnaigh **Download**
   nó **Suiteáil**.
5. **Atosaigh Home Assistant**: tairgeann **Socruithe → Córas →
   Deisiúcháin** an t-atosú, nó úsáid **Socruithe → Córas → Atosaigh**.

Ina dhiaidh sin tairgeann an Margadh gach eisiúint nua mar nuashonrú.

### De láimh

1. Íoslódáil cód foinse na
   [heisiúna is déanaí](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Cóipeáil a fhillteán `custom_components/live_track_commuter_rail` isteach
   san fhillteán `custom_components` i bhfillteán cumraíochta do Home
   Assistant (cruthaigh `custom_components` mura bhfuil sé ann).
3. Atosaigh Home Assistant.

Chun nuashonrú de láimh, cuir fillteán na heisiúna nua in áit an fhillteáin
agus atosaigh.

---

## Socraigh é, céim ar chéim

1. Oscail **Socruithe → Gléasanna & seirbhísí**.
2. Roghnaigh **Cuir comhtháthú leis** (thíos ar dheis) agus cuardaigh **Live
   Track Commuter Rail**.
3. **Réigiún**: roghnaigh tír an iarnróid, nó an tír agus an réigiún. Níl ar an
   liosta ach áiteanna a bhfuil iarnród amháin ar a laghad iontu. Roghnaigh
   **Cuir isteach**.
4. **Iarnród**: roghnaigh an t-iarnród. Roghnaigh **Cuir isteach**.
5. **Eochair API**: do Metra, do na trí iarnród Sualannacha, do NS Sprinter,
   do NSW TrainLink Intercity agus do V/Line commuter amháin. Greamaigh
   d'eochair ([conas ceann a fháil](#eochracha-saor-in-aisce-a-chuireann-tuilleadh-ar-siúl-céim-ar-chéim))
   agus roghnaigh **Cuir isteach**. Scipeálann na hiarnróid eile an chéim seo.

Sin é. Feictear na traenacha laistigh de nóiméad. Nuair a thagann na chéad
stadanna eile ó chlár ama an iarnróid, líontar iad sna chéad nóiméid, a luaithe
a bhíonn an clár ama íoslódáilte. Chun iarnród eile a leanúint, cuir an
comhtháthú leis arís. Diúltaítear don iarnród céanna faoi dhó.

### Athraigh a dtaispeánann sé: na roghanna

Oscail **Socruithe → Gléasanna & seirbhísí → Live Track Commuter Rail →
Cumraigh** (an roth fiaclach) ar an iarnród is mian leat a athrú. Gach rogha,
i bhfocail shimplí:

| Rogha | Cad a dhéanann sé | Réamhshocrú |
|---|---|---|
| **Eatramh léite** | cé chomh minic a léitear foinse an iarnróid, 15 go 600 soicind. Nuashonraítear formhór na bhfoinsí timpeall gach 30 soicind, mar sin is annamh a thaispeánann eatramh níos giorra níos mó | 30 soicind |
| **Taispeáin feithiclí páirceáilte** | as: ní thaispeántar feithiclí nach bhfuil i seirbhís ach fad atá siad ag bogadh, agus fágann siad an léarscáil tar éis 10 nóiméad ina seasamh. Ar siúl: taispeántar gach feithicil san fhoinse, traenacha páirceáilte san áireamh | as |

---

## Eochracha saor in aisce a chuireann tuilleadh ar siúl, céim ar chéim

Iarrann cúig iarnród a eochair féin ar gach úsáideoir. Tá gach ceann de na
heochracha seo saor in aisce, agus faigheann gach duine a shuiteálann Live
Track Commuter Rail a eochair féin. Greamaíonn tú an eochair nuair a iarrann
an dialóg socraithe í ([céim 5 thuas](#socraigh-é-céim-ar-chéim)). Ní iarrtar
ach an eochair: gan pasfhocal ná rún. Stóráiltear an eochair i Home Assistant
leis an gcomhtháthú agus ní scríobhtar sa loga í choíche. Má leanann an
t-iarnród ag diúltú di, iarrann Home Assistant ceann nua ort.

### Metra (ceantar Chicago, Stáit Aontaithe Mheiriceá)

1. Oscail <https://metra.com/developers> agus scrollaigh síos go **GTFS
   Realtime API Key Request Form**.
2. Líon isteach **First Name** (céadainm), **Last Name** (sloinne), **Email
   Address** (seoladh ríomhphoist, iarrtar faoi dhó é) agus **Purpose of Use**
   (an úsáid, mar shampla: Home Assistant).
3. Cuir tic le **I have read and agree to the License Agreement.** (léigh mé
   an comhaontú ceadúnais agus glacaim leis; tá sé ag
   <https://metra.com/gtfs-realtime-api-key-request-license-agreement>) agus
   roghnaigh **Submit**.
4. Greamaigh an eochair a fhaigheann tú ó Metra in **Eochair API** nuair a
   chuireann tú Metra leis.

### Trafikverket (An tSualainn: SL Pendeltåg, Västtågen, Arlanda Express)

1. Oscail <https://data.trafikverket.se/oauth2/Account/register>.
2. Líon isteach **Email**, **Displayname** (ainm taispeána), **Password**
   (pasfhocal) agus **Confirm password**, cuir tic le **Accept license and
   Agreement**, agus roghnaigh **Register**.
3. Oscail <https://data.trafikverket.se/get-started> agus roghnaigh **Create
   key**, faoi **Create a key**. Sínigh isteach leis an gcuntas a rinne tú,
   agus cruthaigh an eochair.
4. Greamaigh in **Eochair API** í nuair a chuireann tú iarnród Sualannach leis.
   Freastalaíonn eochair amháin ar na trí cinn.

### NS (An Ísiltír)

1. Oscail <https://apiportal.ns.nl/>, roghnaigh **Inloggen** (sínigh isteach),
   ansin **Externe bezoeker** (cuairteoir seachtrach).
2. Líon isteach an fhoirm agus seol í. Deimhníonn ríomhphost an clárú. Is
   féidir go dtógfaidh sé suas le 5 nóiméad sula bhfeictear na APIanna sa
   tairseach.
3. Oscail leathanach an **Virtual Train API** (suíomhanna traenacha NS). Faoi
   **Related Products**, oscail a tháirge, tabhair ainm do do shíntiús, agus
   roghnaigh **Subscribe**.
4. Nuair a bheidh an síntiús ceadaithe ag NS, beidh d'eochair ar do leathanach
   próifíle. Greamaigh in **Eochair API** í nuair a chuireann tú NS Sprinter
   leis.

### Transport for NSW (New South Wales, An Astráil)

1. Oscail <https://opendata.transport.nsw.gov.au/>, roghnaigh **Register**,
   cruthaigh cuntas, agus logáil isteach.
2. Roghnaigh deilbhín do phróifíle úsáideora, ansin **API Tokens**.
3. Clóscríobh ainm don eochair agus roghnaigh **CREATE API TOKEN**. Cóipeáil an
   eochair láithreach: ní thaispeánann an suíomh í ach uair amháin.
4. Greamaigh in **Eochair API** í nuair a chuireann tú NSW TrainLink Intercity
   leis. Greamaigh an eochair amháin: cuireann Live Track Commuter Rail an
   focal `apikey` léi féin.

### Transport Victoria (Victoria, An Astráil)

1. Oscail <https://opendata.transport.vic.gov.au/>, roghnaigh **Login**, ansin
   **Sign up**.
2. Iontráil do shonraí agus roghnaigh **Create Account**. Iontráil an cód ón
   ríomhphost a fhaigheann tú agus roghnaigh **Confirm**.
3. Iarrann an tairseach aip fíordheimhnithe ar do ghuthán: scanáil an cód QR
   léi, iontráil cód na haipe agus roghnaigh **Confirm**. Ansin sínigh isteach
   le do sheoladh ríomhphoist, do phasfhocal agus cód na haipe.
4. Roghnaigh **My Account** → **Profile** → **API tokens**. Tá d'eochair ann
   cheana. Greamaigh in **Eochair API** í nuair a chuireann tú V/Line commuter
   leis.

---

## Cuir an léarscáil ar phainéal

Is é [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
an léarscáil, an cárta a dtarraingíonn gach modúl Live Track air. **Suiteáiltear
é le Live Track Commuter Rail**: faic le híoslódáil, faic le cóipeáil, gan aon
acmhainn le cur leis.

1. Oscail painéal, roghnaigh an peann luaidhe (**Cuir painéal in eagar**), ansin
   **Cuir cárta leis**.
2. Scrollaigh go dtí an bun agus roghnaigh **Lámhleabhar** (an rogha láimhe).
3. Greamaigh é seo, agus roghnaigh **Sábháil**:

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

Teastaíonn [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
ón Margadh don fhoirm seo. Má tá modúil eile Live Track suiteáilte agat, cuir
scagaire `- domain: geo_location` eile leis do gach ceann dá bhfoinsí
(`live_track_intercity_rail`, `live_track_aircraft` agus mar sin de).

**Gan auto-entities:** is féidir le LiveTrackMapCard féin a roghnú cad a
thaispeánann sí, le `entity_filter`. Greamaigh é seo ina ionad sin; níl aon
rud eile le suiteáil:

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

Téann modúil eile Live Track in `entity_filter` ar an mbealach céanna: riail
`- domain: geo_location` eile do gach foinse.

**Ar an léarscáil:**

* Is diosca gach traein i ndathanna a líne nó a hiarnróid, lena huimhir
  traenach nó a líne. Ar fhormhór na n-iarnród athraíonn na dathanna leis an
  treo: líonta ag fágáil na príomhchathrach, bán ag dul ina treo.
* Taispeánann saighead an treo ina bhfuil an traein ag dul. Coinníonn traein
  atá ina stad a treo deireanach.
* **Dírigh** ar thraein chun a hiarnród, a huimhir nó a líne a fheiceáil, agus
  cá bhfuil sí ag dul. **Cliceáil** uirthi chun a sonraí go léir a fheiceáil,
  a céad stad eile agus a moill san áireamh.

Má shocraítear acmhainní do phainéal i YAML
(`lovelace: resource_mode: yaml`), ní féidir aon rud a chlárú duit: ansin
tugann ceist faoi **Deisiúcháin** na línte beachta le cur le
`configuration.yaml`. Breathnaíonn siad mar seo, le seoladh an
chomhtháthaithe féin in áit na sealbhóirí áite:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_commuter_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Iompraíonn gach modúl Live Track cóip den chárta agus cláraíonn sé é nuair a
thosaíonn Home Assistant. Le chéile coinníonn siad ró amháin go díreach in
**Socruithe → Deais → Acmhainní**: an leagan is nuaí den chárta atá ag aon
cheann acu, ní leagan níos sine choíche. Ní bhaintear le cárta a shuiteáil tú
féin tríd an Margadh. Nuair a bhaineann tú iarnród deireanach an mhodúil seo,
téann an ró chuig modúl Live Track eile, nó baintear é mura bhfuil aon cheann
fágtha. Má bhaintear comhaid an chomhtháthaithe agus a iarnróid fós
socraithe, agus gan aon mhodúl Live Track eile suiteáilte, bain féin an ró in
**Socruithe → Deais → Acmhainní**.

**Chun an cárta a shuiteáil de láimh ina ionad sin**, lean na céimeanna i
[README an chárta](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
Ní dhírítear ró a rinne tú féin do chóip faoi `/local/` ar chóip an mhodúil
seo ach nuair is eisiúint níos nuaí í cóip an mhodúil seo.

Taispeánann aon chárta léarscáile eile a thaispeánann aonáin `geo_location` na
traenacha freisin, mar ghnáthmharcóirí.

---

## Úsáid é in uathoibrithe

Is gnáthaonán Home Assistant gach rud, mar sin oibríonn eagarthóir na
n-uathoibrithe leo, gan aon chód.

**Fógra ar do ghuthán nuair is beag nach dtaispeánann d'iarnród aon
traein** (b'fhéidir gur stop an fhoinse, nó go bhfuil an tseirbhís
suaite):

1. **Socruithe → Uathoibriú agus radhairc → Cruthaigh uathoibriú → Cruthaigh
   uathoibriú nua**.
2. **Cathain**: **Cuir truicear leis** → **Aonán** → **Numeric state crossed
   threshold** (staid uimhriúil thar thairseach; tá an lipéad seo i mBéarla i
   Home Assistant). Roghnaigh aonán **Trains in service** an iarnróid, agus
   **Thíos** `3`.
3. **Ansin a dhéanamh**: **Cuir gníomh leis**, cuardaigh gníomh fógra do
   ghutháin (tá ainm do ghutháin air), agus iontráil teachtaireacht, mar
   shampla:

   ```text
   Is beag traein ar an léarscáil: féach ar aip an iarnróid
   ```

4. **Sábháil**.

**Smaointe eile:** solas a lasann nuair a bhíonn traein laistigh de 1 km (0.6
míle) de do theach i mBaile Átha Cliath (Éire), ó fhad na marcóirí; comhaireamh
ar an bpainéal de thraenacha Metra i seirbhís le linn bhuaic na maidine
(Chicago, Stáit Aontaithe Mheiriceá); teachtaireacht nuair a ritheann an chéad
traein den lá i Brisbane (An Astráil), nuair a éiríonn **Trains in service**
os cionn 0.

---

## Gach rud ar an léarscáil, go mion

### Traenacha, agus feithiclí nach bhfuil i seirbhís

Is marcóir amháin gach traein. Is é a staid a fad ó do theach, i
gciliméadair. Feictear an marcóir nuair a thuairiscíonn foinse an iarnróid an
traein agus baintear é nuair a fhágann an traein an fhoinse (tar éis 3
nóiméad, ionas nach mbaineann briseadh gearr san fhoinse é).

* **Tá ar thraein i seirbhís** a huimhir traenach nó a líne, mar a uimhríonn
  an t-iarnród iad (deir gach iarnród thíos cé acu).
* **Tá ar fheithicil nach bhfuil i seirbhís** `NIS` agus a huimhir aonaid,
  ionas nach measfar uimhir aonaid mar uimhir traenach choíche. Ní thaispeántar
  í ach fad atá sí ag gluaiseacht, agus fágann sí an léarscáil tar éis 10
  nóiméad ina seasamh. Cuir **Taispeáin feithiclí páirceáilte** ar siúl chun
  gach feithicil san fhoinse a fheiceáil.
* **Idir dhá shuíomh** bogann an cárta léarscáile an marcóir ó shuíomh fíor
  amháin go dtí an chéad cheann eile. Ní chumtar aon rud tar éis an tsuímh fhír
  dheireanaigh.
* **Diúltaítear do shuíomh nach bhfuil ar rian.** Taispeántar traein a
  thuairiscítear lasmuigh de na rianta ag a suíomh deireanach a bhí orthu, ar
  feadh 10 nóiméad ar a mhéad, agus ansin cuirtear i bhfolach í go dtí go
  dtagann sí ar ais. Ní thaispeántar traein a fheictear den chéad uair
  lasmuigh de na rianta.
* **Moillithe agus an-mhoillithe**: nuair a fhoilsíonn an t-iarnród a riail
  féin do thraein mhoillithe, úsáideann an comhtháthú í, agus deir sé é sin
  thíos.

Ar gach traein: `marker_label`, `observed_at` (cathain a bhí a suíomh fíor),
`course_deg` (fad atá sí ag gluaiseacht), `next_stop` agus
`arrival_estimated_at` (nuair is eol iad), `delay_min`, `stalled`,
`attribution`, agus, idir dhá shuíomh, `previous_latitude`,
`previous_longitude`, `previous_observed_at` agus `segment_duration_s`. Tá
`position_source: estimated` ar shuíomh a mheas an comhtháthú, seachas ceann
a thuairiscigh an t-iarnród.

### Adelaide Metro (An Astráil Theas, An Astráil)

Ó fhoinse oscailte Adelaide Metro, ina bhfuil a thramanna agus a bhusanna
freisin (ní tharraingítear anseo iad). Is suíomhanna GPS iad, le treo na
traenach féin. Ní fhoilsíonn Adelaide uimhir traenach, mar sin is é an lipéad
na chéad trí litir de chód an bhealaigh a úsáideann Adelaide Metro (SEA, FLN,
GAW, BEL, OUT agus mar sin de); tugann an bosca a fheictear nuair a dhíríonn tú
air an cód iomlán ("SEAFRD to Seaford · railcar 4006"). Is iad na dathanna
dathanna léarscáil an líonra: Belair glas, Seaford agus Flinders oráiste,
Gawler dearg, Outer Harbor, Port Dock agus Grange gorm; líonta ag fágáil lár
na cathrach, bán ag dul i dtreo Adelaide Railway Station. Diúltaítear do
shuíomh atá níos sine ná 5 nóiméad, nó níos mó ná 1 km ó gach bealach iarnróid
in Adelaide. Moillithe ó 5 nóiméad (riail Adelaide Metro féin),
an-mhoillithe ó 10.

### Traenacha Perth (Iarthar na hAstráile, An Astráil)

⚠ **Ní fhoilsíonn Perth suíomhanna beo.** Tarraingítear gach traein ó chlár
ama Public Transport Authority Iarthar na hAstráile: curtha feadh a bealaigh de
réir a hamanna sceidealta, marcáilte mar mheastachán, gan moill. Seiceáiltear
an clár ama uair sa lá. Is é an lipéad na chéad trí litir den líne (MAN, YAN,
ARM, FRE, MID, ELL, AIR, THO; STA do Stadium Special); deir an bosca a
fheictear nuair a dhíríonn tú air "Mandurah Line · Perth
Underground–Mandurah". Is iad na dathanna dathanna léarscáil an líonra:
líonta ag fágáil Perth, bán ag dul i dtreo Perth.

### NSW TrainLink Intercity (New South Wales, An Astráil)

Ó fhoinsí NSW TrainLink agus Sydney Trains de chuid Transport for NSW, le
d'eochair féin. Is marcóir amháin turas atá sa dá fhoinse. Is é an lipéad cód
na líne (BMT, CCN, HUN, SCO, SHL); tá an turas agus a chríochfoirt sa bhosca a
fheictear nuair a dhíríonn tú air ("Train KN56 · Bomaderry–Kiama"). Dath na
líne ón gclár ama, líonta ag fágáil Sydney Central agus a mhalairt ag dul ina
treo. Is `NIS` agus a dturas iad traenacha folmha, i liath. Is stáisiún an
chéad stad eile, ní ardán choíche. ⚠ Ní tharraingítear suíomh atá níos sine
ná 10 nóiméad, agus baintear traein nuair a bhíonn a turas thart. Moillithe ó
6 nóiméad (tomhas Intercity Transport for NSW), an-mhoillithe ó 12.

### Queensland Rail Citytrain (Queensland, An Astráil)

Ó fhoinse oscailte Translink. ⚠ Is pointí seasta ar an rian iad na
suíomhanna, ní GPS, gan luas ná treo; leanann an tsaighead bealach na traenach
sa chlár ama. Diúltaítear do shuíomh atá níos sine ná 5 nóiméad, mar coinníonn
an fhoinse traein a bhfuil a suíomh reoite go dtí deireadh an lae seirbhíse.
Is é an lipéad uimhir T na líne i ndathanna líne Translink, a mhalairt do
thraenacha ag dul ó dheas, agus réalta do thurais speisialta gan uimhir T.
Moillithe ó 4 nóiméad, 6 ar na línte Gold Coast, Rosewood agus Sunshine Coast
(riail Queensland Rail féin).

### V/Line commuter (Victoria, An Astráil)

Ó fhoinse V/Line de chuid Transport Victoria, le d'eochair féin. Is é an
lipéad cód na líne (GEL, BAT, BGO, SER, TRN); tá uimhir na traenach agus an
líne sa bhosca a fheictear nuair a dhíríonn tú air ("Train 8037 · Bendigo -
Melbourne via Gisborne"). Tá gach líne i gcorcra V/Line: líonta ag fágáil
Melbourne, bán ag dul i dtreo Southern Cross. ⚠ Leanann suíomhanna V/Line an
clár ama níos mó ná an traein: fágann turas an fhoinse thart ar nóiméad tar
éis a theachta sceidealta, cibé áit a bhfuil an traein, agus reonn na
suíomhanna timpeall meán oíche. Mar sin coinníonn traein a suíomh deireanach ar
feadh 10 nóiméad ar a mhéad agus fágann sí an léarscáil ansin, agus is féidir
le traein mhoillithe imeacht roimh a stáisiún deireanach. Moillithe ó 6
nóiméad (riail V/Line do sheirbhísí comaitéara), an-mhoillithe ó 12.

### Iarnród Éireann (Éire)

Ó sheirbhís bheo Iarnród Éireann, le clár ama an Údaráis Náisiúnta Iompair do
na bealaí agus na stáisiúin. ⚠ Ní thuairiscíonn Iarnród Éireann traein ach
nuair a théann sí thar chomharthaí atá cúpla nóiméad óna chéile, mar sin
tarraingítear gach traein óna clár ama agus a moill is déanaí, bogtha feadh a
bealaigh; tagann traenacha Chorcaí, nach leanann Iarnród Éireann, ón gclár ama
amháin. Is é an lipéad uimhir na traenach gan a litir (taispeánann P508 508).
Is é an dath dath na líne ar léarscáil líonra Transport for Ireland, a mhalairt
i dtreo Bhaile Átha Cliath nó Chorcaí. Moillithe ó 5 nóiméad (riail Iarnród
Éireann féin), an-mhoillithe ó 10.

### Traenacha comaitéara VR agus HSL (An Fhionlainn)

Ó Digitraffic de chuid Fintraffic. Is turas traein: a huimhir traenach agus an
lá ar fhág sí. Is é an lipéad litir na líne, daite mar a dhathaíonn léarscáileanna
agus comharthaí stáisiúin HSL na línte: corcra HSL fad atá an chéad stad eile i
gcriosanna táillí A go E HSL, glas VR lasmuigh díobh. Is diosca líonta traein
ag dul ó Heilsincí; is bán traein ag dul ina treo. Taispeántar traein óna chéad
stáisiún go dtí a stad deireanach, agus baintear ansin í. Taispeántar turais
líne V gan phaisinéirí mar `NIS` fad atá siad ag gluaiseacht. Idir dhá shuíomh
sleamhnaíonn traein feadh na rianta. Ní thugann línte I agus P suíomh i dtollán
Ring Rail ag aerfort Heilsincí, mar sin bogann an comhtháthú an traein feadh na
rianta de réir a clár ama go dtí go dtagann suíomh fíor ar ais. Moillithe ó 4
nóiméad (riail VR), an-mhoillithe ó 8. Diúltaítear do shuíomh atá níos sine ná
10 nóiméad.

### Vy, Go-Ahead Norge agus Flytoget (An Iorua)

Ó Entur, gach iarnród ina iontráil féin. Is é an lipéad cód na líne (L1, L2,
L4, L5, FLY1, FLY2); tá uimhir na traenach agus ainm na líne sa bhosca a
fheictear nuair a dhíríonn tú air. Caitheann líne L a dath ón gclár ama, líonta
ag fágáil Oslo S (Bergen ar L4, Stavanger ar L5) agus a mhalairt ag dul ina
treo. Tá Flytoget liath le fáinne oráiste i dtreo aerfort Oslo, agus oráiste le
fáinne liath á fhágáil. Ní fhoilsíonn Entur luas ná treo, mar sin leanann an
tsaighead líne na traenach. I dtolláin fhada Oslo, bogtar traein a stopann a
suíomhanna feadh a líne go dtí go dtagann siad ar ais. Moillithe ó 4 nóiméad,
an-mhoillithe ó 8.

### NS Sprinter (An Ísiltír)

Ó shonraí feithiclí NS, le d'eochair féin. Is é an lipéad uimhir na traenach;
deir an bosca a fheictear nuair a dhíríonn tú air "Sprinter 6632 ·
Dordrecht–Arnhem Centraal". Buí NS le fáinne gorm NS. Is í seo an t-aon
fhoinse anseo a thuairiscíonn luas agus treo na traenach féin, agus cuirtear an
dá cheann ar aghaidh (`speed_kmh`, `course_deg`). Tagann an chéad stad eile
agus an mhoill ó chlár ama OVapi. Is é an rian SpoorKaart NS, íoslódáilte uair
sa lá; sleamhnaíonn traein feadh air idir dhá shuíomh, agus diúltaítear do
shuíomh atá níos mó ná 1 km uaidh. Moillithe ó 3 nóiméad (sainmhíniú NS féin),
an-mhoillithe ó 10.

### Renfe Cercanías agus Rodalies (An Spáinn)

Ó fhoinse oscailte Renfe, gach ceann de na 15 líonra ina iontráil féin. Is é
an lipéad an líne (C5, R2N) i ndath na líne féin ó chlár ama Renfe. Tá uimhir
na traenach agus ainm na líne sa bhosca a fheictear nuair a dhíríonn tú air.
⚠ Cuireann Renfe a dtraenacha ar a mbealach seachas le GPS, mar sin seasann
siad agus léimeann siad ansin. Ní ghluaiseann traein ach ar aghaidh feadh a
líne féin: diúltaítear do shuíomh lasmuigh di, siar feadh na líne nó
dodhéanta tapa, agus coinnítear an ceann maith deireanach ar feadh 10 nóiméad
ar a mhéad. Ní deirtear go bhfuil traein ina stad go dtí tar éis 6 nóiméad san
áit chéanna. Ní fhoilsíonn Renfe aon riail do thraein mhoillithe, mar sin
baineann tairseacha an chárta léarscáile féin.

### SL Pendeltåg, Västtågen agus Arlanda Express (An tSualainn)

Ó Trafikverket, le d'eochair féin saor in aisce (eochair amháin do na trí
cinn). Is é an lipéad uimhir na traenach; tá an branda, an uimhir agus na
stáisiúin deiridh sa bhosca a fheictear nuair a dhíríonn tú air. Tá SL
Pendeltåg bándearg, Västtågen gorm éadrom, Arlanda Express buí; malartaíonn
gach ceann a dhathanna i dtreo Stockholm C (Stockholm City don phendeltåg) nó,
ar thuras nach stopann ag ceachtar acu, i dtreo na cathrach deiridh is mó.
Idir dhá shuíomh sleamhnaíonn traein feadh líne a turais, agus diúltaítear do
shuíomh atá níos mó ná 1 km uaithi. Moillithe ó 3 nóiméad ar SL Pendeltåg
(riail Region Stockholm), an-mhoillithe ó 6; moillithe ó 6 agus an-mhoillithe
ó 12 ar an dá cheann eile (riail Trafikverket).

### Metra agus an South Shore Line (Stáit Aontaithe Mheiriceá)

Metra óna fhoinse féin, le d'eochair féin; an South Shore Line ón bhfoinse a
fhoilsíonn ETA SPOT do NICTD, gan eochair. Is é an lipéad uimhir na traenach.
Ainmníonn Metra an chéad stad eile agus a am. Ní thugann foinse an South Shore
Line ach uimhir stad agus moill, mar sin soláthraíonn a clár ama an stáisiún
agus an t-am. Diúltaítear do shuíomh atá níos mó ná 300 m ó aon rian sa North
American Rail Network (Stáit Aontaithe Mheiriceá), nó ó bhealach an iarnróid
féin. ⚠ Ar roinnt laethanta níor nasc foinse Metra ach beagán dá traenacha le
turas; taispeántar an chuid eile ansin mar `NIS` nó ní thaispeántar ar chor ar
bith iad, agus tá cuma lá ciúin ar an léarscáil. Taispeánann an comhaireamh
**Trains in service** laethanta mar sin ina dhiaidh sin.

---

## Na haonáin go léir a chruthaíonn sé

Do gach iarnród:

| Aonán | Cad é |
|---|---|
| `sensor.<iarnród>_trains_in_service` | **Trains in service**: cé mhéad traein i seirbhís a thuairiscíonn foinse an iarnróid anois. Do Metra: `sensor.metra_chicago_area_trains_in_service` |
| `sensor.<iarnród>_vehicles_not_in_service` | **Vehicles not in service**: cé mhéad feithicil nach bhfuil i seirbhís a thuairiscíonn an fhoinse |
| `geo_location.<iarnród>_unit_…` | ceann amháin in aghaidh gach traenach nó feithicle (`geo_location.metra_unit_8426`); tagann agus imíonn sé leis an traein. Tá `source: live_track_commuter_rail` ar gach ceann, agus is é a staid a fad ó do theach i gciliméadair |

Tá ainmneacha na n-aonán i mBéarla, cibé teanga atá ar do Home Assistant.

Tá cabhlach aitheanta ag gach iarnród. Tagann aitheantas aonáin marcóra ón
iarnród agus ó uimhir na feithicle san fhoinse, ní óna lipéad choíche, mar sin
faigheann an fheithicil chéanna an t-aitheantas aonáin céanna gach uair a
fheictear í: is é `geo_location.metra_unit_8426` carráiste 8426 Metra i
gcónaí. Baintear an marcóir nuair a fhágann an fheithicil an fhoinse, nó tar
éis 10 nóiméad páirceáilte fad atá **Taispeáin feithiclí páirceáilte** as. Níl
aitheantas uathúil ag na marcóirí, mar nach bhfuil ag aon mharcóir léarscáile
Live Track, mar sin ní féidir iad a athainmniú, a fholú ná limistéar a
thabhairt dóibh sa chomhéadan. Tá aitheantas uathúil ag an dá bhraiteoir agus
is féidir iad a athainmniú.

Taifeadtar i stair Home Assistant na tréithe a athraíonn ag gach léamh,
suíomhanna agus amanna na marcóirí, mar a dhéantar do gach aonán. Níl aon
tréithe ag an dá bhraiteoir, mar sin is beag a chosnaíonn sé iad a choinneáil,
agus is iad an taifead ar cé mhéad traein a rith ar lá. Chun na marcóirí a
choinneáil as an stair, cuir é seo le `configuration.yaml`, agus atosaigh:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_unit_*
```

Má tá rannán `recorder:` i do `configuration.yaml` cheana, ná cuir leis ach an
patrún `geo_location.*_unit_*`, faoi `exclude:` agus `entity_globs:`. Ní
oireann an patrún ach do mharcóirí traenacha an mhodúil seo. Ní bheidh rian le
tarraingt ansin ag cárta léarscáile atá socraithe chun stair a tharraingt.

---

## Cad a sheolann sé agus a íoslódálann sé

**Faoi do shuíomh.** Faic. Ní úsáidtear suíomh do thí ach taobh istigh de do
Home Assistant, chun fad gach traenach a thabhairt. Ní sheoltar d'eochair,
nuair a bhíonn ceann de dhíth ar iarnród, ach chuig an iarnród sin. Ní sheoltar
aon rud eile fút áit ar bith. Feiceann gach seirbhís do sheoladh idirlín, mar a
fheiceann aon suíomh gréasáin.

**Cé mhéad.** Léitear gach foinse bheo ag gach léamh, gach 30 soicind de réir
réamhshocraithe (**Eatramh léite**, 15 go 600 soicind), nó níos annaimhe
nuair a deir an tábla é. Nuair a léann roinnt modúl Live Track an fhoinse
chéanna, léann cliant comhroinnte amháin í uair amháin dóibh go léir. Tomhaiste
ar 19 Samhain 2026, 02:20 go 02:40 UTC:

| Iarnród | Foinse bheo, léamh amháin | Clár ama |
|---|---|---|
| Adelaide Metro (An Astráil) | 298 KB | 20 MB, nuair a fhoilsíonn Adelaide Metro leagan nua |
| Traenacha Perth (An Astráil) | faic: ní fhoilsíonn Perth foinse bheo | 28 MB, nuair a athraíonn sé, seiceáilte gach lá |
| NSW TrainLink Intercity (An Astráil) | 402 KB ó cheithre fhoinse, uair amháin gach 55 soicind ar a mhéad | 51 MB (dhá chlár ama), nuair a athraíonn sé, seiceáilte gach lá |
| Queensland Rail Citytrain (An Astráil) | 141 KB | 42 MB, gach lá |
| V/Line commuter (An Astráil) | 14 KB | 59 MB, nuair a athraíonn sé, seiceáilte gach lá |
| Iarnród Éireann (Éire) | 0.2 KB, uair amháin gach 55 soicind ar a mhéad | 6.6 MB, nuair a athraíonn sé, seiceáilte gach lá; liosta na stáisiún, 18 KB, uair sa tseachtain |
| Traenacha comaitéara VR agus HSL (An Fhionlainn) | 1.1 KB comhbhrúite do na suíomhanna, móide na hathruithe ar thraenacha an lae uair sa nóiméad | ní comhad é: tagann traenacha an lae leis na sonraí beo |
| Vy, Go-Ahead Norge, Flytoget (An Iorua) | Vy 497 KB, Go-Ahead Norge 7 KB, Flytoget 233 KB | Vy 67 MB, Go-Ahead Norge 20 MB, Flytoget 0.6 MB, nuair a athraíonn sé, seiceáilte gach lá |
| NS Sprinter (An Ísiltír) | 1.2 KB; moilleanna ó OVapi, 1.6 MB, gach 5 nóiméad agus nuair a athraíonn siad amháin | clár ama OVapi, 274 MB, uair sa tseachtain ar a mhéad agus nuair a athraíonn sé amháin; léarscáil rianta NS, 1.3 MB, gach lá |
| Renfe Cercanías agus Rodalies (An Spáinn) | foinse amháin do na 15 líonra: 26 beart, san oíche gan traenacha ag rith | 16 MB, gach lá |
| SL Pendeltåg, Västtågen, Arlanda Express (An tSualainn) | 3.7 KB an chéad uair, ansin thart ar 2 KB d'athruithe | faic; liosta na stáisiún, 0.15 MB, gach lá |
| Metra (Stáit Aontaithe Mheiriceá) | 18 KB | 0.4 MB, gach lá |
| South Shore Line (Stáit Aontaithe Mheiriceá) | faoi 1 KB | 0.14 MB, gach lá |

⚠ Nuair a tomhaiseadh é seo bhí sé ina lá san Astráil, ina tráthnóna i Stáit
Aontaithe Mheiriceá agus ina oíche san Eoraip. Bíonn foinse bheo ag a laghad
san oíche: i rith an lae bíonn na foinsí Eorpacha níos mó ná mar a thaispeánann
an tábla.

**Tar éis earráide.** Taispeántar na suíomhanna maithe deireanacha ar feadh dhá
léamh theipthe eile; ansin marcáiltear na traenacha mar neamh-infhaighte go
dtí go bhfreagraíonn an fhoinse. Déantar iarracht arís uair an chloig ina
dhiaidh sin ar chlár ama nach féidir a íoslódáil, agus fanann an chóip atá
agat in úsáid. Má leanann an t-iarnród ag diúltú d'eochair, iarrann Home
Assistant ceann nua.

**Ar an diosca.** Coinnítear na cláir ama i bhfillteán `.storage` Home
Assistant faoi ainmneacha a thosaíonn le `saw_`, roinnte leis na modúil Live
Track eile a léann an t-iarnród céanna: iad siúd atá marcáilte "nuair a
athraíonn sé" mar a íoslódáladh iad, na cinn eile mar shliocht níos lú. Má
bhaineann tú Live Track Commuter Rail agus mura n-úsáideann aon mhodúl Live
Track eile iad, is féidir leat iad a scriosadh de láimh.

---

## Cuidigh leis fás

Tá Live Track Commuter Rail fós ag fás. Cuirimid iarnróid agus tíortha leis de
réir mar a aimsímid iad, agus ba mhaith linn a fháil amach cad ba mhaith leat
ina dhiaidh seo.

### Mol rud éigin

An bhfuil do thír nó d'iarnród in easnamh? An bhfuil rud éigin mícheart, nó
deacair a thuiscint? Inis dúinn cibé bealach is fusa duit:

* [**Líon isteach foirm ghearr**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=ga.yml)
  i nGaeilge. Teastaíonn cuntas GitHub saor in aisce uait.
* **Scríobh ríomhphost** chuig
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Níl cuntas de dhíth.

Cibé bealach, cabhraíonn sé má insíonn tú dúinn:

* cad ba mhaith leat a fheiceáil, agus cén áit ar domhan;
* nasc chuig an áit a bhfoilsítear na sonraí, má tá ceann ar eolas agat
  (leathanach sonraí oscailte, foinse phoiblí, suíomh gréasáin seirbhíse): níl
  sé riachtanach, ach cabhraíonn sé;
* teanga do Home Assistant, más é an fhoclaíocht nó aistriúchán an fhadhb.

Scríobh i mBéarla nó i do theanga féin, cibé acu is fusa duit.

### Cuir leis tú féin é, le cabhair uainn

Más mian leat rud éigin a chur leis tú féin, cabhróimid leat é a dhéanamh, ón
gcéad cheist go dtí an eisiúint chríochnaithe. Ní gá duit a bheith i do
fhorbróir chun tosú:

* **Aistriúchán.** Is liosta gearr frásaí i gcomhad téacs amháin iad focail na
  dialóige socraithe. Taispeánfaimid duit cén comhad agus cé na línte.
* **Iarnród nua.** Inis dúinn cá bhfoilsítear na sonraí. Is féidir linn an cód
  a scríobh le chéile, nó féachaint ar do chuid féin.
* **Tástáil san áit a bhfuil tú i do chónaí.** Suiteáil é, féach ar do chuid
  féin den léarscáil, agus inis dúinn cad atá ceart agus cad nach bhfuil.
* **Ceartúchán ar an README seo.** Mura raibh céim ag teacht leis an méid a
  chonaic tú, inis dúinn cad a chonaic tú.

[**Inis dúinn cad atá ar intinn agat**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=ga.yml)
nó scríobh chuig
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
agus freagróimid leis na chéad chéimeanna eile.

---

## Teangacha

An README seo: [English](README.md), [Suomi](README.fi.md),
[Svenska](README.sv.md), [Norsk bokmål](README.nb.md),
[Español](README.es.md), [Nederlands](README.nl.md), **Gaeilge**. Tá gach
README aistrithe iomlán. Níor léigh cainteoir dúchais aon cheann acu fós. Más í
an Ghaeilge do theanga dhúchais, inis dúinn an léann an README seo go maith:
féach [Cuidigh leis fás](#cuidigh-leis-fás).

Feictear an dialóg socraithe agus na roghanna i dteanga do Home Assistant
nuair is ceann díobh seo í: English, Suomi, Svenska, Norsk bokmål, Español,
Nederlands, Gaeilge. Taispeánann aon teanga eile Béarla.

Ar aimsigh tú botún in aistriúchán, nó an bhfuil teanga eile de dhíth ort?
Inis dúinn ag <https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues>,
nó [aistrigh é le cabhair uainn](#cuir-leis-tú-féin-é-le-cabhair-uainn).

---

## Creidiúintí agus ceadúnais

Léitear gach iarnród le linn rite, ag do Home Assistant, óna fhoinse
fhoilsithe féin; níl aon rud ó fhoinse bheo sa stór seo. Luann gach traein a
foinse ina tréith `attribution`. Ceanglaíonn téarmaí gach iarnróid tú, mar an
duine a fhaigheann a shonraí.

* **Metra** (Stáit Aontaithe Mheiriceá): GTFS-Realtime, faoi
  [chomhaontú ceadúnais Metra](https://metra.com/gtfs-realtime-api-key-request-license-agreement),
  a nglacann tú leis nuair a iarrann tú eochair.
* **South Shore Line** (NICTD, Stáit Aontaithe Mheiriceá): foinse agus clár ama
  poiblí a fhoilsíonn ETA SPOT do NICTD, gan eochair agus gan chomhaontú
  ceadúnais.
* **Translink** (Rialtas Queensland, An Astráil): sonraí faoi CC BY 4.0
  ([sonraí oscailte](https://translink.com.au/about-translink/open-data)).
* **Fintraffic / digitraffic.fi** (An Fhionlainn): sonraí faoi CC BY 4.0.
  **HSL** (An Fhionlainn): criosanna táillí, CC BY 4.0.
* **Renfe** (An Spáinn): sonraí faoi CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)), athraithe.
* **Entur** (An Iorua): sonraí faoi cheadúnas na hIorua do Shonraí Oscailte
  Rialtais ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)), dáilte ag Entur.
* **Trafikverket** (An tSualainn): sonraí faoi [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Iarnród Éireann** (Éire): sonraí beo; ní fhoilsíonn Iarnród Éireann aon
  téarmaí. Clár ama ón
  [Údarás Náisiúnta Iompair](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Éire), CC BY 4.0.
* **NS** (An Ísiltír): sonraí feithiclí, le d'eochair féin, ó
  [thairseach API NS](https://apiportal.ns.nl/). Clár ama agus moilleanna ó
  [OVapi](https://gtfs.ovapi.nl), CC0.
* **Transport for NSW** (An Astráil): sonraí faoi CC BY 4.0
  ([ceadúnas sonraí](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (An Astráil): sonraí faoi CC BY 4.0
  ([sonraí oscailte](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Adelaide Metro**, Department for Infrastructure and Transport, South
  Australia: sonraí faoi CC BY 4.0 ([eolas d'fhorbróirí](https://www.adelaidemetro.com.au/developer-info)).
* **Public Transport Authority Iarthar na hAstráile**: sonraí an chláir ama ar
  fáil saor in aisce ó www.transperth.wa.gov.au
  ([rochtain ar shonraí spásúla](https://www.transperth.wa.gov.au/About/Spatial-Data-Access)).
* **Comhaid riain in `rail/`**: an North American Rail Network (Roinn Iompair
  Stáit Aontaithe Mheiriceá), san fhearann poiblí; líonra rianta Fintraffic,
  CC BY 4.0, athraithe; línte Flytoget ó shonraí Entur, NLOD 2.0, athraithe;
  línte na Sualainne rianaithe ar OpenStreetMap, (c) rannpháirtithe
  OpenStreetMap, ODbL 1.0; daonra na gcathracha ó Statistics Sweden, CC0. Tá
  an méid a athraíodh liostaithe in [ATTRIBUTION.md](ATTRIBUTION.md).
* **An cárta léarscáile** is ea [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, cóip de [ha-map-card](https://github.com/nathan-gs/ha-map-card) le
  nathan-gs, MIT. Tá a thíleanna léarscáile agus a gcreidiúintí ina README.

Ní dhearna aon cheann de na heagraíochtaí seo an comhtháthú seo agus níor
fhormhuinigh siad é.

**Cód**: MIT, in [LICENSE](LICENSE).

**D'fhorbróirí:** is cuibheoir amháin gach iarnród in
`custom_components/live_track_commuter_rail/operators/`; atógtar na comhaid
riain in `rail/` leis na scripteanna in `tools/` (`build_rail.py`,
`build_tracks.py`, `build_flytoget_lines.py`, `sweden_lines.py`). Ritear na
tástálacha le `python -m unittest discover -s tests`.

---

## Eochairfhocail

Home Assistant traenacha · traenacha beo · traenacha ar an léarscáil ·
Iarnród Éireann · Irish Rail live trains · traein chomaitéara · Metra · South Shore Line · Renfe Cercanías · Rodalies ·
lähijunat · HSL · VR · pendeltåg · Vy · Flytoget · NS · Sprinter · Queensland
Rail · Translink · NSW TrainLink · V/Line · Adelaide Metro · traenacha Perth ·
GTFS-Realtime · geo_location · cárta léarscáile · Lovelace · HACS · Margadh ·
Live Track · LiveTrack · StrausbergAutomationWorks

---

**Aitheantas.** Aithníonn StrausbergAutomationWorks pobail dhúchasacha gach tíre
agus gach uisce ar an léarscáil seo, ar fud an domhain, agus tugann sé ómós dá
Seanóirí, san am a caitheadh agus inniu.
