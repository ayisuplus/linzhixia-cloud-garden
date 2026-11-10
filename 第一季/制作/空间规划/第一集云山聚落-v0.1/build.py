"""Terrain-bound cloud hamlets; preserve v10 camera poses and existing palette."""
import bpy,bmesh,sys,json,math,random,hashlib,shutil
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1'));import geometry as G
sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
OLD=R/'视频制作/第一集山谷植物-20261024-v0.1';O=R/'视频制作/第一集云山聚落-20261024-v0.1';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OLD/'valley-masterplan-v10.blend'));S=bpy.context.scene
removed=[]
for name in ['12 Valley stone outcrops','13 Valley pine and bamboo','14 Valley shrubs and moss']:
 c=bpy.data.collections.get(name)
 if c:
  for ob in list(c.objects):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
  bpy.data.collections.remove(c)
def col(name):
 c=bpy.data.collections.new(name);S.collection.children.link(c);return c
TREE=col('12 Contour woodland and understory');HOUSE=col('13 Hillside inhabited terraces');STAIR=col('14 Bank to hillside stepped access');ROCK=col('15 Terrain rooted rock seams');G.ARCH=HOUSE
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1]]=m
G.M['moss']=bpy.data.materials['Valley moss using retained leaf and terrain']
rng=random.Random(24102411);records=[];houses=[];stairs=[];roots=[]
poses=json.loads((OLD/'route-poses.json').read_text('utf8'));flight=np.array([p['position'] for p in poses])
plan=json.loads((R/'视频制作/第一集山水总图白模-20261024-v0.1/layout-plan.json').read_text('utf8'))
roads=[(np.array(p['points'])[:,:2],p['width']/2) for p in plan['paths']]
bounds=[]
for name in ['04 Contour courtyard clusters','09 Waterfront streets and inhabited bridgeheads','10 Connected bridges and quays']:
 for ob in bpy.data.collections[name].objects:
  if ob.type=='MESH' and not ob.hide_render:
   v=np.array([ob.matrix_world@Vector(x) for x in ob.bound_box]);bounds.append((v[:,:2].min(0),v[:,:2].max(0)))
bound_a=np.array([a for a,b in bounds]);bound_b=np.array([b for a,b in bounds]);road_bounds=[(p.min(0)-w-4,p.max(0)+w+4) for p,w in roads]
def path_dist(xy,pts):
 a=pts[:-1];d=np.diff(pts,axis=0);u=np.clip(np.sum((xy-a)*d,axis=1)/np.maximum(np.sum(d*d,axis=1),1e-9),0,1)
 return np.linalg.norm(xy-a-u[:,None]*d,axis=1).min()
def protected(xy,r=0):
 for (p,w),(a,b) in zip(roads,road_bounds):
  if np.any(xy<a-r) or np.any(xy>b+r):continue
  if path_dist(xy,p)<w+3+r:return True
 return bool(np.any(np.linalg.norm(np.maximum(np.maximum(bound_a-xy,xy-bound_b),0),axis=1)<r+3))
ground=bpy.data.objects['Continuous stable cloud terrain / river bed and inhabited slopes'];original=np.array([v.co[:] for v in ground.data.vertices]);ss,dd,_=L.nearest(original[:,:2]);side=np.where(dd>=0,1,-1);qq=np.abs(dd)-np.array([float(L.width(s,int(k))) for s,k in zip(ss,side)])
changed=[];protected_count=0
for i in np.where((ss>.14)&(ss<.42)&(qq>16)&(qq<100))[0]:
 s=float(ss[i]);q=float(qq[i]);xy=original[i,:2]
 if protected(xy):protected_count+=1;continue
 fade=math.sin(math.pi*np.clip((s-.14)/.28,0,1))**.6*min(1,(q-16)/12)*min(1,(100-q)/18)
 ridge=sum(6.5*math.exp(-((s-(a+.007*math.sin(q*.08+a*31)))/.009)**2)*math.exp(-((q-65)/28)**2) for a in ([.165,.235,.325,.398] if side[i]>0 else [.182,.252,.336,.402]))
 delta=fade*(ridge+1.1*math.sin(s*133+q*.12))
 newz=original[i,2]+delta
 if np.linalg.norm((flight-np.r_[xy,newz])/np.array([5,5,5]),axis=1).min()<1.5:continue
 ground.data.vertices[i].co.z=newz;changed.append(int(i))
