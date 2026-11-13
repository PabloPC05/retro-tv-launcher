# Fichas del launcher como ventanas de Windows 98: barra de título (azul si está enfocada, gris si no),
# botones _ □ ×, y en el área de la ventana el logo antiguo (o el banner actual recortado de una captura).
# Salida: banners/<paquete>.png y banners/<paquete>_on.png, a 280x157 (el tamaño exacto de una ficha en la tele).
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

S = os.path.dirname(os.path.abspath(__file__))  # carpeta generadores/
OUT = f"{S}/tema-98/banners"
W, H = 280, 157
BOLD = ImageFont.truetype(f"{S}/win98-assets/win98_bold.ttf", 22)
REG = ImageFont.truetype(f"{S}/win98-assets/win98.ttf", 22)
os.makedirs(OUT, exist_ok=True)

# paquete -> (título de la ventana, fondo del área: "white" para logos sueltos)
APPS = {
    "com.spotify.tv.android": "Spotify",
    "com.google.android.youtube.tv": "YouTube",
    "com.netflix.ninja": "Netflix",
    "com.disney.disneyplus": "Disney+",
    "com.wbd.stream": "HBO Max",
    "com.android.tv.settings": "Panel de control",
    "com.antena3.atresplayer.tv": "Atresplayer",
    "com.crunchyroll.crunchyroid": "Crunchyroll",
    "com.nathnetwork.avappnew": "IPTV",
    "com.movistarplus.androidtv": "Movistar+",
    "com.android.vending": "Play Store",
    "com.amazon.amazonvideo.livingroom": "Prime Video",
    "com.rtve.androidtv": "RTVE Play",
    "com.vodfactory.shadowz.es": "Shadowz",
    "com.stremio.one": "Stremio",
    "com.xiaomi.mitv.mediaexplorer": "Archivos USB",
    "com.google.android.youtube.tvmusic": "YouTube Music",
}
# Iconos de Windows 98 para las que no son una plataforma
ICONS = {"com.android.tv.settings": "control-panel.png", "com.xiaomi.mitv.mediaexplorer": "my-computer.png"}

# Logos antiguos que se usan: solo los que son la versión antigua de la misma app (regla de Pablo: si no hay,
# el de ahora). Disney Channel, HBO, Antena 3, Canal+ y el YouTube de 2011 para YouTube Music no lo son.
VIEJOS = {"com.spotify.tv.android", "com.google.android.youtube.tv", "com.netflix.ninja",
          "com.amazon.amazonvideo.livingroom", "com.android.vending", "com.crunchyroll.crunchyroid", "com.rtve.androidtv",
          # pedidos por Pablo: Disney y HBO antiguos para Disney+ y HBO Max, y el Movistar antiguo para Movistar+
          "com.disney.disneyplus", "com.wbd.stream", "com.movistarplus.androidtv"}

# Recortes de los banners actuales en las capturas (x, y) de la esquina de cada ficha de 279x156
CAP = f"{S}/launcher-capturas"
CROPS = {
    "com.spotify.tv.android": ("2-netflix.png", 158, 617),
    "com.google.android.youtube.tv": ("1-inicio.png", 489, 617),
    "com.netflix.ninja": ("1-inicio.png", 820, 617),
    "com.disney.disneyplus": ("1-inicio.png", 1151, 617),
    "com.wbd.stream": ("1-inicio.png", 1482, 617),
    "com.antena3.atresplayer.tv": ("1-inicio.png", 489, 888),
    "com.crunchyroll.crunchyroid": ("1-inicio.png", 820, 888),
    "com.nathnetwork.avappnew": ("1-inicio.png", 1151, 888),
    "com.movistarplus.androidtv": ("1-inicio.png", 1482, 888),
    "com.android.vending": ("3-apps.png", 158, 757),
    "com.amazon.amazonvideo.livingroom": ("3-apps.png", 489, 757),
    "com.rtve.androidtv": ("3-apps.png", 820, 757),
    "com.vodfactory.shadowz.es": ("3-apps.png", 1151, 757),
    "com.stremio.one": ("3-apps.png", 1482, 757),
    "com.google.android.youtube.tvmusic": ("9-abajo.png", 489, 740),
}

def bevel(d, x0, y0, x1, y1, raised=True):
    """Relieve de Windows 98 de dos líneas (2 px cada una) dentro del rectángulo."""
    lt1, rb1, lt2, rb2 = ("#DFDFDF", "#000000", "#FFFFFF", "#808080") if raised else ("#808080", "#FFFFFF", "#000000", "#DFDFDF")
    for i, (lt, rb) in enumerate(((lt1, rb1), (lt2, rb2))):
        o = i * 2
        d.rectangle([x0 + o, y0 + o, x1 - o, y0 + o + 1], fill=lt)
        d.rectangle([x0 + o, y0 + o, x0 + o + 1, y1 - o], fill=lt)
        d.rectangle([x0 + o, y1 - o - 1, x1 - o, y1 - o], fill=rb)
        d.rectangle([x1 - o - 1, y0 + o, x1 - o, y1 - o], fill=rb)

