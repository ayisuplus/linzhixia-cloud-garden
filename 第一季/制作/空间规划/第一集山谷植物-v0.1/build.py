"""Cloud valley planting and rock outcrops. Additive edit of the reviewed v09."""
import bpy,bmesh,sys,json,math,random,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1'));import geometry as G
sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
OLD=R/'视频制作/第一集水巷街桥-20261024-v0.1';O=R/'视频制作/第一集山谷植物-20261024-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(OLD/'waterlane-masterplan-v09.blend'));S=bpy.context.scene
def col(name):
 c=bpy.data.collections.new(name);S.collection.children.link(c);return c
ROCK=col('12 Valley stone outcrops');TREE=col('13 Valley pine and bamboo');LOW=col('14 Valley shrubs and moss')
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1]]=m
if 'rock' not in G.M:
 m=G.M['stone'].copy();m.name='Whitebox / rock';m.diffuse_color=(.32,.37,.33,1)
 for node in m.node_tree.nodes:
  if node.type=='BSDF_PRINCIPLED':node.inputs['Base Color'].default_value=(.32,.37,.33,1);node.inputs['Roughness'].default_value=.9
 G.M['rock']=m
# A muted moss surface stays inside the existing leaf/terrain palette.
m=G.M['leaf'].copy();m.name='Valley moss using retained leaf and terrain';c=tuple(.48*a+.52*b for a,b in zip(G.M['leaf'].diffuse_color,G.M['terrain'].diffuse_color));m.diffuse_color=c
for node in m.node_tree.nodes:
 if node.type=='BSDF_PRINCIPLED':node.inputs['Base Color'].default_value=c;node.inputs['Roughness'].default_value=.96
G.M['moss']=m
rng=random.Random(241024);records=[]
ground=bpy.data.objects['Continuous stable cloud terrain / river bed and inhabited slopes']
gb=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[tuple(f.vertices) for f in ground.data.polygons])
def gz(xy):
 h=gb.ray_cast(Vector((*xy,500)),Vector((0,0,-1)),1000);return h[0].z if h[0] else None
P=json.loads((R/'视频制作/第一集山水总图白模-20261024-v0.1/layout-plan.json').read_text('utf8'))
roads=[(np.array(p['points'])[:,:2],p['width']/2) for p in P['paths']]
flight=np.array([p['position'] for p in json.loads((OLD/'route-poses.json').read_text('utf8'))])
bounds=[]
for cname in ['04 Contour courtyard clusters','09 Waterfront streets and inhabited bridgeheads','10 Connected bridges and quays']:
 for ob in bpy.data.collections[cname].objects:
  if ob.type=='MESH' and not ob.hide_render:
   vs=np.array([ob.matrix_world@Vector(v) for v in ob.bound_box]);bounds.append((vs[:,:2].min(axis=0),vs[:,:2].max(axis=0)))
def clear(xy,rx,ry,h):
 z=gz(xy)
 if z is None:return False
 radius=max(rx,ry)
 for pts,w in roads:
  if np.linalg.norm(pts-xy,axis=1).min()<radius+w+1.2:return False
 for a,b in bounds:
  if np.linalg.norm(np.maximum(np.maximum(a-xy,xy-b),0))<radius+1:return False
 # Reserve a generous three-dimensional flight corridor before placing any asset.
 radii=np.array([rx+4,ry+4,h/2+4]);center=np.r_[xy,z+h/2]
 if np.linalg.norm((flight-center)/radii,axis=1).min()<1.15:return False
 return True
def pos(s,side,q):return L.point(s,side*(float(L.width(s,side))+q))[:2]
def rock(xy,rx,ry,h,seed):
 if not clear(xy,rx,ry,h):return
 z=gz(xy);n=11;vs=[];rr=random.Random(seed);phase=rr.random()*6.28
 # Layered tapered irregular facets, with a buried root and offset ridge.
 for j,(zz,scale) in enumerate([(-1,1),(.15,1.05),(.48,.88),(.78,.63),(1,.28)]):
  for k in range(n):
   a=2*math.pi*k/n;f=1+.16*math.sin(3*a+phase)+.09*rr.uniform(-1,1)
   xx=xy[0]+rx*(math.cos(a)*scale*f+.16*j/4);yy=xy[1]+ry*(math.sin(a)*scale*f-.12*j/4)
   # Rock roots follow the steep actual surface around their whole footprint.
   # A level bottom would visibly hang out of the hillside on its downhill edge.
   base=gz((xx,yy));vs.append((xx,yy,z+zz*h if zz>=0 else base-min(2,h*.2)))
 fs=[]
 for j in range(4):
  for k in range(n):fs.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
 fs.append(tuple(4*n+k for k in range(n)))
 ob=G.mesh('Valley limestone folded outcrop',vs,fs,'rock',ROCK)
 records.append({'type':'rock','name':ob.name,'xy':xy.tolist(),'height':h,'radius':[rx,ry]})
def crown(name,xyz,scale,key,c):
 me=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);ob.location=xyz
 for v in ob.data.vertices:
  f=1+.13*math.sin(v.co.x*7+v.co.y*4+v.co.z*9);v.co*=f
 ob.scale=scale
 for cc in list(ob.users_collection):cc.objects.unlink(ob)
 c.objects.link(ob);ob.data.materials.append(G.M[key]);ob['physical']=True
 for f in ob.data.polygons:f.use_smooth=True
 return ob
