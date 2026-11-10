"""v14: two cloud landmarks, inhabited garden thresholds, and an off-river flight.
All dimensions are design inferences. Source v13 is never saved over.
"""
import bpy, bmesh, sys, json, math, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R=Path(sys.argv[sys.argv.index('--')+1]); D=Path(__file__).parent
sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1')); import layout as L
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1')); import geometry as G
SRC=R/'视频制作/第一集池涧水巷-20261024-v0.1'
O=R/'视频制作/第一集云山园巷-20261024-v0.1'; O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC/'pond-lane-route-58s-v13.blend')); S=bpy.context.scene
for m in bpy.data.materials:
 if ' / ' in m.name: G.M[m.name.split(' / ')[-1].split(' [')[0]]=m
def coll(name):
 c=bpy.data.collections.new(name); S.collection.children.link(c); return c
C=coll('23 Garden thresholds and inhabited shoulders'); G.ARCH=C
def verts(o):
 a=np.empty(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);a=a.reshape(-1,3);m=np.array(o.matrix_world);return a@m[:3,:3].T+m[:3,3]
def bvh(obs):
 vs=[]; fs=[]; names=[]
 for o in obs:
  a=verts(o);off=len(vs);vs.extend(a);fs.extend(tuple(off+i for i in f.vertices) for f in o.data.polygons);names.extend([o.name]*len(o.data.polygons))
 return BVHTree.FromPolygons([Vector(p) for p in vs],fs),names
ground=bpy.data.objects['Continuous stable cloud terrain / river bed and inhabited slopes']
original=verts(ground); oldb,_=bvh([ground]); data={'source_sha256':hashlib.sha256((SRC/'pond-lane-route-58s-v13.blend').read_bytes()).hexdigest(),'gardens':[],'bridges':[],'terrain':{},'new_objects':[]}
# Keep all existing objects and their supports. Only unoccupied slope volumes
# are lowered. XY and vertex color attributes are not altered.
protect=[]
for o in S.objects:
 if o.type!='MESH' or o==ground or o.hide_render:continue
 if any(c.name.startswith(('01 ','02 ','05 ')) for c in o.users_collection):continue
 a=verts(o); bottom=a[:,2].min(); low=a[a[:,2]<bottom+1.0]
 protect.extend(low[:,0:2])
kd=KDTree(len(protect))
for i,p in enumerate(protect):kd.insert(Vector((*p,0)),i)
kd.balance(); ss,dd,_=L.nearest(original[:,:2]); q=np.abs(dd)
clear=np.array([kd.find(Vector((*p,0)))[2] for p in original[:,:2]])
def smooth(x):x=np.clip(x,0,1);return x*x*x*(10+x*(-15+6*x))
mask=smooth((clear-7)/23)*smooth((q-38)/34)
# Two asymmetric landmarks, with lower shoulders between and beyond them.
landmark=34*np.exp(-((ss-.245)/.035)**2-((dd-112)/35)**2)+27*np.exp(-((ss-.365)/.03)**2-((dd+110)/30)**2)
target=L.water_z(ss)+8+.10*q+landmark
newz=original[:,2]-np.maximum(0,original[:,2]-target)*mask
for i,v in enumerate(ground.data.vertices):v.co.z=newz[i]
ground.data.update(); changed=np.abs(newz-original[:,2])>.001
data['terrain']={'changed_vertices':int(changed.sum()),'max_lowering_m':float((original[:,2]-newz).max()),'mean_lowering_changed_m':float(np.mean((original[:,2]-newz)[changed])),'protection':'7m zero-change radius around low vertices of all existing visible assets; 23m smooth transition; XY and colors unchanged','landmarks':[{'s':.245,'d':112},{'s':.365,'d':-110}]}
gb,_=bvh([ground])
def gz(xy):
 hit=gb.ray_cast(Vector((*xy,500)),Vector((0,0,-1)),1000)[0]
 if hit is None:raise ValueError(('no ground',xy))
 return float(hit.z)
def oval(name,pos,scale,key):
 me=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);C.objects.link(o);o.location=pos;o.scale=scale;me.materials.append(G.M[key]);o['physical']=True
 for f in me.polygons:f.use_smooth=True
 return o
