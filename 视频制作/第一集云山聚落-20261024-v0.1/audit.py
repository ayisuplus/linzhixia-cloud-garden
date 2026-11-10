"""Independent CPU v11 scene/flight/walk review. Read only, no render/save."""
import bpy,sys,json,hashlib,array,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云山聚落-20261024-v0.1';OLD=R/'视频制作/第一集山谷植物-20261024-v0.1'
files=[OLD/'valley-masterplan-v10.blend',O/'cloud-hamlet-masterplan-v11.blend',OLD/'valley-route-58s-v10.blend',O/'cloud-hamlet-route-58s-v11.blend',OLD/'route-poses.json',O/'route-poses.json',O/'landscape-data.json']
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
if '--refinement-only' in sys.argv:
 previous=json.loads((O/'audit.json').read_text('utf8'));baseline=Path(str(files[1])+'1');baseline_route=Path(str(files[3])+'1')
 assert sha(baseline)==previous.get('certified_geometry_baseline_hashes',previous['hashes'])[str(files[1])], 'Baseline does not match prior certified geometry'
 assert sha(baseline_route)==previous.get('certified_geometry_baseline_hashes',previous['hashes'])[str(files[3])], 'Baseline route mismatch'
 def activegroups():return {o.name for cn in ['12 Contour woodland and understory','15 Terrain rooted rock seams'] for o in bpy.data.collections[cn].objects}
 bpy.ops.wm.open_mainfile(filepath=str(baseline));before,bmat=snapshot();bn=activegroups()
 bpy.ops.wm.open_mainfile(filepath=str(files[1]));after,amat=snapshot();an=activegroups();outside=[n for n in set(before)|set(after) if n not in bn|an and before.get(n)!=after.get(n)];mdiff=[n for n in bmat if bmat[n]!=amat.get(n)]
 obs={o.name:o for o in bpy.context.scene.objects};cache={}
 def get(o):
  if o.name not in cache:
   v=[o.matrix_world@p.co for p in o.data.vertices];f=[tuple(p.vertices) for p in o.data.polygons];a=np.array(v);cache[o.name]={'name':o.name,'v':v,'f':f,'lo':a.min(0),'hi':a.max(0),'bvh':BVHTree.FromPolygons(v,f)}
  return cache[o.name]
 def combine(gs):
  v=[];f=[];names=[]
  for g in gs:
   off=len(v);v.extend(g['v']);f.extend(tuple(off+i for i in face) for face in g['f']);names.extend([g['name']]*len(g['f']))
  return BVHTree.FromPolygons(v,f),names
 def height(bvh,xy,z=500,distance=1000):
  h=bvh.ray_cast(Vector((xy[0],xy[1],z)),Vector((0,0,-1)),distance);return h[0].z if h[0] is not None else None
 def overlap(a,b):return np.all(a['hi']>=b['lo']) and np.all(b['hi']>=a['lo'])
 ground=get(obs['Continuous stable cloud terrain / river bed and inhabited slopes']);targets=[get(obs[n]) for n in an if obs[n].type=='MESH' and obs[n].get('physical',False)];bvh,names=combine(targets);arch=[get(o) for cn in ['04 Contour courtyard clusters','09 Waterfront streets and inhabited bridgeheads','10 Connected bridges and quays','13 Hillside inhabited terraces'] for o in bpy.data.collections[cn].objects if o.type=='MESH' and not o.hide_render];pairs=[]
 for a in targets:
  for b in arch:
   if overlap(a,b):
    ov=a['bvh'].overlap(b['bvh'])
    if ov:pairs.append({'new':a['name'],'building':b['name'],'pairs':len(ov)})
 poses=json.loads(files[5].read_text('utf8'));positions=np.array([p['position'] for p in poses]);offsets=[Vector((x,y,z)) for x in [-.55,0,.55] for y in [-.55,0,.55] for z in [-.35,0,.35]];hits=[]
 for i,(a,b) in enumerate(zip(positions,positions[1:])):
  a=Vector(a);d=Vector(b)-a
  if d.length<1e-7:continue
  for off in offsets:
   h=bvh.ray_cast(a+off,d.normalized(),d.length)
   if h[0] is not None:hits.append({'frame':i+1,'object':names[h[2]],'point':list(h[0])});break
 P=json.loads((R/'视频制作/第一集山水总图白模-20261024-v0.1/layout-plan.json').read_text('utf8'));D=json.loads(files[6].read_text('utf8'));pathhits=[]
 def roadname(n):
  if n.startswith('bank-'):return 'Continuous bank lane '+n[5:]
  if n.endswith('-entry') and n!='middle-entry':return n[:-6]+' entry connection'
  if n.startswith('hill-'):return 'Upper slope street '+n[5:]
  if n.startswith('slope-link-'):
   side,cs=n[11:].rsplit('-',1);return 'Bank to slope connector '+side+' '+cs
  if n=='middle-entry':return 'Second-level through passage and gallery'
  return None
 for path in P['paths']+D['stairs']:
  if path in D['stairs']:
   gs=[get(o) for o in obs.values() if o.type=='MESH' and o.name.startswith(path['id']+' ') and any(k in o.name for k in ['stone step','landing'])];deck,_=combine(gs)
  else:
   name=roadname(path['id'])
   if name not in obs:continue
   deck=get(obs[name])['bvh']
  pts=np.array(path['points']);row={}
  for a,b in zip(pts,pts[1:]):
   d=b-a;normal=np.array([-d[1],d[0],0]);normal/=max(np.linalg.norm(normal),1e-9)
   for lateral in [-.9,0,.9]:
    aa=a+normal*lateral;bb=b+normal*lateral;za=height(deck,aa,aa[2]+.4,1.0);zb=height(deck,bb,bb[2]+.4,1.0)
    if za is None or zb is None:continue
    aa=Vector((aa[0],aa[1],za));bb=Vector((bb[0],bb[1],zb));dd=bb-aa
    if dd.length<1e-7:continue
    for h in [.15,.9,1.8]:
     hit=bvh.ray_cast(aa+Vector((0,0,h)),dd.normalized(),dd.length)
     if hit[0] is not None:row.setdefault(names[hit[2]],list(hit[0]))
  if row:pathhits.append({'path':path['id'],'hits':row})
 roots=[]
 for g in targets:
  if not g['name'].startswith('Continuous rooted rock seam'):continue
  edges=set()
  for f in g['f']:
   for i,j in zip(f,f[1:]+f[:1]):
    e=tuple(sorted([i,j]))
    if e in edges:edges.remove(e)
    else:edges.add(e)
  ids=sorted({i for e in edges for i in e});off=[g['v'][i].z-height(ground['bvh'],g['v'][i]) for i in ids];roots.append({'name':g['name'],'boundary_vertex_count':len(ids),'boundary_ground_offset_min_max_m':[min(off),max(off)]})
 def action_digest(path):
  bpy.ops.wm.open_mainfile(filepath=str(path));cam=bpy.context.scene.camera;data=[]
  for layer in cam.animation_data.action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for f in bag.fcurves:data.append((f.data_path,f.array_index,[(list(p.co),p.interpolation,list(p.handle_left),list(p.handle_right)) for p in f.keyframe_points]))
  return digest(data)
 ca=action_digest(baseline_route);cb=action_digest(files[3]);ref={'baseline_static_hash':sha(baseline),'baseline_route_hash':sha(baseline_route),'outside_tree_rock_object_changes':outside,'material_changes':mdiff,'tree_rock_building_surface_intersections':pairs,'tree_rock_old_and_new_walk_hits':pathhits,'tree_rock_all_frame_27_swept_hits':hits,'rock_boundary_support':roots,'camera_action_identical':ca==cb,'poses_byte_identical':files[4].read_bytes()==files[5].read_bytes(),'scope':'Prior geometry checks reused only after exact mesh/matrix/material-binding snapshot equality outside tree/rock groups and matching baseline hash; new tree/rock rescanned.'}
 previous.setdefault('certified_geometry_baseline_hashes',previous['hashes']);previous['hashes']=hashes;previous['stable']=all(sha(Path(p))==h for p,h in hashes.items());previous['final_tree_rock_refinement']=ref;(O/'audit.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');print('REFINEMENT_DONE',len(outside),len(mdiff),len(pairs),len(pathhits),len(hits),ca==cb,flush=True);raise SystemExit
