import os
# Second batch of icons. Reuses the helpers of build.py (everything before the "I=R+" line).
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"build.py")).read().split('I=R+"/icons/"')[0]
exec(src)
I=R+"/icons/"; U=R+"/ui/"
si=lambda s: f"{DL}/si_{s}.svg"
pa=lambda s: f"{DL}/pa_{s}.svg"
NAVY=(0,0,60)
new={}

# Play Games: controller (pixelarticons gamepad) on Play-green tile
new["com.google.android.play.games"]=brand("#01875F",pa("gamepad"),24,th=128)

# Google TV: Simple Icons glyph, coloured by region on light tile
def gtv():
    im=tile("#F4F4F4"); p=im.load()
    m=center(mask_from(render(si("googletv"),24),110)); h,w=m.shape
    ox,oy=(G-w)//2,(G-h)//2
    for y in range(h):
        for x in range(w):
            if not m[y,x]: continue
            fx=x/w; fy=y/h
            if fx<0.16 or (fx<0.25 and fy<0.2): col=(236,46,60)       # red, left
            elif fy<0.30: col=(0,140,255)                              # blue, top
            elif fx>0.78: col=(255,200,0)                              # yellow, right
            else: col=(0,190,90)                                       # green, bottom
            p[ox+x,oy+y]=col+(255,)
    return im
new["com.google.android.videos"]=gtv()

# Gallery: hand-placed frame with sky, sun and mountains
# simpler, explicit mountain pass (tri() above uses absolute x relative to frame)
def gallery2():
    im=tile("#2E9BE0"); p=im.load()
    def px(x,y,c): p[x,y]=c+(255,)
    x0,y0,w,h=5,6,22,19
    for y in range(h):
        for x in range(w):
            px(x0+x,y0+y,NAVY if (x in(0,w-1) or y in(0,h-1)) else (252,252,252))
    for y in range(2,h-2):
        for x in range(2,w-2): px(x0+x,y0+y,(150,215,255))
    for (dx,dy) in [(1,0),(2,0),(0,1),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(1,3),(2,3)]:
        px(x0+14+dx,y0+3+dy,(255,214,40))
    gr=(52,170,80); dg=(26,104,52)
    ix0,ix1,iy0,iy1=2,w-3,2,h-3
    def tri(cx,top):
        for y in range(top,iy1+1):
            half=y-top
            for x in range(cx-half,cx+half+1):
                if ix0<=x<=ix1: px(x0+x,y0+y,dg if x>cx else gr)
    tri(7,8); tri(14,11)
    # snow cap
    for (x,y) in [(7,8),(6,9),(7,9),(8,9)]: px(x0+x,y0+y,(252,252,252))
    return im
new["com.mitv.gallery"]=gallery2()

# PatchWall: 3x3 patchwork on purple tile
def patchwall():
    im=tile("#4B2E9E"); p=im.load()
    cols=[[(255,210,50),(252,252,252),(255,130,40)],
          [(190,150,255),(255,210,50),(255,100,150)],
          [(255,130,40),(190,150,255),(252,252,252)]]
    for j in range(3):
        for i in range(3):
            c=cols[j][i]; x0=6+i*7; y0=6+j*7
            for y in range(6):
                for x in range(6):
                    cc=c
                    if y==5 or x==5: cc=dark(c,0.7)
                    if (i+j)%2==1 and x+y>=8: cc=cols[(j+1)%3][(i+1)%3]   # corner triangle -> patchwork look
                    p[x0+x,y0+y]=cc+(255,)
    return im
new["com.mitv.tvhome.atv"]=patchwall()

# Mi TV+: orange tile, "TV+" in Press Start 2P
new["com.mitv.tvhome.mitvplus"]=text_tile("#FF6900",["TV+"],8)

# Miracast: pixelarticons "cast" (screen + waves)
new["com.xiaomi.mitv.smartshare"]=brand("#3949AB",pa("cast"),24,th=128)

