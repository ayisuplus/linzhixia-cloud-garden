"""Independent read-only CPU v10 audit. Run Blender -b -t 2 --python audit.py -- ROOT."""
import bpy,sys,json,hashlib,array,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集山谷植物-20261024-v0.1';OLD=R/'视频制作/第一集水巷街桥-20261024-v0.1'
sys.path.insert(0,str(R/'第一季/制作/空间规划/第一集山水总图白模-v0.1'));import layout as L
files=[OLD/'waterlane-masterplan-v09.blend',O/'valley-masterplan-v10.blend',O/'valley-route-58s-v10.blend',OLD/'route-poses.json',O/'route-poses.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
hashes={str(p):sha(p) for p in files}
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def val(x):
 try:return list(x)
 except TypeError:return x
def material(m):
 ns=[];ls=[]
 if m.use_nodes:
  for n in m.node_tree.nodes:
   ns.append((n.name,n.bl_idname,[(i.name,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]))
  ls=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links)
 return digest([list(m.diffuse_color),m.use_nodes,ns,ls])
def mesh(m):
 h=hashlib.sha256()
 for seq,prop,count,typ in [(m.vertices,'co',3,'f'),(m.loops,'vertex_index',1,'i'),(m.polygons,'loop_start',1,'i'),(m.polygons,'loop_total',1,'i'),(m.polygons,'material_index',1,'i')]:
  a=array.array(typ,[0])*(len(seq)*count);seq.foreach_get(prop,a);h.update(a.tobytes())
 return h.hexdigest()
def snapshot():
 mc={};out={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and o.data.name not in mc:mc[o.data.name]=mesh(o.data)
  out[o.name]={'type':o.type,'mesh':mc.get(o.data.name) if o.type=='MESH' else None,'matrix':[v for row in o.matrix_world for v in row],'materials':[(s.material.name if s.material else None,s.link) for s in o.material_slots]}
 return out,{m.name:material(m) for m in bpy.data.materials}
bpy.ops.wm.open_mainfile(filepath=str(files[0]));old,oldmat=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(files[1]));new,newmat=snapshot();changes=[]
for n,a in old.items():
 if n not in new:changes.append({'object':n,'change':'missing'});continue
 b=new[n]
 for k in ['type','mesh','materials']:
  if a[k]!=b[k]:changes.append({'object':n,'change':k})
 delta=max(abs(x-y) for x,y in zip(a['matrix'],b['matrix']))
 if delta>1e-6:changes.append({'object':n,'change':'matrix','max_abs':delta})
matdiff=[n for n,h in oldmat.items() if newmat.get(n)!=h]
obs={o.name:o for o in bpy.context.scene.objects};added=[o for n,o in obs.items() if n not in old and o.type=='MESH'];cache={}
def get(o):
 if o.name not in cache:
  vs=[o.matrix_world@v.co for v in o.data.vertices];fs=[tuple(p.vertices) for p in o.data.polygons];a=np.array(vs)
  cache[o.name]={'name':o.name,'vs':vs,'fs':fs,'lo':a.min(0),'hi':a.max(0),'bvh':BVHTree.FromPolygons(vs,fs)}
 return cache[o.name]
def combine(gs):
 v=[];f=[];ns=[]
 for g in gs:
  off=len(v);v.extend(g['vs']);f.extend(tuple(off+i for i in face) for face in g['fs']);ns.extend([g['name']]*len(g['fs']))
 return BVHTree.FromPolygons(v,f),ns
ag=[get(o) for o in added];abvh,anames=combine(ag)
buildings=[get(o) for cn in ['04 Contour courtyard clusters','09 Waterfront streets and inhabited bridgeheads','10 Connected bridges and quays'] for o in bpy.data.collections[cn].objects if o.type=='MESH' and not o.hide_render]
intersections=[]
for a in ag:
 for b in buildings:
  if np.all(a['hi']>=b['lo']) and np.all(b['hi']>=a['lo']):
   ov=a['bvh'].overlap(b['bvh'])
   if ov:intersections.append({'new':a['name'],'old':b['name'],'surface_pairs':len(ov)})
P=json.loads((R/'视频制作/第一集山水总图白模-20261024-v0.1/layout-plan.json').read_text('utf8'))
def roadname(n):
 if n.startswith('bank-'):return 'Continuous bank lane '+n[5:]
 if n.endswith('-entry') and n!='middle-entry':return n[:-6]+' entry connection'
 if n.startswith('hill-'):return 'Upper slope street '+n[5:]
 if n.startswith('slope-link-'):
  side,cs=n[11:].rsplit('-',1);return 'Bank to slope connector '+side+' '+cs
 if n=='middle-entry':return 'Second-level through passage and gallery'
 return None
pathhits=[]
for p in P['paths']:
 name=roadname(p['id'])
 if name not in obs:continue
 deck=get(obs[name])['bvh'];pts=np.array(p['points']);hits={}
 for a,b in zip(pts,pts[1:]):
  direction=b-a;side=np.array([-direction[1],direction[0],0]);side/=max(np.linalg.norm(side),1e-9)
  for lateral in [-.9,0,.9]:
   aa=deck.ray_cast(Vector(a+side*lateral+[0,0,20]),Vector((0,0,-1)),40)[0];bb=deck.ray_cast(Vector(b+side*lateral+[0,0,20]),Vector((0,0,-1)),40)[0]
   if aa is None or bb is None:continue
   d=bb-aa
   if d.length<1e-6:continue
   for h in [.15,.9,1.8]:
    hit=abvh.ray_cast(aa+Vector((0,0,h)),d.normalized(),d.length)
    if hit[0] is not None:hits.setdefault(anames[hit[2]],{'point':list(hit[0]),'height':h,'lateral':lateral})
 if hits:pathhits.append({'path':p['id'],'hits':hits})
columns=[get(o) for o in obs.values() if o.type=='MESH' and ('arcade column' in o.name or 'roof column' in o.name)]
cbvh,cnames=combine(columns)
oldposes=json.loads(files[3].read_text('utf8'));poses=json.loads(files[4].read_text('utf8'));positions=np.array([p['position'] for p in poses]);stations=L.nearest(positions[:,:2])[0]
def nearestrow(p,frame,time):
 h=cbvh.find_nearest(Vector(p));return {'frame':frame,'time':time,'position':list(p),'object':cnames[h[2]],'surface_point':list(h[0]),'center_to_surface_m':h[3]}
rows=[nearestrow(p,i+1,i/24) for i,p in enumerate(positions) if .825<=stations[i]<=.916]
dense=[]
for i,(a,b) in enumerate(zip(positions,positions[1:])):
 if not (.825<=stations[i]<=.916 or .825<=stations[i+1]<=.916):continue
 n=max(1,int(math.ceil(np.linalg.norm(b-a)/.1)))
 for k in range(n+1):
  f=k/n;row=nearestrow(a+(b-a)*f,i+1+f,(i+f)/24);dense.append(row)
oldwindow=[nearestrow(p['position'],p['frame'],p['time']) for p in oldposes if 49.6<=p['time']<=50.0]
offsets=[Vector((x,y,z)) for x in [-.55,0,.55] for y in [-.55,0,.55] for z in [-.35,0,.35]];flighthits=[]
for i,(a,b) in enumerate(zip(positions,positions[1:])):
 a=Vector(a);d=Vector(b)-a
 if d.length<1e-6:continue
 for off in offsets:
  h=abvh.ray_cast(a+off,d.normalized(),d.length)
  if h[0] is not None:flighthits.append({'frame':i+1,'object':anames[h[2]],'point':list(h[0])});break
bpy.ops.wm.open_mainfile(filepath=str(files[2]));cam=bpy.context.scene.camera;action=cam.animation_data.action;curves=[]
if hasattr(action,'layers'):
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:curves.extend(bag.fcurves)
else:curves=list(action.fcurves)
loc={f.array_index:f for f in curves if f.data_path=='location'};actual=np.array([[loc[j].evaluate(i+1) for j in range(3)] for i in range(len(positions))]);err=float(np.max(np.abs(actual-positions)))
rot={f.array_index:f for f in curves if f.data_path=='rotation_quaternion'}
qs=np.array([[rot[j].evaluate(i+1) for j in range(4)] for i in range(len(positions))]);qs/=np.linalg.norm(qs,axis=1)[:,None];angles=np.degrees(2*np.arccos(np.clip(np.abs(np.sum(qs[:-1]*qs[1:],axis=1)),0,1)))
flight_snapshot,flight_materials=snapshot();static_vs_flight=[n for n,v in new.items() if flight_snapshot.get(n)!=v];flight_mat_diff=[n for n,v in newmat.items() if flight_materials.get(n)!=v]
result={'hashes':hashes,'stable':all(sha(Path(p))==h for p,h in hashes.items()),'old_object_count':len(old),'added_mesh_count':len(added),'original_object_changes':changes,'original_material_changes':matdiff,'new_against_building_surface_intersections':intersections,'old_walk_core_hits':pathhits,'new_geometry_flight_27_sweeps':flighthits,'saved_camera_parent':cam.parent.name if cam.parent else None,'saved_keyframe_json_position_max_abs_m':err,'static_vs_flight_object_differences':static_vs_flight,'static_vs_flight_material_differences':flight_mat_diff,'saved_camera_max_rotation_deg_per_frame':float(angles.max()),'saved_camera_max_rotation_at_frame':int(angles.argmax()+1),'new_late_dense_column_nearest':min(dense,key=lambda r:r['center_to_surface_m']),'new_late_dense_max_step_m':.1,'new_late_dense_sample_count':len(dense),'new_late_column_nearest':min(rows,key=lambda r:r['center_to_surface_m']),'new_late_frame_range':[rows[0]['frame'],rows[-1]['frame']],'old_49_8_window_column_nearest':min(oldwindow,key=lambda r:r['center_to_surface_m']),'old_nearest_49_8_sample':nearestrow(min(oldposes,key=lambda p:abs(p['time']-49.8))['position'],min(oldposes,key=lambda p:abs(p['time']-49.8))['frame'],min(oldposes,key=lambda p:abs(p['time']-49.8))['time']),'limits':['No render/GPU/save/source edits/Git.','Geometry coordinates/topology/material indices/bindings and matrices; material node input values and links. Not every custom property or arbitrary node attribute.','Surface overlap is not full containment proof. Walk tests use finite swept lines, not exact human volume.','New-entity flight check uses 27 fixed world offsets; not continuous swept-solid certification. Existing collision objects are parent full-route audit scope.','Column distance is path center to actual mesh surface, not vehicle outside clearance; vehicle max corner radius is about 0.853m.','No continuous video viewing in this audit.']}
(O/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print('INDEPENDENT_AUDIT_DONE',len(changes),len(matdiff),len(intersections),len(pathhits),len(flighthits),flush=True)
