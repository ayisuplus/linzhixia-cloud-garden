"""v17 additive garden development. Accepted v16 layout and walking geometry retained.
New terrain appearance, cloud sleeves, architectural envelope and garden planting
are candidates; no simulation or adoption of detailed architectural styling.
"""
import bpy,bmesh,sys,math,json,hashlib,random
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1'));import geometry as G
SRC=R/'视频制作/第一集独立园岛-20261024-v0.1';O=R/'视频制作/第一集园岛深化-20261024-v0.1';O.mkdir(exist_ok=True)
B=SRC/'island-garden-masterplan-v16.blend';bpy.ops.wm.open_mainfile(filepath=str(B));S=bpy.context.scene
P=json.loads((SRC/'planning-data.json').read_text('utf8'));original_names=set(o.name for o in S.objects)
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1].split(' [')[0]]=m
def col(n):c=bpy.data.collections.new(n);S.collection.children.link(c);return c
ARCH=col('09 Garden pavilion envelopes');PLANT=col('10 Rooted garden planting');EDGE=col('11 Cloud edge sleeves');DETAIL=col('12 Living courtyards and water edges');MIST=col('13 Local cloud veils');G.ARCH=ARCH
rec={'version':'v17','source_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'retained_layout':'v16 seven supports, seven bridges, towers/stairs and three water falls unchanged','material_changes':[],'cloud_sleeves':[],'plant_groups':[],'balconies':[],'excluded_plant_positions':0,'removed_source_objects':[]}
def oval(name,loc,sc,key,c=PLANT,sub=2,physical=True):
 me=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=1);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);c.objects.link(o);o.location=loc;o.scale=sc;me.materials.append(G.M[key]);o['physical']=physical
 for f in me.polygons:f.use_smooth=True
 return o