def path(name,points,width,key='stone'):
 # Solid deck, locally supported; walking slope is separately reported.
 vs=[];fs=[]
 for i,p in enumerate(points):
  p=np.array(p);a=np.array(points[max(0,i-1)]);b=np.array(points[min(len(points)-1,i+1)]);n=np.array([-(b-a)[1],(b-a)[0]]);n/=np.linalg.norm(n)
  for dz in [-.28,0]:
   for side in [-1,1]:vs.append(np.r_[p[:2]+side*n*width/2,p[2]+dz])
 for i in range(len(points)-1):
  k=4*i;fs.extend([(k+2,k+3,k+7,k+6),(k,k+4,k+5,k+1),(k,k+2,k+6,k+4),(k+1,k+5,k+7,k+3)])
 fs.extend([(0,1,3,2),(len(vs)-4,len(vs)-2,len(vs)-1,len(vs)-3)])
 return G.mesh(name,vs,fs,key,C)
# Two walkable garden enclosures on the previously empty inner valley banks.
# Wide axial doorways and roofed side galleries avoid isolated flight hoops.
for ident,st,side,d in [('G1 Cloud-entry garden',.162,-1,34),('G2 Hidden-water garden',.333,-1,38)]:
 xy=L.point(st,side*d)[:2];t,n=L.basis(st);n*=side;angle=math.atan2(t[1],t[0]);samples=[gz(xy+t*x+n*y) for x in [-16,0,16] for y in [-11,0,11]];floor=max(samples)+.18
 def p(x,y,z):return np.r_[xy+t*x+n*y,z]
 G.box(ident+' supported stone terrace',p(0,0,(min(samples)-.4+floor)/2),(34,25,floor-min(samples)+.4),'stone',C,angle)
 # Side hall frames the garden with an open veranda toward the shallow pond.
 G.box(ident+' rear hall',p(0,8.5,floor+2.5),(27,6,5),'wall',C,angle)
 G.roof(ident+' rear hall roof',p(0,8.5,floor+5.1),(29,9),2,angle)
 for x in [-10,-5,0,5,10]:
  G.box(ident+' lattice opening',p(x,5.45,floor+2.7),(2.6,.13,2.6),'window',C,angle)
  G.beam(ident+' veranda post',[p(x,3.7,floor),p(x,3.7,floor+5.1)],.14,'redwood',C)
 # End walls have real 10m openings. Continuous cap on side sections only.
 for x in [-16,16]:
  for a,b in [(-12,-5),(5,12)]:
   G.box(ident+' end garden wall',p(x,(a+b)/2,floor+2.4),(.45,b-a,4.8),'wall',C,angle)
   G.box(ident+' wall cap',p(x,(a+b)/2,floor+4.85),(.65,b-a+.3,.22),'roof',C,angle)
 # Low water-side wall gives near/far separation, with two rectangular leak windows.
 for a,b in [(-16,-10),(-6,6),(10,16)]:G.box(ident+' water-side wall',p((a+b)/2,-11,floor+1.9),(b-a,.4,3.8),'wall',C,angle)
 for x in [-8,8]:
  G.box(ident+' leak window sill',p(x,-11,floor+.55),(4,.4,1.1),'wall',C,angle)
  G.box(ident+' leak window lintel',p(x,-11,floor+3.5),(4,.4,.6),'wall',C,angle)
 G.box(ident+' pond basin',p(0,-4,floor+.1),(14,6,.2),'stone',C,angle)
 G.box(ident+' still pond',p(0,-4,floor+.22),(13.3,5.3,.035),'water',C,angle)
 for x in [-7,7]:G.box(ident+' pond rim',p(x,-4,floor+.25),(.3,6.2,.4),'stone',C,angle)
 for y in [-7,-1]:G.box(ident+' pond rim',p(0,y,floor+.25),(14.3,.3,.4),'stone',C,angle)
 G.box(ident+' waterside bench',p(9,-3,floor+.55),(.7,4,.35),'wood',C,angle)
 for x,y in [(-12,0),(12,-7)]:
  G.beam(ident+' planted trunk',[p(x,y,floor-.2),p(x+.6,y,floor+4.7)],.17,'wood',C)
  oval(ident+' airy crown',p(x+.6,y,floor+5),(2.9,2.2,1.2),'pine')
  oval(ident+' rooted rock',p(x+1.8,y,floor+.1),(1.4,1.2,.8),'rock')
 # A real stepped entrance connects the side opening to the existing bank walk.
 start=p(-16,0,floor);end=L.point(st-.011,-(7+3.1),float(L.water_z(st-.011))+2.26);mid=np.r_[xy-t*25-n*10,floor]
 route=[start,mid,end];steps=[]
 for a,b in zip(route,route[1:]):
  length=np.linalg.norm(b[:2]-a[:2]);count=max(2,int(math.ceil(length/.45)),int(math.ceil(abs(b[2]-a[2])/.14)));ang=math.atan2(b[1]-a[1],b[0]-a[0]);tops=[]
  for j in range(count):
   u=(j+.5)/count;pt=a*(1-u)+b*u;bottom=min(gz(pt[:2])-.25,pt[2]-.3);G.box(ident+' grounded entrance step',(*pt[:2],(bottom+pt[2])/2),(length/count+.025,2.5,pt[2]-bottom),'stone',C,ang);tops.append(float(pt[2]))
  steps.append({'length':float(length),'rise':float(b[2]-a[2]),'count':count})
 data['gardens'].append({'id':ident,'s':st,'d':side*d,'center':xy.tolist(),'floor':floor,'entry':start.tolist(),'exit':p(16,0,floor).tolist(),'steps':steps})
