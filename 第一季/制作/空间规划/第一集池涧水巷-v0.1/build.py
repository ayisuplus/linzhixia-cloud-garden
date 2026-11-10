import bpy,bmesh,sys,json,math,hashlib,random,re
from pathlib import Path
import numpy as np
from mathutils import Vector,Quaternion,Matrix
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D));import water_layout as W
L=W.L
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1'));import geometry as G
OLD=R/'视频制作/第一集云城校准-20261024-v0.1';O=R/'视频制作/第一集池涧水巷-20261024-v0.1';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OLD/'cloud-city-route-58s-v12.blend'));S=bpy.context.scene
def col(name):c=bpy.data.collections.new(name);S.collection.children.link(c);return c
BANK=col('21 Garden water edge clusters');GARDEN=col('22 Pocket water gardens')
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1].split(' [')[0]]=m
front=json.loads((R/'视频制作/第一集水巷街桥-20261024-v0.1/design-data.json').read_text('utf8'))['frontages']
raw={};groups={};group_for={}
def vertices(ob):
 x=np.empty(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',x);x=x.reshape(-1,3);m=np.array(ob.matrix_world);return x@m[:3,:3].T+m[:3,3]
def group_name(ob):
 name=ob.name;c=[c.name[:2] for c in ob.users_collection]
 if name=='Practice hall shore access':return None
 if '04' in c:return next((p['id'] for p in L.COURTS if name.startswith(p['id']+' ')),None)
 if '09' in c:return next((p['id'] for p in front if name.startswith(p['id']+' ')),None)
 if name.startswith(('H1 ','H2 ','H3 ')):return name[:2]+' whole mountain access group'
 if '19' in c:
  center=vertices(ob).mean(0);return min([p for p in L.COURTS if p['id'] in ['Zhixia-home','Repair-workshop']],key=lambda p:np.linalg.norm(center[:2]-p['center']))['id']
 if '16' in c:
  if name.startswith(('Dorm private','Dorm open','Dorm packing','Dorm desk','Dorm spare','Dorm doorway','Dorm threshold','Dorm door approach')):return 'Private dorm and doorway'
  if name.startswith(('Open practice','Practice hall','Practice barre')):return 'Practice pavilion'
  if name.startswith(('Dorm parcel','Dorm departure','Dorm jetty')):return 'Dorm berth'
 if '18' in c:
  if name.startswith(('Cloud ferry hull','Ferry canopy','Ferry light','Ferry passenger')):return 'Cloud ferry vehicle'
  if name.startswith('Public lift'):return 'Public lift tower'
 return None
for ob in S.objects:
 if ob.type!='MESH' or any(c.name.startswith('05 ') for c in ob.users_collection):continue
 raw[ob.name]=vertices(ob);g=group_name(ob)
 if g:groups.setdefault(g,[]).append(ob.name);group_for[ob.name]=g
zones=[];groupdelta={}
for name,members in groups.items():
 v=np.concatenate([raw[n] for n in members]);anchor=(v[:,:2].min(0)+v[:,:2].max(0))/2;delta=W.base_map(np.r_[anchor,0])[0,:2]-anchor;groupdelta[name]=delta
 # Floating vehicles and over-water berth keep dimensions but do not bend land.
 if name in ['Cloud ferry vehicle','Dorm berth','Practice pavilion']:continue
 zones.append({'id':name,'lo':(v[:,:2].min(0)-.25).tolist(),'hi':(v[:,:2].max(0)+.25).tolist(),'delta':delta.tolist(),'members':members})
records={'source_sha256':hashlib.sha256((OLD/'cloud-city-route-58s-v12.blend').read_bytes()).hexdigest(),'zones':zones,'rigid_groups':{n:{'members':v,'delta':groupdelta[n].tolist()} for n,v in groups.items()},'retained_clouds':[],'added_plants':[],'added_gardens':[]}
ground=bpy.data.objects['Continuous stable cloud terrain / river bed and inhabited slopes'];old_ground=raw[ground.name];old_faces=[tuple(f.vertices) for f in ground.data.polygons];old_slots=[f.material_index for f in ground.data.polygons];source_ground=BVHTree.FromPolygons([Vector(p) for p in old_ground],old_faces)
old_colors={}
for attr in ground.data.color_attributes:
 if attr.domain=='POINT':
  colors=np.empty(len(attr.data)*4);attr.data.foreach_get('color',colors);old_colors[attr.name]=colors.reshape(-1,4)
for ob in list(S.objects):
 if ob.type!='MESH':continue
 if ob.name not in raw:records['retained_clouds'].append(ob.name);continue
 a=raw[ob.name];g=group_for.get(ob.name)
 if g:b=a.copy();b[:,:2]+=groupdelta[g]
 else:b=W.mapped(a,zones)
 if ob.data.users>1:ob.data=ob.data.copy()
 inv=np.array(ob.matrix_world.inverted());b=b@inv[:3,:3].T+inv[:3,3];ob.data.vertices.foreach_set('co',b.ravel());ob.data.update()
print('MAPPED',len(raw),'rigid groups',len(groups),flush=True)
# Regenerate a single-valued heightfield. Horizontal patch blending is useful
# for links but can fold dense ground triangles at rigid-zone boundaries.
# Therefore terrain is freshly sampled in NEW XY; only heights are feathered.
xs=np.arange(-525,640,2.5);ys=np.arange(-790,950,2.5);xy=np.array([(x,y) for y in ys for x in xs]);ss,dd,_=L.nearest(xy);edge=np.where(dd>=0,L.extent(ss,1)-L.width(ss,1)+W.width(ss,1),L.extent(ss,-1)-L.width(ss,-1)+W.width(ss,-1));keep=np.abs(dd)<edge+10;ids=np.flatnonzero(keep);xy=xy[ids];query=W.inverse_base(np.column_stack([xy,np.zeros(len(xy))]));z=np.full(len(xy),np.nan);midx=np.zeros(len(xy),int);new_colors={name:np.tile(np.array(G.M['terrain'].diffuse_color),(len(xy),1)) for name in old_colors}
for i,p in enumerate(query):
 hit=source_ground.ray_cast(Vector((p[0],p[1],500)),Vector((0,0,-1)),1000)
 if hit[0] is not None:
  z[i]=hit[0].z;midx[i]=old_slots[hit[2]];faceids=list(old_faces[hit[2]]);weight=1/np.maximum(np.linalg.norm(old_ground[faceids,:2]-p[:2],axis=1)**2,1e-6);weight/=weight.sum()
  for name,colors in old_colors.items():new_colors[name][i]=np.sum(colors[faceids]*weight[:,None],axis=0)
for zone in zones:
 lo=np.array(zone['lo'])+zone['delta'];hi=np.array(zone['hi'])+zone['delta'];dist=np.maximum(np.maximum(lo-xy,xy-hi),0).max(1)
 for i in np.where(dist<12)[0]:
  p=xy[i]-zone['delta'];hit=source_ground.ray_cast(Vector((*p,500)),Vector((0,0,-1)),1000)
  if hit[0] is not None:
   t=float(1-W.smooth(dist[i]/12));z[i]=hit[0].z if not np.isfinite(z[i]) else z[i]*(1-t)+hit[0].z*t
valid=np.isfinite(z);index={int(i):j for j,i in enumerate(ids[valid])};vs=np.column_stack([xy[valid],z[valid]]);faces=[];fm=[];nx=len(xs);vm=midx[valid]
for i in ids[valid]:
 if i%nx==nx-1:continue
 q=[int(i),int(i+1),int(i+1+nx),int(i+nx)]
 if all(k in index for k in q):faces.append(tuple(index[k] for k in q));fm.append(int(vm[index[int(i)]]))
materials=list(ground.data.materials);me=bpy.data.meshes.new('v13 Regular XY garden terrain');me.from_pydata(vs,[],faces);me.update();ground.data=me
for mat in materials:me.materials.append(mat)
for f,mi in zip(me.polygons,fm):f.material_index=mi;f.use_smooth=True
for name,colors in new_colors.items():
 attr=me.color_attributes.new(name=name,type='FLOAT_COLOR',domain='POINT');attr.data.foreach_set('color',colors[valid].astype(np.float32).ravel())
records['terrain_rebuilt']={'regular_grid_metres':2.5,'vertices':len(vs),'faces':len(faces),'method':'inverse source sampling; rigid footprint source heights; height-only feathering; no horizontal face fold'}
print('TERRAIN_REGRID',len(vs),len(faces),flush=True)
# Spatially stretched links end exactly on the moved rigid platforms.
def rewrite_link(name,start,end,width):
 ob=bpy.data.objects.get(name)
 if ob is None:return
 for i,v in enumerate(ob.data.vertices):
  p=np.array(v.co);q=i//4;u=q/max(1,len(ob.data.vertices)//4-1);center=start*(1-u)+end*u;direction=end[:2]-start[:2];n=np.array([-direction[1],direction[0]])/np.linalg.norm(direction);v.co=(* (center[:2]+n*((-1 if i%4 in [0,2] else 1)*width/2)),center[2]-(.28 if i%4<2 else 0))
 ob.data.update()
def oldloc(s,side,x,q,z):t,n=L.basis(s);return np.r_[L.center(s)[0]+t*x+n*side*(L.width(s,side)+q),z]
s=.635;t,n=L.basis(s);start=W.mapped(oldloc(s,1,7,0,49.3),zones)[0];boat=oldloc(s,1,7,-15,49.3);boat[:2]+=groupdelta['Cloud ferry vehicle'];end=boat+np.r_[n*2.8,0];rewrite_link('Upper boarding bridge',start,end,2.5)
start=W.mapped(oldloc(.065,-1,0,7,98.26),zones)[0];end=oldloc(.065,-1,0,2,98.26);end[:2]+=groupdelta['Practice pavilion'];rewrite_link('Practice hall shore access',end,start,3)
start=W.mapped(oldloc(.018,1,0,4,98.26),zones)[0];end=oldloc(.018,1,0,-5,98.26);end[:2]+=groupdelta['Dorm berth'];rewrite_link('Dorm shipping jetty',start,end,3.4)
# Water-facing bridge profiles retain connected landings. Their original low
# rise is kept, and the shorter actual span is explicitly audited.
ground=bpy.data.objects['Continuous stable cloud terrain / river bed and inhabited slopes']
def getbvh(obs):
 vs=[];fs=[];names=[]
 for ob in obs:
  off=len(vs);v=vertices(ob);vs.extend(v);fs.extend(tuple(off+i for i in f.vertices) for f in ob.data.polygons);names.extend([ob.name]*len(ob.data.polygons))
 return BVHTree.FromPolygons([Vector(x) for x in vs],fs),names
# Actual court pads and walking surfaces own their occupied heights where
# feathered source regions overlap. Raised bridges/galleries do not fill earth.
roads=[o for o in S.objects if o.type=='MESH' and (o.name.startswith(('Continuous bank lane','Upper slope street','Bank to slope connector')) or o.name.endswith('entry connection'))]
pads=[o for o in S.objects if o.type=='MESH' and o.name.endswith('court floor')]
rb,_=getbvh(roads);pb,_=getbvh(pads);graded=0
# Extend the pad's cut below every triangle crossing its perimeter, rather
# than only modifying vertices already inside the floor's footprint.
gxy=np.array([v.co[:2] for v in ground.data.vertices]);gzvals=np.array([v.co.z for v in ground.data.vertices])
for pad in pads:
 pv=vertices(pad);pad.data.calc_loop_triangles();tris=[];reverse_tris=[]
 for tri in pad.data.loop_triangles:
  ids3=list(tri.vertices);a,b,c=pv[ids3];cross=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
  if cross>1e-8:tris.append(tuple(ids3))
  elif cross< -1e-8:reverse_tris.append(tuple(ids3))
 # Some historical trimmed pavings are one-sided, clockwise meshes. Their
 # real surface still constrains terrain; absence of CCW faces is not absence.
 if not tris:tris=reverse_tris
 if not tris:continue
 flat=[Vector((x,y,0)) for x,y,z0 in pv];foot=BVHTree.FromPolygons(flat,tris,all_triangles=True);lo=pv[:,:2].min(0)-4;hi=pv[:,:2].max(0)+4;mask=np.all((gxy>=lo)&(gxy<=hi),axis=1)
 for i in np.where(mask)[0]:
  hit=foot.find_nearest(Vector((*gxy[i],0)),4.0)
  if hit[0] is None:continue
  a,b,c=pv[list(tris[hit[2]])];uv=np.linalg.solve(np.column_stack([b[:2]-a[:2],c[:2]-a[:2]]),np.array(hit[0])[:2]-a[:2]);height=a[2]+uv[0]*(b[2]-a[2])+uv[1]*(c[2]-a[2]);gzvals[i]=min(gzvals[i],height-.13)
for i,v in enumerate(ground.data.vertices):v.co.z=gzvals[i]
for v in ground.data.vertices:
 p=v.co;hit=pb.ray_cast(Vector((p.x,p.y,500)),Vector((0,0,-1)),1000)[0]
 if hit is not None:p.z=min(p.z,hit.z-.12);graded+=1
 heights=[]
 for dx,dy in [(0,0),(-2.6,0),(2.6,0),(0,-2.6),(0,2.6),(-2.6,-2.6),(-2.6,2.6),(2.6,-2.6),(2.6,2.6)]:
  hit=rb.ray_cast(Vector((p.x+dx,p.y+dy,500)),Vector((0,0,-1)),1000)[0]
  if hit is not None:heights.append(hit.z)
 if heights and p.z>min(heights)-1.5:p.z=min(p.z,min(heights)-.15);graded+=1
ground.data.update();records['terrain_rebuilt']['pad_road_height_samples']=graded
gb,_=getbvh([ground]);physical=[o for o in S.objects if o.type=='MESH' and o.get('physical',False) and not o.hide_render and o!=ground];solid,solidnames=getbvh(physical)
def gz(xy):
 h=gb.ray_cast(Vector((*xy,500)),Vector((0,0,-1)),1000)[0];return float(h.z) if h is not None else None
# Rebuild camera aiming through transformed scene directions, then smooth
# adjacent viewing rotations. No new orbit or isolated framing hoop.
poses=json.loads((OLD/'route-poses.json').read_text('utf8'));oldp=np.array([p['position'] for p in poses]);mappedp=W.mapped(oldp,zones)
# Rigid footprint boundaries can introduce jumps into pointwise mapped camera
# samples even when the geometry is usable. Smooth the entire 3D curve, keeping
# exact endpoint positions, then independently sweep the resulting route.
kernel=np.exp(-.5*(np.arange(-30,31)/10.)**2);kernel/=kernel.sum();newp=np.column_stack([np.convolve(np.pad(mappedp[:,j],(30,30),mode='edge'),kernel,mode='valid') for j in range(3)])
startfix=mappedp[0]-newp[0];endfix=mappedp[-1]-newp[-1]
for i in range(len(newp)):newp[i]+=startfix*(1-W.smooth(i/60))+endfix*W.smooth((i-1331)/60)
# City orientation and longitudinal axis are unchanged. Retain the established
# viewing choreography instead of projecting a short ray through patch seams.
qs=[Quaternion(p['quaternion']) for p in poses]
for i in range(1,len(qs)):
 if qs[i].dot(qs[i-1])<0:qs[i].negate()
arr=np.array([list(q) for q in qs]);sm=arr.copy()
for i in range(len(arr)):
 ids=np.arange(max(0,i-8),min(len(arr),i+9));weight=np.exp(-((ids-i)/4)**2);sm[i]=np.sum(arr[ids]*weight[:,None],axis=0)/sum(weight);sm[i]/=np.linalg.norm(sm[i])
for i,p in enumerate(poses):p['position']=newp[i].tolist();p['quaternion']=sm[i].tolist()
cam=S.camera;cam.animation_data_clear()
for i,p in enumerate(poses):
 cam.location=p['position'];cam.rotation_quaternion=Quaternion(p['quaternion']);cam.keyframe_insert('location',frame=i+1);cam.keyframe_insert('rotation_quaternion',frame=i+1)
S.frame_set(1)
def oval(name,pos,scale,key,c):
 me=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);c.objects.link(ob);ob.location=pos;ob.scale=scale;me.materials.append(G.M[key]);ob['physical']=True
 for v in me.vertices:v.co*=1+.07*math.sin(v.co.x*8+v.co.y*7+v.co.z*6)
 for f in me.polygons:f.use_smooth=True
 return ob
