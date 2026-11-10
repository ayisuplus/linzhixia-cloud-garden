import sys,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(sys.argv[1]);O=R/'视频制作/第一集云山园巷-20261024-v0.1';SRC=R/'视频制作/第一集池涧水巷-20261024-v0.1'
old=json.loads((SRC/'water-design-data.json').read_text('utf8'));new=json.loads((O/'design-data.json').read_text('utf8'))
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
im=Image.new('RGB',(1600,1550),'#edf0e7');dr=ImageDraw.Draw(im)
dr.text((55,25),'云山保留，沿河长廊变成分段展开的园居',font=font(32),fill='#243d37')
dr.text((55,78),'同一座城 · 同一水脉 · 新的58秒观看路径',font=font(22),fill='#4b655b')
def pt(p,k):return(k*790+65+(p[0]+370)*.62,210+(850-p[1])*.74)
for k,folder in enumerate([SRC,O]):
 dr.rounded_rectangle((k*790+30,125,k*790+775,1460),18,fill='#e2e7dc');dr.text((k*790+55,140),'v13 沿水脉观看' if k==0 else 'v14 园院—山肩—屋脊—水湾',font=font(25),fill='#294039')
 for z in old['zones']:
  if z['id'].startswith(('H1','H2','H3')):continue
  lo=np.array(z['lo'])+z['delta'];hi=np.array(z['hi'])+z['delta'];dr.polygon([pt(p,k) for p in [lo,[hi[0],lo[1]],hi,[lo[0],hi[1]]]],fill='#b6beac',outline='#95a18e')
 water=[np.array(x['banks']) for x in old['actual_water']['samples']];dr.polygon([pt(x[0],k) for x in water]+[pt(x[1],k) for x in reversed(water)],fill='#458f88')
 ps=json.loads((folder/'route-poses.json').read_text('utf8'));dr.line([pt(p['position'],k) for p in ps],fill='#be6848',width=3)
 if k:
  for g in new['gardens']:
   x,y=pt(g['center'],k);dr.rectangle((x-12,y-10,x+12,y+10),fill='#d3ae6f',outline='#8c7444')
  for j,(time,title) in enumerate([(7,'离水入园'),(12,'树石山肩'),(19,'隐水庭园'),(27,'邻里屋脊'),(37.5,'公共水湾'),(44,'穿过街巷'),(56.5,'作坊收件')]):
   x,y=pt(ps[round(time*24)]['position'],k);tx=k*790+530;dr.ellipse((x-4,y-4,x+4,y+4),fill='#be6848');dr.line((x,y,tx-12,y),fill='#8d9989');dr.text((tx,y-13),title,font=font(19),fill='#294039')
 dr.text((k*790+55,1390),'蓝绿：连续水系　赭红：实际相机航线',font=font(20),fill='#294039')
dr.text((55,1490),'建筑范围与路线来自工程数据；高差和云雾未画入。创作布局示意，不是施工总图。',font=font(19),fill='#627469');im.save(O/'layout-route-comparison.png')
print('PLAN_READY')
