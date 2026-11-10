"""Build an editable v16 spatial planning candidate from retained v15 architecture.
No continuous terrain, no inherited flight, no external generation.
"""
import bpy,bmesh,sys,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D));import plan as P
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1'));import geometry as G
O=R/'视频制作/第一集独立园岛-20261024-v0.1';O.mkdir(exist_ok=True)
SRC=R/'视频制作/第一集枝水园城-20261024-v0.1/branch-garden-route-58s-v15.blend'
bpy.ops.wm.read_factory_settings(use_empty=True);S=bpy.context.scene
prefixes=[c[1] for c in P.COURTS]
with bpy.data.libraries.load(str(SRC),link=False) as (src,dst):
 dst.materials=src.materials
 dst.objects=[n for n in src.objects if any(n.startswith(p+' / ') or n in [p+' court floor',p+' front wall',p+' front wall.001'] for p in prefixes)]
templates=[o for o in dst.objects if o is not None]
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1].split(' [')[0]]=m
# The source terrain shader reads an old vertex-colour layer. The new support
# has different topology; use the retained terrain diffuse value explicitly.
gm=bpy.data.materials.new('v16 ground from retained terrain diffuse');gm.use_nodes=True;gm.diffuse_color=G.M['terrain'].diffuse_color[:];gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=gm.diffuse_color;gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;G.M['ground']=gm
def col(name):c=bpy.data.collections.new(name);S.collection.children.link(c);return c
BASE=col('01 Separate cloud supports');LAND=col('02 Garden land and planting');A=col('03 Reused courtyard architecture');W=col('04 Local pools and three falls');T=col('05 Bridges and change-level towers');CLOUD=col('06 Optional atmospheric enclosure');GUIDE=col('07 Planning guides hidden from renders');CAM=col('08 Cameras');G.ARCH=A
data={'version':'v16','status':'spatial planning blockout, not adopted final scene','source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'islands':P.ISLANDS,'water':[],'links':[],'courts':[],'route_envelope':P.ROUTE,'route_status':'58 second budget only; not animated or flight-validated','return_water':'local underground return shafts reserved in each water group; no hydraulic simulation'}
def oval(name,loc,scale,key,c=LAND,sub=2):
 me=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=1);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);c.objects.link(o);o.location=loc;o.scale=scale;me.materials.append(G.M[key]);o['physical']=c!=CLOUD
 for f in me.polygons:f.use_smooth=True
 return o
