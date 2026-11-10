"""Original spatial schematic, in local metres; not an engineering plan."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
OUT=Path(__file__).resolve().parent
im=Image.new('RGB',(1400,1500),'#f5f3ed');d=ImageDraw.Draw(im)
font='C:/Windows/Fonts/msyh.ttc'
def ft(s):return ImageFont.truetype(font,s)
def p(x,y):return 180+x*30,1390-y*27
def rect(x1,y1,x2,y2,fill,outline='#7d8980',width=2):d.rectangle((*p(x1,y2),*p(x2,y1)),fill=fill,outline=outline,width=width)
def label(t,x,y,size=23,fill='#29413d'):
    px,py=p(x,y);w=d.textlength(t,font=ft(size));d.text((px-w/2,py-14),t,font=ft(size),fill=fill)
d.text((55,28),'半园两岸 · 作坊—水巷—家门',font=ft(38),fill='#29413d')
d.text((58,88),'空间候选 v0.1｜尺寸为工作假设；图中上方为作坊岸，下方为生活园',font=ft(23),fill='#62716b')
rect(0,0,28,24,'#e2e7d7')
rect(1,2,7,18,'#c5d1bb');label('生活翼',4,10)
rect(8,2,13,7,'#d0d7c8');label('厨房',10.5,4.5)
rect(10,9,15,16,'#9fc8c8');label('池庭',12.5,12.5)
rect(18,4,27,18,'#d5e3c5');label('种植与休息庭院',22.5,12,21);label('原工坊位置腾空',22.5,10.4,18)
rect(18,18,25,22,'#d9cfb8');label('家庭茶廊',21.5,20,20)
rect(0,24,32,27,'#e8dec7');label('生活园岸 · 连续步道',22,25.6,20)
rect(0,27,32,32,'#9fc8c8');label('水巷 · 暂按约5米',23,29.5,23)
rect(0,32,32,35,'#e8dec7');label('作坊岸 · 连续步道',6,33.5,20)
rect(11.5,27,14,32,'#eee8da');label('桥',12.75,29.4,21)
rect(14,35,28.5,36.5,'#d7c5a6');label('临水门廊',24.5,35.8,19)
rect(14,36.5,28.5,44.5,'#eee1ca',width=3)
rect(14.7,37,18.5,40.4,'#dfcaa8');label('接待',16.6,38.5,20)
rect(20.5,38.7,23,39.8,'#b89f7a');label('修复台',21.75,39.2,17)
rect(23.5,37.0,28,40.5,'#e7e5d5');label('干燥试用区',25.75,39,18)
rect(15,42,27.5,44,'#c7c7b6');label('材料收纳／后勤',21.25,43,20)
rect(28.5,36.5,30,39,'#cdd5cc');label('收件',29.3,37.7,16)
label('作坊 · 约14.5×8米',21,45.3,23)
rect(8.8,23.7,11.4,24.3,'#c48b66');label('园门',10.1,22.8,21)
route=[(10.1,24),(10.1,25.5),(12.75,25.5),(12.75,33.5),(19.5,33.5),(19.5,36.5),(18.9,38.5)]
d.line([p(*v) for v in route],fill='#b4653f',width=6)
for v in [route[0],route[-1]]:
    x,y=p(*v);d.ellipse((x-7,y-7,x+7,y+7),fill='#b4653f')
# Workshop sight line towards the home gate; diagram only, no wall visibility proof.
a,b=p(21.5,41.2),p(10.1,24)
for i in range(0,30,2):
    q=lambda t:(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
    d.line((q(i/30),q((i+1)/30)),fill='#477f8d',width=3)
x,y=a;d.ellipse((x-15,y-15,x+15,y+15),fill='#477f8d')
label('概念图机位',19.3,41.1,18)
d.text((55,1440),'橙实线：家与作坊通路　蓝虚线：望向家门的构图方向　｜　未做人物碰撞或无障碍验证',font=ft(22),fill='#62716b')
im.save(OUT/'两岸空间关系-平面候选.png')
(OUT/'layout-proposal.json').write_text(json.dumps({'status':'proposal','units':'meters','home_site':[0,0,28,24],'canal':[0,27,32,32],'workshop':[14,36.5,28.5,44.5],'bridge':[11.5,27,14,32],'workshop_porch':[14,35,28.5,36.5],'trial':[23.5,37,28,40.5],'home_to_workshop_route':route,'camera':[21.5,41.2,1.6],'look_toward':[10.1,24,1.5],'limitations':['diagrammatic proposal, not adopted dimensions','not a rebuilt 3D scene','imagegen concept is not dimensionally validated']},ensure_ascii=False,indent=2),encoding='utf-8')
print('PLAN_DONE')