def root_clear(xy,r):
 for rec in records:
  if rec['type']=='rock' and np.linalg.norm((xy-np.array(rec['xy']))/(np.array(rec['radius'])+r))<1.05:return False
 return True
def pine(xy,h):
 r=h*.3
 if not clear(xy,r+1,r+1,h+2) or not root_clear(xy,1.2):return
 z=gz(xy);lean=np.array([rng.uniform(-1.4,1.4),rng.uniform(-1,1)]);root=np.r_[xy,z-.35];top=np.r_[xy+lean,z+h]
 G.beam('Valley pine rooted trunk',[root,np.r_[xy+lean*.3,z+h*.48],top],h*.025,'wood',TREE)
 for k,(fraction,rad) in enumerate([(.57,r),(.76,r*.83),(.94,r*.58)]):
  a=rng.random()*6.28;off=np.array([math.cos(a),math.sin(a)])*r*.45;end=np.r_[xy+lean*fraction+off,z+h*fraction]
  G.beam('Valley pine branch',[np.r_[xy+lean*fraction,z+h*(fraction-.08)],end],.11,'wood',TREE)
  crown('Valley layered pine canopy',end,(rad,rad*.82,rad*.4),'pine' if k!=1 else 'leaf',TREE)
 records.append({'type':'pine','xy':xy.tolist(),'height':h})
def bamboo(xy,h):
 if not clear(xy,3,3,h+1) or not root_clear(xy,2):return
 z=gz(xy)
 for j in range(7):
  a=j*math.tau/7;off=np.array([math.cos(a),math.sin(a)])*rng.uniform(.4,1.8);q=xy+off;zq=gz(q);hh=h*rng.uniform(.7,1)
  G.beam('Bamboo rooted culm',[np.r_[q,zq-.2],np.r_[q+off*.25,zq+hh]],.07,'pine',TREE)
  for f in [.68,.88]:crown('Bamboo leaf spray',np.r_[q+off*.4,zq+hh*f],(1.45,.65,1.0),'leaf',TREE)
 records.append({'type':'bamboo-clump','xy':xy.tolist(),'height':h})
def shrub(xy,r):
 if not clear(xy,r,r,r*1.1):return
 z=gz(xy);crown('Valley low shrub',(*xy,z+r*.35),(r,r*.8,r*.65),'leaf' if rng.random()<.65 else 'pine',LOW)
 records.append({'type':'shrub','xy':xy.tolist(),'radius':r})
def moss_patch(xy,rx,ry,phase):
 vs=[];n=48;rings=8
 for j in range(rings):
  f=(j+.08)/(rings-1+.08)
  for k in range(n):
   a=k*math.tau/n;rad=1+.14*math.sin(a*3+phase)+.08*math.sin(a*7-phase);p=xy+np.array([rx*math.cos(a),ry*math.sin(a)])*f*rad;z=gz(p)
   vs.append((*p,z+.16))
 fs=[tuple(range(n-1,-1,-1))]
 for j in range(rings-1):
  for k in range(n):fs.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
 G.mesh('Irregular moss and low ground cover',vs,fs,'moss',LOW,False)
anchors=[(.158,1,45),(.185,-1,30),(.215,1,64),(.245,-1,38),(.267,1,65),(.295,-1,40),(.323,1,57),(.352,-1,30),(.378,1,55),(.407,-1,28)]
for index,(s,side,q) in enumerate(anchors):
 print('VALLEY_CLUSTER',index,flush=True)
 xy=pos(s,side,q);t,n=L.basis(s)
 moss_patch(xy,17,12,index*.8)
 rock(xy,rng.uniform(7,11),rng.uniform(5,8),rng.uniform(13,22),index)
 for k in range(5):
  off=t*rng.uniform(-15,15)+n*rng.uniform(-8,10);rock(xy+off,rng.uniform(2.4,5),rng.uniform(2.5,4.6),rng.uniform(4,10),index*10+k+80)
 for k in range(8):
  off=t*rng.uniform(-28,28)+n*rng.uniform(-14,23);pine(xy+off,rng.uniform(9,17))
 for k in range(16):
  off=t*rng.uniform(-25,25)+n*rng.uniform(-16,19);shrub(xy+off,rng.uniform(1.3,3))
 for k in range(2):bamboo(xy+t*rng.uniform(-22,22)+n*rng.uniform(-12,14),rng.uniform(8,12))
# Smaller near-water stones and bamboo alternate sides, without blocking bridge reveals.
for i,s in enumerate(np.linspace(.15,.41,17)):
 side=1 if i%2 else -1;xy=pos(s,side,19)
 rock(xy,3,3,rng.uniform(5,9),500+i);bamboo(xy+L.basis(s)[0]*7,9)
bpy.data.collections['05 Atmospheric envelope optional'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'valley-masterplan-v10.blend'))
(O/'landscape-data.json').write_text(json.dumps({'source_sha256':hashlib.sha256((OLD/'waterlane-masterplan-v09.blend').read_bytes()).hexdigest(),'seed':241024,'assets':records,'palette':'v09 retained materials','scope':'rock and planting reference masses, not final botanical assets'},ensure_ascii=False,indent=2),encoding='utf8')
from collections import Counter
print('VALLEY_READY',dict(Counter(r['type'] for r in records)),flush=True)