GROUND='Continuous stable cloud terrain / river bed and inhabited slopes'
D=json.loads(files[6].read_text('utf8'));allowed=set(D['removed_v10_scatter_objects'])
bpy.ops.wm.open_mainfile(filepath=str(files[0]));old,oldmat=snapshot();oldground=np.array([v.co[:] for v in bpy.data.objects[GROUND].data.vertices]);oldfaces=[tuple(f.vertices) for f in bpy.data.objects[GROUND].data.polygons]
bpy.ops.wm.open_mainfile(filepath=str(files[1]));new,newmat=snapshot();obs={o.name:o for o in bpy.context.scene.objects};changes=[]
for n,a in old.items():
 if n in allowed:
  if n in new:changes.append({'object':n,'change':'approved_delete_not_applied'})
  continue
 if n not in new:changes.append({'object':n,'change':'missing'});continue
 b=new[n]
 for key in ['type','mesh','materials']:
  if n==GROUND and key in ['mesh','materials']:continue
  if a[key]!=b[key]:changes.append({'object':n,'change':key})
 delta=max(abs(x-y) for x,y in zip(a['matrix'],b['matrix']))
 if delta>1e-6:changes.append({'object':n,'change':'matrix','max_abs':delta})
matdiff=[n for n,h in oldmat.items() if newmat.get(n)!=h]
cache={}
def get(o):
 if o.name not in cache:
  v=[o.matrix_world@p.co for p in o.data.vertices];f=[tuple(p.vertices) for p in o.data.polygons];a=np.array(v);cache[o.name]={'name':o.name,'v':v,'f':f,'lo':a.min(0),'hi':a.max(0),'bvh':BVHTree.FromPolygons(v,f)}
 return cache[o.name]