ground.data.update()
print('TERRAIN_READY',len(changed),flush=True)
gb=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[tuple(f.vertices) for f in ground.data.polygons])
def gz(xy):
 hit=gb.ray_cast(Vector((*xy,500)),Vector((0,0,-1)),1000)
 if hit[0] is None:raise ValueError(('No terrain',xy))
 return hit[0].z
def slope(xy):return np.linalg.norm([(gz(xy+np.array([1,0]))-gz(xy-np.array([1,0])))/2,(gz(xy+np.array([0,1]))-gz(xy-np.array([0,1])))/2])
# Interpolated vertex colors avoid grid-shaped material boundaries in flight.
colors=np.tile(np.array(G.M['terrain'].diffuse_color),(len(original),1));rockcolor=np.array(G.M['rock'].diffuse_color);green=np.array(G.M['leaf'].diffuse_color)
for i in changed:
 s=float(ss[i]);q=float(qq[i]);fade=min(1,(q-16)/12)*min(1,(100-q)/23)*min(1,(s-.14)/.02)*min(1,(.42-s)/.02)
 rib=sum(math.exp(-((s-(a+.007*math.sin(q*.08+a*31)))/.012)**2) for a in ([.165,.235,.325,.398] if side[i]>0 else [.182,.252,.336,.402]))
 wr=min(.90,rib*.82)*math.exp(-((q-65)/32)**2)*fade
 wg=.82*math.exp(-((q-37)/23)**2)*(.63+.37*math.sin(s*92+side[i]+q*.06))*fade*(1-wr)
 colors[i]=colors[i]*(1-wr-wg)+rockcolor*wr+green*wg;colors[i,3]=1
attr=ground.data.color_attributes.new(name='Contour strata color',type='FLOAT_COLOR',domain='POINT');attr.data.foreach_set('color',colors.astype(np.float32).ravel())
mat=G.M['terrain'].copy();mat.name='Integrated terrain retaining rock and leaf palette';node=mat.node_tree.nodes.new('ShaderNodeAttribute');node.attribute_name=attr.name
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');mat.node_tree.links.new(node.outputs['Color'],bsdf.inputs['Base Color']);ground.data.materials.append(mat);slot=len(ground.data.materials)-1
painted={'interpolated_ground_faces':0};altered=set(changed)
for f in ground.data.polygons:
 if any(i in altered for i in f.vertices):f.material_index=slot;painted['interpolated_ground_faces']+=1
def pos(s,side,q):return L.point(s,side*(float(L.width(s,side))+q))[:2]
def ellipsoid(name,xyz,scale,key,c):
 me=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);c.objects.link(ob);ob.location=xyz;ob.scale=scale
 for v in me.vertices:v.co*=1+.10*math.sin(v.co.x*7+v.co.y*4+v.co.z*9)
 for f in me.polygons:f.use_smooth=True
 me.materials.append(G.M[key]);ob['physical']=True;return ob
