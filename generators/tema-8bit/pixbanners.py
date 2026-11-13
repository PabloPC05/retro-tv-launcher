#!/usr/bin/env python3
"""8-bit (NES RPG-menu) banner tiles: banners/<pkg>.png and <pkg>_on.png, 280x157 RGBA.
Everything is drawn on a 140x78 'cell' grid (1 cell = 2x2 screen px), then scaled x2 NEAREST."""
import os, re, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "8bit-assets")
ICONS = os.path.join(ASSETS, "icons")
FONT = os.path.join(ASSETS, "pix.ttf")
FONT_B = os.path.join(ASSETS, "pix_bold.ttf")
OUT = os.path.join(HERE, "banners")
W, H, K = 140, 78, 2          # cells; scale
TW, TH = 280, 157

def hx(s): s = s.lstrip("#"); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4)) + (255,)
WHITE, YEL, BLACK = hx("FCFCFC"), hx("FCE020"), hx("000000")
FILL, FILL_ON = hx("08083C"), hx("1C2A8C")
YEL_D = hx("B88800")

def load_apps():
    src = open(os.path.join(os.path.dirname(HERE), "w98banners.py"), encoding="utf-8").read()
    body = re.search(r"^APPS\s*=\s*\{(.*?)^\}", src, re.S | re.M).group(1)
    return dict(re.findall(r'"([^"]+)":\s*"([^"]+)"', body))

HAVE_FONT = os.path.exists(FONT)
def font(bold=False):
    p = FONT_B if bold and os.path.exists(FONT_B) else FONT
    return ImageFont.truetype(p, 8) if HAVE_FONT else ImageFont.load_default()

def text_mask(txt, bold=False):
    """1-bit text at native 8px size -> cropped 'L' image (0/255)."""
    f = font(bold)
    m = Image.new("L", (len(txt) * 9 + 8, 14), 0)
    d = ImageDraw.Draw(m); d.fontmode = "1"
    d.text((2, 2), txt, font=f, fill=255)
    return m.crop(m.getbbox() or (0, 0, 1, 1)).point(lambda v: 255 if v > 127 else 0)

def blit(img, mask, x, y, col):
    img.paste(Image.new("RGBA", mask.size, col), (x, y), mask)

def cut_rect(x0, y0, x1, y1, n):
    """cells of a rect with stepped (notched) corners: remove i+j<n at each corner."""
    cells = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            i, j = min(x - x0, x1 - 1 - x), min(y - y0, y1 - 1 - y)
            if i + j >= n: cells.add((x, y))
    return cells

def put_cells(img, cells, col):
    px = img.load()
    for x, y in cells:
        if 0 <= x < W and 0 <= y < H: px[x, y] = col

BX0, BY0, BX1, BY1 = 11, 1, 139, 77      # box in cells (cursor lives in the left margin)

def cursor(img):
    cy = (BY0 + BY1) // 2
    px = img.load()
    for r in range(-6, 7):                 # black outline triangle, then yellow inside
        w = 8 - abs(r)
        for x in range(1, 1 + w + 1): px[x, cy + r] = BLACK
    for r in range(-4, 5):
        w = 6 - abs(r)
        for x in range(2, 2 + w): px[x, cy + r] = YEL

def icon_cells(pkg, title):
    """returns RGBA cell image of the icon (integer-scaled) or placeholder letter."""
    p = os.path.join(ICONS, pkg + ".png")
    if os.path.exists(p):
        return Image.open(p).convert("RGBA"), False
    m = text_mask((title[0] or "?").upper(), True)
    big = m.resize((m.width * 5, m.height * 5), Image.NEAREST)
    im = Image.new("RGBA", big.size, (0, 0, 0, 0))
    blit(im, big, 0, 0, hx("58A8F8"))
    return im, True

def wrap(title, maxw):
    if len(title) * 8 <= maxw: return [title]
    words = title.split(" ")
    for cut in range(1, len(words)):                       # best 2-line split
        a, b = " ".join(words[:cut]), " ".join(words[cut:])
        if max(len(a), len(b)) * 8 <= maxw: return [a, b]
    return [title]

def tile(pkg, title, on):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    border = YEL if on else WHITE
    put_cells(img, cut_rect(BX0, BY0, BX1, BY1, 3), border)
    put_cells(img, cut_rect(BX0 + 3, BY0 + 3, BX1 - 3, BY1 - 3, 1), FILL_ON if on else FILL)
    if on:   # inner shadow line gives the focused box a little depth
        put_cells(img, {(x, BY0 + 3) for x in range(BX0 + 4, BX1 - 4)}, hx("3C4CC8"))
    cx = (BX0 + BX1) // 2
    lines = wrap(title, (BX1 - BX0) - 12)
    th = 8 * len(lines) + 2 * (len(lines) - 1)
    ty = BY1 - 6 - th
    top, bot = BY0 + 7, ty - 3                              # icon band
    ic, ph = icon_cells(pkg, title)
    n = max(ic.size)
    k = max(1, min((bot - top) // n, (BX1 - BX0 - 16) // ic.width)) if n <= bot - top else 0
    if k == 0:
        s = (bot - top) / n
        ic = ic.resize((max(1, round(ic.width * s)), max(1, round(ic.height * s))), Image.NEAREST); k = 1
    else:
        ic = ic.resize((ic.width * k, ic.height * k), Image.NEAREST)
    img.alpha_composite(ic, (cx - ic.width // 2, top + (bot - top - ic.height) // 2))
    for i, ln in enumerate(lines):
        m = text_mask(ln, True)
        x, y = cx - m.width // 2, ty + i * 10
        blit(img, m, x + 1, y + 1, BLACK)
        blit(img, m, x, y, YEL if on else WHITE)
    if on: cursor(img)
    big = img.resize((W * K, H * K), Image.NEAREST)
    out = Image.new("RGBA", (TW, TH), (0, 0, 0, 0)); out.paste(big, (0, 0))
    return out

def main():
    os.makedirs(OUT, exist_ok=True)
    apps = load_apps()
    real = [p for p in apps if os.path.exists(os.path.join(ICONS, p + ".png"))]
    print(f"font: {'pix.ttf' if HAVE_FONT else 'PLACEHOLDER (Pillow default)'}; real icons: {len(real)}/{len(apps)}")
    for pkg, title in apps.items():
        tile(pkg, title, False).save(f"{OUT}/{pkg}.png")
        tile(pkg, title, True).save(f"{OUT}/{pkg}_on.png")
    # contact sheet on the wallpaper
    wp = os.path.join(HERE, "wallpaper.png")
    bg = Image.open(wp).convert("RGBA") if os.path.exists(wp) else Image.new("RGBA", (1920, 1080), hx("2040C8"))
    sheet = bg.copy(); cols, gx, gy = 3, 580, 170
    for i, pkg in enumerate(apps):
        r, c = divmod(i, cols)
        x, y = 40 + c * gx, 10 + r * gy
        for j, suf in enumerate(("", "_on")):
            sheet.alpha_composite(Image.open(f"{OUT}/{pkg}{suf}.png"), (x + j * 290, y))
    sheet.convert("RGB").save(os.path.join(HERE, "contact_sheet.png"))
main()
