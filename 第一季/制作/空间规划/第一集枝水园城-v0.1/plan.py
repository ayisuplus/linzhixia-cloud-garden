import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(sys.argv[1]);O=R/'视频制作/第一集枝水园城-20261024-v0.1';data=json.loads((O/'design-data.json').read_text('utf8'));old=json.loads((R/'视频制作/第一集池涧水巷-20261024-v0.1/water-design-data.json').read_text('utf8'));font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
im=Image.new('RGB',(1500,1450),'#edf0e7');d=ImageDraw.Draw(im)
d.text((55,30),'一条水脉，向两侧长出水巷、阶池与静水庭',font=font(32),fill='#243d37');d.text((55,83),'v15 枝水园城 · 新增五支回接水系 · 58秒航线保持',font=font(22),fill='#526b60')
def pt(p):return (135+(p[0]+170)*1.15,170+(180-p[1])*1.38)
# Focus on the inhabited region where the new network actually exists.
for z in old['zones']:
 lo=np.array(z['lo'])+z['delta'];hi=np.array(z['hi'])+z['delta']
 if (lo[1]+hi[1])/2>185:continue
 d.polygon([pt(p) for p in [lo,[hi[0],lo[1]],hi,[lo[0],hi[1]]]],fill='#c3cbb9',outline='#98a88f')
water=[np.array(x['banks']) for x in old['actual_water']['samples'] if x['s']>=.41]
d.polygon([pt(x[0]) for x in water]+[pt(x[1]) for x in reversed(water)],fill='#6ba49d')
colors=['#186e6a','#358d85','#22778d','#429795','#276c83'];labels=['东侧邻里阶池水巷','西侧院墙窄涧','水湾东侧静池','水湾西侧回环水巷','下层短桥与跌水']
for bi,(b,c,label) in enumerate(zip(data['branches'],colors,labels)):
 samples=b['samples'];xy=np.array([x['center'] for x in samples]);t=np.gradient(xy,axis=0);t/=np.linalg.norm(t,axis=1)[:,None];n=np.column_stack([-t[:,1],t[:,0]]);w=np.array([x['width'] for x in samples]);left=xy-n*w[:,None]/2;right=xy+n*w[:,None]/2;d.polygon([pt(p) for p in left]+[pt(p) for p in reversed(right)],fill=c)
 p=xy[len(xy)//2];x,y=pt(p);tx=945;ly=[270,380,515,740,910][bi];d.line([(x,y),(tx-80,y),(tx-20,ly)],fill=c,width=2);d.text((tx,ly-14),label,font=font(21),fill='#243d37');d.text((tx,ly+18),f"约{b['length_m']:.0f}m · 落差{b['water_drop_m']:.1f}m",font=font(17),fill='#61766b')
for c in data['crossings']:
 x,y=pt(c['center']);d.rectangle((x-3,y-3,x+3,y+3),fill='#b7824d')
d.text((55,1345),'蓝绿：主水脉与五支水巷　棕色：实际道路交叉处的短桥支承',font=font(21),fill='#29483e')
d.text((55,1390),'按保存工程采样绘制；聚落区局部平面图，高差以文字标注。非水力或施工图。',font=font(18),fill='#61766b');im.save(O/'water-network-plan.png');print('PLAN_READY')