def apply_bool(target,cutter):
 bpy.context.view_layer.objects.active=target;mod=target.modifiers.new('real water basin cut','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
def slabpath(name,points,width,key,c=T,rail=False):
 # Independent closed segment prisms plus convex corner platforms. This does
 # not rely on a twisted average-normal ribbon at sharp changes of direction.
 pts=[Vector(p) for p in points];normals=[];vs=[];fs=[]
 for p,q in zip(pts,pts[1:]):
  v=q-p;normals.append(Vector((-v.y,v.x,0)).normalized()*width/2)
 def prism(poly):
  base=len(vs);n=len(poly);vs.extend([p-Vector((0,0,.6)) for p in poly]);vs.extend(poly)
  fs.append(tuple(base+k for k in reversed(range(n))))
  for k in range(1,n-1):fs.append((base+n,base+n+k,base+n+k+1))
  for k in range(n):j=(k+1)%n;fs.append((base+k,base+j,base+n+j,base+n+k))
 miters=[normals[0]]
 for k in range(1,len(pts)-1):
  n1=normals[k-1];n2=normals[k];m=(n1+n2).normalized();den=m.dot(n2.normalized());m*=min(width*2,width/2/max(den,.25));miters.append(m)
 miters.append(normals[-1])
 for k,(p,q) in enumerate(zip(pts,pts[1:])):
  n=normals[k];prism([p-n,q-n,q+n,p+n])
 for k in range(1,len(pts)-1):
  p=pts[k];corners=[p+n*s for n in [normals[k-1],normals[k],miters[k]] for s in [-1,1]]
  # 2D convex hull, with duplicate samples removed.
  ordered=sorted(set((v.x,v.y) for v in corners))
  def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
  lower=[];upper=[]
  for v in ordered:
   while len(lower)>=2 and cross(lower[-2],lower[-1],v)<=0:lower.pop()
   lower.append(v)
  for v in reversed(ordered):
   while len(upper)>=2 and cross(upper[-2],upper[-1],v)<=0:upper.pop()
   upper.append(v)
  hull=lower[:-1]+upper[:-1]
  if len(hull)>=3:prism([Vector((x,y,p.z)) for x,y in hull])
 o=G.mesh(name,vs,fs,key,c)
 if rail:
  for side in [-1,1]:
   line=[p+miters[k]*side+Vector((0,0,1.2)) for k,p in enumerate(pts)];G.beam(name+' handrail',line,.10,'wood',c)
   for p,q in zip(line,line[1:]):
    for u in np.linspace(0,1,max(2,int((q-p).length/3))):
     v=p.lerp(q,float(u));G.beam(name+' rail post',[v-Vector((0,0,1.2)),v],.09,'wood',c)
 return o
island_objs={};planting_groups=[]
for i in P.ISLANDS:
 outline=P.outline(i);cx,cy,z=i['center'];n=len(outline);vs=[(cx,cy,z)];fs=[]
 # Flat usable garden core, tapering organic support below; different outline and depth per island.
 for scale,dep in [(1,0),(1.025,-3),(.86,-i['depth']*.50),(.53,-i['depth']*.86),(.10,-i['depth'])]:
  for k,(x,y) in enumerate(outline):
   vs.append((cx+(x-cx)*scale,cy+(y-cy)*scale,z+dep+(0 if dep==0 else 1.8*math.sin(k*math.tau/n*3+i['phase']))))
 for k in range(n):fs.append((0,1+k,1+(k+1)%n))
 for ring in range(4):
  for k in range(n):a=1+ring*n+k;b=1+ring*n+(k+1)%n;fs.append((a,1+(ring+1)*n+k,1+(ring+1)*n+(k+1)%n,b))
 fs.append(tuple(reversed(range(1+4*n,1+5*n))))
 o=G.mesh(i['id']+' separate cloud support',vs,fs,'ground',BASE);o.data.materials.append(G.M['cloudwhite']);o['island_id']=i['id']
 for p in o.data.polygons:
  if p.index>=n:p.material_index=1;p.use_smooth=True
 island_objs[i['id']]=o;i['outline']=outline
 # Small cloud shoulders soften selected underside edges without filling inter-island gaps.
 for k in range(0,n,12):
  x,y=outline[k];oval(i['id']+' cloud shoulder',(cx+(x-cx)*.85,cy+(y-cy)*.85,z-8),(13,10,7),'cloudwhite',BASE)
 # Grounded low rock seams and planting clusters occupy the perimeter, leaving centre paths clear.
 rng=random.Random(1600+ord(i['id']))
 for k in range(0,n,5):
  if rng.random()<.35:continue
  x,y=outline[k];fac=.72+rng.random()*.16;x=cx+(x-cx)*fac;y=cy+(y-cy)*fac
  if i['id']=='E' and y>cy:continue
  # Reserve bridge ends and water/outlet direction before planting.
  if any(np.linalg.norm(np.array([x,y])-p[:2])<13 for l in P.LINKS for p in l['points'] if i['id'] in [l['a'],l['b']]):continue
  blocked=False
  for _,aa,bb in P.WATER_PAIRS:
   if i['id']!=aa:continue
   direction=np.array(P.BY_ID[bb]['center'][:2],float)-[cx,cy];direction/=np.linalg.norm(direction);rel=np.array([x-cx,y-cy]);along=rel@direction
   if along>15 and abs(np.cross(direction,rel))<11:blocked=True
  if blocked:continue
  before=set(LAND.objects)
  oval(i['id']+' rooted edge rock',(x,y,z+1),(4+rng.random()*3,3+rng.random()*2,2.4),'rock')
  G.beam(i['id']+' tree trunk',[(x,y,z),(x+1,y,z+7)],.24,'wood',LAND)
  for dx,dy,dz,r in [(0,0,7,3.6),(1.5,.3,9,3.2)]:oval(i['id']+' planted pine',(x+dx,y+dy,z+dz),(r,r*.8,r*.45),'pine' if k%12 else 'leaf')
  for j in range(3):oval(i['id']+' clustered understory',(x+rng.uniform(-4,4),y+rng.uniform(-3,3),z+.5),(2.5,1.9,.9),'leaf')
  planting_groups.append((i['id'],[x,y],list(set(LAND.objects)-before)))
 # No circular paving pad: only individual court floors and the required paths are hard surfaced.

for iid,prefix,xy,angle in P.COURTS:
 objects=[o for o in templates if o.name.startswith(prefix+' / ') or o.name in [prefix+' court floor',prefix+' front wall',prefix+' front wall.001']]
 floor=next(o for o in objects if o.name==prefix+' court floor');vs=[floor.matrix_world@v.co for v in floor.data.vertices];origin=sum(vs,Vector())/len(vs);oldang=math.atan2((vs[1]-vs[0]).y,(vs[1]-vs[0]).x)
 top=max(v.z for v in vs);target=P.BY_ID[iid]['center'][2]+.16
 transform=Matrix.Translation(Vector((*xy,target-(top-origin.z))))@Matrix.Rotation(math.radians(angle)-oldang,4,'Z')@Matrix.Translation(-origin)
 for original in objects:
  o=original.copy();o.data=original.data;A.objects.link(o);o.matrix_world=transform@original.matrix_world;o.name=iid+' reused '+original.name;o['source_object']=original.name;o['island_id']=iid
 data['courts'].append({'island':iid,'source_prefix':prefix,'target_center':xy,'angle':angle,'object_count':len(objects)})
 # Front gate opens to a simple garden approach, leaving interiors as inherited massing.
 a=math.radians(angle);front=Vector((math.sin(a),-math.cos(a),0));p=Vector((*xy,target));slabpath(iid+' courtyard approach',[p+front*17,p+front*25],3.2,'stone',LAND)
for o in templates:bpy.data.objects.remove(o,do_unlink=True)

def edge_in_direction(i,dx,dy):
 # Intersect a ray with polygon segments, avoiding elliptical approximations.
 c=np.array(i['center'][:2]);d=np.array([dx,dy],dtype=float);d/=np.linalg.norm(d);poly=np.array(i['outline']);best=[]
 for p,q in zip(poly,np.roll(poly,-1,axis=0)):
  mat=np.column_stack([d,-(q-p)])
  if abs(np.linalg.det(mat))<1e-8:continue
  t,u=np.linalg.solve(mat,p-c)
  if t>0 and 0<=u<=1:best.append(t)
 return c+d*min(best),d
for ident,aa,bb in P.WATER_PAIRS:
 a=P.BY_ID[aa];b=P.BY_ID[bb];delta=np.array(b['center'][:2])-a['center'][:2];edge,dr=edge_in_direction(a,*delta);fall=edge+dr*6;start=np.array(a['center'][:2])+dr*30;za=a['center'][2]-.45;zb=b['center'][2]-.45
 # Real round basin cut from upper land and lower catchment; retain bed underneath.
 for island,xy,z,rad in [(aa,start,za,10),(bb,fall,zb,11)]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=rad,depth=4,location=(*xy,z+.9));cut=bpy.context.object;apply_bool(island_objs[island],cut)
  bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=rad-.18,depth=.13,location=(*xy,z-.065));pool=bpy.context.object;pool.name=ident+' '+island+' water basin'
  for c in list(pool.users_collection):c.objects.unlink(pool)
  W.objects.link(pool);pool.data.materials.append(G.M['water']);pool['physical']=False
  # Reserve a screened local recirculation intake, not a city-long open river.
  G.box(ident+' return intake',(* (xy+np.array([rad-1,0])),z+.06),(1.1,1.2,.15),'window',W)
 length=np.linalg.norm(fall-start);mid=(start+fall)/2;ang=math.atan2(dr[1],dr[0]);cut=G.box(ident+' channel cutter',(*mid,za+1),(length+1,4.8,4),'stone',W,ang);apply_bool(island_objs[aa],cut)
 slabpath(ident+' supported spillway bed',[(*start,za-.18),(*fall,za-.18)],4.8,'stone',W)
 slabpath(ident+' shallow channel',[(*start,za),(*fall,za)],3.8,'water',W)['physical']=False
 normal=np.array([-dr[1],dr[0]])
 for sign in [-1,1]:slabpath(ident+' spillway curb',[(*(start+normal*sign*2.2),za+.3),(*(fall+normal*sign*2.2),za+.3)],.35,'stone',W)
 # Vertical falling sheet at a true overhanging edge. No horizontal flying river.
 q1=fall-normal*1.9;q2=fall+normal*1.9
 G.mesh(ident+' free fall',[(q1[0],q1[1],za),(q2[0],q2[1],za),(q2[0],q2[1],zb),(q1[0],q1[1],zb)],[(0,1,2,3)],'water',W,False)
 for t in [-.7,0,.7]:G.beam(ident+' fall highlight',[(*(fall+normal*t),za),(*(fall+normal*t),zb)],.08,'cloudwhite',W)['physical']=False
 data['water'].append({'id':ident,'from':aa,'to':bb,'source_pool':start.tolist(),'fall_xy':fall.tolist(),'source_z':za,'catch_z':zb,'fall_height_m':za-zb,'upper_edge':edge.tolist(),'lip_overhang_m':6,'catch_radius':10.82,'flow':'local group; covered return reserved; no simulation'})