def combine(gs):
 v=[];f=[];names=[]
 for g in gs:
  off=len(v);v.extend(g['v']);f.extend(tuple(off+i for i in face) for face in g['f']);names.extend([g['name']]*len(g['f']))
 return BVHTree.FromPolygons(v,f),names
def overlap(a,b):return np.all(a['hi']>=b['lo']) and np.all(b['hi']>=a['lo'])
ground=get(obs[GROUND]);oldgb=BVHTree.FromPolygons([Vector(v) for v in oldground],oldfaces)
def height(bvh,xy,z=500,distance=1000):
 h=bvh.ray_cast(Vector((xy[0],xy[1],z)),Vector((0,0,-1)),distance);return h[0].z if h[0] is not None else None
allphysical=[get(o) for o in obs.values() if o.type=='MESH' and o.get('physical',False) and not o.hide_render];allbvh,allnames=combine(allphysical)
newphysical=[get(o) for n,o in obs.items() if n not in old and o.type=='MESH' and o.get('physical',False) and not o.hide_render];newbvh,newnames=combine(newphysical)
trees=[get(o) for o in bpy.data.collections['12 Contour woodland and understory'].objects if o.type=='MESH'];houses=[get(o) for o in bpy.data.collections['13 Hillside inhabited terraces'].objects if o.type=='MESH'];oldbuild=[get(o) for cn in ['04 Contour courtyard clusters','09 Waterfront streets and inhabited bridgeheads','10 Connected bridges and quays'] for o in bpy.data.collections[cn].objects if o.type=='MESH' and not o.hide_render]
treehits=[];househits=[]
for a in trees:
 for b in houses+oldbuild:
  if overlap(a,b):
   ov=a['bvh'].overlap(b['bvh'])
   if ov:treehits.append({'tree':a['name'],'building':b['name'],'pairs':len(ov)})
for a in houses:
 for b in oldbuild:
  if overlap(a,b):
   ov=a['bvh'].overlap(b['bvh'])
   if ov:househits.append({'house':a['name'],'old':b['name'],'pairs':len(ov)})
poses=json.loads(files[5].read_text('utf8'));positions=np.array([p['position'] for p in poses]);offsets=[Vector((x,y,z)) for x in [-.55,0,.55] for y in [-.55,0,.55] for z in [-.35,0,.35]];flighthits=[]
for i,(a,b) in enumerate(zip(positions,positions[1:])):
 a=Vector(a);d=Vector(b)-a
 if d.length<1e-6:continue
 for off in offsets:
  h=allbvh.ray_cast(a+off,d.normalized(),d.length)
  if h[0] is not None:flighthits.append({'frame':i+1,'object':allnames[h[2]],'point':list(h[0])});break
rocks=[get(o) for o in bpy.data.collections['15 Terrain rooted rock seams'].objects if o.type=='MESH'];rockhits=[];rockroots=[]
for a in rocks:
 for b in houses+oldbuild:
  if overlap(a,b):
   ov=a['bvh'].overlap(b['bvh'])
   if ov:rockhits.append({'rock':a['name'],'building':b['name'],'pairs':len(ov)})
 edges=set()
 for face in a['f']:
  for i,j in zip(face,face[1:]+face[:1]):
   e=tuple(sorted([i,j]))
   if e in edges:edges.remove(e)
   else:edges.add(e)
 ids=sorted(set(i for e in edges for i in e));off=[a['v'][i].z-height(ground['bvh'],a['v'][i]) for i in ids];rockroots.append({'name':a['name'],'boundary_vertex_count':len(ids),'boundary_ground_offset_min_max_m':[min(off),max(off)]})