rng=random.Random(24102413)
def free(xy,r,h):
 z=gz(xy)
 if z is None:return None
 if np.min(np.linalg.norm((newp-np.r_[xy,z+h*.5])/np.array([r+2.5,r+2.5,h*.5+2]),axis=1))<1:return None
 for d in [(0,0),(-r,0),(r,0),(0,-r),(0,r)]:
  p=Vector((xy[0]+d[0],xy[1]+d[1],z+.3));hit=solid.ray_cast(p,Vector((0,0,1)),h+1)
  if hit[0] is not None:return None
 return z
# Planting is in grouped bank pockets with open gaps, not a continuous hedge.
for k,(st,side) in enumerate([(.032,-1),(.082,1),(.145,-1),(.172,1),(.231,-1),(.258,1),(.316,-1),(.335,1),(.39,-1),(.415,1),(.445,-1),(.535,1),(.565,-1),(.705,1),(.75,-1),(.80,1),(.835,-1),(.92,1)]):
 for j in range(7):
  s=st+rng.uniform(-.004,.004);q=rng.uniform(.6,2.6);p=W.mapped(oldloc(s,side,0,q,0),zones)[0];r=rng.uniform(.4,.85);z=free(p[:2],r,1.6)
  if z is None:continue
  oval('Grouped riparian shrub',(*p[:2],z+.12),(r,r*.78,r*.7),'leaf' if j%3 else 'pine',BANK);records['added_plants'].append({'type':'bank shrub','center':[float(p[0]),float(p[1]),z],'r':r})
 for j in range(3):
  p=W.mapped(oldloc(st+(j-1)*.002,side,0,.3,0),zones)[0];z=free(p[:2],1,2)
  if z is not None:oval('Bank rooted rock cluster',(*p[:2],z-.15),(1.15,.85,.7),'rock',BANK)
 # One small leaning tree in selected wider land pockets.
 if k%3==0:
  p=W.mapped(oldloc(st,side,0,3.1,0),zones)[0];z=free(p[:2],1.5,5)
  if z is not None:
   t,n=L.basis(st);top=p[:2]-n*side*.8;G.beam('Water garden leaning trunk',[(*p[:2],z-.2),(*top,z+4.2)],.13,'wood',BANK);oval('Water garden airy crown',(*top,z+4.3),(1.7,1.4,.9),'pine',BANK);records['added_plants'].append({'type':'leaning bank tree','center':[float(p[0]),float(p[1]),z]})