new_paths=[];house_bounds=[]
def make_house(gid,s,side,q,xoffset,length):
 origin=pos(s,side,0);t,n=L.basis(s);out=n*side;xy=origin+t*xoffset+out*q;angle=math.atan2(t[1],t[0]);depth=12
 def pt(x,y,z):return np.r_[xy+t*x+out*y,z]
 samples=[gz(pt(x,y,0)[:2]) for x in np.linspace(-length/2,length/2,7) for y in [-depth/2,0,depth/2]]
 floor=max(samples)+.45;wallh=5.8
 G.box(gid+' deck',(*xy,floor-.23),(length,depth,.46),'wood',HOUSE,angle)
 postdata=[]
 for x in [-length/2+.8,0,length/2-.8]:
  for y in [-depth/2+.7,depth/2-.7]:
   p=pt(x,y,0);z=gz(p[:2]);G.box(gid+' grounded stilt',(*p[:2],(z-.35+floor)/2),(.5,.5,floor-z+.35),'wood',HOUSE,angle);postdata.append({'xy':p[:2].tolist(),'bottom':z-.35,'top':floor})
 # Visible masonry footing follows the uphill edge instead of hanging over the slope.
 for x in np.linspace(-length/2+.6,length/2-.6,12):
  p=pt(x,depth/2-.55,0);z=gz(p[:2]);G.box(gid+' hillside stone footing',(*p[:2],(z+floor-.3)/2),(length/11,1.1,max(.2,floor-z+.3)),'stone',HOUSE,angle)
 for xa,xb in [(-length/2+.8,0),(0,length/2-.8)]:
  a=pt(xa,-depth/2+.7,0);b=pt(xb,-depth/2+.7,floor-.6);a[2]=gz(a[:2])+.5
  G.beam(gid+' downhill cross brace',[a,b],.18,'wood',HOUSE)
 # The room sits back on the terrace; front door is a real gap in the wall.
 roomlength=length-3;back=4.8;front=-2.8
 for x in [-roomlength/2,roomlength/2]:G.box(gid+' side wall',pt(x,(back+front)/2,floor+wallh/2),(.35,back-front,wallh),'wall',HOUSE,angle)
 G.box(gid+' back wall',pt(0,back,floor+wallh/2),(roomlength,.35,wallh),'wall',HOUSE,angle)
 for xsign in [-1,1]:
  span=(roomlength-3)/2;cx=xsign*(1.5+span/2)
  G.box(gid+' front wall beside opening',pt(cx,front,floor+wallh/2),(span,.35,wallh),'wall',HOUSE,angle)
  G.box(gid+' lattice window',pt(cx,front-.22,floor+3.1),(max(2,span-1.3),.13,2.7),'window',HOUSE,angle)
  for dx in np.linspace(-max(2,span-1.3)/2,max(2,span-1.3)/2,5):G.box(gid+' window lattice',pt(cx+dx,front-.32,floor+3.1),(.11,.12,2.8),'wood',HOUSE,angle)
 G.box(gid+' doorway lintel',pt(0,front,floor+5.1),(3.2,.42,1.4),'wood',HOUSE,angle)
 G.box(gid+' room floor',pt(0,1,floor+.02),(roomlength,7.5,.08),'wood',HOUSE,angle)
 G.roof(gid+' swept tiled roof',pt(0,1,floor+wallh),(length+1,11),2.2,angle)
 for x in [-length/2+.5,0,length/2-.5]:G.beam(gid+' veranda support',[pt(x,-5.3,floor),pt(x,-5.3,floor+wallh)],.17,'redwood',HOUSE)
 G.beam(gid+' balcony handrail',[pt(-length/2,-5.7,floor+1.1),pt(length/2,-5.7,floor+1.1)],.11,'wood',HOUSE)
 for x in np.linspace(-length/2,length/2,12):G.beam(gid+' balcony baluster',[pt(x,-5.7,floor),pt(x,-5.7,floor+1.1)],.08,'wood',HOUSE)
 rec={'id':gid,'s':s,'side':side,'q':q,'xoffset':xoffset,'center':xy.tolist(),'floor':floor,'length':length,'depth':depth,'posts':postdata,'door':pt(0,front,floor).tolist(),'side_entry':pt(-length/2,0,floor).tolist()};houses.append(rec)
 house_bounds.append((xy,t,out,length/2+2,depth/2+2))
 return rec