stepbottom=[]
for o in bpy.data.collections['14 Bank to hillside stepped access'].objects:
 if o.type!='MESH' or not('stone step' in o.name or 'landing' in o.name):continue
 vals=[]
 for v in list(o.data.vertices)[:4]:
  p=o.matrix_world@v.co;vals.append(p.z-height(ground['bvh'],p))
 stepbottom.append({'name':o.name,'bottom_corner_ground_offsets_m':vals})
print('FLIGHT',len(flighthits),flush=True)
P=json.loads((R/'视频制作/第一集山水总图白模-20261024-v0.1/layout-plan.json').read_text('utf8'))
def roadname(n):
 if n.startswith('bank-'):return 'Continuous bank lane '+n[5:]
 if n.endswith('-entry') and n!='middle-entry':return n[:-6]+' entry connection'
 if n.startswith('hill-'):return 'Upper slope street '+n[5:]
 if n.startswith('slope-link-'):
  side,cs=n[11:].rsplit('-',1);return 'Bank to slope connector '+side+' '+cs
 if n=='middle-entry':return 'Second-level through passage and gallery'
 return None
oldpathhits=[];roadterrain=[]
for path in P['paths']:
 name=roadname(path['id'])
 if name not in obs:continue
 deck=get(obs[name])['bvh'];pts=np.array(path['points']);hits={};maxdelta=0.;maxrow=None
 for a,b in zip(pts,pts[1:]):
  d=b-a;side=np.array([-d[1],d[0],0]);side/=max(np.linalg.norm(side),1e-9)
  for lateral in [-.9,0,.9]:
   qa=a+side*lateral;qb=b+side*lateral;za=height(deck,qa,qa[2]+20,40);zb=height(deck,qb,qb[2]+20,40)
   if za is None or zb is None:continue
   ga=height(ground['bvh'],qa);go=height(oldgb,qa);delta=abs(ga-go)
   if delta>maxdelta:maxdelta=delta;maxrow={'point':qa.tolist(),'new_ground':ga,'old_ground':go}
   aa=Vector((qa[0],qa[1],za));bb=Vector((qb[0],qb[1],zb));dd=bb-aa
   if dd.length<1e-6:continue
   for h in [.15,.9,1.8]:
    hit=newbvh.ray_cast(aa+Vector((0,0,h)),dd.normalized(),dd.length)
    if hit[0] is not None:hits.setdefault(newnames[hit[2]],{'point':list(hit[0]),'height':h,'lateral':lateral})
  # Ground protection sampled also at both outer road edges, independent of mesh unchanged.
  for lat in [-path['width']/2,path['width']/2]:
   q=a+side*lat;ga=height(ground['bvh'],q);go=height(oldgb,q)
   if ga is not None and go is not None and abs(ga-go)>maxdelta:maxdelta=abs(ga-go);maxrow={'point':q.tolist(),'new_ground':ga,'old_ground':go}
 if hits:oldpathhits.append({'path':path['id'],'hits':hits})
 if maxdelta>.001:roadterrain.append({'path':path['id'],'max_abs_ground_change':maxdelta,'sample':maxrow})
print('OLD_WALK',len(oldpathhits),'TERRAIN',len(roadterrain),flush=True)
posts=[]
for g in houses:
 if 'grounded stilt' not in g['name']:continue
 bottom=min(v.z for v in g['v']);pts=[v for v in g['v'] if abs(v.z-bottom)<1e-4];offset=[v.z-height(ground['bvh'],v) for v in pts];posts.append({'name':g['name'],'bottom_corner_ground_offsets_m':offset})
