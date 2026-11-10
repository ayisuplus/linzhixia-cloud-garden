"""Additive camera-facing town fabric and atmospheric layers on preserved v18."""
import bpy,bmesh,sys,math,json,random,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D));import routing
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1'));import geometry as G
SRC=R/'视频制作/第一集低亭云渡-20261024-v0.1';O=R/'视频制作/第一集云城层次-20261024-v0.1';O.mkdir(exist_ok=True)
B=SRC/'low-pavilion-cloud-ferry-v18.blend';bpy.ops.wm.open_mainfile(filepath=str(B));S=bpy.context.scene
P=json.loads((SRC/'planning-data.json').read_text('utf8'));T=json.loads((SRC/'transport-data.json').read_text('utf8'));old=set(o.name for o in S.objects)
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1].split(' [')[0]]=m
def col(name):c=bpy.data.collections.new(name);S.collection.children.link(c);return c
ARCH=col('18 Neighbourhood edges');PLANT=col('19 Joined planting');BG=col('20 Distant garden quarters');CLOUD=col('21 Cloud streets');LIFE=col('22 Everyday scale');G.ARCH=ARCH
rec={'version':'v19','source_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'source_modified_objects':[],'source_removed_objects':[],'main_buildings':[],'street_edges':[],'background_islands':[],'clouds':[],'plant_groups':[],'rejected_groups':[],'purpose':'camera-facing reference, not complete city navigation'}
route=routing.raw_route()[::8]
def oval(name,loc,sc,key,c,sub=2,physical=True):
 me=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=1);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);c.objects.link(ob);ob.location=loc;ob.scale=sc;me.materials.append(G.M[key] if isinstance(key,str) else key);ob['physical']=physical
 for f in me.polygons:f.use_smooth=True
 return ob
def bvh(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons])
cores={i['id']:bvh(bpy.data.objects[i['id']+' separate cloud support']) for i in P['islands']}
protected=[];blockers={}
roads=[(np.array(a,float),np.array(b,float),next(i['center'][2] for i in P['islands'] if i['id']==iid)) for iid,paths in P['internal_paths'].items() for pts in paths for a,b in zip(pts,pts[1:])]
for ob in S.objects:
 if ob.type!='MESH' or not ob.get('physical',False) or 'separate cloud support' in ob.name or ob.hide_render or any(c.hide_render for c in ob.users_collection):continue
 if 'internal garden path' in ob.name or 'A revised garden approach' in ob.name:continue
 bb=np.array([ob.matrix_world@Vector(v) for v in ob.bound_box]);protected.append((bb.min(0),bb.max(0),ob.name))
def supported(i,xy,r):
 z=i['center'][2]
 return all(cores[i['id']].ray_cast(Vector((xy[0]+dx,xy[1]+dy,z+.1)),Vector((0,0,-1)),.4)[0] is not None for dx,dy in [(0,0),(r,0),(-r,0),(0,r),(0,-r),(.7*r,.7*r),(-.7*r,-.7*r)])
def clear(xy,z,r,h=8):
 xy=np.array(xy)
 for a,b,zz in roads:
  if abs(z-zz)>1:continue
  u=b-a;t=np.clip((xy-a)@u/(u@u),0,1)
  if np.linalg.norm(xy-(a+t*u))<r+2.8:return False
 if np.any((np.linalg.norm(route[:,:2]-xy,axis=1)<r+2.4)&(route[:,2]>z-1)&(route[:,2]<z+h+2)):return False
 for lo,hi,nm in protected:
  if hi[2]<z-.3 or lo[2]>z+h:continue
  if np.linalg.norm(np.maximum(np.maximum(lo[:2]-xy,xy-hi[:2]),0))<r+1.2:
   blockers[nm]=blockers.get(nm,0)+1;return False
 return True
