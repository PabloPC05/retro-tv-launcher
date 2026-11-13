import subprocess, io, os, re
from PIL import Image, ImageDraw, ImageFont
import numpy as np
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL=R+"/_dl"
G=32; S=4  # 32 art px -> 128

def render(svg, size, color="#ffffff"):
    t=open(svg).read()
    t=t.replace('currentColor',color)
    t=re.sub(r'fill="#ffffff"',f'fill="{color}"',t)
    t=t.replace('width="1em" height="1em"','')
    png=subprocess.run(["/opt/homebrew/bin/rsvg-convert","-w",str(size),"-h",str(size),"-a"],input=t.encode(),capture_output=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")

def mask_from(img,th=110):
    a=np.array(img)[:,:,3]
    return a>th

def hexc(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def dark(c,f=0.45): return tuple(int(x*f) for x in c)

def tile(bg, outline=None):
    """32x32 art canvas (array RGBA) with a rounded tile"""
    c=hexc(bg); o=outline or dark(c)
    im=Image.new("RGBA",(G,G),(0,0,0,0)); p=im.load()
    for y in range(G):
        for x in range(G):
            cx=min(x,G-1-x); cy=min(y,G-1-y)
            if cx==0 and cy==0: continue
            if cx==0 or cy==0 or (cx==1 and cy==1): p[x,y]=o+(255,)
            else: p[x,y]=c+(255,)
    # highlight line top-inside (NES shading)
    hl=tuple(min(255,int(v*1.25+30)) for v in c)
    for x in range(3,G-3): p[x,1]=hl+(255,)
    sh=dark(c,0.7)
    for x in range(3,G-3): p[x,G-2]=sh+(255,)
    return im

def stamp(im, mask, color, ox, oy, shadow=None):
    p=im.load()
    h,w=mask.shape
    if shadow:
        for y in range(h):
            for x in range(w):
                if mask[y,x]:
                    X,Y=ox+x+1,oy+y+1
                    if 0<=X<G and 0<=Y<G and p[X,Y][3]: p[X,Y]=shadow+(255,)
    for y in range(h):
        for x in range(w):
            if mask[y,x]:
                X,Y=ox+x,oy+y
                if 0<=X<G and 0<=Y<G: p[X,Y]=color+(255,)

def center(mask):
    ys,xs=np.where(mask); 
    m=mask[ys.min():ys.max()+1, xs.min():xs.max()+1]
    return m

def brand(bg, svg, size=20, color=(255,255,255), th=110):
    im=tile(bg)
    m=center(mask_from(render(svg,size*3 if False else size),th))
    h,w=m.shape
    stamp(im,m,color,(G-w)//2,(G-h)//2,shadow=dark(hexc(bg),0.6))
    return im

def text_tile(bg, lines, fs=8, color=(255,255,255), gap=2, fg_shadow=True):
    im=tile(bg); f=ImageFont.truetype(R+"/pix.ttf",fs)
    # render text to 1-bit mask
    ms=[]
    for ln in lines:
        t=Image.new("L",(fs*len(ln)+2,fs+2),0); ImageDraw.Draw(t).text((0,0),ln,font=f,fill=255)
        a=np.array(t)>127; ms.append(center(a))
    H=sum(m.shape[0] for m in ms)+gap*(len(ms)-1); y=(G-H)//2
    for m in ms:
        h,w=m.shape; stamp(im,m,color,(G-w)//2,y,shadow=dark(hexc(bg),0.6) if fg_shadow else None); y+=h+gap
    return im

def ascii_img(rows, pal):
    h=len(rows); w=max(len(r) for r in rows)
    im=Image.new("RGBA",(w,h),(0,0,0,0)); p=im.load()
    for y,r in enumerate(rows):
        for x,ch in enumerate(r):
            if ch in pal: p[x,y]=pal[ch]+(255,)
    return im

def paste_art(base, art, ox, oy): base.alpha_composite(art,(ox,oy))

def save(im, path, scale=S):
    im.resize((im.width*scale,im.height*scale),Image.NEAREST).save(path)

I=R+"/icons/"
si=lambda s: f"{DL}/si_{s}.svg"
icons={}
icons["com.spotify.tv.android"]=brand("#1DB954",si("spotify"),22)
icons["com.google.android.youtube.tv"]=brand("#E02020",si("youtube"),22)
icons["com.netflix.ninja"]=brand("#B20710",si("netflix"),18)
icons["com.wbd.stream"]=text_tile("#3A22C8",["max"],8)
icons["com.crunchyroll.crunchyroid"]=brand("#F47521",si("crunchyroll"),22)
icons["com.stremio.one"]=brand("#6B4FD8",si("stremio"),22)
icons["com.google.android.youtube.tvmusic"]=brand("#C01818",si("youtubemusic"),22)
# Disney+
icons["com.disney.disneyplus"]=text_tile("#1236B5",["D+"],8)
icons["com.antena3.atresplayer.tv"]=text_tile("#E8412A",["a3"],8)
icons["com.movistarplus.androidtv"]=text_tile("#0A8CE0",["M+"],8)
icons["com.rtve.androidtv"]=text_tile("#C8102E",["RT","VE"],8,gap=2)

# Prime Video
im=tile("#00A8E1"); pp=im.load(); W=(255,255,255,255)
for y in range(15):
    wd=int(min(y,14-y)*1.6)+1
    for x in range(wd): pp[10+x,3+y]=W
pts=[(6,21),(7,22),(8,23)]+[(x,24) for x in range(9,21)]+[(21,23),(22,22),(23,21),(24,20),(23,20),(22,20),(24,19),(24,18)]
for (x,y) in pts:
    pp[x,y]=W
    if (x,y) not in [(24,19),(24,18),(23,20),(22,20)]: pp[x,y+1]=W
icons["com.amazon.amazonvideo.livingroom"]=im

def floppy():
    im=tile("#E8A020"); p=im.load()
    def rect(x0,y0,x1,y1,c):
        for y in range(y0,y1):
            for x in range(x0,x1): p[x,y]=c+(255,)
    rect(5,5,27,27,(0,0,60)); rect(6,6,26,26,(236,236,236))
    rect(6,6,26,8,(236,236,236))
    rect(10,6,22,13,(70,80,110)); rect(17,7,20,12,(236,236,236))
    rect(9,16,23,26,(252,252,252)); rect(9,16,23,17,(200,200,200))
    for yy in (19,21,23): rect(11,yy,21,yy+1,(150,150,170))
    return im
def gear_mask(n=24):
    import math
    m=np.zeros((n,n),bool); c=(n-1)/2
    for y in range(n):
        for x in range(n):
            dx,dy=x-c,y-c; r=math.hypot(dx,dy)
            if r<=7.6: v=True
            elif r<=11.3:
                a=math.atan2(dy,dx)%(math.pi/4); d=min(a,math.pi/4-a)
                v=r*math.sin(d)<=2.3
            else: v=False
            if r<=3.6: v=False
            m[y,x]=v
    return m
# IPTV (tv glyph), USB (floppy), settings (gear), shadowz (skull)
icons["com.nathnetwork.avappnew"]=brand("#00897B",DL+"/pa_tv.svg",24,th=128)
icons["com.xiaomi.mitv.mediaexplorer"]=floppy()
_t=tile("#6C6C7C"); stamp(_t,gear_mask(24),(252,252,252),4,4,shadow=(40,40,60)); icons["com.android.tv.settings"]=_t
icons["com.android.vending"]=None
# Shadowz
icons["com.vodfactory.shadowz.es"]=brand("#A01020",DL+"/pa_skull.svg",24,th=128)

# Google Play: white tile with coloured triangle
def gplay():
    im=tile("#F4F4F4"); 
    m=mask_from(render(si("googleplay"),24),110); m=center(m); h,w=m.shape
    ox,oy=(G-w)//2,(G-h)//2; p=im.load()
    for y in range(h):
        for x in range(w):
            if not m[y,x]: continue
            fx=x/w; fy=(y+.5)/h
            if fx>0.68 and 0.25<fy<0.75: col=(255,208,0)
            elif fx<0.5 and fy<0.5 or (fx<0.5 and False): col=(0,160,255)
            elif fx<0.5: col=(236,46,60)
            elif fy<0.5: col=(0,200,90)
            else: col=(236,46,60) if fx<0.55 else (0,200,90) if False else (255,208,0) if fx>0.6 else (236,46,60)
            p[ox+x,oy+y]=col+(255,)
    return im
icons["com.android.vending"]=gplay()

for k,v in icons.items(): save(v,I+k+".png")

# ---- UI icons
def uiicon(svg, fill=(252,252,252), line=(0,0,60)):
    m=gear_mask(24) if svg=="gear" else mask_from(render(svg,24),128)
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
ui={"apps":"grid-3x3","wifi":"wifi","settings":"gear-solid","paint":"brush","start":"gamepad","clock":"clock"}
for k,v in ui.items(): save(uiicon("gear" if v=="gear-solid" else f"{DL}/pa_{v}.svg"),R+f"/ui/{k}.png")
# cursor: stepped triangle arrow
m=np.zeros((G,G),bool)
for y in range(24):
    half=min(y,23-y)//1
    for x in range(0,half+1): 
        m[4+y, 8+x]=True
        m[4+y, 8+x]=True
ol=m.copy()
for dy,dx in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
    ol|=np.roll(np.roll(m,dy,0),dx,1)
im=Image.new("RGBA",(G,G),(0,0,0,0)); p=im.load()
for y in range(G):
    for x in range(G):
        if m[y,x]: p[x,y]=(252,216,60,255)
        elif ol[y,x]: p[x,y]=(0,0,60,255)
save(im,R+"/ui/cursor.png")

# contact sheet
import glob
files=sorted(glob.glob(R+"/icons/*.png"))+sorted(glob.glob(R+"/ui/*.png"))
cols=7; cell=160
rows=(len(files)+cols-1)//cols
sh=Image.new("RGB",(cols*cell,rows*cell),(0,0,168))
for i,f in enumerate(files):
    ic=Image.open(f).convert("RGBA"); sh.paste(ic,((i%cols)*cell+16,(i//cols)*cell+16),ic)
sh.save(R+"/_gen/contact.png"); print(len(files))