# Tailscale: 3x3 dot grid (6 solid, 3 dim like the real logo)
def tailscale():
    im=tile("#2B2B36"); p=im.load()
    solid={(0,0),(1,0),(0,1),(1,1),(2,1),(1,2)}
    for j in range(3):
        for i in range(3):
            x0=6+i*7; y0=6+j*7
            c=(252,252,252) if (i,j) in solid else (96,96,120)
            for y in range(5):
                for x in range(5):
                    if (x in(0,4)) and (y in(0,4)): continue
                    p[x0+x,y0+y]=c+(255,)
    return im
new["com.tailscale.ipn"]=tailscale()

# This launcher (gathin tvhome): pixel house
def house():
    im=tile("#E0589A"); p=im.load()
    pal={'O':NAVY+(255,),'R':(214,52,52,255),'r':(140,28,40,255),'W':(252,252,252,255),'w':(200,200,214,255),
         'D':(120,70,40,255),'B':(90,190,255,255),'C':(120,120,140,255)}
    rows=[
"..........OO........",
"..........OCO.......",
"....OOO...OCO.......",
"...OORROOOOCOOO.....",
]
    # build programmatically
    art=Image.new("RGBA",(22,20),(0,0,0,0)); q=art.load()
    def put(x,y,k): q[x,y]=pal[k]
    # roof: triangle rows
    for y in range(9):
        half=y+1
        for x in range(11-half,11+half):
            if 0<=x<22: put(x,y,'O' if (x in(11-half,11+half-1) or y==0) else ('R' if x<11 else 'r'))
    for x in range(22): put(x,9,'O')   # eave line
    # chimney
    for y in range(1,5):
        for x in range(16,19): put(x,y,'O' if (x in(16,18) or y==1) else 'C')
    # walls
    for y in range(10,20):
        for x in range(3,19):
            put(x,y,'O' if (x in(3,18) or y==19) else 'W')
    # door
    for y in range(13,19):
        for x in range(8,13): put(x,y,'O' if (x in(8,12) or y==13) else 'D')
    # window
    for y in range(12,16):
        for x in range(14,17): put(x,y,'O' if (x in(14,16) or y in(12,15)) else 'B')
    put(15,13,'B'); put(15,14,'B')
    for y in range(12,16): put(15,y,'O') if False else None
    im.alpha_composite(art,(5,6))
    return im
new["com.gathin.tvhome"]=house()

for k,v in new.items():
    if os.path.exists(I+k+".png"): print("exists, skip",k); continue
    save(v,I+k+".png")

# ---- UI icons (same recipe as uiicon in build.py)
def uiicon(svg, fill=(252,252,252), line=(0,0,60)):
    m=svg if isinstance(svg,np.ndarray) else mask_from(render(svg,24),128)
    big=np.zeros((G,G),bool); big[4:28,4:28]=m
    ol=big.copy()
    for dy,dx in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
        ol|=np.roll(np.roll(big,dy,0),dx,1)
    im=Image.new("RGBA",(G,G),(0,0,0,0)); p=im.load()
    for y in range(G):
        for x in range(G):
            if big[y,x]: p[x,y]=fill+(255,)
            elif ol[y,x]: p[x,y]=line+(255,)
    return im
def reorder_mask():
    m=np.zeros((24,24),bool)
    def arrow(cx,up):
        for i in range(6):                      # stepped head, 2px per row
            y=(1+i) if up else (22-i)
            m[y,cx-i-0:cx+i+1]=True if False else False
        for i in range(6):
            y=(2+i) if up else (21-i)
            m[y,cx-i:cx+i+1]=True
        for y in (range(8,23) if up else range(1,16)):
            m[y,cx-1:cx+2]=True
    arrow(5,True); arrow(18,False)
    return m
for k,svg in {"reorder":reorder_mask(),"home":pa("home")}.items():
    save(uiicon(svg),U+k+".png")

# ---- contact sheet
import glob
files=sorted(glob.glob(R+"/icons/*.png"))+sorted(glob.glob(R+"/ui/*.png"))
cols=8; cell=160
rows=(len(files)+cols-1)//cols
sh=Image.new("RGB",(cols*cell,rows*cell),(0,0,168))
for i,f in enumerate(files):
    ic=Image.open(f).convert("RGBA"); sh.paste(ic,((i%cols)*cell+16,(i//cols)*cell+16),ic)
sh.save(R+"/_gen/contact.png"); print(len(files))