def tower(name,xy,low,high):
 x,y=xy;levels=max(1,math.ceil((high-low)/4));h=(high-low)/levels;stairs=[]
 for k in range(levels+1):
  z=low+k*h
  G.box(name+' landing',(x,y-5.7,z-.16),(16,2.6,.32),'stone',T)
  G.box(name+' lift access',(x+6,y,z-.16),(3.5,11.5,.32),'stone',T)
 # Two flights per storey; walking rise <=0.185, tread >=0.30; not accessibility certification.
 for k in range(levels):
  z=low+k*h;n=max(1,math.ceil(h/2/.185));rise=h/(2*n);run=8.8/n
  for f in [0,1]:
   for j in range(n):
    yy=y-4.4+(j+.5)*run if f==0 else y+4.4-(j+.5)*run
    top=z+(f*n+j+1)*rise;G.box(name+' stair tread',(x+(-2.5 if f==0 else 1.3),yy,top-.13),(3.4,run+.015,.26),'stone',T)
  G.box(name+' half landing',(x-.6,y+5.7,z+h/2-.16),(7.2,2.6,.32),'stone',T)
  stairs.append({'level':k,'risers_per_flight':n,'riser_m':rise,'tread_m':run})
 for dx in [-7.4,7.4]:
  for dy in [-6.4,6.4]:G.beam(name+' timber frame',[(x+dx,y+dy,low-.15),(x+dx,y+dy,high+4)],.23,'redwood',T)
 G.box(name+' lift shaft reserved',(x+6,y,(low+high)/2),(2.5,3,high-low),'window',T)
 # The upper bridge uses the south landing; centre and north remain open
 # over the final return flight and the half-storey landing below it.
 # bottom and upper door threshold at x=0 are unobstructed; operating lift and doors not simulated.
 old=G.ARCH;G.ARCH=T;G.roof(name+' roof',(x,y,high+4),(18,15),2.5,0);G.ARCH=old
 return {'xy':xy,'lower_z':low,'upper_z':high,'levels':levels,'stairs':stairs,'lift':'occupied shaft with access landings; not operational'}