def gradient(img, box, c0, c1):
    x0, y0, x1, y1 = box
    a, b = Image.new("RGB", (1, 1), c0).getpixel((0, 0)), Image.new("RGB", (1, 1), c1).getpixel((0, 0))
    d = ImageDraw.Draw(img)
    for x in range(x0, x1 + 1):
        t = (x - x0) / max(1, x1 - x0)
        d.line([x, y0, x, y1], fill=tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))

def caption_button(img, x, y, kind):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + 19, y + 17], fill="#C0C0C0")
    bevel(d, x, y, x + 19, y + 17)
    k = "#000000"
    if kind == "min":
        d.rectangle([x + 5, y + 11, x + 12, y + 12], fill=k)
    elif kind == "max":
        d.rectangle([x + 4, y + 3, x + 14, y + 13], outline=k)
        d.rectangle([x + 4, y + 3, x + 14, y + 4], fill=k)
    else:
        for o in range(2):
            d.line([x + 5 + o, y + 4, x + 12 + o, y + 12], fill=k)
            d.line([x + 12 + o, y + 4, x + 5 + o, y + 12], fill=k)

def fit(im, w, h):
    im = im.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    return im

def window(pkg, title, active, content, white, boxed=False):
    img = Image.new("RGB", (W, H), "#C0C0C0")
    d = ImageDraw.Draw(img)
    bevel(d, 0, 0, W - 1, H - 1)
    tb = (6, 6, W - 7, 31)
    gradient(img, tb, "#000080" if active else "#808080", "#1084D0" if active else "#B5B5B5")
    # botones a la derecha; el título se corta con «...» si no cabe
    bx = W - 7
    t = title
    while BOLD.getlength(t) > bx - 18 and len(t) > 1:
        t = t[:-1]
    if t != title: t = t[:-2].rstrip() + "..."
    # La negrita no trae «+»: ese carácter va en la normal
    x = 12
    for ch in t:
        f = REG if ch == "+" else BOLD
        d.text((x, 8), ch, font=f, fill="#FFFFFF" if active else "#C0C0C0")
        x += f.getlength(ch)
    # sin botones _ □ ×: en la tele no se pueden pulsar, y aquí nada es solo decorado
    # área de la ventana, hundida
    ca = (6, 35, W - 7, H - 7)
    fill = "#FFFFFF" if white else "#000000"
    # logo que es un recuadro de color (Spotify 2008, Netflix 2001, RTVE 1991): la ventana toma ese color
    if white and boxed and content.mode == "RGBA":
        px = content.getpixel((max(1, content.width // 50), content.height // 2))
        if px[3] == 255 and min(px[:3]) < 235: fill = px[:3]
    d.rectangle(ca, fill=fill)
    bevel(d, *ca, raised=False)
    iw, ih = ca[2] - ca[0] - 7, ca[3] - ca[1] - 7
    if white:
        c = fit(content, int(iw * 0.86), int(ih * 0.9))
    else:
        c = content.resize((iw, ih), Image.LANCZOS)
    px = ca[0] + 4 + (iw - c.width) // 2
    py = ca[1] + 4 + (ih - c.height) // 2
    img.paste(c, (px, py), c if c.mode == "RGBA" else None)
    return img

def content_for(pkg, logos):
    if pkg in ICONS:
        return Image.open(f"{S}/win98-assets/{ICONS[pkg]}").convert("RGBA"), True, "icono Windows 98"
    m = logos.get(pkg) if pkg in VIEJOS else None
    if m:
        im = Image.open(f"{S}/logos-antiguos/{m['file']}").convert("RGBA")
        bb = im.getbbox()
        if bb: im = im.crop(bb)
        # recorta también el margen blanco de los logos que no son transparentes (el Spotify de 2008)
        from PIL import ImageChops
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        diff = ImageChops.difference(im.convert("RGBA"), bg).convert("L").point(lambda v: 255 if v > 24 else 0)
        bb = diff.getbbox()
        if bb: im = im.crop(bb)
        return im, True, "logo antiguo" + ("" if m.get("transparent", True) else " (recuadro)")
    if pkg in CROPS:
        f, x, y = CROPS[pkg]
        im = Image.open(f"{CAP}/{f}").convert("RGB").crop((x + 12, y + 10, x + 279 - 12, y + 156 - 10))
        return im, False, "banner actual"
    return None, False, "nada"

if __name__ == "__main__":
    logos = {}
    mf = f"{S}/logos-antiguos/manifest.json"
    if os.path.exists(mf):
        logos = {k: v for k, v in json.load(open(mf)).items() if isinstance(v, dict) and v.get("file")
                 and os.path.exists(f"{S}/logos-antiguos/{v['file']}")}
    for pkg, title in APPS.items():
        c, white, how = content_for(pkg, logos)
        if c is None:
            print(f"{pkg}: sin imagen, se queda el banner del launcher"); continue
        boxed = how.endswith("(recuadro)")
        window(pkg, title, False, c, white, boxed).save(f"{OUT}/{pkg}.png")
        window(pkg, title, True, c, white, boxed).save(f"{OUT}/{pkg}_on.png")
        print(f"{pkg}: {how}")