# Three cross-water galleries interrupt the long corridor without damming it.
# They use the existing narrow water and both bank footpaths, with no end walls.
water=bpy.data.objects['Main water spine / upstream to downstream collection'];wv=verts(water).reshape(-1,2,3)
for k,st in enumerate([.142,.407,.746]):
 idx=round(st*(len(wv)-1));xy=wv[idx,:,:2].mean(0);t,n=L.basis(st);angle=math.atan2(n[1],n[0]);width=float(np.linalg.norm(wv[idx,1,:2]-wv[idx,0,:2]));half=width/2+13;floor=float(L.water_z(st))+2.28;ident=f'Cross-water gallery {k+1}'
 def p(x,y,z):return np.r_[xy+t*x+n*y,z]
 deck=G.box(ident+' walking deck',p(0,0,floor-.14),(2*half,6,.28),'stone',C,angle)
 # Match the longitudinal grade of the two bank paths rather than setting
 # a level slab across a descending channel.
 for vi,v in enumerate(deck.data.vertices):
  station=float(L.nearest(np.array(v.co[:2])[None,:])[0][0]);v.co.z=float(L.water_z(station))+2.26-(.28 if vi<4 else 0)
 deck.data.update()
 G.roof(ident+' tiled roof',p(0,0,floor+5.5),(2*half+1,8),1.8,angle)
 for y in [-half+1,-width/2-.8,width/2+.8,half-1]:
  for x in [-2.55,2.55]:
   bottom=min(gz(p(x,y,0)[:2])-.3,floor-.2);G.beam(ident+' grounded post',[p(x,y,bottom),p(x,y,floor+5.5)],.17,'redwood',C)
 for side in [-1,1]:
  a=p(0,side*half,floor);b=p(0,side*(half+4),gz(p(0,side*(half+4),0)[:2])+.16);path(ident+' landward ramp',[a,b],3.5)
 data['bridges'].append({'id':ident,'s':st,'width':width,'half_span':half,'floor':floor})
# A continuous planted shoulder around the new west-bank route. Dense pockets
# flank open sightlines; every trunk and stone is rooted in the current terrain.
for gi,(st,dd0) in enumerate([(.207,-62),(.232,-70),(.255,-72),(.352,-55)]):
 t,n=L.basis(st);center=L.point(st,dd0)[:2]
 for j,(x,y) in enumerate([(-8,0),(-3,4),(4,2),(8,-2),(0,-5)]):
  xy=center+t*x+n*y;z=gz(xy);h=5.7+(j%3)*1.1
  G.beam(f'Shoulder grove {gi} rooted trunk',[(*xy,z-.3),(*(xy+t*.6),z+h)],.18,'wood',C)
  for k in range(3):oval(f'Shoulder grove {gi} layered crown',(*(xy+t*(k-1)*1.5+n*.6),z+h-.3*k),(3.6,2.7,1.25),'pine' if j%2 else 'leaf')
 for j in range(12):
  x=-13+j*2.2;y=4*math.sin(j*.9);xy=center+t*x+n*y;z=gz(xy)
  oval(f'Shoulder grove {gi} rooted undergrowth',(*xy,z+.15),(1.8,1.3,.75),'leaf')
  if j%3==0:oval(f'Shoulder grove {gi} embedded stone',(*(xy+n*1.8),gz(xy+n*1.8)-.3),(2.8,1.6,1.2),'rock')