def connect(name,points):
 # Each segment is an actual flight of steps with a landing and side guardrails.
 steps=[];route=[]
 for j,(a,b) in enumerate(zip(points,points[1:])):
  a=np.array(a);b=np.array(b);length=np.linalg.norm(b[:2]-a[:2]);n=max(2,int(math.ceil(length/.4)),int(math.ceil(abs(b[2]-a[2])/.11)));xy=np.linspace(a[:2],b[:2],n+1)
  travel=np.linspace(0,length,n+1);lead=min(2.1,length*.18);u=np.clip((travel-lead)/(length-2*lead),0,1);zz=a[2]+(b[2]-a[2])*u
  angle=math.atan2(*(b[:2]-a[:2])[::-1]);normal=np.array([-math.sin(angle),math.cos(angle)])
  for k in range(n):
   p=(xy[k]+xy[k+1])/2;top=(zz[k]+zz[k+1])/2;bottom=min(top-.3,min(gz(p+normal*d) for d in [-1.2,0,1.2])-.2);ob=G.box(name+' stone step',(*p,(top+bottom)/2),(length/n+.035,2.4,top-bottom),'stone',STAIR,angle)
   steps.append({'name':ob.name,'top':top,'center':p.tolist(),'going':length/n})
  ids=[k for k in range(n+1) if travel[k]>lead and travel[k]<length-lead and not(j==0 and 'bank approach' in name and travel[k]<6)]
  for si in [-1,1]:
   if len(ids)>1:G.beam(name+' stair handrail',[np.r_[xy[k]+normal*si*1.25,zz[k]+1.05] for k in ids],.07,'wood',STAIR)
  # Flat, open turning landings prevent successive stair flights crossing overhead.
  if j>0:G.box(name+' turning landing',a-np.array([0,0,.15]),(3.0,3.0,.3),'stone',STAIR,angle)
  route.extend([np.r_[p,z].tolist() for p,z in zip(xy,zz)])
 G.box(name+' arrival landing',np.array(points[-1])-np.array([0,0,.15]),(2.6,2.6,.3),'stone',STAIR,angle)
 stairs.append({'id':name,'points':route,'steps':steps,'max_rise':float(np.abs(np.diff(np.array(route)[:,2])).max())});new_paths.append(np.array(route)[:,:2])
for idx,(s,side,dx) in enumerate([(.199,1,-19),(.284,-1,23),(.374,1,-24)]):
 print('BUILD_HAMLET',idx+1,flush=True)
 lower=make_house(f'H{idx+1} lower',s,side,38,0,23 if idx!=1 else 19);upper=make_house(f'H{idx+1} upper',s,side,61,dx,18)
 origin=pos(s,side,0);t,n=L.basis(s);out=n*side
 def pp(x,q,z=None):
  p=origin+t*x+out*q
  if q==7:
   st=float(L.nearest(p)[0][0]);p=pos(st,side,7);z=float(L.water_z(st))+2.26
  return np.r_[p,gz(p)+.15 if z is None else z]
 xend=-lower['length']/2
 connect(f'H{idx+1} bank approach',[pp(-28,7),pp(-30,22),pp(-25,31),pp(xend,38,lower['floor'])])
 # Upper house direction differs by hamlet, avoiding repeated identical terraces.
 ux=dx-upper['length']/2
 upperpath=[pp(xend,38,lower['floor']),pp(xend-10,43),pp(ux-12,48),pp(ux-12,61),pp(ux,61,upper['floor'])] if dx<0 else [pp(xend,38,lower['floor']),pp(xend-9,45),pp(ux-12,54),pp(ux,61,upper['floor'])]
 connect(f'H{idx+1} uphill steps',upperpath)
# Cut a small continuous bench under the full stair width, including turning landings.
# Road geometry and its protected terrain remain untouched.
graded=[]
for route in stairs:
 pts=np.array(route['points']);lo=pts[:,:2].min(0)-3;hi=pts[:,:2].max(0)+3
 for i in np.where(np.all((original[:,:2]>=lo)&(original[:,:2]<=hi),axis=1))[0]:
  xy=original[i,:2]
  if protected(xy):continue
  a=pts[:-1,:2];d=np.diff(pts[:,:2],axis=0);u=np.clip(np.sum((xy-a)*d,axis=1)/np.maximum(np.sum(d*d,axis=1),1e-9),0,1);dist=np.linalg.norm(xy-a-u[:,None]*d,axis=1);k=int(dist.argmin())
  if dist[k]>2.8:continue
  near=dist<2.8;caps=pts[:-1,2]*(1-u)+pts[1:,2]*u-.6;cap=float(caps[near].min())
  current=ground.data.vertices[int(i)].co.z;weight=min(1,max(0,(2.8-dist[k])/.4));newz=current+(min(current,cap)-current)*weight
  if newz<current-.001:ground.data.vertices[int(i)].co.z=newz;graded.append(int(i))
