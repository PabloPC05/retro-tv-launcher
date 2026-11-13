# Tema 8-bit del launcher del piso

Primera de las estéticas que le gustaron a una compañera (ver la nota de memoria). `glass_style: "8bit"`:
fondo pixelado propio (cielo por bandas, montañas, colinas y suelo de ladrillos; `make_wallpaper.py`), fichas como
cajas de diálogo NES con borde blanco de esquinas escalonadas que se vuelve amarillo con un cursor ▶ al enfocar
(`pixbanners.py`), iconos de cada app en pixel-art de 32×32 (generados a partir de Simple Icons, pixelarticons o
a mano; no había versiones pixel-art descargables), barra inferior negra tipo marcador con el botón rojo START y
la hora en amarillo, menú en caja azul con selección amarilla, y letra Press Start 2P (OFL).
Compilar con `bldskin.sh 8bit`. El fondo es PNG aunque se suba como wallpaper.jpg (el launcher lo lee igual).

## Completado (2026-11-13)
- Iconos pixelados también en «Todas las apps» (carpeta `icons/` del tema, 25 apps) y en el menú START.
- Avisos de Personalizar con el estilo de cada skin (estilos BitDialog, XpDialog, W98Dialog).
- Salvapantallas con estrellas cuadradas en rejilla de píxeles.
- Arreglado: Android borraba al compilar los dibujos que se piden por nombre (xp_*, bit_*): ahora están en `res/raw/keep.xml`.
- Arreglados solapes: fecha más pequeña, iconos de arriba más estrechos con nombres cortos, nombres de «Todas las apps» más pequeños, menú del ancho de su entrada más larga.
- Cambiar de skin: `../skin.sh win98|xp|8bit` (instala el APK con su letra y sube tema, fichas e iconos).
