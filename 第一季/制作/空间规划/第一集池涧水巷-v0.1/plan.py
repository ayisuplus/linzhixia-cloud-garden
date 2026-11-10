import sys,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(sys.argv[1]);D=Path(__file__).parent;sys.path.insert(0,str(D));import water_layout as W
L=W.L;O=R/'视频制作/第一集池涧水巷-20261024-v0.1';data=json.loads((O/'water-design-data.json').read_text('utf8'))
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
im=Image.new('RGB',(1600,1550),'#edf0e7');draw=ImageDraw.Draw(im)
draw.text((60,25),'从宽河主导，改为池、涧、水巷与一处公共湾',font=font(32),fill='#243d37')
draw.text((60,80),'同一城市跨度 · 建筑单体保持尺寸 · 58秒参考航程',font=font(21),fill='#4b655b')
def pt(p,k):return (k*790+65+(p[0]+370)*.62,210+(850-p[1])*.74)
old=[np.array([L.point(s,-L.width(s,-1))[:2],L.point(s,L.width(s,1))[:2]]) for s in np.linspace(0,1,201)]
houses=json.loads((R/'视频制作/第一集云山聚落-20261024-v0.1/landscape-data.json').read_text('utf8'))['houses']
new=[np.array(x['banks'])[:,:2] for x in data['actual_water']['samples']]
for k,water in enumerate([old,new]):
 draw.rounded_rectangle((k*790+30,125,k*790+775,1460),18,fill='#e2e7dc')
 draw.text((k*790+55,140),'v12 连续宽水面' if k==0 else 'v13 池涧与水巷',font=font(26),fill='#294039')
 for z in data['zones']:
  if z['id'].startswith(('H1','H2','H3')):continue
  lo=np.array(z['lo']);hi=np.array(z['hi']);d=np.zeros(2) if k==0 else np.array(z['delta']);corners=[lo, [hi[0],lo[1]],hi,[lo[0],hi[1]]];draw.polygon([pt(np.array(c)+d,k) for c in corners],fill='#afb6a2',outline='#899c8b')
 for h in houses:
  center=np.array(h['center']);t,n=L.basis(h['s']);delta=np.zeros(2) if k==0 else np.array(data['rigid_groups'][h['id'][:2]+' whole mountain access group']['delta']);corners=[center+delta+t*x+n*y for x,y in [(-h['length']/2,-6),(h['length']/2,-6),(h['length']/2,6),(-h['length']/2,6)]];draw.polygon([pt(p,k) for p in corners],fill='#afb6a2',outline='#899c8b')
 polygon=[pt(w[0],k) for w in water]+[pt(w[1],k) for w in reversed(water)];draw.polygon(polygon,fill='#458f88')
 for st,label in [(.065,'校园庭池'),(.28,'山间窄涧'),(.48,'聚落水巷'),(.635,'公共水湾'),(.87,'作坊水巷')]:
  pos=L.point(st,0)[:2];x,y=pt(pos,k);draw.ellipse((x-4,y-4,x+4,y+4),fill='#bb7b43');tx=k*790+520;draw.line((x,y,tx-10,y),fill='#718273',width=1);draw.text((tx,y-14),label,font=font(19),fill='#294039')
 draw.text((k*790+55,1400),'水面最宽约104米' if k==0 else '水面最宽约34米；谷涧约4.5—7.5米',font=font(21),fill='#294039')
draw.text((60,1490),'按工程平面投影绘制；建筑以保护范围示意，非建筑施工总图。云雾与高差未画入。',font=font(19),fill='#627469');im.save(O/'water-layout-comparison.png')
actual=data['actual_water'];report={'source':'saved Blender water cross-sections; projected main water only, courtyard pools excluded','old_main_water_area_m2':actual['old_plan_area_m2'],'new_main_water_area_m2':actual['new_plan_area_m2'],'reduction_fraction':1-actual['new_plan_area_m2']/actual['old_plan_area_m2'],'min_width_m':actual['min_width_m'],'max_width_m':actual['max_width_m'],'courtyard_pools':data['added_gardens'],'dimension_status':'inferred design dimensions'};(O/'design-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('PLAN_READY',flush=True)
