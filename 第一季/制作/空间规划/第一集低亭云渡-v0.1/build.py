"""v18 low pavilions and cloud ferries, replacing six high connector towers.
Static boarding/shaft design candidate. No operating lift or transport simulation.
"""
import bpy,sys,json,math,hashlib,bmesh
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1'));import geometry as G
SRC=R/'视频制作/第一集园岛深化-20261024-v0.1';O=R/'视频制作/第一集低亭云渡-20261024-v0.1';O.mkdir(exist_ok=True)
B=SRC/'island-garden-developed-v17.blend';bpy.ops.wm.open_mainfile(filepath=str(B));S=bpy.context.scene
P=json.loads((SRC/'planning-data.json').read_text('utf8'));DEV=json.loads((SRC/'development-data.json').read_text('utf8'))
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1].split(' [')[0]]=m
def col(n):c=bpy.data.collections.new(n);S.collection.children.link(c);return c
ST=col('14 Low ferry pavilions');PIER=col('15 Short boarding piers');BOAT=col('16 Static cloud skiffs');LIFT=col('17 Embedded school lift and side port');G.ARCH=ST
data={'version':'v18','source_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'removed_objects':[],'modified_source_objects':['A separate cloud support'],'retained_link':'L5 only, 6m level change, two storeys','stations':[],'ferry_links':[('A','B'),('B','C'),('C','E'),('E','D'),('F','G'),('B','D')],'status':'static low-rise transport candidate, not operational transport','source_materials':'unchanged'}
for ob in list(S.objects):
 if any(ob.name.startswith('L'+str(k)+' ') for k in [1,2,3,4,6,7]) or ob.name=='A internal garden path 0':
  data['removed_objects'].append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)

def prism(name,poly,z,thick,key,c):
 vs=[(*p,z-thick) for p in poly]+[(*p,z) for p in poly];n=len(poly);fs=[tuple(reversed(range(n)))]
 fs.extend((n,n+k,n+k+1) for k in range(1,n-1))
 fs.extend((k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n))
 return G.mesh(name,vs,fs,key,c)
def path(name,pts,width,z,key='stone',c=PIER,rail=False,railclear=0):
 # Separate closed prisms and filled corner disks; no folded ribbon corners.
 parts=[]
 for k,(a,b) in enumerate(zip(pts,pts[1:])):
  a=np.array(a,float);b=np.array(b,float);d=b-a;d/=np.linalg.norm(d);n=np.array([-d[1],d[0]])*width/2
  parts.append(prism(name+f' segment {k}',[a-n,b-n,b+n,a+n],z,.3,key,c))
  if rail:
   for side in [-1,1]:
    p=a+d*min(railclear,np.linalg.norm(b-a)-.1)+n*side;q=b+n*side;G.beam(name+' rail',[(*p,z+1.1),(*q,z+1.1)],.07,'wood',c)
    for u in np.linspace(0,1,max(2,int(np.linalg.norm(q-p)/2.5))):
     v=p*(1-u)+q*u;G.beam(name+' post',[(*v,z),(*v,z+1.1)],.07,'wood',c)
 for k,p in enumerate(pts[1:-1]):
  poly=[np.array(p)+width/2*np.array([math.cos(t),math.sin(t)]) for t in np.linspace(0,math.tau,24,endpoint=False)];parts.append(prism(name+f' corner {k}',poly,z,.3,key,c))
 return parts