for l in P.LINKS:
 pts=l['points'];slabpath(l['id']+' cross-cloud bridge',pts,5,'wood',T,True)
 lower=P.BY_ID[l['low']]['center'][2];rec=dict(l);rec['tower_geometry']=tower(l['id']+' change-level pavilion',l['tower'],lower,pts[0][2]);data['links'].append(rec)
 # Bridges have explicit cloud-material keel support, separate from non-solid atmospheric mist.
 for k in range(len(pts)-1):
  p=Vector(pts[k]);q=Vector(pts[k+1]);m=p.lerp(q,.5);m.z-=1.4;beam=G.beam(l['id']+' structural cloud keel',[p-Vector((0,0,1.4)),m,q-Vector((0,0,1.4))],.85,'cloudwhite',T);beam['role']='reinforced cloud material, not ordinary fog'

# Internal paths connect bridge/tower landings and courtyard forecourts as explicit planning ribbons.
PATHS={
 'A':[[[-229,103],[-230,115],[-267,105]],[[-230,115],[-215,152]],[[-215,152],[-264,151]]],
 'B':[[[-160,61],[-149,65],[-126,75],[-105,85]],[[-126,75],[-107,55]]],
 'C':[[[-55,10],[-45,-28],[-22,-30]],[[-22,-30],[-4,-24],[-4,4]]],
 'D':[[[65,137],[65,151],[47,156]],[[65,151],[100,155]]],
 'E':[[[65,-33],[76,-48],[120,-48]],[[90,-10],[90,-48]]],
 'F':[[[190,-83],[182,-105],[190,-135],[205,-130]],[[205,-130],[268,-125],[268,-95]]],
 'G':[[[307,-92],[323,-103],[347,-89]]],
}
PATHS['B'].append([[-105,85],[-85,88],[-68,93],[-57,85],[-57,70.3],[-68,70.3]])
PATHS['D'].append([[23,154],[47,156]])
# Match the ground approach to the actual first stair landing, not tower centre.
for paths in PATHS.values():
 for pts in paths:
  for p in pts:
   for link in P.LINKS:
    if p==link['tower']:p[1]-=5.7;break
