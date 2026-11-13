# Live Track Commuter Rail

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk](README.nb.md) · **Español** · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md)

Trenes de cercanías en tiempo real en el mapa de Home Assistant. Live Track
Commuter Rail es una integración de Home Assistant (custom component, se
instala desde el Marketplace / HACS) que muestra cada tren de las redes de
cercanías que elijas, en tiempo real: dónde está, su número y su línea, si va
con retraso, su próxima parada y cuándo llega a ella. Las posiciones vienen de
los datos abiertos de cada operador. Cada tren es una entidad `geo_location` y se
mueve cuando se actualiza la fuente.

## En España: Renfe Cercanías y Rodalies

**Renfe Cercanías** de Madrid, Asturias, Sevilla, Cádiz, Málaga, Valencia,
Murcia/Alicante, Cartagena, Ferrol, León, Bilbao, San Sebastián, Cantabria y
Zaragoza, y **Rodalies de Catalunya** (Barcelona): quince redes, cada una añadida
por separado. Datos: Renfe ([data.renfe.com](https://data.renfe.com/)),
CC BY 4.0, modificados. No hace falta clave ni cuenta.

* El marcador lleva la línea (C5, R2N) en el color de su ruta según el horario
  de Renfe, en blanco con contorno oscuro, como la dibuja Renfe; una línea
  blanca lleva un fino anillo negro. El número de tren y el nombre de la línea
  aparecen al pasar el cursor.
* Renfe sitúa los trenes sobre la ruta del viaje, no por GPS: se paran y luego
  saltan. La flecha sigue la ruta, y cada tren solo avanza por su propia línea:
  una posición a más de 150 m de ella, más de 100 m hacia atrás o a más de
  200 km/h se descarta y se mantiene la última buena hasta 10 minutos. Una
  posición a más de 1 km de todas las rutas de la red se descarta.
* Renfe no publica una regla de puntualidad, así que no se envían umbrales de
  retraso y se usan los de la tarjeta.

## Todas las redes

Metra y South Shore Line (Chicago), Renfe Cercanías y Rodalies (España),
VR lähijunat (Finlandia), Vy, Go-Ahead Norge y Flytoget (Noruega), SL
Pendeltåg, Västtågen y Arlanda Express (Suecia), NS Sprinter (Países Bajos),
Irish Rail (Irlanda), Queensland Rail Citytrain, NSW TrainLink Intercity, V/Line y Adelaide Metro (Australia). Claves y condiciones: [la tabla del README en
inglés](README.md#supported-railroads).

## Parte de Live Track

Live Track es un sistema de módulos para Home Assistant. Cada módulo sigue un
tipo de cosa que se mueve, y todos dibujan en el mismo mapa. Comparten una
biblioteca de Python ([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
y una tarjeta de mapa ([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)),
así que instalar otro módulo no añade peticiones a una fuente compartida.
Publicados: Live Track Commuter Rail,
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)
y [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT).
En desarrollo: Live Track Intercity Rail, Live Track Ships y Live Track Weather.

## Requisitos

- Home Assistant 2026.11 o posterior.
- Ninguna clave para las redes de Renfe.
- Home Assistant instala los paquetes de Python necesarios la primera vez que
  carga la integración.

## Instalación

### Desde el Marketplace

La integración aún no está en el catálogo del Marketplace. Añádela por enlace:

1. **Settings > Marketplace** y **Add from link**.
2. Escribe `StrausbergAutomationWorks/LiveTrackCommuterRail`. Si pide el tipo,
   elige **Integration**.
3. Instala **Live Track Commuter Rail**.
4. Reinicia Home Assistant. El Marketplace ofrece el reinicio como reparación en
   **Settings > System > Repairs**.

### A mano

1. Descarga el código fuente de la [última
   versión](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail/releases/latest).
2. Copia su carpeta `custom_components/live_track_commuter_rail` en la carpeta
   `custom_components` del directorio de configuración de Home Assistant.
3. Reinicia Home Assistant.

## Configuración

**Settings > Devices & services > Add integration > Live Track Commuter Rail**.
Elige la región y después la red. El diálogo y los nombres de las regiones aparecen en español
cuando Home Assistant está en español. Los nombres de menú de arriba son los
de la interfaz en inglés.

## Datos y licencia

Los trenes se leen mientras la integración funciona, directamente de la fuente
de cada operador; este repositorio no contiene datos de esas fuentes. El atributo
`attribution` de cada tren indica su fuente. Los archivos de vías y líneas que
se incluyen y sus licencias: [ATTRIBUTION.md](ATTRIBUTION.md). Código: MIT.

Esta integración no está patrocinada, afiliada ni operada por ninguno de los
operadores. Todos los detalles: [README en inglés](README.md).

## Palabras clave

Home Assistant trenes en el mapa · Cercanías en tiempo real · Rodalies en temps
real · posición de los trenes · Renfe Cercanías Madrid · Rodalies Barcelona ·
data.renfe.com · GTFS-Realtime · integración HACS