def cut(ob,center,size):
 cutter=G.box('temporary opening cutter',center,size,'stone',LIFT);mod=ob.modifiers.new('local lift opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
def pavilion(ident,xy,z,size=(12,10),h=4.4):
 x,y=xy;w,d=size;G.box(ident+' waiting platform',(x,y,z-.14),(w,d,.28),'stone',ST)
 for dx in [-w/2+1,w/2-1]:
  for dy in [-d/2+1,d/2-1]:G.beam(ident+' pavilion post',[(x+dx,y+dy,z),(x+dx,y+dy,z+h)],.15,'redwood',ST)
 G.roof(ident+' low tiled roof',(x,y,z+h),(w+2,d+2),1.4,0)
 # Short seats stay on the side, leaving a clear cross-shaped access area.
 for side in [-1,1]:
  if (ident,side) in [('A ferry',-1),('F ferry',-1),('G ferry',1)]:continue
  G.box(ident+' bench',(x+side*(w/2-1.3),y,z+.52),(.6,3.5,.18),'wood',ST)
  for yy in [-1.2,1.2]:G.box(ident+' bench support',(x+side*(w/2-1.3),y+yy,z+.23),(.45,.18,.46),'wood',ST)
 return {'xy':xy,'floor':z,'roof_top':z+h+1.4,'size':size}

nodes={'A':[-229,103],'B':[-160,55.3],'C':[-55,4.3],'D':[65,137],'E':[90,-15.7],'F':[268,-125],'G':[307,-97.7]}
new_walks=[]
# Reroute one short school path around the real lift shaft, not through it.
pp=[[-229,103],[-239,103],[-239,116],[-230,116],[-267,105]];path('A revised garden approach',pp,3.2,126.14,c=ST);new_walks.append({'id':'A revised garden approach','island':'A','points':pp,'z':126.14,'width':3.2})
P['internal_paths']['A'][0]=pp

for i in P['islands']:
 iid=i['id'];xy=np.array(nodes[iid],float);z=i['center'][2]+.16;pav=pavilion(iid+' ferry',xy.tolist(),z)
 if iid=='A':
  # Shaft is wholly local to the school cloud body: 14m, not the entire 44m
  # inter-island difference. Passengers then use a cloud ferry for the rest.
  core=bpy.data.objects['A separate cloud support'];cut(core,(-229,110,119.5),(5,5,16))
  cut(core,(-229,94.5,114.35),(5,32,4.7))
  # Exposed lower doorway and continuous floor through the cloud body.
  lower=112.16;path('A inside-cloud concourse',[[-229,110],[-229,78]],4.6,lower,c=LIFT)
  for xx in [-231.6,-226.4]:G.box('A lower portal side',(xx,91,114.35),(.32,2.0,4.7),'stone',LIFT)
  G.box('A lower portal lintel',(-229,91,116.75),(5.5,2,.3),'stone',LIFT)
  # Lift guides stay within the cutout, with a car parked at the upper landing.
  for xx in [-231.25,-226.75]:G.beam('A concealed lift guide',[(xx,112.2,lower),(xx,112.2,z+2.6)],.07,'wood',LIFT)
  G.box('A lift car floor parked upper',(-229,110,z-.12),(4.8,4.8,.24),'wood',LIFT)
  # Upper landing access is from the south; guards occupy the other three edges.
  G.beam('A upper shaft guard',[(-231.55,107.5,z+1.1),(-231.55,112.55,z+1.1),(-226.45,112.55,z+1.1),(-226.45,107.5,z+1.1)],.09,'wood',LIFT)
  for xx in [-231.55,-226.45]:
   for yy in [108,110,112.4]:G.beam('A upper guard post',[(xx,yy,z),(xx,yy,z+1.1)],.08,'wood',LIFT)
  path('A upper lift threshold',[[-229,106],[-229,108]],3.2,z,c=LIFT)
  # A low hood shelters the upper lift access without a tall external shaft.
  G.ARCH=LIFT;G.roof('A low lift entrance hood',(-229,110,z+3.1),(6.6,7),1.1,0);G.ARCH=ST
  for xx in [-232,-226]:G.beam('A lift hood post',[(xx,113,z),(xx,113,z+3.1)],.13,'redwood',LIFT)
  # Lower gate is closed while the displayed car is at the upper landing.
  G.box('A lower lift closed gate',(-229,107.5,lower+1.1),(4.8,.12,2.2),'window',LIFT)
  start=np.array([-229.,78.]);direction=np.array([0.,-1.]);end=start+direction*14;dockz=lower
  data['embedded_lift']={'island':'A','shaft_xy':[-229,110],'upper':z,'lower':lower,'travel_m':14,'cutouts':[{'center':[-229,110,119.5],'size':[5,5,16]},{'center':[-229,94.5,114.35],'size':[5,32,4.7]}],'concourse':[[-229,110],[-229,78]],'car_state':'parked upper; lower gate closed','operation':'not simulated'}
 else:
  # Shortest shoreline is a candidate only; the existing living path owns the
  # pavilion position. The generated pier is checked against actual geometry.
  poly=np.array(i['outline']);candidates=[]
  for a,b in zip(poly,np.roll(poly,-1,axis=0)):
   d=b-a;t=np.clip((xy-a)@d/max(d@d,1e-9),0,1);p=a+t*d;candidates.append(p)
  edge=min(candidates,key=lambda v:np.linalg.norm(v-xy));direction=(edge-xy);direction/=np.linalg.norm(direction);start=xy;end=edge+direction*9;dockz=z
 # Full-width pier with an open boarding end. A reinforced cloud keel is a
 # fictional structural element, kept separate from non-bearing fog.
 # Keep the platform's cross access open; rails begin beyond its footprint.
 railclear=0 if iid=='A' else min((pav['size'][0]/2+.3)/max(abs(direction[0]),1e-6),(pav['size'][1]/2+.3)/max(abs(direction[1]),1e-6))
 path(iid+' cloud landing pier',[start.tolist(),end.tolist()],3.6,dockz,'wood',PIER,True,railclear)
 G.beam(iid+' pier cloud keel',[(*start,dockz-.9),(*end,dockz-.9)],.45,'cloudwhite',PIER)
 # Static boat beside the pier's terminal, with an actual connecting gangway.
 center=end+direction*7;normal=np.array([-direction[1],direction[0]]);angle=math.atan2(direction[1],direction[0]);v=[]
 hull=[(-6,-1.0),(-4.4,-2),(3.8,-2),(6,0),(3.8,2),(-4.4,2),(-6,1.0)]
 def boatp(x,y,h):return (*(center+direction*x+normal*y),dockz+h)
 for scale,dz in [(.72,-1.25),(1,-.05)]:
  v.extend(boatp(x*scale,y*scale,dz) for x,y in hull)
 n=len(hull);faces=[tuple(reversed(range(n)))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
 G.mesh(iid+' cloud skiff hull',v,faces,'wood',BOAT)
 prism(iid+' skiff deck',[center+direction*x+normal*y for x,y in hull],dockz,.14,'wood',BOAT)
 path(iid+' boarding gangway',[end.tolist(),(center-direction*5).tolist()],2.0,dockz,'wood',PIER)
 for side in [-1,1]:
  G.beam(iid+' boat rail',[boatp(-5,side*1.3,.9),boatp(-4,side*1.9,.9),boatp(3.8,side*1.9,.9),boatp(5.6,side*.25,.9)],.065,'wood',BOAT)
  for xx in [-3.5,3]:G.beam(iid+' canopy post',[boatp(xx,side*1.6,0),boatp(xx,side*1.6,2.7)],.11,'redwood',BOAT)
 G.ARCH=BOAT;G.roof(iid+' boat canopy',boatp(0,0,2.7),(8.5,4.8),.9,angle);G.ARCH=ST
 record={'id':iid,'pavilion':pav,'pier_points':[start.tolist(),end.tolist()],'pier_z':dockz,'boat_center':center.tolist(),'boat_heading':angle,'gangway':[end.tolist(),(center-direction*5).tolist()],'boarding_width':2.0,'mode':'cloud ferry','boat_static':True};data['stations'].append(record)
 new_walks.append({'id':iid+' cloud landing pier','island':iid,'points':[start.tolist(),end.tolist()],'z':dockz,'width':3.6})

# Two formerly high transfer sites become small garden resting shelters.
for iid,xy in [('B',[-68,76]),('C',[-4,4])]:
 z=next(i['center'][2] for i in P['islands'] if i['id']==iid)+.16;pavilion(iid+' former transfer garden shelter',xy,z,(8,7),3.5)

# Remove only new-transport planting conflicts, in coherent clusters. Record
# every removal; never move an existing house, pond or whole garden to fit a pier.
def segdist(p,a,b):
 p=np.array(p);a=np.array(a);b=np.array(b);v=b-a;t=np.clip((p-a)@v/max(v@v,1e-9),0,1);return np.linalg.norm(p-a-t*v)
def neartransport(xy,z,r):
 return any(abs(w['z']-z)<3 and any(segdist(xy,a,b)<r+w['width']/2+1 for a,b in zip(w['points'],w['points'][1:])) for w in new_walks)
remove=set()
for g in DEV['plant_groups']:
 z=next(i['center'][2] for i in P['islands'] if i['id']==g['island'])
 if neartransport(g['xy'],z,g['radius']*1.5):remove.update(o.name for o in S.objects if o.name.startswith(g['id']+' '))
# Legacy planting: if a trunk intersects a pier, remove its local canopy/rock
# group by spatial neighbourhood instead of leaving a floating crown behind.
for ob in list(S.objects):
 if 'tree trunk' not in ob.name or ' rooted cluster ' in ob.name:continue
 pts=np.array([ob.matrix_world@v.co for v in ob.data.vertices]);low=pts[pts[:,2]<pts[:,2].min()+.5];anchor=low.mean(0)
 if not neartransport(anchor[:2],anchor[2],2):continue
 for other in S.objects:
  if other.type!='MESH' or not any(t in other.name for t in ['tree trunk','planted pine','rooted edge rock','clustered understory']):continue
  if other.name[0]!=ob.name[0]:continue
  bb=np.array([other.matrix_world@Vector(v) for v in other.bound_box]);center=bb.mean(0)
  if np.linalg.norm(center[:2]-anchor[:2])<9:remove.add(other.name)
for name in sorted(remove):
 ob=bpy.data.objects.get(name)
 if ob:data['removed_objects'].append(name);bpy.data.objects.remove(ob,do_unlink=True)

data['walk_checks']=new_walks
P['version']='v18';P['status']='low pavilion and static ferry transport candidate';P['links']=[x for x in P['links'] if x['id']=='L5'];P['transport']=data['stations'];P['ferry_links']=data['ferry_links'];P['source_sha256']=data['source_sha256']
S['status']='v18 low-rise cloud crossings; ferries and concealed school lift are static candidates';S.render.resolution_x=1440;S.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath=str(O/'low-pavilion-cloud-ferry-v18.blend'))
(O/'planning-data.json').write_text(json.dumps(P,ensure_ascii=False,indent=2),encoding='utf8');(O/'transport-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('V18_BUILD_READY',len(S.objects),'removed',len(data['removed_objects']),flush=True)