data['internal_paths']=PATHS
for iid,paths in PATHS.items():
 z=P.BY_ID[iid]['center'][2]+.14
 for idx,pts in enumerate(paths):slabpath(iid+f' internal garden path {idx}',[(*p,z) for p in pts],3.2,'stone',LAND)
# Two local mountain shoulders, not a continuous mountain chain.
for iid,xy,sc in [('D',[120,147],[10,7,14]),('A',[-285,189],[13,10,12])]:
 z=P.BY_ID[iid]['center'][2];oval(iid+' planted mountain shoulder',(*xy,z+sc[2]*.35),sc,'rock');oval(iid+' mountain moss',(*xy,z+sc[2]*.75),(sc[0]*.8,sc[1]*.8,sc[2]*.30),'leaf')

def segdist(p,a,b):
 p=np.array(p);a=np.array(a);b=np.array(b);v=b-a;t=np.clip((p-a)@v/max(v@v,1e-9),0,1);return np.linalg.norm(p-a-t*v)
data['planting_clearance_removed']=0
for iid,xy,objects in planting_groups:
 blocked=any(segdist(xy,a,b)<9 for pts in PATHS[iid] for a,b in zip(pts,pts[1:]))
 blocked=blocked or any(np.linalg.norm(np.array(xy)-court[2])<29 for court in P.COURTS if court[0]==iid)
 for w in data['water']:
  if iid==w['from']:blocked=blocked or segdist(xy,w['source_pool'],w['fall_xy'])<12 or np.linalg.norm(np.array(xy)-w['source_pool'])<18
  if iid==w['to']:blocked=blocked or np.linalg.norm(np.array(xy)-w['fall_xy'])<19
 if blocked:
  data['planting_clearance_removed']+=1
  for ob in objects:bpy.data.objects.remove(ob,do_unlink=True)

