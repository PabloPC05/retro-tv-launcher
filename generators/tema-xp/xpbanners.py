# Fichas del launcher como ventanas de Windows XP (Luna): barra de título (azul si está enfocada, gris si no),
# botones _ □ ×, y en el área de la ventana el logo antiguo (o el banner actual recortado de una captura).
# Salida: banners/<paquete>.png y banners/<paquete>_on.png, a 280x157 (el tamaño exacto de una ficha en la tele).
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # carpeta generadores/
OUT = f"{S}/tema-xp/banners"
W, H = 280, 157
def _font(size):
    for p in (f"{S}/xp-assets/xp_bold.ttf", "/System/Library/Fonts/Supplemental/Tahoma Bold.ttf",
              "/System/Library/Fonts/Supplemental/Verdana Bold.ttf"):
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except OSError: pass
    return ImageFont.load_default()
BOLD = _font(19)
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
# Iconos de Windows XP (Luna) para las que no son una plataforma
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

def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def vgrad(w, h, stops):
    """Degradado vertical RGBA de w x h; stops = [(posición 0..1, '#rrggbb'), ...]."""
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    st = [(p, hexrgb(c)) for p, c in stops]
    for y in range(h):
        t = y / max(1, h - 1)
        for (p0, c0), (p1, c1) in zip(st, st[1:]):
            if p0 <= t <= p1:
                u = (t - p0) / max(1e-9, p1 - p0)
                d.line([0, y, w, y], fill=tuple(round(c0[i] + (c1[i] - c0[i]) * u) for i in range(3)))
                break
    return im

def fit(im, w, h):
    im = im.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    return im

R = 8       # radio de las esquinas de arriba
TB = 30     # alto de la barra de título
SS = 4      # supersampling para los bordes redondeados

def top_round_mask(w, h, r):
    """Máscara L con las esquinas de arriba redondeadas y abajo recto, con antialiasing."""
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1 + r * SS * 2], radius=r * SS, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def window(pkg, title, active, content, white, boxed=False):
    # colores Luna
    if active:
        bar = [(0, "#3D95FF"), (0.12, "#1C70EE"), (0.5, "#0A5ADB"), (0.88, "#0A52CC"), (1, "#0841B4")]
        frame_l, frame_r, frame_b = "#2A5BE8", "#0831D9", "#0831D9"
        ttxt = "#FFFFFF"
        top_line = "#A9CFFF"
    else:
        bar = [(0, "#A6B8E8"), (0.5, "#8FA6E2"), (1, "#7A96DF")]
        bar = [(0, "#9DB0E6"), (0.5, "#8CA3E2"), (1, "#7A96DF")]
        frame_l, frame_r, frame_b = "#7F99E0", "#6C88D8", "#6C88D8"
        ttxt = "#D8E4F8"
        top_line = "#C9D6F2"
    img = Image.new("RGB", (W, H), frame_b)
    d = ImageDraw.Draw(img)
    # marco: degradado horizontal sutil (más claro a la izquierda/arriba)
    fl, fr = hexrgb(frame_l), hexrgb(frame_r)
    for x in range(W):
        t = x / (W - 1)
        d.line([x, 0, x, H], fill=tuple(round(fl[i] + (fr[i] - fl[i]) * t) for i in range(3)))
    FW = 4  # grosor del marco
    # barra de título (llega hasta los bordes, el marco la rodea)
    img.paste(vgrad(W, TB, bar), (0, 0))
    d.line([0, 0, W, 0], fill=top_line)
    d.line([1, 1, W - 2, 1], fill=tuple((a + b) // 2 for a, b in zip(hexrgb(top_line), hexrgb(bar[0][1]))))
    # líneas de luz en los bordes laterales de la barra
    d.line([0, 0, 0, TB], fill=hexrgb(frame_l)); d.line([W - 1, 0, W - 1, TB], fill=hexrgb(frame_r))
    # título: negrita blanca con sombra oscura suave; el título se corta con «...» si no cabe
    t = title
    maxw = W - 24
    while BOLD.getlength(t) > maxw and len(t) > 1:
        t = t[:-1]
    if t != title: t = t[:-2].rstrip() + "..."
    ty = (TB - 19) // 2 - 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    x = 10
    for ch in t:
        sd.text((x + 1, ty + 1), ch, font=BOLD, fill=(0, 0, 40, 150 if active else 70))
        x += BOLD.getlength(ch)
    img.paste(sh, (0, 0), sh)
    d = ImageDraw.Draw(img)
    x = 10
    for ch in t:
        d.text((x, ty), ch, font=BOLD, fill=ttxt)
        x += BOLD.getlength(ch)
    # área de cliente: blanca (o del color del recuadro del logo), con un borde interior fino
    ca = (FW, TB, W - FW - 1, H - FW - 1)
    fill = (255, 255, 255)
    # logo que es un recuadro de color (Spotify 2008, Netflix 2001, RTVE 1991): la ventana toma ese color
    if white and boxed and content.mode == "RGBA":
        px = content.getpixel((max(1, content.width // 50), content.height // 2))
        if px[3] == 255 and min(px[:3]) < 235: fill = px[:3]
    d.rectangle(ca, fill=fill)
    d.rectangle(ca, outline="#0831D9" if active else "#6C88D8")
    iw, ih = ca[2] - ca[0] - 3, ca[3] - ca[1] - 3
    if white:
        c = fit(content, int(iw * 0.86), int(ih * 0.9))
    else:
        c = content.resize((iw, ih), Image.LANCZOS)
    px = ca[0] + 2 + (iw - c.width) // 2
    py = ca[1] + 2 + (ih - c.height) // 2
    img.paste(c, (px, py), c if c.mode == "RGBA" else None)
    out = img.convert("RGBA")
    out.putalpha(top_round_mask(W, H, R))
    return out

def content_for(pkg, logos):
    if pkg in ICONS:
        return Image.open(f"{S}/xp-assets/{ICONS[pkg]}").convert("RGBA"), True, "icono XP"
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