ground.data.update();gb=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[tuple(f.vertices) for f in ground.data.polygons]);changed=sorted(set(changed+graded))
for ob in STAIR.objects:
 if ob.type!='MESH' or ('stone step' not in ob.name and 'landing' not in ob.name):continue
 top=max(v.co.z for v in ob.data.vertices)
 for v in list(ob.data.vertices)[:4]:v.co.z=min(top-.3,gz(np.array(v.co[:2]))-.25)
 ob.data.update()
rock_centers=[]
for ix,(s,side,q0,q1) in enumerate([(.162,1,27,59),(.232,1,35,77),(.265,-1,29,65),(.319,1,32,70),(.353,-1,29,67),(.403,1,31,72)]):
 vs=[];fs=[];long=29;cross=13
 for j in range(long):
  u=j/(long-1);q=q0+(q1-q0)*u;st=s+.005*math.sin(u*7.7+ix);center=pos(st,side,q);t,n=L.basis(st);width=10*(.12+.88*math.sin(math.pi*u)**.55)*(1+.24*math.sin(u*19+ix))
  for k in range(cross):
   v=2*k/(cross-1)-1;xy=center+t*(v*width);h=(4.4+1.6*math.cos(u*19+ix+v*3))*math.sin(math.pi*u)**1.3*max(0,1-v*v)**.8-.6
   # Feather into real terrain before reaching routes, buildings or the camera.
   if protected(xy,1) or any(path_dist(xy,p)<3.8 for p in new_paths):h=-.3
   for hc,ht,hn,rx,ry in house_bounds:
    d=xy-hc
    if abs(np.dot(d,ht))<rx+2 and abs(np.dot(d,hn))<ry+2:h=-.3
   z=gz(xy)
   if np.linalg.norm((flight-np.r_[xy,z+max(0,h)])/np.array([5,5,5]),axis=1).min()<1.3:h=-.3
   vs.append((*xy,z+h))
   if h>.1:rock_centers.append(xy)
 for j in range(long-1):
  for k in range(cross-1):a=j*cross+k;fs.append((a,a+1,a+1+cross,a+cross))
 G.mesh(f'Continuous rooted rock seam {ix+1}',vs,fs,'rock',ROCK)
rock_centers=np.array(rock_centers)
def plant_clear(xy,r,h):
 if protected(xy,r):return False
 for center,t,n,rx,ry in house_bounds:
  d=xy-center
  if abs(np.dot(d,t))<rx+r and abs(np.dot(d,n))<ry+r:return False
 if any(path_dist(xy,p)<r+2 for p in new_paths):return False
 if len(rock_centers) and np.linalg.norm(rock_centers-xy,axis=1).min()<r+1:return False
 if slope(xy)>1.05:return False
 z=gz(xy)
 if np.linalg.norm((flight-np.r_[xy,z+h/2])/np.array([r+4,r+4,h/2+4]),axis=1).min()<1.2:return False
 return True
def tree(xy,h,bamboo=False):
 radius=2.8 if bamboo else h*.31
 if not plant_clear(xy,radius,h):return False
 z=gz(xy);roots.append({'xy':xy.tolist(),'z':z,'type':'bamboo' if bamboo else 'pine'})
 if bamboo:
  for j in range(5):
   a=j*2.4;p=xy+np.array([math.cos(a),math.sin(a)])*.9;zz=gz(p);hh=h*rng.uniform(.75,1)
   G.beam('Rooted bamboo culm',[np.r_[p,zz-.2],np.r_[p+[.3,.4],zz+hh]],.07,'pine',TREE)
   ellipsoid('Bamboo airy leaf crown',np.r_[p,zz+hh*.83],(1.6,1,hh*.24),'leaf',TREE)
 else:
  lean=np.array([rng.uniform(-1,1),rng.uniform(-1,1)]);G.beam('Rooted hillside pine',[np.r_[xy,z-.3],np.r_[xy+lean,z+h*.85]],.22,'wood',TREE)
  for j in range(4):
   a=j*2.4+rng.random();p=xy+lean+np.array([math.cos(a),math.sin(a)])*radius*.52;zz=z+h*(.58+.09*j)
   G.beam('Pine lateral branch',[np.r_[xy+lean,z+h*(.5+.08*j)],np.r_[p,zz]],.12,'wood',TREE)
   ellipsoid('Contour pine irregular crown',np.r_[p,zz],(radius*.75,radius*.6,radius*.35),'pine' if j%3 else 'leaf',TREE)
 return True