def register(xy,z,r,h):protected.append((np.array([xy[0]-r,xy[1]-r,z]),np.array([xy[0]+r,xy[1]+r,z+h]),'new group'))
def house(name,xy,z,w,d,h,ang,c,detail=True):
 x,y=xy;G.ARCH=c
 def at(a,b,hh):return (x+a*math.cos(ang)-b*math.sin(ang),y+a*math.sin(ang)+b*math.cos(ang),z+hh)
 G.box(name+' footing',at(0,0,.12),(w+.5,d+.5,.24),'stone',c,ang)
 G.box(name+' plaster body',at(0,0,h/2+.24),(w,d,h),'wall',c,ang)
 G.roof(name+' tiled roof',at(0,0,h+.24),(w+1.8,d+1.8),1.45,ang)
 if detail:
  G.box(name+' door',at(0,-d/2-.035,1.3),(1.7,.08,2.6),'wood',c,ang)
  for xx in [-w*.30,w*.30]:
   G.box(name+' window',at(xx,-d/2-.08,h*.55),(w*.20,.1,1.55),'window',c,ang)
   for dx in [-.5,0,.5]:G.box(name+' mullion',at(xx+dx,-d/2-.15,h*.55),(.08,.12,1.55),'wood',c,ang)
  G.roof(name+' porch',at(0,-d/2-1.4,3.1),(w+1,3.2),.5,ang)
  for xx in [-w/2,w/2]:G.beam(name+' porch post',[at(xx,-d/2-2.6,.15),at(xx,-d/2-2.6,3.15)],.13,'redwood',c)
 return at

# Small buildings occupy genuinely unused ground next to existing living routes.
# Exact sources remain unchanged; no broad clearing of trees or moving of courts.
for i in P['islands']:
 iid=i['id'];z=i['center'][2];rng=random.Random(1900+ord(iid));count=0
 for pts in P['internal_paths'][iid]:
  for a,b in zip(pts,pts[1:]):
   a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
   for t in [.2,.5,.8]:
    for side in [-1,1]:
     xy=a*(1-t)+b*t+n*side*13;w=rng.uniform(7,10);dd=rng.uniform(5,7);r=math.hypot(w/2+1,dd/2+3);h=4.0+rng.random()*.8
     if not supported(i,xy,r+1) or not clear(xy,z,r,h+2):continue
     name=f'{iid} neighbour {count:02}';angle=math.atan2(u[1],u[0])+(0 if side==1 else math.pi)
     at=house(name,xy,z,w,dd,h,angle,ARCH)
     rec['main_buildings'].append({'id':name,'island':iid,'xy':xy.tolist(),'z':z,'radius':r,'height':h+2});register(xy,z,r,h+2);count+=1
     # A short threshold joins the nearby street, never closing it.
     near=a*(1-t)+b*t;front=np.array(at(0,-dd/2-2.7,.0))[:2];delta=near-front
     if np.linalg.norm(delta)>1:
      mid=(front+near)/2;G.box(name+' threshold',(mid[0],mid[1],z+.07),(np.linalg.norm(delta),1.6,.14),'stone',ARCH,math.atan2(delta[1],delta[0]))

# Broken walls and roofed fragments give parallax, gaps and actual garden edges.
for i in P['islands']:
 iid=i['id'];z=i['center'][2];count=0
 for pts in P['internal_paths'][iid]:
  for a,b in zip(pts,pts[1:]):
   a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);u=(b-a)/L;n=np.array([-u[1],u[0]]);angle=math.atan2(u[1],u[0])
   for t in np.linspace(.2,.8,max(2,int(L/12))):
    for side in [-1,1]:
     xy=a*(1-t)+b*t+n*side*7.0;length=min(6,L*.30);r=length/2+.4
     if not supported(i,xy,r) or not clear(xy,z,r,3.8):continue
     name=f'{iid} lane screen {count:02}'
     # Real rectangular lattice openings, rather than isolated solid slabs.
     def wp(a,h):return (xy[0]+u[0]*a,xy[1]+u[1]*a,z+h)
     hole=min(2.1,length*.5);G.box(name+' sill',wp(0,.65),(length,.42,1.3),'wall',ARCH,angle);G.box(name+' lintel',wp(0,2.95),(length,.42,.5),'wall',ARCH,angle)
     for side2 in [-1,1]:G.box(name+' pier',wp(side2*(length+hole)/4,2.0),((length-hole)/2,.42,1.4),'wall',ARCH,angle)
     for dx in np.linspace(-hole/2,hole/2,5):G.box(name+' lattice',wp(dx,2.0),(.07,.11,1.4),'wood',ARCH,angle)
     G.box(name+' transom',wp(0,2.0),(hole,.11,.07),'wood',ARCH,angle);G.ARCH=ARCH;G.roof(name+' coping',wp(0,3.15),(length+.5,1.05),.22,angle)
     register(xy,z,r,3.8);rec['street_edges'].append({'id':name,'island':iid,'xy':xy.tolist(),'length':length,'angle':angle});count+=1
     # A planted seam grows from this wall's outer foot, not scattered dots.
     for k in [-.65,0,.65]:
      pp=xy+u*k*length*.45+n*side*1.4
      oval(name+' planted foot',(pp[0],pp[1],z+.45),(2.2,1.35,.65),'leaf',PLANT)