stairresults=[]
for route in D['stairs']:
 id=route['id'];pts=np.array(route['points']);steps=[get(o) for o in obs.values() if o.type=='MESH' and o.name.startswith(id+' ') and any(s in o.name for s in ['stone step','turning landing','arrival landing'])];walkbvh,walknames=combine(steps+ [g for g in houses if g['name'].endswith(' deck')]);supports=[]
 for g in steps:
  if 'stone step' not in g['name']:continue
  bottom=float(g['lo'][2]);vs=[v for v in g['v'] if abs(v.z-bottom)<1e-4];center=sum(vs,Vector())/len(vs);gap=bottom-height(ground['bvh'],center);supports.append({'name':g['name'],'bottom_center_ground_gap_m':gap,'point':list(center)})
 missing=[];buried=[];headhits={};floorpoints=[];risers=[]
 for a,b in zip(pts,pts[1:]):
  delta=b-a;length=np.linalg.norm(delta[:2])
  if length<1e-7:continue
  side=np.array([-delta[1],delta[0],0])/length
  for f in np.linspace(0,1,max(2,int(math.ceil(length/.2))+1)):
   p=a+delta*f
   for lat in [-.8,0,.8]:
    q=p+side*lat;z=height(walkbvh,q,q[2]+.4,1.0)
    if z is None:
     if len(missing)<30:missing.append(q.tolist())
     continue
    gz=height(ground['bvh'],q)
    if gz-z>.04 and len(buried)<40:buried.append({'point':[q[0],q[1],z],'ground_above_step_m':gz-z})
    hit=allbvh.ray_cast(Vector((q[0],q[1],z+.06)),Vector((0,0,1)),1.74)
    if hit[0] is not None:headhits.setdefault(allnames[hit[2]],{'point':list(hit[0]),'floor_z':z,'headroom_m':hit[0].z-z,'lateral':lat,'path_point':p.tolist()})
    if lat==0:floorpoints.append([q[0],q[1],z])
 for st in route['steps']:
  ob=obs.get(st['name'])
  if ob is not None:risers.append({'name':ob.name,'actual_top':float(get(ob)['hi'][2]),'declared_top':st['top']})
 rise=max((abs(b['actual_top']-a['actual_top']) for a,b in zip(risers,risers[1:])),default=0)
 stairresults.append({'id':id,'missing_samples':missing,'terrain_intrusions':buried,'headroom_hits':headhits,'step_support_bottom_center_max_gap_m':max((v['bottom_center_ground_gap_m'] for v in supports),default=None),'step_support_bottom_center_max_gap_sample':max(supports,key=lambda x:x['bottom_center_ground_gap_m']) if supports else None,'max_successive_step_top_difference_m':rise,'step_top_max_plan_difference_m':max((abs(x['actual_top']-x['declared_top']) for x in risers),default=0),'sample_count_center':len(floorpoints)})
print('STAIRS',[(r['id'],len(r['missing_samples']),len(r['terrain_intrusions']),len(r['headroom_hits'])) for r in stairresults],flush=True)
def camera_snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));cam=bpy.context.scene.camera;action=cam.animation_data.action;curves=[]
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:curves.extend(bag.fcurves)
 ch={(f.data_path,f.array_index):f for f in curves};ps=[[ch['location',j].evaluate(i) for j in range(3)] for i in range(1,1393)];qs=[[ch['rotation_quaternion',j].evaluate(i) for j in range(4)] for i in range(1,1393)]
 return {'positions':ps,'quats':qs,'lens':cam.data.lens,'clip_start':cam.data.clip_start,'clip_end':cam.data.clip_end,'parent':cam.parent.name if cam.parent else None}
oc=camera_snapshot(files[2]);nc=camera_snapshot(files[3]);camchanges={k:float(np.max(np.abs(np.array(oc[k])-np.array(nc[k])))) for k in ['positions','quats']};camchanges.update({k:[oc[k],nc[k]] for k in ['lens','clip_start','clip_end','parent'] if oc[k]!=nc[k]})
report={'hashes':hashes,'stable':all(sha(Path(p))==h for p,h in hashes.items()),'allowed_removed_count':len(allowed),'original_unallowed_object_changes':changes,'original_material_changes':matdiff,'ground_changed_vertex_count':len(D['terrain_changed_vertices']),'tree_building_surface_intersections':treehits,'new_house_old_building_surface_intersections':househits,'full_flight_27_swept_hits':flighthits,'old_walk_core_new_object_hits':oldpathhits,'old_road_ground_change_samples':roadterrain,'rock_building_surface_intersections':rockhits,'rock_boundary_support':rockroots,'step_landing_bottom_corners':stepbottom,'stilt_bottom_corners':posts,'stairs':stairresults,'poses_byte_identical':files[4].read_bytes()==files[5].read_bytes(),'camera_actual_keyframe_changes':camchanges,'saved_camera_vs_json_max_position_error_m':float(np.max(np.abs(np.array(nc['positions'])-positions))),'limits':['Read only CPU, no render/save/Git.','Original object summary includes mesh coordinates/topology/material indices/bindings/matrix, and material node input/link summaries. Ground and allowed deletions excluded.','Surface intersection is not complete solid containment test.','Full flight is 27 finite offset sweeps, including actual terrain; not exact swept-solid proof.','Old road footprint terrain protection samples route stations/edges; stair width +/-0.8m and <=0.2m along segment samples. Not infinite-resolution navigation proof.','No continuous playback or cloud visual acceptance.']}
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('AUDIT_DONE',flush=True)