# A few planted stone ledges obscure the connecting runnel; the water continues
# underneath them and is caught downstream instead of ending in empty sky.
for st,side in [(.151,1),(.228,-1),(.318,1),(.391,-1)]:
 p=W.mapped(oldloc(st,side,0,.6,0),zones)[0];z=gz(p[:2]);t,n=L.basis(st)
 if z is not None and free(p[:2],1.2,2) is not None:
  oval('Runnel side rock shoulder',(*p[:2],z-.35),(2.8,1.15,1.1),'rock',BANK)
# Small off-line garden pools and sheltered seats occupy the land between
# village courts and the bank path. Narrow covered channels return to the runnel.
G.ARCH=GARDEN
for st,side in [(.445,-1),(.535,1),(.705,1),(.80,-1)]:
 t,n=L.basis(st);n=n*side;p=W.mapped(oldloc(st,side,11,18,0),zones)[0];samples=[];clear=True
 for x in [-6,0,6]:
  for y in [-4.5,0,4.5,7]:
   xy=p[:2]+t*x+n*y;zz=gz(xy)
   if zz is None:clear=False;continue
   samples.append(zz);near=solid.find_nearest(Vector((*xy,zz+.2)),.65)
   if near[0] is not None:clear=False
   if free(xy,.5,5) is None:clear=False
 if not clear or max(samples)-min(samples)>1.8:continue
 f=max(samples)+.22;a=math.atan2(t[1],t[0]);ident=f'Pocket pool {st:.3f}'
 def pp(x,y,z):return np.r_[p[:2]+t*x+n*y,z]
 G.box(ident+' planted garden foundation',pp(0,0,(f+min(samples)-.25)/2),(13,9,f-min(samples)+.25),'stone',GARDEN,a)
 G.box(ident+' recessed basin',pp(0,0,f+.10),(8.5,5.2,.2),'stone',GARDEN,a)
 G.box(ident+' still garden water',pp(0,0,f+.22),(8,4.7,.035),'water',GARDEN,a)
 for x in [-4.4,4.4]:G.box(ident+' rim',pp(x,0,f+.32),(.32,5.7,.44),'stone',GARDEN,a)
 for y in [-2.7,2.7]:G.box(ident+' rim',pp(0,y,f+.32),(8.8,.32,.44),'stone',GARDEN,a)
 # Low open shelter stands on real ground beside the pond; no circulation hoop.
 roofp=pp(0,5.9,f+4.5);G.roof(ident+' waterside shelter',roofp,(10,3.6),1.1,a)
 for x in [-4,4]:
  for y in [4.7,7.1]:
   xy=pp(x,y,0)[:2];zz=gz(xy);G.beam(ident+' grounded shelter post',[(*xy,zz-.2),(*xy,f+4.5)],.13,'wood',GARDEN)
 G.box(ident+' sitting bench',pp(0,5.8,f+.55),(6,.8,.3),'wood',GARDEN,a)
 for x in [-5.3,5.3]:oval(ident+' garden planting',pp(x,1,f+.25),(1,1.4,.55),'leaf',GARDEN)
 # The channel is hidden below the existing bank walk at the crossing.
 ca=W.mapped(oldloc(st,side,11,10,0),zones)[0];cb=W.mapped(oldloc(st,side,11,-.1,0),zones)[0];ca[2]=float(L.water_z(st))+1.9;cb[2]=float(L.water_z(st))+.03
 G.beam(ident+' covered return channel',[pp(0,-2.8,f+.16),ca],.18,'stone',GARDEN)
 G.beam(ident+' downstream clean-water return',[ca,cb],.15,'water',GARDEN)
 records['added_gardens'].append({'id':ident,'station':st,'side':side,'center':p[:2].tolist(),'floor':f,'kind':'small still pool with covered return, planted rim and grounded waterside shelter; no water simulation'})
