"""Diagrams derived from the saved Blender plan, not concept art or flight validation."""
import json,math,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(sys.argv[1]);O=R/'视频制作/第一集独立园岛-20261024-v0.1';p=json.loads((O/'planning-data.json').read_text('utf8'))
font='C:/Windows/Fonts/msyh.ttc'
def F(n):return ImageFont.truetype(font,n)
ink='#203c38';muted='#5d746d';green='#c6d2b7';water='#178d95';brown='#a66c45';gold='#d3a040';bg='#f4f3eb'
im=Image.new('RGB',(1800,1180),bg);d=ImageDraw.Draw(im)
def txt(xy,t,n=24,fill=ink):d.text(xy,t,font=F(n),fill=fill)
txt((60,35),'长洲 · 独立园岛总图',48);txt((62,103),'v16 空间规划白模  /  七个园居与交通单元，两个局部水系组',25,muted)
def xy(p):return (70+(p[0]+355)*1.44,195+(270-p[1])*1.44)
for i in p['islands']:
 poly=[xy(v) for v in i['outline']];d.polygon(poly,fill=green,outline='#879f80');cx,cy,z=i['center']
 for q in p['courts']:
  if q['island']!=i['id']:continue
  a=math.radians(q['angle']);x,y=q['target_center'];corners=[xy((x+dx*math.cos(a)-dy*math.sin(a),y+dx*math.sin(a)+dy*math.cos(a))) for dx,dy in [(-18.5,-18.5),(18.5,-18.5),(18.5,18.5),(-18.5,18.5)]];d.polygon(corners,fill='#ede6d3',outline='#667e72')
for l in p['links']:
 pts=[xy(v) for v in l['points']];d.line(pts,fill=brown,width=5)
 x,y=xy(l['tower_geometry']['xy']);d.rectangle([x-7,y-7,x+7,y+7],fill=brown)
for w in p['water']:
 a=xy(w['source_pool']);b=xy(w['fall_xy']);d.line([a,b],fill=water,width=8)
 for x,y in [a,b]:d.ellipse([x-10,y-10,x+10,y+10],fill=water)
 txt((b[0]+12,b[1]+2),f"↓{w['fall_height_m']:.0f}m",20,water)
route=[xy(v) for v in p['route_envelope']]
for a,b in zip(route,route[1:]):
 dist=math.dist(a,b);n=max(1,int(dist/13))
 for k in range(n):
  if k%2==0:
   u=k/n;v=(k+1)/n;d.line([(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u),(a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v)],fill=gold,width=3)
offset={'A':(-52,-74),'B':(-50,54),'C':(-32,62),'D':(-58,-72),'E':(-50,43),'F':(-50,59),'G':(-20,-72)}
for i in p['islands']:
 x,y=xy(i['center']);dx,dy=offset[i['id']];txt((x+dx,y+dy),i['id']+' '+i['name'],23);txt((x+dx,y+dy+32),f"园面 +{i['center'][2]} m",18,muted)
# Separate sidebar keeps text outside the actual topography.
d.line([(1250,180),(1250,1030)],fill='#c2cdc1',width=2)
txt((1290,195),'空间组织',30)
for y,title,lines in [(255,'① 学园叠水组',['A → B → C：两级落水','主体错位，局部边缘搭接']),
 (390,'② 半园—作坊组',['F → G：窄水庭与短瀑','保留隔水相望的生活关系']),
 (525,'③ 云间通路',['B—C—E—D—B 构成回路','桥接楼亭，楼梯与升降井换层']),
 (660,'④ 新飞行逻辑',['出园 → 越隙 → 穿云 → 换层','58 秒仅为预算，旧轨迹退出'])]:
 txt((1290,y),title,25)
 for j,line in enumerate(lines):txt((1290,y+43+j*34),line,21,muted)
txt((75,970),'青绿：局部水路与跌水　　赭色：步行桥廊　　金色虚线：飞行走廊草案',24)
txt((75,1018),'园内方框为复用院落占位；岛屿投影可局部重叠，真实分离需结合高程关系图。',23,muted)
txt((75,1060),'没有贯穿全城的大江或连续陆地；本图是第一集沿线样段，不是全城建设总规。',23,muted)
im.save(O/'masterplan.png')

im=Image.new('RGB',(1800,1030),bg);d=ImageDraw.Draw(im)
txt((60,35),'园岛高差与跨云连接',46);txt((60,101),'沿东西方向的正投影关系示意；不是同一条直线剖切，前后位置请对照总图。',24,muted)
def sec(x,z):return (70+(x+355)*2.05,820-z*4.3)
for z in [0,32,48,66,82,104,126,150]:
 y=sec(0,z)[1];d.line([(50,y),(1720,y)],fill='#dce2d8',width=1);txt((10,y-23),str(z),17,muted)
for i in p['islands']:
 x,y,z=i['center'];xmin=min(v[0] for v in i['outline']);xmax=max(v[0] for v in i['outline']);dep=i['depth']
 points=[sec(xmin,z),sec(xmax,z),sec(x+(xmax-x)*.86,z-dep*.5),sec(x+(xmax-x)*.53,z-dep*.86),sec(x,z-dep),sec(x+(xmin-x)*.53,z-dep*.86),sec(x+(xmin-x)*.86,z-dep*.5)]
 d.polygon(points,fill='#d1e0df',outline='#8bafac');d.line([sec(xmin,z),sec(xmax,z)],fill='#789577',width=6)
 sx,sy=sec(x,z);txt((sx-45,sy-45),f"{i['id']}  +{z}m",23)
for l in p['links']:
 d.line([sec(v[0],v[2]) for v in l['points']],fill=brown,width=3);t=l['tower_geometry'];x=t['xy'][0];d.line([sec(x,t['lower_z']),sec(x,t['upper_z'])],fill=brown,width=5)
for w in p['water']:
 x=w['fall_xy'][0];d.line([sec(x,w['source_z']),sec(x,w['catch_z'])],fill=water,width=7);sx,sy=sec(x,(w['source_z']+w['catch_z'])/2);txt((sx-100 if w['id']=='W3' else sx+10,sy+32 if w['id']=='W3' else sy),str(int(w['fall_height_m']))+'m 跌水',20,water)
txt((75,885),'水只在局部园岛之间下降；桥廊可同高接入下一园楼亭，再由楼梯或升降设施换层。',24)
txt((75,933),'尺寸均为本轮创作推定。楼亭及云质承托为机制白模，尚未完成建筑美术与运营设计。',23,muted)
im.save(O/'height-and-connections.png')
print('DIAGRAMS_READY')
