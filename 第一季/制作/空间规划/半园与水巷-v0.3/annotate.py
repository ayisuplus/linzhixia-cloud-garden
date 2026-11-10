"""Add captions to original local Blender renders and inventory the artifacts."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw, ImageFont
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'视频制作'/'半园与水巷布局-20261014-v0.3'
FONT='C:/Windows/Fonts/msyh.ttc'
def ft(size):return ImageFont.truetype(FONT,size)
bg='#f4f3ee';ink='#29413d';sub='#62716b'
specs=[
('01_lane','01 水巷望园门','沿水步道连续通过；园门与墙洞分别提供进入、窥见的关系。','视角01-水巷望园门.png'),
('02_entry','02 转过入口，看见池庭','树池与转廊形成前景；池水、对面的生活翼随后展开。','视角02-进门见池庭.png'),
('03_workshop','03 从修复台望向院外','近处工作台，中间池庭与廊柱，右侧门边借到水巷的一角。','视角03-工坊望院外.png'),
('04_overview','半园与水巷 · 空间调整 v0.3','缩小茶廊、增加入口树池与临池停留处，打开工坊面向庭院的一侧。','半园与水巷-总览v0.3.png'),
('05_plan','半园与水巷 · 动线与机位','橙：来访与试用　蓝：回家　绿：巷道通行　01—03：三个实际相机位置','半园与水巷-动线机位图.png'),
]
for raw,title,desc,file in specs:
    im=Image.new('RGB',(1600,1210),bg)
    im.paste(Image.open(OUT/(raw+'.png')).convert('RGB'),(0,130))
    d=ImageDraw.Draw(im)
    d.text((45,25),title,font=ft(35),fill=ink)
    d.text((47,80),desc,font=ft(23),fill=sub)
    d.text((45,1156),'空间草模 / 待讨论 · 同一模型实拍渲染 · 材质、植物与光照均为示意',font=ft(23),fill=sub)
    if raw=='05_plan':
        def xy(x,y):return (800+(x-14)*1600/61,630+(17-y)*1600/61)
        for label,x,y in [('园门',10.1,23.7),('茶廊',21.4,21.1),('工坊',24,15.4),('起居',3.8,15.2),('卧室',3.8,4),('卫浴',3.8,8.5),('厨房',11.2,4),('池庭',12.4,12),('试用廊',16.2,4),('内门',8.2,18.6)]:
            px,py=xy(x,y);w=d.textlength(label,font=ft(22))
            d.rounded_rectangle((px-w/2-8,py-17,px+w/2+8,py+17),radius=4,fill=bg)
            d.text((px-w/2,py-15),label,font=ft(22),fill=ink)
        for label,px,py,tx,ty in [('01',17.5,33,10.4,23.7),('02',14.6,21.5,12.7,11.2),('03',23.8,10.5,12,18.5)]:
            a=xy(px,py);b=xy(tx,ty)
            dx,dy=b[0]-a[0],b[1]-a[1];length=(dx*dx+dy*dy)**.5
            end=(a[0]+dx/length*65,a[1]+dy/length*65)
            d.line((a,end),fill='#9d4e30',width=4)
            d.ellipse((a[0]-21,a[1]-21,a[0]+21,a[1]+21),fill='#9d4e30')
            d.text((a[0]-15,a[1]-15),label,font=ft(23),fill='white')
    im.save(OUT/file)
files=[]
for p in sorted(OUT.iterdir()):
    if p.suffix in ['.png','.blend','.json'] and p.name!='artifact-manifest.json':
        files.append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
base=HERE.parent/'半园与水巷-v0.2/build_layout.py'
(OUT/'artifact-manifest.json').write_text(json.dumps({'status':'proposal, not adopted','source':'original local Blender geometry','base_script':str(base.relative_to(ROOT)),'base_script_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'files':files},ensure_ascii=False,indent=2),encoding='utf-8')
print('CAPTIONED',len(specs),'INVENTORY',len(files))