# Three small rock-side basins discharge visibly into the lower runnel. Their
# water is above retained support geometry and below the stone rims.
for st,side in [(.205,-1),(.29,1),(.365,-1)]:
 t,n=L.basis(st);n*=side;p=W.mapped(oldloc(st,side,0,2,0),zones)[0];zz=free(p[:2],1.7,2.5)
 if zz is None:continue
 a=math.atan2(t[1],t[0]);f=zz+.16;ident=f'Rock-side cascade {st:.3f}'
 def rp(x,y,z):return np.r_[p[:2]+t*x+n*y,z]
 G.box(ident+' grounded basin',rp(0,0,f-.12),(4.2,3.2,.45),'rock',GARDEN,a)
 G.box(ident+' quiet upper water',rp(0,0,f+.14),(3.7,2.7,.04),'water',GARDEN,a)
 for x in [-2,2]:G.box(ident+' side rim',rp(x,0,f+.25),(.25,3.3,.5),'rock',GARDEN,a)
 G.box(ident+' rear rim',rp(0,1.55,f+.25),(4.2,.25,.5),'rock',GARDEN,a)
 for x in [-1.35,1.35]:G.box(ident+' split front rim',rp(x,-1.55,f+.25),(1.45,.25,.5),'rock',GARDEN,a)
 bottom=float(L.water_z(st))+.05;G.box(ident+' visible drop',rp(0,-1.65,(f+.14+bottom)/2),(1.1,.09,f+.14-bottom),'water',GARDEN,a)
 outlet=W.mapped(oldloc(st,side,0,-.6,bottom),zones)[0];G.beam(ident+' lower receiving run',[rp(0,-1.65,bottom),outlet],.22,'water',GARDEN)
 for x in [-2.4,2.4]:oval(ident+' rooted rock',rp(x,.4,zz+.1),(.9,1.3,.65),'rock',GARDEN)
 records['added_gardens'].append({'id':ident,'station':st,'side':side,'center':p[:2].tolist(),'floor':f,'kind':'small upper rock basin, actual vertical drop and receiving runnel; no flow simulation'})