# A usable lookout sits beside the planted saddle, not across a flight opening.
st=.23;xy=L.point(st,-58)[:2];t,n=L.basis(st);a=math.atan2(t[1],t[0]);f=max(gz(xy+t*x+n*y) for x in [-5,5] for y in [-4,4])+.2
G.box('Saddle lookout supported floor',(*xy,f-.3),(12,9,.6),'stone',C,a)
G.roof('Saddle lookout tiled roof',(*xy,f+5),(14,11),2,a)
for x in [-5,5]:
 for y in [-3.5,3.5]:
  pp=xy+t*x+n*y;G.beam('Saddle lookout grounded post',[(*pp,gz(pp)-.3),(*pp,f+5)],.19,'redwood',C)
G.box('Saddle lookout bench',(*(xy+n*2.5),f+.5),(7,.65,.35),'wood',C,a)
pp=L.point(st,-10,float(L.water_z(st))+2.26);end=np.r_[xy+t*(-5),f];length=np.linalg.norm(end[:2]-pp[:2]);steps=max(2,int(length/.45),int(abs(end[2]-pp[2])/.13));ang=math.atan2(*(end[:2]-pp[:2])[::-1])
for j in range(steps):
 p=pp+(end-pp)*(j+.5)/steps;bottom=min(gz(p[:2])-.2,p[2]-.3);G.box('Saddle lookout grounded access step',(*p[:2],(p[2]+bottom)/2),(length/steps+.03,2.1,p[2]-bottom),'stone',C,ang)
cloudcol=bpy.data.collections['05 Atmospheric envelope optional'];template=bpy.data.objects['Ink campus exit atmospheric veil'];data['cloud_veils']=[]
for st,dd0,rel in [(.225,-46,20),(.397,28,18),(.746,48,15)]:
 ob=template.copy();ob.data=template.data.copy();cloudcol.objects.link(ob);ob.name='Garden reveal thin cloud';ob.location=L.point(st,dd0,float(L.water_z(st))+rel);ob.scale=(23,13,9);ob.rotation_euler.z=math.atan2(L.basis(st)[0][1],L.basis(st)[0][0]);ob['physical']=False;data['cloud_veils'].append({'name':ob.name,'s':st,'d':dd0,'position':list(ob.location),'purpose':'small edge veil, not opaque scene replacement'})
# Cut only beneath the new garden steps. Padding covers terrain triangles
# crossing the narrow footprint, not just vertices already inside the stair.
gxy=np.array([v.co[:2] for v in ground.data.vertices]);gz0=np.array([v.co.z for v in ground.data.vertices]);gzz=gz0.copy()
for ob in C.objects:
 if 'grounded entrance step' not in ob.name and 'grounded access step' not in ob.name:continue
 vv=verts(ob);top=vv[4:8];a,b,c=top[:3];u=b[:2]-a[:2];u/=np.linalg.norm(u);n=np.array([-u[1],u[0]]);center=top[:,:2].mean(0);uv=(gxy-center)@np.column_stack([u,n]);half=np.max(abs((top[:,:2]-center)@np.column_stack([u,n])),axis=0)
 ids=np.where(np.all(abs(uv)<half+2.8,axis=1))[0];gzz[ids]=np.minimum(gzz[ids],float(top[:,2].mean())-.17)
for i,v in enumerate(ground.data.vertices):v.co.z=gzz[i]
ground.data.update();gb,_=bvh([ground]);data['terrain']['stair_cut_vertices']=int(np.sum(abs(gzz-gz0)>.001))
for ob in C.objects:
 if 'grounded entrance step' not in ob.name and 'grounded access step' not in ob.name:continue
 for v in list(ob.data.vertices)[:4]:v.co.z=min(v.co.z,gz(v.co[:2])-.25)
 ob.data.update()