def nodesmat(name):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;bs=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None) or n.new('ShaderNodeBsdfPrincipled');out=next((x for x in n if x.type=='OUTPUT_MATERIAL'),None) or n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(bs.outputs[0],out.inputs['Surface']);return m,n,m.node_tree.links,bs
# Keep all source palette materials intact. New land appearance uses the saved
# stone and leaf colours rather than a missing legacy vertex-colour layer.
ground,n,lk,bs=nodesmat('v17 planted ground / retained stone and leaf families')
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.12;noise.inputs['Detail'].default_value=3
tc=n.new('ShaderNodeTexCoord');lk.new(tc.outputs['Object'],noise.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB')
stone=G.M['stone'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value[:]
leaf=G.M['leaf'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value[:]
ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=tuple(.68*stone[k]+.32*leaf[k] for k in range(3))+(1,)
ramp.color_ramp.elements[1].position=.75;ramp.color_ramp.elements[1].color=tuple(.22*stone[k]+.78*leaf[k] for k in range(3))+(1,)
lk.new(noise.outputs['Fac'],ramp.inputs[0]);lk.new(ramp.outputs[0],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.93
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.08;lk.new(noise.outputs['Fac'],bump.inputs['Height']);lk.new(bump.outputs[0],bs.inputs['Normal'])
G.M['ground17']=ground
for i in P['islands']:
 ob=bpy.data.objects[i['id']+' separate cloud support'];rec['material_changes'].append({'object':ob.name,'slot':0,'old':ob.data.materials[0].name,'new':ground.name});ob.data.materials[0]=ground

# New moss uses the exact retained leaf material; no recolouring architecture.
G.M['moss17']=G.M['leaf']

# All new landscaping is checked against protected source meshes in plan.
protected=[]
for ob in list(S.objects):
 if ob.type!='MESH':continue
 if any(token in ob.name for token in ['internal garden path','courtyard approach','cross-cloud bridge','change-level pavilion',' reused ','water basin','shallow channel','spillway','free fall']):
  a=np.array([ob.matrix_world@Vector(v) for v in ob.bound_box]);protected.append((a.min(0),a.max(0)))
def blocked(x,y,z,r):
 for lo,hi in protected:
  if hi[2]<z-.5 or lo[2]>z+18:continue
  if np.linalg.norm(np.maximum(np.maximum(lo[:2]-[x,y],[x,y]-hi[:2]),0))<r+2:return True
 return False
def field_bvh(i):
 ob=bpy.data.objects[i['id']+' separate cloud support'];return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons])
def supports(b,x,y,z,r):
 for dx,dy in [(0,0),(r,0),(-r,0),(0,r),(0,-r)]:
  hit=b.ray_cast(Vector((x+dx,y+dy,z+.1)),Vector((0,0,-1)),.4)[0]
  if hit is None:return False
 return True

# Replace the equally spaced under-edge beads with asymmetric interlocking
# cloud sleeves. They stay below the garden and outside free-fall corridors.
for ob in list(S.objects):
 if ' cloud shoulder' in ob.name:rec['removed_source_objects'].append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
for i in P['islands']:
 cx,cy,z=i['center'];rng=random.Random(1700+ord(i['id']));poly=i['outline'];b=field_bvh(i)
 for k in range(0,len(poly),5):
  if rng.random()<.24:continue
  x,y=poly[k];x=cx+(x-cx)*.97;y=cy+(y-cy)*.97;rx=rng.uniform(5,12);ry=rng.uniform(4,10);rz=rng.uniform(3,6)
  if any(np.linalg.norm(np.array([x,y])-w['fall_xy'])<max(rx,ry)+7 for w in P['water']):continue
  ob=oval(i['id']+' cloud sleeve', (x,y,z-rz-.8),(rx,ry,rz),'cloudwhite',EDGE,3);ob['island_id']=i['id'];rec['cloud_sleeves'].append({'object':ob.name,'island':i['id']})
 # Irregular clusters inside gardens, not rings of identical trees.
 accepted=[]
 for attempt in range(170):
  ang=rng.random()*math.tau;rad=math.sqrt(rng.random())*.94;x=cx+i['radius'][0]*rad*math.cos(ang);y=cy+i['radius'][1]*rad*math.sin(ang);size=rng.uniform(3.0,6.5)
  if blocked(x,y,z,size+2) or not supports(b,x,y,z,size+2) or any(math.hypot(x-a,y-bb)<size+rr+2 for a,bb,rr in accepted):rec['excluded_plant_positions']+=1;continue
  accepted.append((x,y,size));group=i['id']+f' rooted cluster {len(accepted):02}'
  oval(group+' planted mound',(x,y,z-.1),(size*1.35,size,1.4),'moss17')
  # Connected overlapping rock seam with moss, not isolated decorative balls.
  if len(accepted)%3!=0:
   for j in range(3):oval(group+' rock seam',(x+(j-1)*size*.55,y+math.sin(j)*1.2,z+.45),(size*.65,size*.5,1.4+rng.random()*1.3),'rock')
  h=rng.uniform(6,11);trunk=Vector((x,y,z));crown=Vector((x+1.2,y+.3,z+h));G.beam(group+' trunk',[trunk,trunk.lerp(crown,.55)+Vector((.6,0,0)),crown],.22,'wood',PLANT)
  for j in range(4):
   t=j*2.3;tip=crown+Vector((math.cos(t)*size*.55,math.sin(t)*size*.55,(j-2)*1.2));G.beam(group+' branch',[crown-Vector((0,0,2)),tip],.10,'wood',PLANT);oval(group+' canopy',tip,(size*.65,size*.55,1.1),'pine' if j%3 else 'leaf')
  for j in range(7):
   t=rng.random()*math.tau;rr=rng.uniform(size*.5,size*1.1);oval(group+' understory',(x+math.cos(t)*rr,y+math.sin(t)*rr,z+.4),(1.4,1.2,.7),'leaf')
  rec['plant_groups'].append({'id':group,'island':i['id'],'xy':[x,y],'radius':size})
  if len(accepted)>= (16 if i['id']=='A' else 10):break

# Tall connector frames become open garden towers. Facades are outside the
# walking footprint; large south doors and south-west balcony access stay open.
for l in P['links']:
 ident=l['id'];x,y=l['tower'];t=l['tower_geometry'];lo=t['lower_z'];hi=t['upper_z'];lev=t['levels'];h=(hi-lo)/lev
 for k in range(lev):
  zz=lo+k*h
  for side in [-1,1]:
   # Left facade starts beyond the south landing, providing balcony access.
   yy=y+1.5 if side==-1 else y;length=10 if side==-1 else 14.4
   if k>0:G.box(ident+' outer wall sill',(x+side*8.05,yy,zz+.55),(.3,length,1.1),'wall',ARCH)
   G.box(ident+' outer wall lintel',(x+side*8.05,yy,zz+h-.3),(.3,length,.6),'wall',ARCH)
   for dy in ([-3,1,5] if k>0 else []):
    G.box(ident+' window jamb',(x+side*8.05,y+dy,zz+h/2),(.32,.24,h),'redwood',ARCH)
    G.box(ident+' horizontal lattice',(x+side*8.08,y+dy+1.5,zz+h*.63),(.13,2.7,.09),'wood',ARCH)
  # Rear wall remains beyond the half landing; windows are actual open spaces.
  G.box(ident+' rear parapet',(x-.5,y+7.3,zz+h/2+.5),(8,.26,1),'wall',ARCH)
  for dx in [-4.5,3.5]:G.beam(ident+' rear window post',[(x+dx,y+7.3,zz),(x+dx,y+7.3,zz+h)],.13,'redwood',ARCH)
  # Front facade leaves a 6m doorway aligned to the 5m bridge at every level.
  for side in ([-1,1] if k>0 else []):
   G.box(ident+' front side pier',(x+side*5.7,y-7.25,zz+h/2),(4.4,.3,h),'wall',ARCH)
   G.box(ident+' front window inset',(x+side*5.7,y-7.42,zz+h*.55),(2.7,.05,h*.43),'window',ARCH)
   for dx in [-1.1,0,1.1]:G.box(ident+' front window lattice',(x+side*5.7+dx,y-7.46,zz+h*.55),(.07,.07,h*.43),'wood',ARCH)
   for dz in [-.12,.12]:G.box(ident+' front window transom',(x+side*5.7,y-7.46,zz+h*(.55+dz)),(2.7,.07,.07),'wood',ARCH)
  # Horizontal ring-eaves are split at bridge/door line, and stay outside stair wells.
  if k>0 and k!=(lev//2 if lev>=5 else -1) and (k%3==0 or lev<=3):
   for side in [-1,1]:G.roof(ident+' outer side eave',(x+side*9.2,y,zz+.25),(15.5,2.3),.55,math.pi/2)
   G.roof(ident+' rear eave',(x,y+8.1,zz+h/2+2.5),(18,2.0),.45,0)
 # Inspectable stair guards: exact rising rails on outer sides of both flights.
 for k in range(lev):
  zz=lo+k*h
  for side,xx in [(0,x-4.28),(1,x+3.08)]:
   a=(xx,y-4.35,zz+1.05) if side==0 else (xx,y+4.35,zz+h/2+1.05)
   b2=(xx,y+4.35,zz+h/2+1.05) if side==0 else (xx,y-4.35,zz+h+1.05)
   G.beam(ident+' stair outside handrail',[a,b2],.065,'wood',ARCH)
   for u in [.1,.35,.6,.85]:
    pp=Vector(a).lerp(Vector(b2),u);G.beam(ident+' stair guard post',[pp-Vector((0,0,1)),pp],.06,'wood',ARCH)
 # One or two small viewing balconies on the tall towers, varied by purpose.
 levels=[lev//2] if lev>=5 else []
 for k in levels:
  zz=lo+k*h;G.box(ident+' viewing balcony',(x-10,y-3.7,zz-.18),(4.4,6.6,.36),'wood',ARCH)
  G.beam(ident+' balcony rail',[(x-12.2,y-7,zz+1.1),(x-12.2,y-.4,zz+1.1),(x-8,y-.4,zz+1.1)],.08,'wood',ARCH)
  for yy in np.arange(y-7,y-.3,1.1):G.beam(ident+' balcony baluster',[(x-12.2,yy,zz),(x-12.2,yy,zz+1.1)],.06,'wood',ARCH)
  G.box(ident+' viewing bench',(x-9.8,y-1.2,zz+.48),(3.4,.65,.18),'wood',ARCH)
  for dx in [-1.2,1.2]:G.box(ident+' bench leg',(x-9.8+dx,y-1.2,zz+.22),(.18,.5,.44),'wood',ARCH)
  rec['balconies'].append({'link':ident,'floor':zz,'access':'west end of south landing','use':'viewing and rest'})

# Give reused courts a readable threshold, veranda and small daily-use details.
for c in P['courts']:
 iid=c['island'];z=next(i['center'][2] for i in P['islands'] if i['id']==iid)+.16;cx,cy=c['target_center'];ang=math.radians(c['angle']);ident=iid+' '+c['source_prefix']
 def at(x,y,h):return (cx+x*math.cos(ang)-y*math.sin(ang),cy+x*math.sin(ang)+y*math.cos(ang),z+h)
 for x in [-3.2,3.2]:G.beam(ident+' entrance post',[at(x,-17,0),at(x,-17,4.5)],.16,'redwood',DETAIL)
 G.ARCH=DETAIL;G.roof(ident+' garden entry eave',at(0,-17,4.5),(8.3,3.5),1.2,ang)
 G.roof(ident+' veranda eave',at(0,6.4,4.2),(30.5,4.2),1.1,ang)
 for x in [-14,-7,7,14]:G.beam(ident+' veranda column',[at(x,4.8,0),at(x,4.8,4.2)],.14,'redwood',DETAIL)
 for x in [-10,10]:
  for y in [5.3,6.3]:G.box(ident+' veranda bench',at(x,y,.55),(4,.45,.17),'wood',DETAIL,ang)
  for dx in [-1.5,1.5]:G.box(ident+' veranda bench support',at(x+dx,5.8,.27),(.16,1.4,.54),'wood',DETAIL,ang)
 # Rear facade retains openings/material; add lattice strips and a dark door marker.
 for x in [-9.9,9.9]:
  for dx in [-2,-1,0,1,2]:G.box(ident+' lattice mullion',at(x+dx,8.35,2.7),(.065,.08,2.7),'wood',DETAIL,ang)
  for h in [1.6,2.6,3.6]:G.box(ident+' lattice transom',at(x,8.35,h),(4.6,.08,.065),'wood',DETAIL,ang)
 if iid in ['F','G']:
  G.box(ident+' work or tea table',at(-7,0,1),(3,1.3,.18),'wood',DETAIL,ang)
  for xx in [-8.2,-5.8]:G.box(ident+' table legs',at(xx,0,.5),(.16,.8,1),'wood',DETAIL,ang)
  for j in range(3):G.box(ident+' daily objects',at(-7.7+j*.65,0,1.23),(.35,.4,.28),'stone' if iid=='F' else 'wood',DETAIL,ang)
 G.ARCH=ARCH

# Irregular low bank rock groups on selected portions of pools. Do not turn
# them into circular raised walls or cover the water/falling-water centre.
for w in P['water']:
 for iid,center,z,rad in [(w['from'],w['source_pool'],w['source_z'],10),(w['to'],w['fall_xy'],w['catch_z'],11)]:
  island=next(i for i in P['islands'] if i['id']==iid);b=field_bvh(island);rng=random.Random(17000+ord(iid)+int(w['id'][1])*20)
  direction=np.array(w['fall_xy'])-w['source_pool'];angle=math.atan2(direction[1],direction[0])
  for k in range(18):
   a=k*math.tau/18
   if math.cos(a-angle)>.7 and iid==w['from']:continue
   x=center[0]+math.cos(a)*(rad+1.2);y=center[1]+math.sin(a)*(rad+1.2)
   # Protect roads/towers/courts but omit pool bounds for its own shoreline.
   if not supports(b,x,y,z+.45,1.1):continue
   avoid=False
   for ob in S.objects:
    if ob.type!='MESH' or not any(t in ob.name for t in ['internal garden path','change-level pavilion',' reused ']):continue
    bb=np.array([ob.matrix_world@Vector(v) for v in ob.bound_box]);lo=bb.min(0);hi=bb.max(0)
    if lo[2]<=z+2 and hi[2]>=z-.5 and np.linalg.norm(np.maximum(np.maximum(lo[:2]-[x,y],[x,y]-hi[:2]),0))<2:avoid=True;break
   if avoid:continue
   oval(w['id']+' '+iid+' natural pool edge',(x,y,z+.45),(1.4+rng.random(),1.0,.65+rng.random()*.45),'rock',DETAIL)
 # Transparent sheen and fine separated strands articulate the existing fall.
 fall=bpy.data.objects[w['id']+' free fall'];mat=G.M['water'].copy();mat.name=w['id']+' water curtain detail';fall.data.materials[0]=mat
 bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.18
 n=mat.node_tree.nodes;lk=mat.node_tree.links;noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.6;noise.inputs['Detail'].default_value=2;bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.045;lk.new(noise.outputs['Fac'],bump.inputs['Height']);lk.new(bump.outputs[0],bs.inputs['Normal'])
 rec['material_changes'].append({'object':fall.name,'slot':0,'old':G.M['water'].name,'new':mat.name})

# Local veils intersect garden edges at different heights, not a fog blanket.
cm=bpy.data.materials['v16 atmosphere, non-bearing mist'].copy();cm.name='v17 edge mist non bearing';cm.node_tree.nodes.get('Map Range').inputs['To Min'].default_value=.035;G.M['edge_mist']=cm
# Cloud shoulder lobes are optical mist around the unchanged bearing core.
# Using a volume avoids a necklace of opaque white balls around each garden.
shoulder=cm.copy();shoulder.name='v17 soft shoulder mist';shoulder.node_tree.nodes.get('Map Range').inputs['To Min'].default_value=.18
for ob in EDGE.objects:ob.data.materials.clear();ob.data.materials.append(shoulder);ob['physical']=False;ob['role']='non-bearing cloud around retained solid support'
for material in [cm,shoulder]:
 vol=next(n for n in material.node_tree.nodes if n.type=='PRINCIPLED_VOLUME');vol.inputs['Emission Color'].default_value=(.86,.92,1,1);links=material.node_tree.links;density=next(link.from_socket for link in links if link.to_socket==vol.inputs['Density']);gain=material.node_tree.nodes.new('ShaderNodeMath');gain.operation='MULTIPLY';gain.inputs[1].default_value=.12;links.new(density,gain.inputs[0]);links.new(gain.outputs[0],vol.inputs['Emission Strength'])
rec['cloud_sleeve_role']='non-bearing volume; structural core stays in source separate cloud support'
for i in P['islands']:
 cx,cy,z=i['center'];poly=i['outline'];rng=random.Random(1730+ord(i['id']))
 for k in [12,48,83]:
  x,y=poly[k];x=cx+(x-cx)*.98;y=cy+(y-cy)*.98
  if any(np.linalg.norm(np.array([x,y])-w['fall_xy'])<30 for w in P['water']):continue
  oval(i['id']+' non-bearing cloud veil',(x,y,z-1),(22+rng.random()*12,14+rng.random()*8,9+rng.random()*7),'edge_mist',MIST,3,False)
G.ARCH=ARCH
S['status']='v17 garden development candidate; accepted v16 spatial skeleton retained';S.render.resolution_x=1440;S.render.resolution_y=1000;S.eevee.taa_render_samples=40;S.eevee.volumetric_samples=64
bpy.ops.wm.save_as_mainfile(filepath=str(O/'island-garden-developed-v17.blend'))
P['version']='v17';P['status']='garden development on accepted v16 layout';P['source_sha256']=rec['source_sha256'];(O/'planning-data.json').write_text(json.dumps(P,ensure_ascii=False,indent=2),encoding='utf8')
rec['new_objects']=sorted(set(o.name for o in S.objects)-original_names);(O/'development-data.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf8')
print('V17_BUILD_READY',len(S.objects),len(rec['plant_groups']),flush=True)