# Interior pools bind the retained courtyard rooms to water directly. They sit
# inside real existing courtyards rather than occupying the public bank path.
for group,st in [('West-neighbourhood',.467),('East-neighbourhood',.519),('Lower-lane',.808)]:
 court=min([p for p in L.COURTS if p['group']==group],key=lambda p:abs(p['s']-st));name=court['id'];t=np.array(court['tangent']);n=np.array(court['outward']);center=np.array(court['center'])+groupdelta[name];f=court['floor'];a=math.atan2(t[1],t[0]);ident=name+' enclosed garden pool'
 def cp(x,y,z):return np.r_[center+t*x+n*y,z]
 G.box(ident+' shallow basin',cp(0,-2,f+.17),(6.4,8.8,.10),'stone',GARDEN,a)
 G.box(ident+' still water',cp(0,-2,f+.24),(5.8,8.2,.025),'water',GARDEN,a)
 for x in [-3.1,3.1]:G.box(ident+' stone rim',cp(x,-2,f+.3),(.2,8.8,.24),'stone',GARDEN,a)
 for y in [-6.3,2.3]:G.box(ident+' stone rim',cp(0,y,f+.3),(6.4,.2,.24),'stone',GARDEN,a)
 for x,y in [(-5,-6),(5,2)]:oval(ident+' planted corner',cp(x,y,f+.25),(1,1.4,.7),'leaf',GARDEN)
 G.box(ident+' sitting edge',cp(4.9,-2,f+.55),(.65,3,.35),'wood',GARDEN,a)
 records['added_gardens'].append({'id':ident,'court':name,'station':court['s'],'center':center.tolist(),'floor':f,'kind':'small still courtyard pool; retained rooms frame it; concealed return is reserved, not simulated'})
