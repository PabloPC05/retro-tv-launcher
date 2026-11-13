# Tema Windows 98 del launcher del piso

Escritorio verde azulado, fichas como ventanas de Windows 98 (barra de título azul la enfocada y gris las demás),
recuadro de foco punteado, nombre seleccionado en azul marino, barra de tareas con «Inicio» y el reloj en la
bandeja, y los iconos de Mi PC, Entorno de red y Papelera en el fondo. Fuente MS Sans Serif.

Necesita el launcher con `../parche-win98/` aplicado (modo `glass_style: "win98"`, fichas propias en
`banners/<paquete>.png` y `_on.png`, que el proveedor de temas acepta). Sin el parche, el tema solo pone el fondo.

- `w98banners.py`: genera las fichas (logo antiguo si está en `logos-antiguos/`, si no el banner actual).
- `tema.sh <carpeta>`: sube `config.json` y `wallpaper.jpg` y reinicia Inicio.
- `banners.sh`: sube las fichas.

Fuente e iconos de Windows 98: ver `../parche-win98/CREDITOS-win98-assets.txt` (uso privado).

## Funcional, no solo estética (2026-11-12)

- Barra de tareas: se llega bajando desde la última fila; Arriba vuelve a la ficha de la que se vino.
  - **Inicio** abre el menú Inicio: Programas (biblioteca de apps), Panel de control (ajustes de la tele),
    Red e Internet, Ordenar iconos, Configurar el launcher y Reloj de pantalla completa. Back lo cierra.
  - El icono de red de la bandeja abre la red; el reloj de la bandeja solo informa.
- Reloj y fecha grandes arriba, como antes. Botones de wifi y ajustes de arriba, con relieve.
- Sin botones _ □ × en las fichas ni iconos de escritorio pintados: no se podían pulsar.
- Logos antiguos solo cuando son la versión antigua de la misma app (Spotify, YouTube, Netflix, Prime Video
  como Amazon Instant Video, Play Store como Android Market, Crunchyroll y RTVE); las demás llevan el actual.
- `rows_below_dock: 2` y la columna reserva el alto de la barra: tres filas de apps sin hueco arriba.

## Iconos de escritorio arriba a la derecha (2026-11-12)

En lugar de los botones de wifi y ajustes, iconos de Windows 98 (dibujo y nombre debajo) que hacen algo:
Todas las apps (biblioteca), Wi-Fi (red), Panel de control (ajustes de la tele) y Personalizar (ajustes del
launcher). Sin Papelera: no tenía utilidad. Se llega con Arriba
desde la primera fila; el seleccionado se pinta como en Windows (dibujo sombreado y nombre en azul marino).
Disney+, HBO Max y Movistar+ llevan la firma clásica de Disney, el HBO clásico y la M de Movistar de 2004.

Ajustes ya no sale como ficha (está arriba como Panel de control); el explorador USB se llama «Archivos USB».
La barra de tareas tiene 52 dp con márgenes; la píldora moderna de la biblioteca está oculta.

## Resto de pantallas del launcher (2026-11-13)

Hechas por cuatro agentes y unidas en `parche-win98/win98.patch` (un único parche binario contra el original,
`git apply --binary`): «Todas las apps» como ventana de Explorador (`AppLibraryDialog`), Personalizar como cuadro de
propiedades (`Win98Settings`), salvapantallas «Campo de estrellas» con una ventana de reloj que se mueve
(`Win98Saver`/`ClockScene`), y menús emergentes, avisos y diálogos como menús de Windows 98 (`Win98Menus`).
Todo depende de `Win98.on()`. Las apps de terceros y los Ajustes de Android no se pueden tematizar sin root.
