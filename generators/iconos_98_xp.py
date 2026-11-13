# Iconos de «Todas las apps» para las skins Windows 98 y XP: el mismo contenido que sus fichas (logo antiguo,
# icono del sistema o recorte del banner actual), centrado en 128x128. Salida: tema-98/icons y tema-xp/icons.
import os, sys, json, importlib.util
from PIL import Image
G = os.path.dirname(os.path.abspath(__file__))
logos = {k: v for k, v in json.load(open(f"{G}/logos-antiguos/manifest.json")).items() if isinstance(v, dict) and v.get("file")}
for skin, path in (("98", f"{G}/w98banners.py"), ("xp", f"{G}/tema-xp/xpbanners.py")):
    spec = importlib.util.spec_from_file_location("g" + skin, path); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
    out = f"{G}/tema-{skin}/icons"; os.makedirs(out, exist_ok=True)
    for pkg in g.APPS:
        c = g.content_for(pkg, logos)[0]
        if c is None: continue
        c = c.convert("RGBA"); bb = c.getbbox(); c = c.crop(bb) if bb else c
        c.thumbnail((120, 120), Image.LANCZOS)
        im = Image.new("RGBA", (128, 128), (0, 0, 0, 0)); im.paste(c, ((128 - c.width) // 2, (128 - c.height) // 2), c)
        im.save(f"{out}/{pkg}.png")
    print(skin, "ok")