# Density-faded volume lobes envelop sides/top locally, with air corridors left open.
cm=bpy.data.materials.new('v16 atmosphere, non-bearing mist');cm.use_nodes=True;nd=cm.node_tree.nodes;nd.clear();out=nd.new('ShaderNodeOutputMaterial');vol=nd.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.86,.91,.94,1);vol.inputs['Anisotropy'].default_value=.15
tex=nd.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2.8;tex.inputs['Detail'].default_value=2
coord=nd.new('ShaderNodeTexCoord');sub=nd.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,.5);length=nd.new('ShaderNodeVectorMath');length.operation='LENGTH';ramp=nd.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.18;ramp.inputs['From Max'].default_value=.5;ramp.inputs['To Min'].default_value=.012;ramp.inputs['To Max'].default_value=0;ramp.clamp=True;mul=nd.new('ShaderNodeMath');mul.operation='MULTIPLY'
lk=cm.node_tree.links;lk.new(coord.outputs['Generated'],tex.inputs['Vector']);lk.new(coord.outputs['Generated'],sub.inputs[0]);lk.new(sub.outputs[0],length.inputs[0]);lk.new(length.outputs['Value'],ramp.inputs[0]);lk.new(tex.outputs['Fac'],mul.inputs[0]);lk.new(ramp.outputs[0],mul.inputs[1]);lk.new(mul.outputs[0],vol.inputs['Density']);lk.new(vol.outputs[0],out.inputs['Volume']);G.M['mist']=cm
for k,(p,sc) in enumerate([((-260,240,126),(170,55,62)),((-80,180,170),(120,45,48)),((115,225,126),(140,55,75)),((335,20,74),(110,45,68)),((160,-170,65),(150,55,70)),((-100,-40,26),(90,40,35)),((12,82,72),(38,45,25))]):oval('Atmosphere enclosure '+str(k),p,sc,'mist',CLOUD,3)
GUIDE.hide_render=True
slabpath('58 second route envelope only',P.ROUTE,1.2,'gold',GUIDE)
world=bpy.data.worlds.new('Open sky between cloud gardens');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.48,.65,.80,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7;S.world=world
sun=bpy.data.lights.new('Warm morning sun','SUN');sun.energy=2.5;sun.angle=.15;so=bpy.data.objects.new('Warm morning sun',sun);CAM.objects.link(so);so.rotation_euler=(math.radians(25),math.radians(-22),math.radians(-25))
ca=bpy.data.cameras.new('Planning overview');cam=bpy.data.objects.new('Planning overview',ca);CAM.objects.link(cam);S.camera=cam;cam.rotation_mode='QUATERNION';ca.lens=42
cam.location=(690,-850,610);cam.rotation_quaternion=(Vector((5,60,65))-cam.location).to_track_quat('-Z','Y')
S.render.engine='BLENDER_EEVEE';S.eevee.taa_render_samples=32;S.eevee.volumetric_samples=48;S.render.resolution_x=1440;S.render.resolution_y=1000;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='Standard';S.view_settings.look='Medium High Contrast';S.view_settings.exposure=0;S.view_settings.gamma=1
S.camera.data.clip_end=5000;S.unit_settings.system='METRIC';S['status']='v16 planning candidate; no frozen 58s animation';S['previous_route']='retired as layout constraint'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'island-garden-masterplan-v16.blend'))
(O/'planning-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('V16_BUILD_READY',len(S.objects),flush=True)