water=bpy.data.objects['Main water spine / upstream to downstream collection'];wv=vertices(water).reshape(-1,2,3);widths=np.linalg.norm(wv[:,1,:2]-wv[:,0,:2],axis=1);ow=raw[water.name].reshape(-1,2,3)
def plan_area(v):
 a=v[:-1,0,:2];b=v[:-1,1,:2];c=v[1:,1,:2];d=v[1:,0,:2];return float(np.sum(abs(np.cross(b-a,c-a))*.5+abs(np.cross(c-a,d-a))*.5))
records['actual_water']={'section_count':len(wv),'min_width_m':float(widths.min()),'max_width_m':float(widths.max()),'old_plan_area_m2':plan_area(ow),'new_plan_area_m2':plan_area(wv),'samples':[{'s':i/(len(wv)-1),'width_m':float(widths[i]),'banks':wv[i].tolist()} for i in range(0,len(wv),5)]}
records['width_samples']=[{'s':float(s),'old_full':float(L.width(s,1)+L.width(s,-1)),'target_full':float(W.full_width(s)),'z':float(L.water_z(s))} for s in np.linspace(0,1,201)]
records['flight']={'frames':1392,'seconds':58,'scope':'mapped positions, transformed and smoothed view directions; independently audit before render'}
(O/'route-poses.json').write_text(json.dumps(poses),encoding='utf8');(O/'water-design-data.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
S['v13_scope']='Garden ponds, narrow runnels, intimate water lanes and one public bay; dimensions inferred';S.frame_start=1;S.frame_end=1392;S.render.fps=24
bpy.ops.wm.save_as_mainfile(filepath=str(O/'pond-lane-route-58s-v13.blend'));print('V13_READY',len(S.objects),len(zones),len(records['added_plants']),flush=True)