# Dense cores fade into bare shoulders; several stretches are deliberately unplanted.
groves=[(.168,1,32,.017,14,1),(.211,1,31,.019,11,1),(.263,-1,40,.027,17,0),(.308,-1,31,.015,12,0),(.337,1,33,.012,10,1),(.393,1,37,.022,17,1),(.405,-1,25,.015,9,0)]
counts={'trees':0,'bamboo':0,'understory':0}
for s,side,q,ds,dq,pine in groves:
 group_count=0
 for trial in range(95):
  st=rng.gauss(s,ds*.55);offset=rng.gauss(q,dq*.5)
  if not .145<st<.418 or offset<18 or offset>58:continue
  xy=pos(st,side,offset)
  if any(np.linalg.norm(xy-np.array(r['xy']))<5 for r in roots):continue
  if tree(xy,rng.uniform(8,13),not pine):counts['trees' if pine else 'bamboo']+=1;group_count+=1
  if group_count>=12:break
# Understory grows at the feet of the groves, leaving rocky openings between them.
for root in roots:
 for k in range(3):
  xy=np.array(root['xy'])+np.array([rng.uniform(-2,2),rng.uniform(-2,2)]);r=rng.uniform(1.6,2.6)
  if not plant_clear(xy,r,2):continue
  z=gz(xy);ellipsoid('Rooted woodland understory',np.r_[xy,z+.05],(r,r*.85,r*.34),'leaf' if k else 'pine',TREE);counts['understory']+=1
# Thin shoulder mist complements the retained enclosing clouds; not structural geometry.
CLOUD=bpy.data.collections['05 Atmospheric envelope optional'];base=bpy.data.materials['Ordinary cloud / local soft enclosure'];mist=base.copy();mist.name='Cloud hamlet shoulder mist'
for node in mist.node_tree.nodes:
 if node.type=='MAP_RANGE':node.inputs['To Min'].default_value=.007
for i,(s,side,q,zrel) in enumerate([(.198,1,64,19),(.283,-1,68,16),(.374,1,67,18)]):
 xy=pos(s,side,q);me=bpy.data.meshes.new('Shoulder mist mesh');bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(f'Hamlet shoulder veil {i+1}',me);CLOUD.objects.link(ob);ob.location=(*xy,float(L.water_z(s))+zrel);ob.scale=(63,23,11);t,n=L.basis(s);ob.rotation_euler.z=math.atan2(t[1],t[0]);me.materials.append(mist);ob['physical']=False
CLOUD.hide_render=False
S['v11_scope']='Terrain-bound vegetation and three hillside hamlets; camera unchanged from v10'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'cloud-hamlet-masterplan-v11.blend'))
# Exact frame poses, lens and camera clipping copied from the approved v10 reference route.
with bpy.data.libraries.load(str(OLD/'valley-route-58s-v10.blend'),link=False) as (src,dst):dst.objects=['FPV landscape route']
cam=dst.objects[0];S.collection.objects.link(cam);S.camera=cam;S.frame_start=1;S.frame_end=1392;S.render.fps=24;S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'cloud-hamlet-route-58s-v11.blend'));shutil.copy2(OLD/'route-poses.json',O/'route-poses.json')
data={'source_v10_sha256':hashlib.sha256((OLD/'valley-masterplan-v10.blend').read_bytes()).hexdigest(),'removed_v10_scatter_objects':removed,'terrain_changed_vertices':changed,'terrain_protected_candidates':protected_count,'terrain_material_faces':painted,'houses':houses,'stairs':stairs,'roots':roots,'counts':counts,'camera_poses_sha256':hashlib.sha256((O/'route-poses.json').read_bytes()).hexdigest(),'cloud_volumes_added':3,'palette':'v10 retained; moss uses existing blend'}
(O/'landscape-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');print('HAMLET_READY',counts,'terrain',len(changed),'houses',len(houses),'max_step',max(p['max_rise'] for p in stairs),flush=True)
