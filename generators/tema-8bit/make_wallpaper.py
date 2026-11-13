#!/usr/bin/env python3
"""8-bit landscape wallpaper: 240x135 art pixels -> 1920x1080 (x8, NEAREST)."""
import os, random
from PIL import Image

W, H, S = 240, 135, 8
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallpaper.png")
random.seed(8)

def hx(s): s = s.lstrip("#"); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))

SKY = [hx(c) for c in ("0A0A4A", "141C86", "2040C8", "3478E8", "58A8F8", "94D0FC", "C4ECFC")]
WHITE, CSHADE = hx("FCFCFC"), hx("B4D4F4")
YEL = hx("FCE020")
MFAR, MFAR_L = hx("4458B8"), hx("6C84D8")     # far mountains
MNEAR, MNEAR_L, SNOW = hx("2C7C6C"), hx("48A488"), hx("E4F0FC")
HILL_D, HILL, HILL_L = hx("006800"), hx("10A010"), hx("58D850")
DIRT, DIRT_D, DIRT_L = hx("A85010"), hx("683008"), hx("D07828")
BASE = hx("402004")  # plain bottom (status bar covers it)

img = Image.new("RGB", (W, H))
px = img.load()

# --- sky: hard colour bands with 2-row checker dither at the seams
HORIZON = 112
bands = [0, 14, 30, 46, 62, 78, 94]          # starting rows
for y in range(HORIZON):
    bi = max(i for i, b in enumerate(bands) if y >= b)
    nxt = bands[bi + 1] if bi + 1 < len(bands) else HORIZON
    for x in range(W):
        c = SKY[bi]
        if bi + 1 < len(SKY) and y >= nxt - 4:        # dither zone before next band
            k = y - (nxt - 4)
            if (x + y) % 2 == 0 and k >= 2: c = SKY[bi + 1]
            elif (x + y) % 2 == 0 and k < 2 and (x // 2 + y) % 2 == 0 and k == 1: c = SKY[bi + 1]
        px[x, y] = c

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: px[x, y] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1): put(x, y, c)

# --- stars / sparkles (kept out of the clock and desktop-icon zones)
stars = [(96, 8), (112, 20), (127, 6), (103, 30), (138, 27), (4, 30), (30, 34), (62, 33), (78, 40),
         (155, 36), (188, 30), (222, 36), (238, 28), (120, 42), (14, 44), (205, 44)]
for i, (x, y) in enumerate(stars):
    put(x, y, WHITE)
    if i % 4 == 0:   # plus-shaped sparkle
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): put(x + dx, y + dy, YEL if i % 8 == 0 else SKY[5])
        put(x, y, WHITE)

# --- clouds: blocky, chunky stepped shapes
def cloud(x, y, w, big=True):
    h = 5 if big else 4
    # body
    rect(x + 2, y + 2, x + w - 2, y + h, WHITE)
    rect(x, y + 3, x + w, y + h, WHITE)
    rect(x + 4, y, x + 4 + w // 3, y + 2, WHITE)
    rect(x + 4 + w // 3 + 2, y + 1, x + w - 5, y + 3, WHITE)
    # underside shade
    rect(x + 1, y + h - 1, x + w - 1, y + h, CSHADE)
cloud(100, 52, 26); cloud(40, 50, 18, False); cloud(158, 46, 22); cloud(205, 58, 28)
cloud(8, 70, 16, False); cloud(124, 72, 14, False); cloud(180, 76, 14, False)

# --- mountains: blocky stepped triangles
def mountain(cx, peak, half, base, col, light, snow=None, slope=1.0):
    for y in range(peak, base):
        d = y - peak
        w = int(d * slope) // 1
        w = (w // 2) * 2                           # steps of 2 px -> chunky edges
        for x in range(cx - w, cx + w + 1):
            c = col
            if x > cx + (w // 3) and w > 3: c = light if False else col
            put(x, y, c)
            if x <= cx - w // 2 and w > 4 and (x + y) % 6 == 0: pass
        # lit left face
        for x in range(cx - w, cx - w // 3):
            put(x, y, light)
        if snow and d < snow:
            for x in range(cx - w, cx + w + 1):
                put(x, y, SNOW if (x - cx) < 0 or d % 2 == 0 else CSHADE)
for cx, pk, sl in ((30, 70, 1.5), (78, 62, 1.6), (130, 72, 1.4), (178, 60, 1.7), (222, 68, 1.5), (-4, 74, 1.2)):
    mountain(cx, pk, 0, HORIZON, MFAR, MFAR_L, snow=0 if False else 6, slope=sl)
for cx, pk, sl in ((54, 82, 1.9), (110, 88, 2.0), (158, 84, 1.8), (204, 90, 2.1), (244, 82, 1.8)):
    mountain(cx, pk, 0, HORIZON, MNEAR, MNEAR_L, snow=0, slope=sl)

# --- rolling hills (blocky half-discs)
def hill(cx, top, r, c, cl):
    for y in range(top, HORIZON + 6):
        d = y - top
        w = int(((2 * r * d) - d * d) ** .5) if d <= r else r
        w = (w // 2) * 2
        for x in range(cx - w, cx + w + 1):
            put(x, y, cl if (x - cx) < -w // 2 and d < r else c)
for cx, top, r, c, cl in ((20, 96, 24, HILL_D, HILL), (88, 100, 20, HILL, HILL_L), (140, 94, 26, HILL_D, HILL),
                          (200, 98, 22, HILL, HILL_L), (236, 96, 18, HILL_D, HILL)):
    hill(cx, top, r, c, cl)

# --- ground: grass strip + brick-like dirt tiles, plain base for the status bar
GT = 110
rect(0, GT, W, H, DIRT)
rect(0, GT, W, GT + 2, HILL_L)
rect(0, GT + 2, W, GT + 5, HILL)
rect(0, GT + 5, W, GT + 6, HILL_D)
for x in range(0, W, 2):                      # grass tufts / fringe
    if (x // 2) % 3 == 0: put(x, GT + 5, HILL); put(x + 1, GT + 6, HILL_D)
for ty in range(GT + 6, H - 9, 8):
    for x in range(W):
        put(x, ty + 7, DIRT_D)
        put(x, ty, DIRT_L) if (x // 16) % 2 == 0 else None
    off = 8 if ((ty - GT) // 8) % 2 else 0
    for x in range(off, W, 16):
        for y in range(ty, ty + 8): put(x, y, DIRT_D)
        put(x + 1, ty + 1, DIRT_L); put(x + 2, ty + 1, DIRT_L)
    for x in range(W):                         # speckles
        if (x * 7 + ty * 3) % 23 == 0: put(x, ty + 4, DIRT_D)
rect(0, H - 9, W, H, BASE)                     # plain strip under the status bar
rect(0, H - 9, W, H - 8, DIRT_D)

# small pixel bushes and flowers on the grass line
def bush(x, y):
    rect(x + 1, y - 2, x + 7, y, HILL_D); rect(x, y - 1, x + 8, y + 1, HILL_D)
    rect(x + 2, y - 2, x + 5, y - 1, HILL)
for x in (14, 70, 150, 214): bush(x, GT)
for x, c in ((44, YEL), (100, WHITE), (176, YEL), (232, WHITE)):
    put(x, GT - 1, c); put(x, GT, HILL_D)

img.resize((W * S, H * S), Image.NEAREST).save(OUT, optimize=True)
cols = len(set(img.getdata()))
print(OUT, os.path.getsize(OUT) // 1024, "KB,", cols, "colours")