data['relocated_plants']=[]
for name,shift in [('Rooted woodland understory.129',-7),('Rooted woodland understory.130',-7),('Rooted woodland understory.131',-7),('Grouped riparian shrub.009',14),('Grouped riparian shrub.011',14),('Grouped riparian shrub.012',14),('Grouped riparian shrub.095',14)]:
 ob=bpy.data.objects.get(name)
 if ob is None:continue
 vv=verts(ob);xy=vv[:,:2].mean(0);st0,dd0,_=L.nearest(xy[None,:]);n=L.basis(float(st0[0]))[1];delta=n*(shift if shift<0 else shift*np.sign(dd0[0]));oldheight=oldb.ray_cast(Vector((*xy,500)),Vector((0,0,-1)),1000)[0].z;newheight=gz(xy+delta);move=np.r_[delta,newheight-oldheight];ob.location+=Vector(move)
 data['relocated_plants'].append({'name':name,'delta':move.tolist(),'purpose':'clear new walking deck or stair; retain mesh and material'})
for j in range(95,100):
 stem=bpy.data.objects[f'Rooted bamboo culm.{j:03d}'];leaf=bpy.data.objects[f'Bamboo airy leaf crown.{j:03d}'];vv=verts(stem);xy=vv[:,:2].mean(0);st0=L.nearest(xy[None,:])[0][0];delta=L.basis(float(st0))[1]*(-7);oldheight=oldb.ray_cast(Vector((*xy,500)),Vector((0,0,-1)),1000)[0].z;move=np.r_[delta,gz(xy+delta)-oldheight]
 for ob in [stem,leaf]:
  ob.location+=Vector(move);data['relocated_plants'].append({'name':ob.name,'delta':move.tolist(),'purpose':'move bamboo stem and its crown together outside new stair cut; retain mesh and material'})
data['new_objects']=[o.name for o in C.objects]
print('GEOMETRY_READY',data['terrain'],len(C.objects),flush=True)
# Re-route by broad intentional arcs. Start, public dock view and destination
# retain their choreography. New headings are generated from the new path.
oldposes=json.loads((SRC/'route-poses.json').read_text('utf8'));oldp=np.array([p['position'] for p in oldposes]);st,ds,_=L.nearest(oldp[:,:2]);times=np.arange(1392)/24
knots=np.array([0,.12,.15,.17,.20,.25,.29,.33,.36,.40,.435,.467,.50,.53,.56,.61,.65,.69,.73,.765,.80,.84,.88,.915,.94,1.])
offsets=np.array([0,0,-25,-34,-42,-53,-37,-38,-12,34,40,48,42,18,-11,-18,-6,30,46,42,36,20,-23,-24,0,0.])
def cubic(x,xs,ys):
 slopes=np.gradient(ys,xs);i=np.clip(np.searchsorted(xs,x)-1,0,len(xs)-2);h=xs[i+1]-xs[i];u=np.clip((x-xs[i])/h,0,1)
 return (2*u**3-3*u**2+1)*ys[i]+(u**3-2*u*u+u)*h*slopes[i]+(-2*u**3+3*u*u)*ys[i+1]+(u**3-u*u)*h*slopes[i+1]
desired=cubic(st,knots,offsets);weight=smooth((times-4.8)/2)*(1-smooth((times-51.8)/2))
weight*=1-smooth((times-30)/2)*(1-smooth((times-39)/2))
nd=ds*(1-weight)+desired*weight;normals=np.array([L.basis(s)[1] for s in st]);positions=oldp.copy();positions[:,:2]+=normals*(nd-ds)[:,None]
physical=[o for o in S.objects if o.type=='MESH' and o.get('physical',False) and not o.hide_render];solid,names=bvh(physical)
# Required height over the actual roof/ground footprint, dilated ahead and
# behind then smoothly raised. This prevents single-frame roof avoidance hops.
need=np.zeros(1392)
for i,p in enumerate(positions):
 if weight[i]<.001:continue
 heights=[]
 for dx,dy in [(0,0),(-1.8,0),(1.8,0),(0,-1.8),(0,1.8)]:
  hit=solid.ray_cast(Vector((p[0]+dx,p[1]+dy,500)),Vector((0,0,-1)),1000)[0]
  if hit is not None:heights.append(hit.z)
 if heights:need[i]=max(0,max(heights)+4.8-p[2])