# Link the southern home-garden screens into one recognisable garden boundary.
home=[x for x in rec['street_edges'] if x['id'] in ['F lane screen 03','F lane screen 04','F lane screen 05','F lane screen 06','F lane screen 07']]
for a,b in zip(home,home[1:]):
 aa=np.array(a['xy']);bb=np.array(b['xy']);u=(bb-aa)/np.linalg.norm(bb-aa);p=aa+u*a['length']/2;q=bb-u*b['length']/2;mid=(p+q)/2;L=np.linalg.norm(q-p);ang=math.atan2(u[1],u[0])
 G.box('F continuous garden boundary',(mid[0],mid[1],66+1.05),(L,.42,2.1),'wall',ARCH,ang);G.ARCH=ARCH;G.roof('F linked wall coping',(mid[0],mid[1],68.08),(L+.2,.8),.15,ang)

# Two identity-specific additions at inspected empty sites, with open sides.
G.ARCH=ARCH
G.box('A study arcade paving',(-238,145,126.08),(17,3.8,.16),'stone',ARCH)
G.roof('A study arcade eave',(-238,145,130.3),(18,4.8),.65,0)
for xx in [-246,-242,-238,-234,-230]:
 for yy in [143.5,146.5]:G.beam('A study arcade post',[(xx,yy,126.16),(xx,yy,130.3)],.13,'redwood',ARCH)
G.box('A study arcade threshold',(-238,149,126.07),(1.8,4.2,.14),'stone',ARCH)
G.box('G craft shed paving',(319,-84,48.08),(9,6,.16),'stone',ARCH)
G.roof('G craft shed roof',(319,-84,51.7),(10,7),.9,0)
for xx in [315,323]:
 for yy in [-86.5,-81.5]:G.beam('G craft shed post',[(xx,yy,48.16),(xx,yy,51.7)],.14,'redwood',ARCH)
G.box('G craft workbench',(319,-82,49),(5,1.1,.18),'wood',LIFE)
for xx in [317,321]:G.box('G craft bench leg',(xx,-82,48.5),(.2,.7,1),'wood',LIFE)
for j in range(3):G.box('G craft stored box',(320.5+j*.65,-85,48.5),(.6,.65,.9),'wood',LIFE)
G.box('G shed approach',(317.5,-93,48.07),(1.7,13,.14),'stone',ARCH)
rec['purpose_built']=['A study arcade','G craft shed','F continuous garden boundary']

