"""Editable SVG and matching PNG: original schematic floor plan, not image editing."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from html import escape
import math

OUT=Path(__file__).resolve().parent
W,H=1800,1630
PAPER='#f7f5ed'; INK='#354d48'; MUTED='#748079'; WALL='#4b5751'
HOUSE='#e9ddc9'; PRIVATE='#dfded2'; WALK='#eeeadc'; WATER='#c7e2de'; GREEN='#d8e3cc'
S=36; OX,OY=150,455
FONT='C:/Windows/Fonts/msyh.ttc'; BOLD='C:/Windows/Fonts/msyhbd.ttc'

def render(routes=False):
    im=Image.new('RGB',(W,H),PAPER); d=ImageDraw.Draw(im)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="100%" height="100%" fill="{PAPER}"/>']
    def line(points,fill=INK,width=2,dash=False):
        points=[(round(x,2),round(y,2)) for x,y in points]
        if dash:
            for a,b in zip(points,points[1:]):
                length=math.dist(a,b)
                for t in range(0,int(length),15):
                    end=min(t+8,length)
                    d.line([(a[0]+(b[0]-a[0])*q/length,a[1]+(b[1]-a[1])*q/length) for q in [t,end]],fill=fill,width=width)
        else:d.line(points,fill=fill,width=width,joint='curve')
        ps=' '.join(f'{x},{y}' for x,y in points)
        svg.append(f'<polyline points="{ps}" fill="none" stroke="{fill}" stroke-width="{width}"'+(' stroke-dasharray="8 7"' if dash else '')+'/>')
    def rect(x,y,w,h,fill,stroke=None,sw=2):
        d.rectangle((x,y,x+w,y+h),fill=fill,outline=stroke,width=sw)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
    def poly(points,fill,stroke=INK,sw=2):
        d.polygon(points,fill=fill)
        if stroke: d.line(points+[points[0]],fill=stroke,width=sw,joint='curve')
        ps=' '.join(f'{x},{y}' for x,y in points)
        svg.append(f'<polygon points="{ps}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
    def circle(x,y,r,fill,stroke=None,sw=2):
        d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=sw)
        svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
    def text(x,y,value,size=24,fill=INK,bold=False,anchor='mm'):
        font=ImageFont.truetype(BOLD if bold else FONT,size)
        d.text((x,y),value,font=font,fill=fill,anchor=anchor)
        align={'mm':'middle','lm':'start','rm':'end'}[anchor]
        svg.append(f'<text x="{x}" y="{y}" text-anchor="{align}" dominant-baseline="central" font-family="Microsoft YaHei, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}">{escape(value)}</text>')
    def p(x,y):return OX+x*S,OY+y*S
    def r(x,y,w,h,fill,stroke=None,sw=2):rect(*p(x,y),w*S,h*S,fill,stroke,sw)
    def l(points,fill=INK,width=2,dash=False):line([p(*v) for v in points],fill,width,dash)
    def t(x,y,s,size=24,fill=INK,bold=False):text(*p(x,y),s,size,fill,bold)
    def room(x,y,w,h,fill=HOUSE):r(x,y,w,h,fill,WALL,5)
    def gap(a,b,fill=HOUSE):l([a,b],fill,9)
    def window(a,b):l([a,b],'#739b9b',7); l([a,b],PAPER,2)
    def tree(x,y,radius=1.2):
        xx,yy=p(x,y); rr=radius*S
        for dx,dy in [(-.30,0),(.27,-.1),(0,.24),(0,-.26)]:circle(xx+dx*rr,yy+dy*rr,rr*.7,GREEN,'#a8b899',1)
        circle(xx,yy,4,'#829771')
    def badge(x,y,s,color=INK):circle(*p(x,y),17,color);t(x,y,s,19,'#ffffff',True)
    def arrow(points,color,width=4,dash=False):
        coords=[p(*v) for v in points];line(coords,color,width,dash)
        a,b=coords[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);rr=13
        poly([b,(b[0]-rr*math.cos(ang-.45),b[1]-rr*math.sin(ang-.45)),(b[0]-rr*math.cos(ang+.45),b[1]-rr*math.sin(ang+.45))],color,None)

    text(85,62,'半园',52,bold=True,anchor='lm')
    text(222,70,'生活在园中，手艺在窗边',28,anchor='lm')
    text(85,120,'平面讨论稿 01  /  北入 · 东坊 · 西南居 · 池庭相连',25,MUTED,anchor='lm')
    text(85,161,'建议尺度 28 × 24 m（约 672㎡） · 单层 · 剖切示意，不是施工图',23,MUTED,anchor='lm')
    for x,col,lab in [(85,HOUSE,'接待 / 工作'),(330,PRIVATE,'居住 / 生活'),(575,WALK,'有顶廊'),(770,WATER,'水'),(900,GREEN,'植栽')]:
        rect(x,200,24,24,col,INK,1);text(x+36,212,lab,22,anchor='lm')
    text(85,259,'动线叠加版' if routes else '功能与空间版',25,bold=True,anchor='lm')
    # North arrow and top-level dimensions.
    line([(1165,207),(1165,135)],INK,3);poly([(1165,126),(1155,149),(1175,149)],INK,None)
    text(1165,106,'北 N',23)
    line([p(0,-4.35),p(28,-4.35)],MUTED,1)
    for x in [0,28]: l([(x,-4.6),(x,-4.1)],MUTED,2)
    t(22,-4.95,'28 m  /  暂定',21,MUTED)
    line([p(-1.15,0),p(-1.15,24)],MUTED,1)
    for y in [0,24]:l([(-1.4,y),(-.9,y)],MUTED,2)
    t(-1.15,12,'24m',20,MUTED)

    # External setting is contextual, not part of the 28×24m site.
    r(0,-3.7,28,1.25,WATER)
    t(21,-3.1,'北侧水巷（外部环境）',23)
    r(0,-2.45,28,2.45,'#e8e6dc')
    t(4,-1.1,'沿水步道',21,MUTED)
    r(11.2,-3.15,4,2.7,'#ded2bd',INK,2)
    circle(*p(13.2,-1.8),26,PAPER,'#869a93',2);t(13.2,-1.8,'D',23)
    t(15.9,-2.6,'门外收件台',20)
    r(15.2,-.9,2.1,.9,WALK)

    r(0,0,28,24,'#f0eee3',WALL,7)
    gap((7.2,0),(9.2,0),WALK)
    # Front court and east covered spine.
    r(1.3,1.1,12.2,5.3,'#e7e9db')
    r(6.6,0,3.2,4.1,WALK)
    r(9.6,4.1,10.4,3.4,WALK)
    r(18.2,6.5,1.8,13,WALK)
    for y in [7.2,10.2,13.2,16.2,19]:circle(*p(18.05,y),4,WALL)
    l([(18.2,6.5),(18.2,19.5)],'#c6bcaa',1,True)
    r(6.5,4.4,3.8,.3,WALL)
    t(8.35,5.25,'照壁',21)
    tree(3.3,3.2,1.2);tree(11.9,2.5,.85)
    t(6.8,2.3,'入园前庭',24,bold=True)
    t(8.2,.7,'门',20)
    # Reception, materials, workshop and an adaptable covered testing bay.
    room(14.5,2,5,4.5); t(17,3.45,'接待茶廊',25,bold=True)
    r(15.25,4.25,1.4,.7,'#c7b597',INK,1)
    for xx in [15.4,16.4]:circle(*p(xx,5.4),8,'#b5a286')
    gap((15.1,6.5),(18.3,6.5),WALK)
    room(21.5,2,5,4.5);t(24,3.2,'工具材料间',23,bold=True)
    r(22,4.3,4,1.1,'#c9bda5',INK,1); t(24,4.85,'分类柜',19)
    room(20,6.5,6.5,8);t(23.2,7.7,'修复工作室',26,bold=True)
    gap((23,6.5),(24.5,6.5));window((21.6,2),(24,2))
    gap((20,8.3),(20,10),WALK)
    l([(20.2,8.3),(20.2,9.1)],'#869b91',2)
    window((20,10.8),(20,13.5));window((26.5,8.5),(26.5,12.5))
    r(21.9,10.2,1.4,2.8,'#baa17b',INK,2);t(24.1,11.5,'主工作台',20)
    circle(*p(24,10.7),10,'#ad9779',INK,1)
    r(25,13.1,1,.8,'#c9ddd8',INK,1);t(23.3,13.6,'清洁 / 辅助检测',19)
    room(20,14.5,6.5,5,'#e8e3d5');gap((22.2,14.5),(24.5,14.5),WALK)
    gap((20,16),(20,18),WALK)
    r(21,15.25,4.5,3.5,PAPER)
    l([(21,15.25),(25.5,15.25),(25.5,18.75),(21,18.75),(21,15.25)],'#a7997f',2,True)
    t(23.25,16.15,'多用试用廊',24,bold=True)
    t(23.25,17.2,'净空约 4.5 × 3.5 m',19)
    t(23.25,18.15,'平整 · 干燥 · 无杂物',18,MUTED)
    # Garden pond: irregular edge, not a symbolically forced semicircle.
    pond=[(10,8.4),(14.8,7.8),(17.2,9.4),(17,13.5),(15.5,15.2),(11.5,14.7),(10,12.4)]
    poly([p(*v) for v in pond],WATER,'#82aaa4',3)
    for x,y in [(12,9.4),(13.5,12.8),(12.2,13.4)]:l([(x,y),(x+.7,y),(x+1,y+.08)],'#97bfba',2)
    t(13.55,10.6,'小池',28,bold=True)
    t(13.6,11.7,'坐廊与工作窗互相借景',18,MUTED)
    r(9,16.5,8,2,WALK);t(13,17.45,'临水坐廊',24,bold=True)
    r(10,16.6,3,.35,'#bca780')
    tree(16.8,6.9,.6);tree(16.9,15.7,.6)
    # Quiet west garden, screened private passage, and optional old-object room.
    r(6,7.4,2.8,11.1,WALK)
    l([(1.4,7.1),(7.1,7.1)],WALL,4);l([(9.2,7.1),(10.1,7.1)],WALL,4)
    l([(7.1,7.1),(7.1,8.3)],'#869b91',3)
    t(8.2,7.65,'可闭内门',17)
    tree(3.7,7.4,1.4)
    room(1.5,9,4.5,4.5,PRIVATE);t(3.75,10.2,'旧物藏间',23,bold=True)
    t(3.75,11.15,'兼弹性空间',19,MUTED)
    r(1.9,12,2.9,.85,'#c0bdad',INK,1)
    gap((6,11.8),(6,13),WALK);window((1.5,9.6),(1.5,11))
    room(1.5,14,4.5,3,PRIVATE);t(3.6,15.15,'卫浴 / 洗衣',21,bold=True)
    gap((6,14.8),(6,16),WALK)
    r(1.85,15.8,1.2,.8,'#bfd0ca',INK,1)
    r(3.5,17,5.3,1.5,WALK)
    # Southern living bar: three rooms with explicit openings and a south light strip.
    room(1.5,18.5,4.5,4,PRIVATE);room(6,18.5,6.5,4,PRIVATE);room(12.5,18.5,4.5,4,PRIVATE)
    gap((3.7,18.5),(5.1,18.5),WALK)
    gap((9.2,18.5),(11,18.5),WALK)
    gap((13.7,18.5),(15,18.5),WALK)
    gap((6,19.5),(6,20.6),PRIVATE);gap((12.5,19.5),(12.5,21),PRIVATE)
    t(3.8,19.55,'知夏卧室',23,bold=True)
    r(2,20.3,2.1,1.5,'#c3bca9',INK,1);r(2.1,20.4,.5,1.3,PAPER)
    t(9.3,19.7,'起居 / 读写',24,bold=True)
    r(7,20.4,3.2,.7,'#c2b8a2',INK,1);r(9.5,21.4,1.5,.55,'#c2b8a2',INK,1)
    t(14.7,19.7,'厨房 / 餐叙',22,bold=True)
    r(13,21.1,3.3,.8,'#bebba9',INK,1)
    for xa,xb in [(2,4.5),(7,10.7),(13,15.8)]:window((xa,22.5),(xb,22.5))
    t(10,23.3,'南侧采光与维护带',20,MUTED)
    # Garden maintenance remains off the clear public circulation spine.
    r(17,19.5,9.5,3,'#e0e5d6')
    tree(18.7,21.5,.75);tree(23.7,21.8,.85)
    r(25.4,20.4,1.1,1.6,'#c6d9d6',INK,2)
    t(21.1,20.9,'院务维护角',20)
    # Numbered spatial anchors, not technology decisions.
    for x,y,s in [(10.3,.8,'1'),(14.8,2.45,'2'),(20.5,7.15,'3'),(20.5,15.05,'4'),(9.7,16.8,'5'),(6.5,19,'6')]:badge(x,y,s)
    if routes:
        arrow([(8.2,-1.7),(8.2,3.4),(11,3.4),(11,6.9),(18.9,6.9),(18.9,9),(21.3,9)],'#bb7351',5)
        arrow([(18.9,9),(18.9,16.9),(20.6,16.9)],'#bb7351',5)
        arrow([(7,3.4),(5.8,3.4),(5.8,5.6),(8.1,5.6),(8.1,17.8),(10,17.8),(10,20)],'#637b9c',4,True)
        text(88,1480,'橙线：来访 / 修复 / 试穿    蓝虚线：生活内院动线',25,anchor='lm')
    else:
        text(88,1480,'开口为门；青色双线为窗。浅色廊道有顶；树冠为示意投影。',24,anchor='lm')
    # Editorial notes panel.
    rect(1240,282,480,1110,'#eeece2')
    text(1270,324,'这张图先决定什么',29,bold=True,anchor='lm')
    notes=[('01  入园与收件',['门外取件，照壁后向东接待。','工作、生活在这里分流。']),
           ('02  接待茶廊',['坐下说清旧物的来历与需求，','也能等候、闲聊、看庭院。']),
           ('03  修复工作室',['工具材料间靠近主工作台，','桌边、门口、隔池都能取景。']),
           ('04  多用试用廊',['平整干燥，与水边分开；','首集试穿，以后用于物件试用。']),
           ('05  临水坐廊',['连接起居与池庭，留下休息、','读书、聊天和安静相处的位置。']),
           ('06  生活内院',['卧室、起居、厨房和卫浴，','以可关闭内门保留私密。'])]
    yy=393
    for title,rows in notes:
        text(1270,yy,title,25,bold=True,anchor='lm')
        for j,row in enumerate(rows):text(1270,yy+39+j*34,row,22,MUTED,anchor='lm')
        yy+=136
    text(1270,1235,'科技候选：配送、检测、环境调节。',21,MUTED,anchor='lm')
    text(1270,1280,'所有新增房间与尺寸均为提案',22,bold=True,anchor='lm')
    text(1270,1320,'先讨论平面，再定科技表达。',21,MUTED,anchor='lm')
    # Scale and final labels.
    for i in range(5):rect(OX+i*S,1383,S,9,INK if i%2==0 else PAPER,INK,1)
    text(OX,1415,'0',20,anchor='lm');text(OX+5*S,1415,'5 m',20,anchor='rm')
    text(540,1408,'图面按米等比例绘制；屏幕显示比例不固定。',21,MUTED,anchor='lm')
    text(88,1540,'半园平面 v0.1  ·  2026-10-10  ·  先讨论空间，再讨论古典园林与科技如何融合',23,MUTED,anchor='lm')
    text(88,1580,'既有设定：半旧小园 / 半园半坊、半居半店 / 小池、草木、修了一半的旧物。',21,MUTED,anchor='lm')
    svg.append('</svg>')
    name='半园-动线讨论图-v0.1' if routes else '半园-功能平面图-v0.1'
    (OUT/(name+'.svg')).write_text('\n'.join(svg),encoding='utf-8')
    im.save(OUT/(name+'.png'))
    print(OUT/(name+'.png'))

render(False)
render(True)
