# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · **Español** · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md) · [Todos los idiomas](#idiomas)

**Trenes de cercanías para Home Assistant, en un solo mapa.** Live Track
Commuter Rail pone en tu mapa de Home Assistant cada tren de las redes de
cercanías que elijas, en vivo: dónde está, su número de tren o su línea, si va
con retraso y su próxima parada. Cada red se añade por separado, a partir de
sus propios datos abiertos.

> **Live Track Commuter Rail es un módulo de Live Track**, una familia de
> integraciones de Home Assistant que dibujan todo lo que se mueve, y el tiempo
> por el que se mueve, en un mapa compartido: aviones, barcos, trenes y tiempo.
> Instálalo solo, o junto a los demás módulos
> ([lista más abajo](#parte-de-live-track-los-demás-módulos)).

> **En crecimiento, y abierto a ideas.** Live Track Commuter Rail cubre hoy 31
> redes en 8 países de 3 continentes, y vamos añadiendo más redes y países.
> ¿Falta la tuya? [Sugiérela](#ayúdanos-a-hacerlo-crecer), o añádela tú mismo:
> te ayudaremos a hacerlo.

**Estado: 0.1.4, publicado.** Se añade al Marketplace por su enlace
([más abajo](#instalarlo-paso-a-paso)); todavía no está en el catálogo del
Marketplace.

Obra original de StrausbergAutomationWorks. Sin relación con Metra, el
Northern Indiana Commuter Transportation District (NICTD), ETA SPOT, Renfe,
Fintraffic, HSL, VR, Entur, Vy, Go-Ahead Norge, Flytoget, Trafikverket, SL,
Västtågen, Arlanda Express, Irish Rail, la National Transport Authority
(Irlanda), NS, OVapi, Translink, Queensland Rail, Transport for NSW,
Transport Victoria, V/Line, Adelaide Metro, la Public Transport Authority de
Australia Occidental ni ninguna otra red, y sin su respaldo.

---

## Contenido

1. [Todo lo que hace](#todo-lo-que-hace)
2. [Dónde funciona](#dónde-funciona)
3. [Parte de Live Track: los demás módulos](#parte-de-live-track-los-demás-módulos)
4. [Antes de empezar](#antes-de-empezar)
5. [Instalarlo, paso a paso](#instalarlo-paso-a-paso)
6. [Configurarlo, paso a paso](#configurarlo-paso-a-paso)
7. [Claves gratuitas que activan más, paso a paso](#claves-gratuitas-que-activan-más-paso-a-paso)
8. [Poner el mapa en un panel de control](#poner-el-mapa-en-un-panel-de-control)
9. [Usarlo en automatizaciones](#usarlo-en-automatizaciones)
10. [Todo lo del mapa, en detalle](#todo-lo-del-mapa-en-detalle)
11. [Todas las entidades que crea](#todas-las-entidades-que-crea)
12. [Qué envía y qué descarga](#qué-envía-y-qué-descarga)
13. [Ayúdanos a hacerlo crecer](#ayúdanos-a-hacerlo-crecer)
14. [Idiomas](#idiomas)
15. [Créditos y licencias](#créditos-y-licencias)
16. [Palabras clave](#palabras-clave)

---

## Todo lo que hace

### En el mapa, sin nada que configurar

Añades una **red**: eliges un país o una región, y luego una de sus redes de
cercanías. Todo lo de abajo aparece entonces para esa red. Añade la
integración otra vez por cada red que quieras.

| Qué | Dónde | De dónde |
|---|---|---|
| **Trenes en servicio**: un marcador por tren, con su número de tren o su línea, en los colores de la propia red, girado en el sentido en que circula | todas las redes | el canal en vivo de cada red |
| **Retraso**: un tren aparece con retraso o con mucho retraso según la propia regla de la red, donde la red publica una | todas las redes que informan de retrasos | el canal y el horario de cada red |
| **Próxima parada y su hora**: la estación donde el tren para a continuación, y cuándo se le espera | todas las redes cuyo canal u horario lo indica | el canal y el horario de cada red |
| **Trenes que siguen la vía**: entre dos posiciones el tren se desliza por la línea, no en línea recta | Finlandia, Países Bajos, Suecia | archivos de vía incluidos en la integración o descargados por ella |
| **Material fuera de servicio**: trenes vacíos que van entre cocheras, mostrados mientras se mueven | redes cuyos canales los indican | el canal de cada red |
| **Dos recuentos por red**: trenes en servicio y vehículos fuera de servicio | todas las redes | el mismo canal |

### Activado con tu propia clave o cuenta gratuita

| Clave o cuenta gratuita | Qué añade |
|---|---|
| Clave de **Metra** | los trenes de Metra (área de Chicago, Estados Unidos) |
| Clave de **Trafikverket** | SL Pendeltåg, el pendeltåg de Västtågen y Arlanda Express (Suecia) |
| Clave del **portal de API de NS** | los trenes NS Sprinter (Países Bajos) |
| Clave de **Transport for NSW Open Data** | los trenes NSW TrainLink Intercity (Nueva Gales del Sur, Australia) |
| Clave de **Transport Victoria Open Data** | los trenes de cercanías de V/Line (Victoria, Australia) |

Cada una se consigue en pocos minutos: [paso a paso más abajo](#claves-gratuitas-que-activan-más-paso-a-paso).
Las otras 26 redes no necesitan clave.

---

## Dónde funciona

| Región | Qué obtienes | De dónde | Necesita |
|---|---|---|---|
| **Australia**: Nueva Gales del Sur | NSW TrainLink Intercity: las líneas Blue Mountains, Central Coast and Newcastle, Hunter, South Coast y Southern Highlands desde Sídney | Transport for NSW | una clave gratuita |
| **Australia**: Queensland | Queensland Rail Citytrain, sureste de Queensland (Brisbane) | Translink | nada |
| **Australia**: Australia Meridional | los trenes de Adelaide Metro: las líneas Belair, Gawler, Outer Harbor y Seaford | Adelaide Metro | nada |
| **Australia**: Victoria | los trenes de cercanías de V/Line: las líneas Geelong, Ballarat, Bendigo, Seymour y Traralgon | Transport Victoria | una clave gratuita |
| **Australia**: Australia Occidental | los trenes de Perth, las nueve líneas, solo a partir del horario ([por qué](#trenes-de-perth-australia-occidental-australia)) | Public Transport Authority de Australia Occidental | nada |
| **Europa**: España | Renfe Cercanías y Rodalies de Catalunya, 15 núcleos: Madrid, Barcelona, Asturias, Sevilla, Cádiz, Málaga, Valencia, Murcia y Alicante, Cartagena, Ferrol, León, Bilbao, San Sebastián, Cantabria, Zaragoza | Renfe | nada |
| **Europa**: Finlandia | los trenes de cercanías de VR y HSL en torno a Helsinki | Fintraffic Digitraffic | nada |
| **Europa**: Irlanda | los trenes de cercanías de Irish Rail en torno a Dublín y Cork | Irish Rail, National Transport Authority | nada |
| **Europa**: Noruega | las líneas L1, L2 y L4 de Vy (área de Oslo, Bergen), la L5 de Go-Ahead Norge (Stavanger), Flytoget (aeropuerto de Oslo) | Entur | nada |
| **Europa**: Países Bajos | los trenes NS Sprinter, todo el país | NS, OVapi | una clave gratuita |
| **Europa**: Suecia | SL Pendeltåg (Estocolmo), el pendeltåg de Västtågen (Gotemburgo), Arlanda Express | Trafikverket | una clave gratuita |
| **Norteamérica**: Estados Unidos | Metra (área de Chicago: Illinois, Wisconsin) | Metra | una clave gratuita |
| **Norteamérica**: Estados Unidos | South Shore Line (de Chicago a South Bend: Illinois, Indiana) | NICTD, a través de ETA SPOT | nada |

¿No está en la lista? [Dínoslo](#ayúdanos-a-hacerlo-crecer). Donde alguien
publique los datos abiertamente, estudiaremos añadirlos.

⚠ **Un tren es tan bueno como el canal de su red.** Algunas redes colocan sus
trenes según el horario y no por GPS, otras informan de un tren solo en
señales separadas por unos minutos, y algunos canales se detienen o se
congelan durante un tiempo. Las limitaciones de cada red están en
[Todo lo del mapa, en detalle](#todo-lo-del-mapa-en-detalle).

⚠ **No es la información oficial de la red.** Antes de viajar, consulta la
aplicación o la web de la propia red.

---

## Parte de Live Track: los demás módulos

Live Track es un conjunto de integraciones de Home Assistant, una por cada
tipo de cosa que se mueve, todas dibujadas en la misma tarjeta de mapa. Cada
una funciona sola; juntas forman una sola imagen en vivo. Comparten la tarjeta
de mapa y una biblioteca de Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
así que instalar otra no añade peticiones a una fuente que otra ya lee.

| Módulo | Qué pone en el mapa | Estado |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aviones sobre ti por ADS-B, con rutas e iconos por tipo | publicado |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | buques y barcos por AIS, cerca de ti o en cualquier lugar | publicado |
| **Live Track Commuter Rail** | trenes de cercanías en Norteamérica, Europa y Australia (este módulo) | publicado |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | trenes interurbanos y de larga distancia en Norteamérica, Europa y Australia | publicado |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aviones y buques de inmigración y de las fuerzas federales del orden, a partir de listas públicas | publicado |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | tiempo, tormentas y riesgos naturales | publicado |
| Live Track Stations | paneles de salidas y avisos de "hora de salir" para cada estación | previsto |
| Live Track Satellites | satélites que pasan sobre ti | previsto |
| Live Track Freight Trains | trenes de mercancías y de obras donde los ferrocarriles los publican | previsto |
| Live Track Transit | autobuses urbanos, tranvías, ferris y metro | previsto |
| Live Track Intercity Buses | autocares interurbanos y regionales | previsto |
| Live Track Commuter Buses | autobuses de cercanías | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la tarjeta de mapa compartida en la que dibuja cada módulo | publicada, instalada con cada módulo |

Todo es gratuito y de código abierto. Nada se reserva para patrocinadores.

---

## Antes de empezar

* **Home Assistant** 2026.11 o posterior.
* **El Marketplace** (HACS) en tu Home Assistant, para instalarlo y
  actualizarlo de la forma fácil. Sin él puedes copiar los archivos a mano.
* **Acceso a internet** para Home Assistant: cada tren viene del canal público
  de su propia red.
* **Opcional: auto-entities** del Marketplace, para poner los marcadores en el
  mapa (ver [Poner el mapa en un panel de control](#poner-el-mapa-en-un-panel-de-control)).
* Nada que pagar. 26 de las 31 redes no necesitan
  cuenta; las otras cinco necesitan una clave propia gratuita
  ([más arriba](#activado-con-tu-propia-clave-o-cuenta-gratuita)).
* Home Assistant instala por sí solo los paquetes de Python que necesita
  (`saw-livetrack`, `gtfs-realtime-bindings` y `tzdata`) la primera vez que
  se carga la integración.

---

## Instalarlo, paso a paso

### Desde el Marketplace (recomendado)

Live Track Commuter Rail todavía no está en el catálogo del Marketplace.
Añádelo por su enlace:

1. En Home Assistant, abre **Configuración → Marketplace** (HACS).
2. Elige **Añadir desde enlace** (o el menú de tres puntos → **Repositorios
   personalizados**).
3. Escribe `StrausbergAutomationWorks/LiveTrackCommuterRail`. Si te pide el
   tipo, elige **Integración**.
4. Busca **Live Track Commuter Rail** en la lista y elige **Descargar** o
   **Instalar**.
5. **Reinicia Home Assistant**: **Configuración → Sistema → Reparaciones**
   ofrece el reinicio, o usa **Configuración → Sistema → Reiniciar**.

Después, el Marketplace te ofrece cada nueva versión como actualización.

### A mano

1. Descarga el código fuente de la
   [última versión](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Copia su carpeta `custom_components/live_track_commuter_rail` dentro de la
   carpeta `custom_components` de la carpeta de configuración de tu Home
   Assistant (crea `custom_components` si no existe).
3. Reinicia Home Assistant.

Para actualizar a mano, sustituye la carpeta por la de la nueva versión y
reinicia.

---

## Configurarlo, paso a paso

1. Abre **Configuración → Dispositivos y servicios**.
2. Elige **Añadir integración** (abajo a la derecha) y busca **Live Track
   Commuter Rail**.
3. **Región**: elige el país, o el país y la región, de la red. Solo aparecen
   los lugares con al menos una red. Elige **Enviar**.
4. **Red**: elige la red. Elige **Enviar**.
5. **Clave de API**: solo para Metra, las tres redes suecas, NS Sprinter, NSW
   TrainLink Intercity y V/Line commuter. Pega tu clave
   ([cómo conseguirla](#claves-gratuitas-que-activan-más-paso-a-paso)) y elige
   **Enviar**. Las demás redes se saltan este paso.

Eso es todo. Los trenes aparecen en un minuto. Donde las próximas paradas de
una red vienen de su horario, se completan en los primeros minutos, cuando el
horario se ha descargado. Para seguir otra red, añade la integración otra vez.
La misma red dos veces se rechaza.

### Cambiar lo que muestra: las opciones

Abre **Configuración → Dispositivos y servicios → Live Track Commuter Rail →
Configurar** (la rueda dentada) en la red que quieras cambiar. Cada opción,
en palabras sencillas:

| Opción | Qué hace | Por defecto |
|---|---|---|
| **Intervalo de consulta** | cada cuánto se lee el canal de la red, de 15 a 600 segundos. La mayoría de los canales se actualizan cada 30 segundos más o menos, así que un intervalo más corto rara vez muestra más | 30 segundos |
| **Mostrar material estacionado** | desactivado: el material fuera de servicio aparece solo mientras se mueve y desaparece del mapa tras 10 minutos parado. Activado: se muestran todos los vehículos del canal, incluidos los trenes estacionados | desactivado |

---

## Claves gratuitas que activan más, paso a paso

Cinco redes piden a cada usuario su propia clave. Todas estas claves son
gratuitas, y cada persona que instala Live Track Commuter Rail consigue la
suya. Pegas la clave cuando el diálogo de configuración te la pide
([paso 5 más arriba](#configurarlo-paso-a-paso)). Solo se pide la clave: ni
contraseña ni secreto. La clave se guarda en Home Assistant con la
integración y nunca se escribe en el registro. Si la red sigue rechazándola,
Home Assistant te pide una nueva.

### Metra (área de Chicago, Estados Unidos)

1. Abre <https://metra.com/developers> y baja hasta **GTFS Realtime API Key
   Request Form**.
2. Rellena **First Name** (nombre), **Last Name** (apellido), **Email
   Address** (correo, se pide dos veces) y **Purpose of Use** (uso previsto,
   por ejemplo: Home Assistant).
3. Marca **I have read and agree to the License Agreement.** (he leído y
   acepto el acuerdo de licencia, que está en
   <https://metra.com/gtfs-realtime-api-key-request-license-agreement>) y
   elige **Submit**.
4. Pega la clave que recibas de Metra en **Clave de API** cuando añadas Metra.

### Trafikverket (Suecia: SL Pendeltåg, Västtågen, Arlanda Express)

1. Abre <https://data.trafikverket.se/oauth2/Account/register>.
2. Rellena **Email**, **Displayname** (nombre visible), **Password**
   (contraseña) y **Confirm password**, marca **Accept license and
   Agreement** y elige **Register**.
3. Abre <https://data.trafikverket.se/get-started> y elige **Create key**,
   bajo **Create a key**. Inicia sesión con la cuenta que creaste y crea la
   clave.
4. Pégala en **Clave de API** cuando añadas una red sueca. Una sola clave
   sirve para las tres.

### NS (Países Bajos)

1. Abre <https://apiportal.ns.nl/>, elige **Inloggen** (iniciar sesión) y
   luego **Externe bezoeker** (visitante externo).
2. Rellena el formulario y envíalo. Un correo confirma el registro. Las API
   pueden tardar hasta 5 minutos en aparecer en el portal.
3. Abre la página de la **Virtual Train API** (las posiciones de los trenes
   de NS). En **Related Products**, abre su producto, ponle un nombre a tu
   suscripción y elige **Subscribe**.
4. Cuando NS apruebe la suscripción, tu clave está en tu página de perfil.
   Pégala en **Clave de API** cuando añadas NS Sprinter.

### Transport for NSW (Nueva Gales del Sur, Australia)

1. Abre <https://opendata.transport.nsw.gov.au/>, elige **Register**, crea
   una cuenta e inicia sesión.
2. Elige el icono de tu perfil y luego **API Tokens**.
3. Escribe un nombre para la clave y elige **CREATE API TOKEN**. Copia la
   clave en ese momento: el sitio la muestra una sola vez.
4. Pégala en **Clave de API** cuando añadas NSW TrainLink Intercity. Pega solo
   la clave: Live Track Commuter Rail añade la palabra `apikey` por sí solo.

### Transport Victoria (Victoria, Australia)

1. Abre <https://opendata.transport.vic.gov.au/>, elige **Login** y luego
   **Sign up**.
2. Escribe tus datos y elige **Create Account**. Escribe el código del correo
   que recibes y elige **Confirm**.
3. El portal pide una aplicación de autenticación en tu teléfono: escanea con
   ella el código QR, escribe el código de la aplicación y elige **Confirm**.
   Después inicia sesión con tu correo, tu contraseña y el código de la
   aplicación.
4. Elige **My Account** → **Profile** → **API tokens**. Tu clave ya está ahí.
   Pégala en **Clave de API** cuando añadas V/Line commuter.

---

## Poner el mapa en un panel de control

El mapa es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la tarjeta en la que dibujan todos los módulos de Live Track. **Se instala con
Live Track Commuter Rail**: nada que descargar, nada que copiar, ningún
recurso que añadir.

1. Abre un panel de control, elige el lápiz (**Editar panel de control**) y
   luego **Añadir tarjeta**.
2. Desplázate hasta abajo y elige **Manual**.
3. Pega esto y elige **Guardar**:

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

Los marcadores necesitan [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
del Marketplace. Si tienes otros módulos de Live Track, añade un filtro
`- domain: geo_location` más por cada una de sus fuentes
(`live_track_intercity_rail`, `live_track_aircraft`, etc.).

**En el mapa:**

* Cada tren es un disco en los colores de su línea o de su red, con su número
  de tren o su línea. En la mayoría de las redes los colores cambian con el
  sentido: relleno al salir de la ciudad principal, blanco hacia ella.
* Una flecha muestra el sentido en que circula el tren. Un tren parado
  conserva su último sentido.
* **Señala** un tren para ver su red, su número o su línea, y por dónde
  circula. **Haz clic** en él para ver todos sus detalles, incluidos su
  próxima parada y su retraso.

Si los recursos de tus paneles se definen en YAML
(`lovelace: resource_mode: yaml`), no se puede registrar nada por ti: una
incidencia en **Reparaciones** te da entonces las líneas exactas que hay que
añadir a `configuration.yaml`. Son como estas, con la dirección propia de la
integración en lugar de los marcadores:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_commuter_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Cada módulo de Live Track lleva una copia de la tarjeta y la registra al
arrancar Home Assistant. Entre todos mantienen exactamente una fila en
**Configuración → Paneles de control → Recursos**: la versión más nueva de la
tarjeta que lleve cualquiera de ellos, nunca una más antigua. Una tarjeta que
hayas instalado tú desde el Marketplace no se toca. Cuando quitas la última
red de este módulo, la fila pasa a otro módulo de Live Track, o se elimina si
no queda ninguno. Si se eliminan los archivos de la integración mientras sus
redes siguen configuradas, y no hay ningún otro módulo de Live Track
instalado, elimina tú la fila en **Configuración → Paneles de control →
Recursos**.

**Para instalar la tarjeta a mano**, sigue los pasos del
[README de la tarjeta](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
Una fila que hayas creado tú para una copia en `/local/` solo se apunta a la
copia de este módulo cuando esa copia es una versión más nueva.

Cualquier otra tarjeta de mapa que muestre entidades `geo_location` muestra
también los trenes, como marcadores simples.

---

## Usarlo en automatizaciones

Todo es una entidad normal de Home Assistant, así que el editor de
automatizaciones funciona con ella, sin código.

**Una notificación en el teléfono cuando tu red muestra casi ningún tren**
(el canal puede haberse detenido, o el servicio puede estar alterado):

1. **Configuración → Automatizaciones y escenas → Crear automatización → Crear
   nueva automatización**.
2. **Cuando**: **Añadir disparador** → **Entidad** → **El estado numérico
   cruzó el umbral**. Elige la entidad **Trains in service** de la red, y
   **Por debajo de** `3`.
3. **Entonces hacer**: **Añadir acción**, busca la acción de notificación de
   tu teléfono (lleva el nombre de tu teléfono) y escribe un mensaje, por
   ejemplo:

   ```text
   Casi ningún tren en el mapa: consulta la aplicación de la red
   ```

4. **Guardar**.

**Otras ideas:** una luz que se enciende cuando un tren está a menos de 1 km
(0,6 millas) de tu casa en Madrid (España), a partir de la distancia de los
marcadores; un recuento en el panel de los trenes de Metra en servicio en la
hora punta de la mañana (Chicago, Estados Unidos); un mensaje cuando circula
el primer tren del día en Brisbane (Australia), cuando **Trains in service**
sube por encima de 0.

---

## Todo lo del mapa, en detalle

### Trenes y material fuera de servicio

Cada tren es un marcador. Su estado es su distancia a tu casa, en kilómetros.
El marcador aparece cuando el canal de la red informa del tren y se elimina
cuando el tren sale del canal (al cabo de 3 minutos, para que un corte breve
del canal no lo elimine).

* **Un tren en servicio** lleva su número de tren o su línea, tal como los
  numera la red (cada red, más abajo, dice cuál).
* **El material fuera de servicio** lleva `NIS` y su número de unidad, para
  que un número de unidad nunca se confunda con un número de tren. Se muestra
  solo mientras se mueve y desaparece del mapa tras 10 minutos parado. Activa
  **Mostrar material estacionado** para ver todos los vehículos del canal.
* **Entre dos posiciones** la tarjeta de mapa mueve el marcador de una
  posición real a la siguiente. No se inventa nada más allá de la última
  posición real.
* **Una posición que no está en una vía se rechaza.** Un tren que aparece
  fuera de las vías se muestra en su última posición que sí estaba en ellas,
  durante 10 minutos como máximo, y después se oculta hasta que vuelve. Un
  tren que aparece por primera vez fuera de las vías no se muestra.
* **Con retraso y con mucho retraso**: donde la red publica su propia regla
  para un tren con retraso, la integración la usa, y lo dice más abajo.

En cada tren: `marker_label`, `observed_at` (cuándo era cierta su posición),
`course_deg` (mientras se mueve), `next_stop` y `arrival_estimated_at`
(cuando se conocen), `delay_min`, `stalled`, `attribution` y, entre dos
posiciones, `previous_latitude`, `previous_longitude`, `previous_observed_at`
y `segment_duration_s`. Una posición que la integración ha estimado, en lugar
de una que haya dado la red, lleva `position_source: estimated`.

### NSW TrainLink Intercity (Nueva Gales del Sur, Australia)

De los canales de NSW TrainLink y de Sydney Trains de Transport for NSW, con
tu propia clave. Un servicio que está en los dos canales es un solo marcador.
La etiqueta es el código de la línea (BMT, CCN, HUN, SCO, SHL); el servicio y
sus extremos están en el recuadro emergente ("Train KN56 · Bomaderry–Kiama").
El color de la línea según el horario, relleno al salir de Sydney Central y
al revés hacia allí. Los trenes vacíos son `NIS` y su servicio, en gris. La
próxima parada es una estación, nunca un andén. ⚠ Una posición de más de 10
minutos no se dibuja, y un tren se elimina cuando termina su servicio. Con
retraso desde 6 minutos (la medida Intercity de Transport for NSW), con mucho
retraso desde 12.

### Queensland Rail Citytrain (Queensland, Australia)

Del canal abierto de Translink. ⚠ Las posiciones son puntos fijos en la vía,
no GPS, sin velocidad ni sentido; la flecha sigue la ruta del tren en el
horario. Una posición de más de 5 minutos se rechaza, porque el canal conserva
un tren cuya posición se congeló hasta el final del día de servicio. La
etiqueta es el número T de la línea en los colores de línea de Translink, al
revés para los trenes hacia el sur, y una estrella para los servicios
especiales sin número T. Con retraso desde 4 minutos, 6 en las líneas Gold
Coast, Rosewood y Sunshine Coast (la propia regla de Queensland Rail).

### Adelaide Metro (Australia Meridional, Australia)

Del canal abierto de Adelaide Metro, que también lleva sus tranvías y
autobuses (no se dibujan aquí). Las posiciones son GPS, con el sentido del
propio tren. Adelaida no publica número de tren, así que la etiqueta son las
tres primeras letras del código de ruta que usa Adelaide Metro (SEA, FLN, GAW,
BEL, OUT, etc.); el recuadro emergente da el código completo ("SEAFRD to
Seaford · railcar 4006"). Los colores son los del mapa de la red: Belair
verde, Seaford y Flinders naranja, Gawler rojo, Outer Harbor, Port Dock y
Grange azul; relleno al salir del centro, blanco hacia Adelaide Railway
Station. Una posición de más de 5 minutos, o a más de 1 km de cualquier ruta
ferroviaria de Adelaida, se rechaza. Con retraso desde 5 minutos (la propia
regla de Adelaide Metro), con mucho retraso desde 10.

### V/Line commuter (Victoria, Australia)

Del canal de V/Line de Transport Victoria, con tu propia clave. La etiqueta
es el código de la línea (GEL, BAT, BGO, SER, TRN); el número de tren y la
línea están en el recuadro emergente ("Train 8037 · Bendigo - Melbourne via
Gisborne"). Todas las líneas son del morado de V/Line: relleno al salir de
Melbourne, blanco hacia Southern Cross. ⚠ Las posiciones de V/Line siguen más
el horario que el tren: un viaje sale del canal un minuto después de su
llegada prevista, esté donde esté el tren, y las posiciones se congelan hacia
medianoche. Por eso un tren conserva su última posición durante 10 minutos
como máximo y luego sale del mapa, y un tren con retraso puede desaparecer
antes de su última estación. Con retraso desde 6 minutos (la regla de V/Line
para los servicios de cercanías), con mucho retraso desde 12.

### Trenes de Perth (Australia Occidental, Australia)

⚠ **Perth no publica posiciones en vivo.** Cada tren se dibuja a partir del
horario de la Public Transport Authority de Australia Occidental: colocado a
lo largo de su ruta según sus horas previstas, marcado como estimación, sin
retraso. El horario se comprueba una vez al día. La etiqueta son las tres
primeras letras de la línea (MAN, YAN, ARM, FRE, MID, ELL, AIR, THO; STA para
un Stadium Special); el recuadro emergente dice "Mandurah Line · Perth
Underground–Mandurah". Los colores son los del mapa de la red: relleno al
salir de Perth, blanco hacia allí.

### Renfe Cercanías y Rodalies (España)

Del canal abierto de Renfe, cada uno de los 15 núcleos en su propia entrada.
La etiqueta es la línea (C5, R2N) en el propio color de la línea según el
horario de Renfe. El número de tren y el nombre de la línea están en el
recuadro emergente. ⚠ Renfe coloca sus trenes sobre su ruta y no por GPS, así
que se paran y luego saltan. Un tren solo avanza por su propia línea: una
posición fuera de ella, hacia atrás o imposiblemente rápida se rechaza, y la
última buena se conserva durante 10 minutos como máximo. Un tren se considera
detenido solo tras 6 minutos en el mismo sitio. Renfe no publica ninguna regla
para un tren con retraso, así que se aplican los umbrales propios de la
tarjeta de mapa.

### Trenes de cercanías de VR y HSL (Finlandia)

De Digitraffic de Fintraffic. Un tren es un servicio: su número de tren y el
día en que salió. La etiqueta es la letra de la línea, coloreada como la
colorean los mapas y los carteles de estación de HSL: morado de HSL mientras
la próxima parada está en las zonas tarifarias A a E de HSL, verde de VR
fuera de ellas. Un tren que se aleja de Helsinki es un disco relleno; uno que
va hacia allí es blanco. Un tren se muestra desde su primera estación hasta su
última parada, y luego se elimina. Los servicios de la línea V que no llevan
viajeros se muestran como `NIS` mientras se mueven. Entre dos posiciones un
tren se desliza por las vías. Las líneas I y P no dan posición en el túnel de
Ring Rail del aeropuerto de Helsinki, así que allí la integración mueve el
tren por las vías según su horario hasta que vuelve una posición real. Con
retraso desde 4 minutos (la regla de VR), con mucho retraso desde 8. Una
posición de más de 10 minutos se rechaza.

### Irish Rail (Irlanda)

Del servicio en vivo de Irish Rail, con el horario de la National Transport
Authority para las rutas y estaciones. ⚠ Irish Rail informa de un tren solo
cuando pasa por señales separadas por unos minutos, así que cada tren se
dibuja a partir de su horario y su último retraso, desplazado por su ruta; los
trenes de Cork, que Irish Rail no sigue, salen solo del horario. La etiqueta
es el número de tren sin su letra (P508 muestra 508). El color es el de la
línea en el mapa de la red de Transport for Ireland, al revés hacia Dublín o
Cork. Con retraso desde 5 minutos (la propia regla de Irish Rail), con mucho
retraso desde 10.

### Vy, Go-Ahead Norge y Flytoget (Noruega)

De Entur, cada red en su propia entrada. La etiqueta es el código de la línea
(L1, L2, L4, L5, FLY1, FLY2); el número de tren y el nombre de la línea están
en el recuadro emergente. Una línea L lleva su color del horario, relleno al
salir de Oslo S (Bergen en la L4, Stavanger en la L5) y al revés hacia allí.
Flytoget es gris con un anillo naranja hacia el aeropuerto de Oslo, y naranja
con un anillo gris al salir de él. Entur no publica velocidad ni sentido, así
que la flecha sigue la línea del tren. En los túneles largos de Oslo, un tren
cuyas posiciones se interrumpen se desplaza por su línea hasta que vuelven.
Con retraso desde 4 minutos, con mucho retraso desde 8.

### NS Sprinter (Países Bajos)

De los datos de vehículos de NS, con tu propia clave. La etiqueta es el número
de tren; el recuadro emergente dice "Sprinter 6632 · Dordrecht–Arnhem
Centraal". Amarillo de NS con un anillo azul de NS. Es el único canal de aquí
que da la velocidad y el sentido del propio tren, y los dos se transmiten
(`speed_kmh`, `course_deg`). La próxima parada y el retraso vienen del horario
de OVapi. La vía es la SpoorKaart de NS, descargada una vez al día; un tren se
desliza por ella entre dos posiciones, y una posición a más de 1 km de ella se
rechaza. Con retraso desde 3 minutos (la propia definición de NS), con mucho
retraso desde 10.

### SL Pendeltåg, Västtågen y Arlanda Express (Suecia)

De Trafikverket, con tu propia clave gratuita (una clave para las tres). La
etiqueta es el número de tren; la marca, el número y las estaciones extremas
están en el recuadro emergente. SL Pendeltåg es rosa, Västtågen azul claro,
Arlanda Express amarillo; cada uno invierte sus colores hacia Stockholm C
(Stockholm City para el pendeltåg) o, en un viaje que no para en ninguna de
las dos, hacia su ciudad extrema más grande. Entre dos posiciones un tren se
desliza por la línea de su viaje, y una posición a más de 1 km de ella se
rechaza. Con retraso desde 3 minutos en SL Pendeltåg (la regla de Region
Stockholm), con mucho retraso desde 6; con retraso desde 6 y con mucho
retraso desde 12 en las otras dos (la regla de Trafikverket).

### Metra y la South Shore Line (Estados Unidos)

Metra desde su propio canal, con tu propia clave; la South Shore Line desde el
canal que ETA SPOT publica para NICTD, sin clave. La etiqueta es el número de
tren. Metra da el nombre de la próxima parada y su hora. El canal de la South
Shore Line solo da un número de parada y un retraso, así que su horario aporta
la estación y la hora. Una posición a más de 300 m de cualquier vía de la
North American Rail Network (Estados Unidos), o de la propia ruta de la red,
se rechaza. ⚠ Algunos días el canal de Metra ha asignado a un viaje pocos de
sus trenes; los demás aparecen entonces como `NIS` o no aparecen, y el mapa
parece un día tranquilo. El recuento **Trains in service** muestra esos días
después.

---

## Todas las entidades que crea

Por cada red:

| Entidad | Qué es |
|---|---|
| `sensor.<red>_trains_in_service` | **Trains in service**: cuántos trenes en servicio indica ahora el canal de la red. Para Metra: `sensor.metra_chicago_area_trains_in_service` |
| `sensor.<red>_vehicles_not_in_service` | **Vehicles not in service**: cuántos vehículos indica el canal que no están en servicio |
| `geo_location.<red>_unit_…` | uno por tren o vehículo (`geo_location.metra_unit_8426`); aparece y desaparece con el tren. Cada uno lleva `source: live_track_commuter_rail`, y su estado es su distancia a tu casa en kilómetros |

Los nombres de las entidades están en inglés, sea cual sea el idioma de tu
Home Assistant.

Cada red tiene una flota conocida. El ID de entidad de un marcador viene de la
red y del número del vehículo en el canal, nunca de su etiqueta, así que el
mismo vehículo recibe el mismo ID de entidad cada vez que aparece:
`geo_location.metra_unit_8426` es siempre el coche 8426 de Metra. El marcador
se elimina cuando el vehículo sale del canal, o tras 10 minutos estacionado
mientras **Mostrar material estacionado** está desactivado. Los marcadores no
tienen ID único, como ningún marcador de mapa de Live Track, así que no se
pueden renombrar, ocultar ni asignar a un área desde la interfaz. Los dos
sensores tienen ID único y se pueden renombrar.

Los atributos que cambian en cada consulta, las posiciones y horas de los
marcadores, se guardan en el historial de Home Assistant, como los de
cualquier entidad. Los dos sensores no tienen atributos, así que guardarlos
cuesta poco, y son el registro de cuántos trenes circularon un día. Para
dejar los marcadores fuera del historial, añade esto a `configuration.yaml` y
reinicia:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_unit_*
```

Si tu `configuration.yaml` ya tiene una sección `recorder:`, añade solo el
patrón `geo_location.*_unit_*`, bajo `exclude:` y `entity_globs:`. El patrón
coincide solo con los marcadores de trenes de este módulo. Una tarjeta de
mapa configurada para dibujar el historial ya no tendrá rastro que dibujar.

---

## Qué envía y qué descarga

**Sobre tu ubicación.** Nada. La posición de tu casa se usa solo dentro de tu
Home Assistant, para dar la distancia de cada tren. Tu clave, cuando una red
la necesita, se envía solo a esa red. No se envía nada más sobre ti a ningún
sitio. Cada servicio ve tu dirección de internet, como cualquier web.

**Cuánto.** Cada canal en vivo se lee en cada consulta, cada 30 segundos por
defecto (**Intervalo de consulta**, de 15 a 600 segundos), o con menos
frecuencia donde la tabla lo indica. Donde varios módulos de Live Track leen
el mismo canal, un único cliente compartido lo lee una vez para todos. Medido
el 19 de noviembre de 2026, de 02:20 a 02:40 UTC:

| Red | Canal en vivo, una lectura | Horario |
|---|---|---|
| Adelaide Metro (Australia) | 298 KB | 20 MB, cuando Adelaide Metro publica una versión nueva |
| Trenes de Perth (Australia) | ninguno: Perth no publica canal en vivo | 28 MB, cuando cambia, comprobado a diario |
| NSW TrainLink Intercity (Australia) | 402 KB de cuatro canales, como mucho una vez cada 55 segundos | 51 MB (dos horarios), cuando cambia, comprobado a diario |
| Queensland Rail Citytrain (Australia) | 141 KB | 42 MB, cada día |
| V/Line commuter (Australia) | 14 KB | 59 MB, cuando cambia, comprobado a diario |
| Renfe Cercanías y Rodalies (España) | un canal para los 15 núcleos: 26 bytes, de noche sin trenes en circulación | 16 MB, cada día |
| Trenes de cercanías de VR y HSL (Finlandia) | 1,1 KB comprimidos para las posiciones, más los cambios en los trenes del día una vez por minuto | ninguno como archivo: los trenes del día llegan con los datos en vivo |
| Irish Rail (Irlanda) | 0,2 KB, como mucho una vez cada 55 segundos | 6,6 MB, cuando cambia, comprobado a diario; la lista de estaciones, 18 KB, una vez por semana |
| Vy, Go-Ahead Norge, Flytoget (Noruega) | Vy 497 KB, Go-Ahead Norge 7 KB, Flytoget 233 KB | Vy 67 MB, Go-Ahead Norge 20 MB, Flytoget 0,6 MB, cuando cambia, comprobado a diario |
| NS Sprinter (Países Bajos) | 1,2 KB; retrasos de OVapi, 1,6 MB, cada 5 minutos y solo cuando cambian | el horario de OVapi, 274 MB, como mucho una vez por semana y solo cuando cambia; el mapa de vías de NS, 1,3 MB, cada día |
| SL Pendeltåg, Västtågen, Arlanda Express (Suecia) | 3,7 KB la primera vez, luego unos 2 KB de cambios | ninguno; la lista de estaciones, 0,15 MB, cada día |
| Metra (Estados Unidos) | 18 KB | 0,4 MB, cada día |
| South Shore Line (Estados Unidos) | menos de 1 KB | 0,14 MB, cada día |

⚠ Cuando se midió era de día en Australia, de tarde en los Estados Unidos y
de noche en Europa. Un canal en vivo es más pequeño de noche: de día los
canales europeos son más grandes de lo que indica la tabla.

**Tras un error.** Se muestran las últimas posiciones buenas durante dos
lecturas fallidas más; después los trenes se marcan como no disponibles hasta
que el canal responde. Un horario que no se puede descargar se intenta de
nuevo una hora después, y la copia que tienes sigue en uso. Si la red sigue
rechazando tu clave, Home Assistant te pide una nueva.

**En disco.** Los horarios se guardan en la carpeta `.storage` de Home
Assistant, con nombres que empiezan por `saw_`, compartidos con los demás
módulos de Live Track que leen la misma red: los marcados "cuando cambia" tal
como se descargan, los demás como un extracto más pequeño. Si quitas Live
Track Commuter Rail y ningún otro módulo de Live Track los usa, puedes
borrarlos a mano.

---

## Ayúdanos a hacerlo crecer

Live Track Commuter Rail sigue creciendo. Añadimos redes y países a medida que
los encontramos, y queremos saber qué te gustaría a continuación.

### Sugerir algo

¿Falta tu país o tu red? ¿Hay algo mal, o difícil de entender? Cuéntanoslo de
la forma que te resulte más fácil:

* [**Rellena un formulario corto**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=es.yml)
  en español. Necesitas una cuenta gratuita de GitHub.
* **Escribe un correo** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No hace falta cuenta.

En cualquier caso, ayuda que nos digas:

* qué te gustaría ver, y en qué parte del mundo;
* un enlace a donde se publican los datos, si conoces uno (una página de
  datos abiertos, un canal público, la web de un servicio): no es necesario,
  pero ayuda;
* el idioma de tu Home Assistant, si el problema es la redacción o una
  traducción.

Escribe en inglés o en tu propio idioma, lo que te resulte más fácil.

### Añadirlo tú mismo, con nuestra ayuda

Si quieres añadir algo tú mismo, te ayudaremos a hacerlo, desde la primera
pregunta hasta la versión terminada. No necesitas ser desarrollador para
empezar:

* **Una traducción.** Los textos del diálogo de configuración son una lista
  corta de frases en un archivo de texto. Te mostraremos qué archivo y qué
  líneas.
* **Una nueva red.** Dinos dónde se publican los datos. Podemos escribir el
  código juntos, o revisar el tuyo.
* **Probarlo donde vives.** Instálalo, mira tu parte del mapa y dinos qué está
  bien y qué no.
* **Una corrección de este README.** Si un paso no coincidía con lo que
  viste, dinos lo que viste.

[**Cuéntanos qué tienes en mente**](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues/new?template=es.yml)
o escribe a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
y te responderemos con los siguientes pasos.

---

## Idiomas

Este README: [English](README.md), [Suomi](README.fi.md),
[Svenska](README.sv.md), [Norsk bokmål](README.nb.md), **Español**,
[Nederlands](README.nl.md), [Gaeilge](README.ga.md). Cada README traducido
está completo. Ninguno lo ha leído todavía un hablante nativo. Si el
español es tu lengua materna, dinos si este README se lee bien: ver
[Ayúdanos a hacerlo crecer](#ayúdanos-a-hacerlo-crecer).

El diálogo de configuración y las opciones aparecen en el idioma de tu Home
Assistant cuando es uno de estos: English, Suomi, Svenska, Norsk bokmål,
Español, Nederlands, Gaeilge. Cualquier otro idioma muestra el inglés.

¿Has encontrado un error en una traducción, o necesitas otro idioma? Dínoslo
en <https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/issues>,
o [tradúcelo con nuestra ayuda](#añadirlo-tú-mismo-con-nuestra-ayuda).

---

## Créditos y licencias

Cada red se lee en tiempo de ejecución, desde tu Home Assistant, en su propio
canal publicado; nada de un canal en vivo está en este repositorio. Cada tren
cita su fuente en su atributo `attribution`. Las condiciones de cada red te
obligan a ti, como persona que recibe sus datos.

* **Metra** (Estados Unidos): GTFS-Realtime, bajo el
  [acuerdo de licencia de Metra](https://metra.com/gtfs-realtime-api-key-request-license-agreement),
  que aceptas al pedir una clave.
* **South Shore Line** (NICTD, Estados Unidos): canal y horario públicos que
  ETA SPOT publica para NICTD, sin clave y sin acuerdo de licencia.
* **Translink** (Gobierno de Queensland, Australia): datos bajo CC BY 4.0
  ([datos abiertos](https://translink.com.au/about-translink/open-data)).
* **Fintraffic / digitraffic.fi** (Finlandia): datos bajo CC BY 4.0. **HSL**
  (Finlandia): zonas tarifarias, CC BY 4.0.
* **Renfe** (España): datos bajo CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)), modificados.
* **Entur** (Noruega): datos bajo la licencia noruega de datos abiertos del
  Gobierno ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)), distribuidos por
  Entur.
* **Trafikverket** (Suecia): datos bajo [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irlanda): datos en vivo; Irish Rail no publica condiciones.
  Horario de la [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irlanda), CC BY 4.0.
* **NS** (Países Bajos): datos de vehículos, con tu propia clave, del
  [portal de API de NS](https://apiportal.ns.nl/). Horario y retrasos de
  [OVapi](https://gtfs.ovapi.nl), CC0.
* **Transport for NSW** (Australia): datos bajo CC BY 4.0
  ([licencia de datos](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australia): datos bajo CC BY 4.0
  ([datos abiertos](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Adelaide Metro**, Department for Infrastructure and Transport, South
  Australia: datos bajo CC BY 4.0 ([información para desarrolladores](https://www.adelaidemetro.com.au/developer-info)).
* **Public Transport Authority de Australia Occidental**: datos de horarios
  disponibles gratuitamente en www.transperth.wa.gov.au
  ([acceso a datos espaciales](https://www.transperth.wa.gov.au/About/Spatial-Data-Access)).
* **Archivos de vía incluidos en `rail/`**: la North American Rail Network
  (Departamento de Transporte de los Estados Unidos), dominio público; la red
  de vías de Fintraffic, CC BY 4.0, modificada; las líneas de Flytoget a
  partir de datos de Entur, NLOD 2.0, modificadas; las líneas de Suecia
  trazadas sobre OpenStreetMap, (c) colaboradores de OpenStreetMap, ODbL 1.0;
  la población de las ciudades de Statistics Sweden, CC0. Lo que se ha
  cambiado figura en [ATTRIBUTION.md](ATTRIBUTION.md).
* **La tarjeta de mapa** es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, una copia de [ha-map-card](https://github.com/nathan-gs/ha-map-card)
  de nathan-gs, MIT. Sus mosaicos de mapa y sus créditos están en su README.

Ninguna de estas organizaciones ha hecho ni respaldado esta integración.

**Código**: MIT, en [LICENSE](LICENSE).

**Para desarrolladores:** cada red es un adaptador en
`custom_components/live_track_commuter_rail/operators/`; los archivos de vía
de `rail/` se reconstruyen con los scripts de `tools/` (`build_rail.py`,
`build_tracks.py`, `build_flytoget_lines.py`, `sweden_lines.py`). Las pruebas
se ejecutan con `python -m unittest discover -s tests`.

---

## Palabras clave

Home Assistant trenes · seguimiento de trenes en Home Assistant · mapa de
trenes en vivo · cercanías · trenes en tiempo real · Renfe Cercanías ·
Rodalies · Rodalies en temps real · trenes en el mapa · Metra · South Shore
Line · lähijunat · HSL · VR · pendeltåg · Vy · Flytoget · NS · Sprinter ·
Irish Rail · Queensland Rail · Translink · NSW TrainLink · V/Line · Adelaide
Metro · trenes de Perth · GTFS-Realtime · geo_location · tarjeta de mapa ·
Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks
