# Fondo de escritorio Frutiger Aero 1920x1080, dibujado entero en código (sin fotos, original).
import numpy as np, os, warnings
warnings.filterwarnings('ignore')
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallpaper.jpg")
rng = np.random.default_rng(7)

def lerp(a, b, t):
    return a + (b - a) * t

def vgrad(stops):
    """Degradado vertical: stops = [(pos 0..1, (r,g,b)), ...] -> array HxWx3 float."""
    ys = np.linspace(0, 1, H)
    pos = [s[0] for s in stops]
    out = np.zeros((H, 3))
    for c in range(3):
        out[:, c] = np.interp(ys, pos, [s[1][c] for s in stops])
    return np.repeat(out[:, None, :], W, axis=1)

def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")

def over(base, layer_rgba):
    base = base.convert("RGBA")
    return Image.alpha_composite(base, layer_rgba)

# ---------- cielo ----------
sky = vgrad([(0.0, (6, 72, 200)), (0.25, (20, 120, 235)), (0.55, (80, 185, 250)),
             (0.78, (190, 238, 252)), (1.0, (235, 252, 255))])
# luz más clara a la izquierda (de donde viene el sol)
xs = np.linspace(0, 1, W)[None, :, None]
sky = sky + (1 - xs) ** 2 * 18 * np.linspace(1, 0.3, H)[:, None, None]
img = to_img(sky).convert("RGBA")

# ---------- rayos de luz desde arriba a la izquierda ----------
rays = Image.new("L", (W, H), 0)
rd = ImageDraw.Draw(rays)
ox, oy = -60, -80
import math
for ang, wid, a in [(16, 3, 120), (24, 6, 90), (31, 2, 140), (38, 7, 80), (46, 3, 120), (54, 8, 70),
                    (63, 3, 100), (72, 6, 70), (82, 3, 70)]:
    L = 2600
    a0, a1 = math.radians(ang - wid / 2), math.radians(ang + wid / 2)
    rd.polygon([(ox, oy), (ox + L * math.cos(a0), oy + L * math.sin(a0)),
                (ox + L * math.cos(a1), oy + L * math.sin(a1))], fill=a)
rays = rays.filter(ImageFilter.GaussianBlur(12))
# se desvanecen con la distancia
dist = np.hypot(*np.meshgrid(np.arange(W) - ox, np.arange(H) - oy))
fade = np.clip(1 - dist / 2300, 0, 1) ** 1.3
# los rayos no pasan por la zona del reloj (x 80-700, y 40-180): quedan más tenues allí
yy0, xx0 = np.mgrid[:H, :W]
clock = np.exp(-(((xx0 - 390) / 420.0) ** 2 + ((yy0 - 110) / 120.0) ** 2) ** 1.5)
fade = fade * (1 - 0.8 * clock)
rays = Image.fromarray((np.asarray(rays, dtype=float) * fade * 0.6).astype(np.uint8))
white = Image.new("RGBA", (W, H), (255, 255, 255, 0))
white.putalpha(rays)
img = over(img, white)

# ---------- brillo (lens flare) arriba a la izquierda ----------
def glow(cx, cy, r, color, strength):
    yy, xx = np.ogrid[:H, :W]
    d = np.hypot(xx - cx, yy - cy) / r
    a = np.clip(1 - d, 0, 1) ** 2 * strength
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., :3] = color
    lay[..., 3] = np.clip(a * 255, 0, 255)
    return Image.fromarray(lay, "RGBA")

img = over(img, glow(0, 0, 700, (255, 255, 255), 0.35))
img = over(img, glow(0, 0, 240, (255, 255, 240), 0.8))
# destellos a lo largo de la diagonal del flare (lejos del reloj)
for t, r, col, s in [(0.28, 70, (200, 240, 255), 0.35), (0.40, 38, (255, 255, 255), 0.4),
                     (0.52, 110, (170, 230, 255), 0.22), (0.66, 55, (210, 255, 240), 0.28)]:
    img = over(img, glow(int(lerp(0, 1500, t)), int(lerp(0, 840, t)), r, col, s))

# ---------- nubes ----------
def cloud(cx, cy, w, h, alpha=235, seed=0):
    r = np.random.default_rng(seed)
    lay = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lay)
    n = 11
    for i in range(n):
        t = (i + 0.5) / n
        ex = cx + (t - 0.5) * w * 0.85 + r.normal(0, w * 0.03)
        # perfil abombado: más alto en el centro
        eh = h * (0.45 + 0.75 * math.sin(math.pi * t)) * r.uniform(0.8, 1.15)
        ew = w * r.uniform(0.17, 0.27)
        ey = cy + h * 0.15 - eh * 0.25
        d.ellipse([ex - ew, ey - eh, ex + ew, ey + eh * 0.7], fill=alpha)
    # base plana y suave
    d.ellipse([cx - w * 0.5, cy - h * 0.12, cx + w * 0.5, cy + h * 0.42], fill=alpha)
    lay = lay.filter(ImageFilter.GaussianBlur(h * 0.16))
    # sombreado azulado abajo
    shade = np.asarray(lay, dtype=float) / 255
    yy = np.arange(H)[:, None]
    k = np.clip((yy - (cy - h * 0.1)) / (h * 0.7), 0, 1)
    rgb = np.zeros((H, W, 4), np.uint8)
    rgb[..., 0] = 255 - 38 * k
    rgb[..., 1] = 255 - 20 * k
    rgb[..., 2] = 255 - 2 * k * 0
    rgb[..., 3] = (shade * 255).astype(np.uint8)
    return Image.fromarray(rgb, "RGBA")

for (cx, cy, w, h, a, s) in [(1500, 300, 640, 150, 225, 1), (1000, 470, 520, 110, 200, 2),
                              (1740, 560, 460, 100, 190, 3), (520, 520, 420, 90, 170, 4),
                              (1230, 130, 380, 80, 150, 5)]:
    img = over(img, cloud(cx, cy, w, h, a, s))

# ---------- colinas ----------
def hill_curve(base, amp1, f1, ph1, amp2, f2, ph2, slope=0.0):
    x = np.arange(W)
    return base + amp1 * np.sin(x / W * f1 * math.pi + ph1) + amp2 * np.sin(x / W * f2 * math.pi + ph2) + slope * (x - W / 2)

def paint_hill(img, curve, top, bottom, sheen, haze=0.0):
    yy = np.arange(H)[:, None]
    mask = (yy >= curve[None, :]).astype(float)
    # borde suavizado (antialiasing)
    mask = np.clip(yy - curve[None, :] + 0.5, 0, 1)
    depth = np.clip((yy - curve[None, :]) / (H - curve.min()), 0, 1)
    # degradado vertical hacia abajo + más luz en el borde superior (brillo)
    col = np.zeros((H, W, 3))
    for c in range(3):
        col[..., c] = lerp(top[c], bottom[c], np.clip(depth * 1.6, 0, 1))
    rim = np.exp(-np.clip(yy - curve[None, :], 0, None) / 38.0)
    # brillo más fuerte a la izquierda (sol)
    xs = np.linspace(0, 1, W)[None, :]
    rim = rim * (0.55 + 0.6 * (1 - xs))
    for c in range(3):
        col[..., c] = col[..., c] + (sheen[c] - col[..., c]) * np.clip(rim, 0, 1) * 0.75
    # bruma azulada para colinas lejanas
    if haze:
        for c, h in enumerate((170, 225, 245)):
            col[..., c] = col[..., c] + (h - col[..., c]) * haze
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    lay[..., 3] = (mask * 255).astype(np.uint8)
    return over(img, Image.fromarray(lay, "RGBA"))

# colina lejana (más pálida)
far = hill_curve(690, 28, 1.5, 0.6, 12, 3.7, 1.0, 0.012)
img = paint_hill(img, far, (110, 205, 90), (60, 170, 60), (190, 245, 140), haze=0.32)
# colina principal (~40% inferior)
main = hill_curve(700, 55, 1.15, 3.3, 14, 2.8, 0.3, -0.022)
img = paint_hill(img, main, (92, 214, 40), (20, 130, 24), (210, 255, 130))
# loma delantera, suave, que baja hacia la barra de tareas
front = hill_curve(900, 34, 1.4, 1.2, 9, 3.2, 2.0, 0.02)
img = paint_hill(img, front, (60, 190, 34), (12, 105, 20), (170, 240, 90))

# ---------- burbujas ----------
def bubble(size, tint, seed):
    S = size * 4  # supersampling
    r = S / 2
    yy, xx = np.mgrid[:S, :S]
    dx, dy = (xx - r + 0.5) / r, (yy - r + 0.5) / r
    d = np.hypot(dx, dy)
    inside = np.clip((1 - d) * r / 2.0, 0, 1)
    out = np.zeros((S, S, 4))
    tr, tg, tb = tint
    # relleno: casi transparente con más cuerpo hacia abajo-derecha (como cristal)
    lit = np.clip((dx * 0.55 + dy * 0.75 + 1) / 2, 0, 1)
    base_a = 0.14 + 0.28 * lit ** 2
    # aro de luz de borde (fresnel)
    rim = np.clip((d - 0.80) / 0.2, 0, 1) ** 2
    rim_a = rim * (0.8 + 0.2 * (1 - lit))
    col = np.array([tr, tg, tb], float)
    a = base_a + rim_a
    rgb = np.zeros((S, S, 3))
    for c in range(3):
        rgb[..., c] = col[c] * (1 - rim * 0.9) + 255 * rim * 0.9
    # reflejo azul-cian en la parte inferior (luz rebotada)
    glow_b = np.exp(-(((dx - 0.1) ** 2) / 0.35 + ((dy - 0.62) ** 2) / 0.06))
    rgb = rgb + (np.array([200, 255, 255]) - rgb) * glow_b[..., None] * 0.7
    a = a + glow_b * 0.25
    out[..., :3] = np.clip(rgb, 0, 255) / 255
    out[..., 3] = np.clip(a, 0, 1) * inside
    im = Image.fromarray((out * 255).astype(np.uint8), "RGBA")
    # brillo especular arriba a la izquierda: elipse blanca inclinada con degradado
    spec = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = np.zeros((S, S))
    # elipse rotada
    ang = math.radians(-38)
    cx, cy = -0.38, -0.42
    ux = (dx - cx) * math.cos(ang) + (dy - cy) * math.sin(ang)
    uy = -(dx - cx) * math.sin(ang) + (dy - cy) * math.cos(ang)
    e = np.hypot(ux / 0.36, uy / 0.17)
    sd = np.clip(1 - e, 0, 1) ** 0.7
    sd = np.minimum(sd, 1) * (d < 0.9)
    spec_arr = np.zeros((S, S, 4))
    spec_arr[..., :3] = 1
    spec_arr[..., 3] = sd * 0.95
    spec = Image.fromarray((spec_arr * 255).astype(np.uint8), "RGBA")
    im = Image.alpha_composite(im, spec)
    # punto brillante pequeño abajo-derecha
    dot = np.zeros((S, S, 4))
    dd = np.hypot(dx - 0.5, dy - 0.55) / 0.08
    dot[..., :3] = 1
    dot[..., 3] = np.clip(1 - dd, 0, 1) * 0.6
    im = Image.alpha_composite(im, Image.fromarray((dot * 255).astype(np.uint8), "RGBA"))
    return im.resize((size, size), Image.LANCZOS)

tints = [(120, 220, 255), (150, 235, 255), (110, 200, 255), (170, 255, 235), (190, 245, 255)]
# (x, y, diámetro): sobre todo arriba y a la derecha; nada en el reloj (x<720,y<190) ni en la barra (y>1020)
bubbles = [
    (1480, 90, 150), (1700, 210, 96), (1810, 90, 54), (1560, 380, 210), (1330, 250, 64),
    (1850, 420, 120), (1230, 80, 40), (1010, 160, 58), (1650, 590, 72), (1390, 520, 90),
    (1790, 640, 170), (860, 330, 34), (770, 460, 84), (1120, 400, 26), (1900, 300, 40),
    (1060, 600, 46), (560, 290, 30), (330, 380, 64), (1480, 700, 38), (150, 560, 52),
    (1250, 330, 22), (940, 250, 22), (1595, 170, 28), (1700, 790, 56), (90, 330, 36),
    (1880, 820, 30), (1960 - 60, 560, 24),
]
bubble_cache = {}
bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for i, (x, y, dia) in enumerate(bubbles):
    b = bubble(dia, tints[i % len(tints)], i)
    bl.alpha_composite(b, (int(x - dia / 2), int(y - dia / 2))) if (x - dia / 2 >= 0 and y - dia / 2 >= 0 and x + dia / 2 <= W and y + dia / 2 <= H) else bl.paste(b, (int(x - dia / 2), int(y - dia / 2)), b)
# sombra suave bajo cada burbuja sobre el cielo no hace falta; las burbujas flotan
img = Image.alpha_composite(img, bl)

# ---------- brillo final: viñeta suave abajo y retoque de saturación ----------
final = img.convert("RGB")
a = np.asarray(final, dtype=float)
# viñeta muy sutil en las esquinas inferiores
yy, xx = np.mgrid[:H, :W]
v = np.clip((np.hypot((xx - W / 2) / (W / 2), (yy - H * 0.45) / (H * 0.7)) - 0.8) / 0.8, 0, 1)
a = a * (1 - 0.12 * v[..., None])
# banda de la barra de tareas inferior: sin detalle (la hierba se oscurece suave y uniforme)
band = np.clip((yy - (H - 150)) / 150, 0, 1)[..., None]
a = a * (1 - 0.18 * band)
# grano mínimo para evitar bandas en el degradado
a = a + rng.normal(0, 0.9, a.shape)
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(OUT, quality=88, optimize=True, subsampling=0 if False else 2)
print(OUT, os.path.getsize(OUT) // 1024, "KB")
