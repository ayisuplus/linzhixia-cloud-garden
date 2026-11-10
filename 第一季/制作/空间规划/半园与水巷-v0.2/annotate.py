"""Label the authored Blender study renders; no generated reference image edits."""
from pathlib import Path
import json, hashlib
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'视频制作'/'半园与水巷布局-20261014-v0.2'
P=json.loads((OUT/'label-projections.json').read_text(encoding='utf-8'))
FONT='C:/Windows/Fonts/msyh.ttc'
def ft(s):return ImageFont.truetype(FONT,s)
bg='#f3f4f0';ink='#283d3b';sub='#596966'
def sheet(name,title,subtitle):
    im=Image.new('RGB',(1600,1320),bg);im.paste(Image.open(OUT/(name+'.png')).convert('RGB'),(0,135))
    d=ImageDraw.Draw(im);d.text((55,28),title,font=ft(40),fill=ink)
    d.text((57,88),subtitle,font=ft(23),fill=sub)
    d.text((55,1255),'空间讨论稿 v0.2 · 2026-10-14 ｜ 尺度、房间与形体均待审阅；颜色仅区分功能',font=ft(23),fill=sub)
    return im,d
def tag(d,text,x,y,target=None,size=25):
    f=ft(size);b=d.textbbox((0,0),text,font=f);w=b[2]-b[0]+24;h=b[3]-b[1]+18
    x=max(8,min(1592-w,x));y=max(140,min(1225-h,y))
    if target:
        tx,ty=target;ty+=135
        d.line([(tx,ty),(x+w/2,y+h/2)],fill=ink,width=2)
        d.ellipse((tx-4,ty-4,tx+4,ty+4),fill=ink)
    d.rounded_rectangle((x,y,x+w,y+h),radius=5,fill='#fafbf7',outline='#9baba5',width=1)
    d.text((x+12,y+7-b[1]),text,font=f,fill=ink)

im,d=sheet('overview','半园与门外水巷｜三维体块','北入 · 东坊 · 西居 · 中间池庭；家里保持同层，层叠感留给邻里环境')
positions={'门外水巷':(1020,1060),'北侧园门':(1170,730),'接待茶廊':(150,880),'修复工坊':(80,640),'西侧生活翼':(1110,310),'池庭':(600,660),'干燥试用廊':(140,340),'邻里小桥':(1320,890)}
for k,(x,y) in positions.items():tag(d,k,x,y,P['overview'][k])
im.save(OUT/'半园与水巷-三维总览.png')

im,d=sheet('plan','半园与门外水巷｜揭顶平面','上北下南；橙线为来访 / 修复 / 试用，蓝线为进入生活区')
for k,(x,y) in P['plan'].items():
    size=21
    if k.startswith(('06','07','08')):size=19
    f=ft(size);b=d.textbbox((0,0),k,font=f)
    tag(d,k,x-(b[2]-b[0]+24)/2,y+135-20,size=size)
d.text((75,190),'北 ↑',font=ft(28),fill=ink)
d.text((75,960),'院界：暂按 28 × 24 m',font=ft(24),fill=ink)
d.text((75,1000),'沿水步道：约 3 m',font=ft(24),fill=ink)
d.text((75,1040),'试用留空：4.5 × 3.5 m',font=ft(24),fill=ink)
d.text((75,1080),'公共画舫站：巷口方向，未入模',font=ft(22),fill=sub)
# 5m scale consistent with plan orthographic width=64m and image width=1600.
d.line((80,1170,205,1170),fill=ink,width=4)
for x in [80,205]:d.line((x,1163,x,1177),fill=ink,width=3)
d.text((215,1150),'5 m',font=ft(22),fill=ink)
im.save(OUT/'半园与水巷-功能平面.png')

im,d=sheet('cutaway','半园｜去顶观察','来客使用东侧工坊；西侧内门可关闭；厨房、卫浴与卧室由有顶内廊相连')
for k,(x,y) in P['cutaway'].items():
    f=ft(22);b=d.textbbox((0,0),k,font=f)
    tag(d,k,x-(b[2]-b[0]+24)/2,y+135-20,size=22)
im.save(OUT/'半园-去顶观察.png')

files=[]
for p in sorted(OUT.iterdir()):
    if p.suffix in ['.png','.blend','.json'] and p.name!='artifact-manifest.json':
        files.append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(OUT/'artifact-manifest.json').write_text(json.dumps({'status':'spatial proposal; not adopted','generator':'Blender 5.1 + Pillow labels','files':files},ensure_ascii=False,indent=2),encoding='utf-8')
print('Annotated 3 views and wrote artifact manifest.')
