import sys
from fontTools.ttLib import TTFont
need="áéíóúÁÉÍÓÚñÑü¿¡+:.,-0123456789·"
for f in sys.argv[1:]:
    c=TTFont(f).getBestCmap()
    print(f,[ch for ch in need if ord(ch) not in c] or "ALL OK")