# The inherited south hall was a solid block behind the later entrance eave.
# Cut a real through-hall entrance aligned with that existing 12-degree eave.
entry_angle=math.radians(12);entry_center=(347+11.5*math.sin(entry_angle),-64-11.5*math.cos(entry_angle),50.0)
cutter=G.box('temporary workshop doorway cutter',entry_center,(3.8,14,3.85),'stone',ARCH,entry_angle)
for nm in ['G reused Repair-workshop / back hall','G reused Repair-workshop / back hall opening.001']:
 hall=bpy.data.objects[nm];materials=list(hall.data.materials);mod=hall.modifiers.new('workshop through-hall opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=hall;bpy.ops.object.modifier_apply(modifier=mod.name)
 hall.data.materials.clear()
 for m in materials:hall.data.materials.append(m)
 for face in hall.data.polygons:
  if face.material_index>=len(materials):face.material_index=0
 rec['source_modified_objects'].append(nm)
bpy.data.objects.remove(cutter,do_unlink=True)
rec['workshop_opening']={'objects':rec['source_modified_objects'],'center':entry_center,'size':[3.8,14,3.85],'angle':entry_angle,'purpose':'actual doorway behind existing south entrance eave'}
G.box('G entrance passage floor',(entry_center[0],entry_center[1],48.10),(3.6,15,.16),'stone',ARCH,entry_angle)
def gateat(x,y,z):return (347+x*math.cos(entry_angle)-y*math.sin(entry_angle),-64+x*math.sin(entry_angle)+y*math.cos(entry_angle),z)
for xx in [-1.96,1.96]:G.beam('G workshop doorway jamb',[gateat(xx,-16.1,48.18),gateat(xx,-16.1,52.0)],.12,'wood',ARCH)
G.beam('G workshop doorway lintel',[gateat(-2.05,-16.1,52.0),gateat(2.05,-16.1,52.0)],.12,'wood',ARCH)

# Soft, connected planting ribbons fill remaining clear slopes in small groups.
for i in P['islands']:
 rng=random.Random(19100+ord(i['id']));cx,cy,z=i['center'];count=0
 for k in range(200):
  ang=rng.uniform(0,math.tau);rad=rng.uniform(.45,.86);xy=np.array([cx+i['radius'][0]*rad*math.cos(ang),cy+i['radius'][1]*rad*math.sin(ang)])
  if not supported(i,xy,4.5) or not clear(xy,z,4.5,5):continue
  name=f'{i["id"]} linked planting {count:02}'
  for j in range(5):
   xx,yy=xy+np.array([math.cos(ang),math.sin(ang)])*(j-2)*1.4
   oval(name+' shrub',(xx,yy,z+.5),(2.1,1.5,.9),'leaf' if j%3 else 'pine',PLANT)
  for j in [-1,1]:
   xx,yy=xy+np.array([j*1.4,j*.6]);G.beam(name+' bamboo',[(xx,yy,z),(xx+.1,yy,z+4.5)],.06,'wood',PLANT)
   for zz in [2.8,3.6,4.5]:oval(name+' bamboo leaf',(xx+j*.5,yy,z+zz),(1.5,.6,.25),'pine',PLANT)
  rec['plant_groups'].append({'id':name,'island':i['id'],'xy':xy.tolist()});register(xy,z,4.5,5);count+=1
  if count>=5:break

# Beyond the seven hero islands: overlapping neighbourhoods, all low pitched roofs.
# Geometry is volumetric and supported, but distant doors/streets are visual proxies.
bg=[(-355,-55,80,75,52),(-180,-155,36,69,48),(-20,-205,58,76,47),(155,-245,87,80,52),(350,-225,32,83,55),(490,-110,78,78,50),(410,100,118,80,50),(250,165,140,85,53),(-80,265,158,86,52),(-310,300,108,92,50),(-490,145,54,95,65),(-430,-240,20,96,58),(40,-400,16,110,63),(290,-410,60,104,60),(560,-300,106,100,60),(620,90,65,105,70),(430,330,166,100,65),(120,390,114,100,64)]
for k,(cx,cy,z,rx,ry) in enumerate(bg):
 rng=random.Random(19200+k);name=f'Q{k+1:02} background quarter';N=64;poly=[]
 for j in range(N):
  t=j*math.tau/N;v=1+.08*math.sin(3*t+k)+.04*math.sin(7*t);poly.append((cx+rx*v*math.cos(t),cy+ry*v*math.sin(t),z))
 vs=[(cx,cy,z)]+poly+[(cx+(x-cx)*.65,cy+(y-cy)*.65,z-15) for x,y,_ in poly]+[(cx,cy,z-26)]
 fs=[(0,1+j,1+(j+1)%N) for j in range(N)]+[(1+j,1+N+j,1+N+(j+1)%N,1+(j+1)%N) for j in range(N)]+[(1+N+j,2*N+1,1+N+(j+1)%N) for j in range(N)]
 ob=G.mesh(name+' cloud core',vs,fs,'cloudwhite',BG);ob.data.materials.append(bpy.data.materials['v17 planted ground / retained stone and leaf families'])
 for f in ob.data.polygons:
  if f.index<N:f.material_index=1
  else:f.use_smooth=True
 houses=[]
 for row in range(-2,3):
  for column in range(-3,4):
   xx=cx+column*19+row*3;yy=cy+row*16+3*math.sin(column)
   if ((xx-cx)/rx)**2+((yy-cy)/ry)**2>.64 or rng.random()<.20:continue
   w=rng.uniform(10,16);dd=rng.uniform(7,10);h=rng.uniform(4,6);a=.1*math.sin(k)+.08*row
   house(name+f' house {row} {column}',(xx,yy),z,w,dd,h,a,BG,False);houses.append([xx,yy,h])
 # Visible district lanes and planted edges have continuous solid support.
 for row in [-1,1]:G.box(name+' lane',(cx,cy+row*8,z+.05),(rx*1.3,2.7,.1),'stone',BG,.08)
 for t in np.linspace(0,math.tau,11,endpoint=False):
  xx=cx+rx*.78*math.cos(t);yy=cy+ry*.74*math.sin(t);h=rng.uniform(5,8)
  G.beam(name+' tree',[(xx,yy,z),(xx+.5,yy,z+h)],.2,'wood',BG);oval(name+' crown',(xx,yy,z+h),(4.5,3.4,1.8),'pine' if k%2 else 'leaf',BG)
 rec['background_islands'].append({'id':name,'center':[cx,cy,z],'radius':[rx,ry],'houses':houses,'role':'distant visual quarter; no full interior/navigation'})

# Non-bearing cloud streets: localized density and soft boundaries, no opaque shell.
def cloudmat(name,density):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();lk=m.node_tree.links;out=n.new('ShaderNodeOutputMaterial');vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.90,.94,1,1);vol.inputs['Anisotropy'].default_value=.22
 tc=n.new('ShaderNodeTexCoord');sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,.5);lk.new(tc.outputs['Generated'],sub.inputs[0]);length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';lk.new(sub.outputs[0],length.inputs[0]);r=n.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=.16;r.inputs['From Max'].default_value=.52;r.inputs['To Min'].default_value=density;r.inputs['To Max'].default_value=0;lk.new(length.outputs['Value'],r.inputs[0])
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4.5;noise.inputs['Detail'].default_value=3;lk.new(tc.outputs['Generated'],noise.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';lk.new(r.outputs[0],mul.inputs[0]);lk.new(noise.outputs['Fac'],mul.inputs[1]);lk.new(mul.outputs[0],vol.inputs['Density']);em=n.new('ShaderNodeMath');em.operation='MULTIPLY';em.inputs[1].default_value=.65;lk.new(mul.outputs[0],em.inputs[0]);lk.new(em.outputs[0],vol.inputs['Emission Strength']);vol.inputs['Emission Color'].default_value=(.87,.94,1,1);lk.new(vol.outputs[0],out.inputs['Volume']);return m
cm=cloudmat('v19 layered cloud streets',.20);thin=cloudmat('v19 transparent reveal veils',.032)
# Around background quarters and selected sides of main islands; middle stays readable.
for k,i in enumerate(P['islands']):
 cx,cy,z=i['center']
 for j,t in enumerate([.5,2.8,4.9]):
  x=cx+i['radius'][0]*math.cos(t);y=cy+i['radius'][1]*math.sin(t)
  if any(np.linalg.norm(np.array([x,y])-w['fall_xy'])<35 for w in P['water']):continue
  ob=oval(f'{i["id"]} street cloud {j}',(x,y,z-5),(36,22,15),cm,CLOUD,3,False);rec['clouds'].append(ob.name)
for k,(cx,cy,z,rx,ry) in enumerate(bg):
 for j in [0,1]:
  ob=oval(f'Q{k+1:02} enclosing cloud {j}',(cx+(-1 if j==0 else 1)*rx*.65,cy-ry*.25,z+2),(rx*.82,ry*.82,22),cm,CLOUD,2,False);rec['clouds'].append(ob.name)
 ob=oval(f'Q{k+1:02} under-cloud',(cx,cy,z-12),(rx*.95,ry*.9,23),cm,CLOUD,2,False);rec['clouds'].append(ob.name)
ob=oval('E lower cloud reveal',(69,-40,62),(34,30,15),cm,CLOUD,3,False);rec['clouds'].append(ob.name)
for name,p,sc in [('AB reveal',(-178,84,121),(18,12,10)),('BC reveal',(-80,21,72),(20,15,13)),('CE reveal',(24,-41,64),(20,16,13)),('FG reveal',(290,-117,62),(17,13,10))]:
 ob=oval(name,p,sc,thin,CLOUD,3,False);rec['clouds'].append(ob.name)

# Reject only new local groups that intersect the reserved flight swept centre band.
# Remaining exact scene collision tests are performed by flight.py and independent review.
S['status']='v19 additive neighbourhood fabric; 58s flight candidate, no cloud generation'
S.render.resolution_x=1440;S.render.resolution_y=900;S.eevee.taa_render_samples=32;S.eevee.volumetric_samples=64
rec['new_objects']=sorted(set(o.name for o in S.objects)-old)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'cloud-neighbourhood-v19.blend'))
P['version']='v19';P['source_sha256']=rec['source_sha256'];P['route_status']='new flight path from routing.py; inspect saved route-check before use'
(O/'planning-data.json').write_text(json.dumps(P,ensure_ascii=False,indent=2),encoding='utf8');(O/'transport-data.json').write_text(json.dumps(T,ensure_ascii=False,indent=2),encoding='utf8');(O/'development-data.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf8')
print('V19_BUILD_READY',len(S.objects),'main houses',len(rec['main_buildings']),'screens',len(rec['street_edges']),'quarters',len(bg),'plant groups',len(rec['plant_groups']),flush=True)
print('BLOCKERS',sorted(blockers.items(),key=lambda kv:-kv[1])[:25],flush=True)
