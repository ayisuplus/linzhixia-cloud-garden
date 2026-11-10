"""v16 planning data: separate garden supports, local water groups, independent circulation.
All dimensions are inferred design candidates, metres, not adopted construction data.
"""
import math
ISLANDS=[
 dict(id='A',name='学园',center=[-230,155,126],radius=[100,72],angle=-15,depth=28,phase=.3),
 dict(id='B',name='听瀑园',center=[-123,85,82],radius=[78,58],angle=20,depth=22,phase=1.2),
 dict(id='C',name='收水庭',center=[-32,15,32],radius=[77,62],angle=-10,depth=20,phase=2.4),
 dict(id='D',name='山居植物园',center=[75,175,104],radius=[76,54],angle=25,depth=27,phase=3.1),
 dict(id='E',name='云间换层亭',center=[90,-35,72],radius=[48,37],angle=-8,depth=17,phase=.8),
 dict(id='F',name='半园',center=[228,-95,66],radius=[66,49],angle=-12,depth=22,phase=1.7),
 dict(id='G',name='修复作坊',center=[330,-65,48],radius=[62,46],angle=18,depth=19,phase=2.8),
]
BY_ID={x['id']:x for x in ISLANDS}
def outline(i,n=120,scale=1):
 a=math.radians(i['angle']);out=[]
 for k in range(n):
  t=k*math.tau/n;w=1+.065*math.sin(3*t+i['phase'])+.035*math.sin(5*t-i['phase'])
  x=i['radius'][0]*math.cos(t)*w*scale;y=i['radius'][1]*math.sin(t)*w*scale
  out.append([i['center'][0]+x*math.cos(a)-y*math.sin(a),i['center'][1]+x*math.sin(a)+y*math.cos(a)])
 return out
COURTS=[
 ('A','School-+1-00',[-264,176],0),('A','School-+1-01',[-215,177],0),('A','School-+1-02',[-267,130],0),
 ('B','Water-bay-+1-00',[-105,110],-12),('C','Water-bay-+1-02',[-22,-5],8),
 ('D','Slope-neighbourhood-+1-00',[47,181],-8),('D','Slope-neighbourhood--1-00',[100,180],12),
 ('F','Zhixia-home',[205,-105],-8),('G','Repair-workshop',[347,-64],12),
]
# Same-level bridges terminate at actual upper landings. Stairs/lift shaft occupy space on lower islands.
LINKS=[
 dict(id='L1',a='A',b='B',points=[[-229,103,126],[-197,72,126],[-160,61,126]],tower=[-160,61],low='B'),
 dict(id='L2',a='B',b='C',points=[[-107,55,82],[-83,22,82],[-55,10,82]],tower=[-55,10],low='C'),
 dict(id='L3',a='C',b='E',points=[[-4,4,72],[30,-17,72],[65,-33,72]],tower=[-4,4],low='C'),
 dict(id='L4',a='E',b='D',points=[[90,-10,104],[111,48,104],[83,96,104],[65,137,104]],tower=[90,-10],low='E'),
 dict(id='L5',a='E',b='F',points=[[120,-48,72],[156,-62,72],[190,-83,72]],tower=[190,-83],low='F'),
 dict(id='L6',a='F',b='G',points=[[268,-95,66],[287,-102,66],[307,-92,66]],tower=[307,-92],low='G'),
 dict(id='L7',a='B',b='D',points=[[-68,76,104],[-23,118,104],[23,154,104]],tower=[-68,76],low='B'),
]
# The bridge enters the south landing, never the stair well at the tower centre.
for link in LINKS:
 pts=link['points'];x,y=link['tower']
 if pts[0][:2]==link['tower']:
  pts[0][1]-=5.7;pts[1:1]=[[x,y-13,pts[0][2]],[x+19,y-13,pts[0][2]]]
 elif pts[-1][:2]==link['tower']:
  pts[-1][1]-=5.7;sign=-1 if pts[-2][0]<x else 1;pts[-1:-1]=[[x+sign*19,y-13,pts[-1][2]],[x,y-13,pts[-1][2]]]
WATER_PAIRS=[('W1','A','B'),('W2','B','C'),('W3','F','G')]
# Route envelope only. No frozen positions, no animation or collision claim.
ROUTE=[[-232,145,137],[-185,123,139],[-153,85,110],[-109,40,103],[-53,12,96],[25,-12,103],[108,-51,84],[177,-80,81],[251,-76,75],[293,-72,55],[321,-64,54]]
CHAPTERS=[('0–10秒','学园出廊，看见下方听瀑园'),('10–22秒','侧过跌水，穿云隙换层'),('22–36秒','跨向云间亭，借景侧上方山居园'),('36–48秒','进入半园与作坊的局部水庭'),('48–58秒','短段贴水，抵达作坊收件处')]
