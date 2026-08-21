from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W=1000
im=Image.new('RGBA',(W,W),(0,0,0,0))
d=ImageDraw.Draw(im)
G=(214,159,55,255); GH=(255,218,126,255); WHITE=(232,234,238,255); SH=(160,165,174,255); RED=(126,18,20,255)

def font(size,bold=False):
    paths=[r'C:\Windows\Fonts\segoeuib.ttf' if bold else r'C:\Windows\Fonts\segoeui.ttf',r'C:\Windows\Fonts\arial.ttf']
    for p in paths:
        try:return ImageFont.truetype(p,size)
        except:pass
    return ImageFont.load_default()

def gold_circle(cx,cy,r):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(115,70,18,255),outline=GH,width=8)
    d.ellipse((cx-r+16,cy-r+16,cx+r-16,cy+r-16),fill=(218,155,53,255),outline=(248,205,112,255),width=5)

# backpack
d.rounded_rectangle((590,260,735,570),38,fill=(130,90,34,255),outline=GH,width=8)
# legs
d.polygon([(410,580),(520,575),(510,795),(430,870),(370,810)],fill=WHITE)
d.polygon([(530,575),(640,570),(710,795),(650,870),(560,795)],fill=WHITE)
for box in [(370,780,515,875),(605,770,755,875)]: d.rounded_rectangle(box,42,fill=SH,outline=G,width=8)
# torso
d.ellipse((300,300,690,690),fill=WHITE,outline=G,width=9)
d.ellipse((330,330,660,650),fill=(246,247,248,255))
# arms
d.line((340,410,190,590),fill=WHITE,width=95); d.line((340,410,190,590),fill=G,width=8)
gold_circle(160,625,52)
d.line((650,405,835,530),fill=WHITE,width=110); d.line((650,405,835,530),fill=G,width=9)
gold_circle(880,558,58)
for dx,dy in [(45,-24),(52,-7),(48,15),(32,34)]: d.line((886,558,886+dx,558+dy),fill=GH,width=14)
# neck ring
d.ellipse((365,275,615,385),fill=(100,66,22,255),outline=GH,width=9)
# helmet shell
d.ellipse((280,75,705,420),fill=(234,236,239,255),outline=G,width=10)
# integrated bear ears
gold_circle(350,110,84); gold_circle(625,105,84)
d.ellipse((305,150,680,385),fill=(91,57,12,255),outline=GH,width=10)
d.ellipse((325,165,660,365),fill=(186,125,32,255))
d.ellipse((355,180,620,315),fill=(231,183,76,120))
# bear muzzle/nose
d.ellipse((450,300,525,340),fill=(212,147,43,255),outline=GH,width=3)
d.ellipse((466,307,512,327),fill=(255,220,130,255))
# chest plate
d.rounded_rectangle((390,455,630,610),18,fill=RED,outline=GH,width=7)
fb=font(54,True); fs=font(21,True)
for text,y,f in [('BALI',478,fb),('NIGHTCLUB',548,fs)]:
    bb=d.textbbox((0,0),text,font=f); tw=bb[2]-bb[0]; d.text((510-tw/2,y),text,font=f,fill='white')
# shoulder patch
d.rounded_rectangle((650,360,740,410),9,fill=RED,outline=GH,width=4)
f=font(20,True); d.text((662,371),'BALI',font=f,fill='white')
# seams and gold rings
for y in (700,760): d.arc((395,y-38,650,y+45),5,175,fill=G,width=6)
# highlight on visor
d.ellipse((370,170,555,225),fill=(255,255,255,38))

Path('assets').mkdir(exist_ok=True)
im.save('assets/bali_astronaut.png')
print('generated assets/bali_astronaut.png')