# Smooth upper envelope, never below the local clearance requirement.
lift=np.zeros_like(need)
for i in np.where(need>0)[0]:
 ids=np.arange(max(0,i-66),min(1392,i+67));shape=1-smooth(abs(ids-i)/66);lift[ids]=np.maximum(lift[ids],need[i]*shape)
kernel=np.exp(-.5*(np.arange(-12,13)/5)**2);kernel/=kernel.sum();lift=np.convolve(np.pad(lift,(12,12),mode='edge'),kernel,'valid');lift=np.maximum(lift,need)
positions[:,2]+=lift
# Keep the trajectory gently C2-like at mapped lateral boundaries.
kernel=np.exp(-.5*(np.arange(-15,16)/5)**2);kernel/=kernel.sum()
for j in range(3):positions[:,j]=np.convolve(np.pad(positions[:,j],(15,15),mode='edge'),kernel,'valid')
positions[:100]=oldp[:100];positions[1300:]=oldp[1300:]
for i in range(100,140):positions[i]=oldp[i]*(1-smooth((i-100)/40))+positions[i]*smooth((i-100)/40)
for i in range(1260,1300):positions[i]=positions[i]*(1-smooth((i-1260)/40))+oldp[i]*smooth((i-1260)/40)
qs=[]
for i,p in enumerate(positions):
 a=positions[max(0,i-8)];b=positions[min(1391,i+18)];v=b-a;v[2]-=np.linalg.norm(v[:2])*.10
 q=Vector(v).to_track_quat('-Z','Y');oldq=Quaternion(oldposes[i]['quaternion']);w=float(weight[i]);q=oldq.slerp(q,w)
 if qs and q.dot(qs[-1])<0:q.negate()
 qs.append(q)
qa=np.array([list(q) for q in qs]);sm=qa.copy()
for i in range(1392):
 ids=np.arange(max(0,i-10),min(1392,i+11));ww=np.exp(-.5*((ids-i)/5)**2);sm[i]=np.sum(qa[ids]*ww[:,None],axis=0)/sum(ww);sm[i]/=np.linalg.norm(sm[i])
poses=[];cam=S.camera;cam.animation_data_clear();cam.rotation_mode='QUATERNION'
for i,p in enumerate(oldposes):
 p['position']=positions[i].tolist();p['quaternion']=sm[i].tolist();poses.append(p);cam.location=positions[i];cam.rotation_quaternion=Quaternion(sm[i]);cam.keyframe_insert('location',frame=i+1);cam.keyframe_insert('rotation_quaternion',frame=i+1)
hits=[]
for i,(a,b) in enumerate(zip(positions,positions[1:])):
 v=Vector(b-a)
 if v.length<1e-8:continue
 for dx,dy,dz in [(x,y,z) for x in [-.65,0,.65] for y in [-.65,0,.65] for z in [-.4,0,.4]]:
  h=solid.ray_cast(Vector(a)+Vector((dx,dy,dz)),v.normalized(),v.length)
  if h[0] is not None:hits.append({'frame':i+1,'object':names[h[2]],'point':list(h[0])});break
delta=np.linalg.norm(np.diff(positions,axis=0),axis=1);angles=np.degrees(2*np.arccos(np.clip(abs(np.sum(sm[1:]*sm[:-1],axis=1)),0,1)))
data['flight']={'frames':1392,'seconds':58,'hits':hits,'max_step_m':float(delta.max()),'length_m':float(delta.sum()),'max_rotation_deg':float(angles.max()),'max_lift_m':float(lift.max()),'old_river_axis_median_distance_m':float(np.median(abs(ds))),'new_river_axis_median_distance_m':float(np.median(abs(L.nearest(positions[:,:2])[1]))),'knots_s':knots.tolist(),'target_offsets_m':offsets.tolist()}
(O/'route-poses.json').write_text(json.dumps(poses),encoding='utf8');(O/'design-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
S.frame_start=1;S.frame_end=1392;S.render.fps=24;S.frame_set(1)
S['v14_scope']='Cloud landmarks and garden thresholds; linked but visually segmented water; off-river 58s route'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'cloud-garden-route-58s-v14.blend'))
print('V14_READY',data['flight'],flush=True)
