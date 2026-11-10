"""v12 independent CPU review. No rendering or scene saving."""
import bpy,sys,json,hashlib,array,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云城校准-20261024-v0.1';OLD=R/'视频制作/第一集云山聚落-20261024-v0.1'
files=[OLD/'cloud-hamlet-masterplan-v11.blend',O/'cloud-city-route-58s-v12.blend',O/'route-poses.json',O/'world-repair-data.json']
files.append(R/'第一季/制作/空间规划/第一集云城校准-v0.1/build.py')
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
D=json.loads(files[3].read_text('utf8'));GROUND='Continuous stable cloud terrain / river bed and inhabited slopes'
bpy.ops.wm.open_mainfile(filepath=str(files[0]));old,oldmat=snapshot();og=bpy.data.objects[GROUND];oldgv=np.array([v.co[:] for v in og.data.vertices]);oldfaces=[tuple(f.vertices) for f in og.data.polygons]
oldrocks={o.name:{'v':np.array([v.co[:] for v in o.data.vertices]),'f':[tuple(f.vertices) for f in o.data.polygons]} for o in bpy.data.collections['15 Terrain rooted rock seams'].objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(files[1]));new,newmat=snapshot();obs={o.name:o for o in bpy.context.scene.objects};changed=[];bindings=[];removed=set(D['removed'])
for n,a in old.items():
 if n in removed:continue
 if n not in new:changed.append({'name':n,'change':'missing'});continue
 b=new[n]
 for k in ['type','mesh']:
  if (n==GROUND or n in oldrocks) and k=='mesh':continue
  if a[k]!=b[k]:changed.append({'name':n,'change':k})
 if a['matrix']!=b['matrix']:changed.append({'name':n,'change':'matrix','max_abs':max(abs(x-y) for x,y in zip(a['matrix'],b['matrix']))})
 if a['materials']!=b['materials']:
  valid=len(a['materials'])==len(b['materials']) and all(x[1]==y[1] and (x[0]==y[0] or y[0]==str(x[0])+' [campus ink region v12]') for x,y in zip(a['materials'],b['materials']))
  bindings.append({'name':n,'allowed_regional_copy':valid})
matdiff=[n for n,h in oldmat.items() if n in newmat and newmat[n]!=h]
matmissing=[n for n in oldmat if n not in newmat]
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
def height(bvh,xy,z=600,distance=1200):
 h=bvh.ray_cast(Vector((xy[0],xy[1],z)),Vector((0,0,-1)),distance);return h[0].z if h[0] is not None else None
def overlapping(a,b):return np.all(a['hi']>=b['lo']) and np.all(b['hi']>=a['lo'])
ground=get(obs[GROUND]);oldgb=BVHTree.FromPolygons([Vector(v) for v in oldgv],oldfaces);ngv=np.array([v.co[:] for v in obs[GROUND].data.vertices]);terrain={'old_vertex_count':len(oldgv),'new_vertex_count':len(ngv),'old_face_count':len(oldfaces),'new_face_count':len(ground['f'])}
if ngv.shape==oldgv.shape:
 delta=np.max(np.abs(ngv-oldgv),axis=1);ids=np.flatnonzero(delta>1e-5);sys.path.insert(0,str(R/'第一季/制作/空间规划/第一集山水总图白模-v0.1'));import layout as L
 ss,dd,_=L.nearest(oldgv[ids,:2]);q=np.abs(dd)-np.where(dd>=0,L.width(ss,1),L.width(ss,-1));allowed=((ss>.155)&(ss<.415)&(q>80))|((dd>0)&(ss>.23)&(ss<.34)&(q>58));terrain.update({'changed_vertices':len(ids),'xy_max_abs':float(np.max(abs(ngv[:,:2]-oldgv[:,:2]))),'outside_allowed_s_q_count':int(np.sum(~allowed)),'scope':'outer .155-.415 q>80 plus left .23-.34 q>58'})
rockcheck=[]
for n,r in oldrocks.items():
 ob=obs[n];vs=np.array([v.co[:] for v in ob.data.vertices]);dz_expected=[];dz_actual=[]
 for oldv,newv in zip(r['v'],vs):
  a=height(oldgb,oldv);b=height(ground['bvh'],newv)
  if a is not None and b is not None:dz_expected.append(b-a);dz_actual.append(newv[2]-oldv[2])
 rockcheck.append({'name':n,'topology_unchanged':r['f']==[tuple(f.vertices) for f in ob.data.polygons],'xy_max_abs':float(np.max(abs(vs[:,:2]-r['v'][:,:2]))),'height_follow_error_m':float(np.max(abs(np.array(dz_actual)-dz_expected))) if dz_actual else None})
allgs=[get(o) for o in obs.values() if o.type=='MESH' and o.get('physical',False) and not o.hide_render];bvh,names=combine(allgs);added=[get(o) for n,o in obs.items() if n not in old and o.type=='MESH' and o.get('physical',False) and not o.hide_render];newbvh,newnames=combine(added)
oldarch=[get(o) for cn in ['04 Contour courtyard clusters','09 Waterfront streets and inhabited bridgeheads','10 Connected bridges and quays','13 Hillside inhabited terraces'] for o in bpy.data.collections[cn].objects if o.type=='MESH' and not o.hide_render];newold=[]
for a in added:
 for b in oldarch:
  if overlapping(a,b):
   hits=a['bvh'].overlap(b['bvh'])
   if hits:newold.append({'new':a['name'],'old':b['name'],'surface_pairs':len(hits)})
poses=json.loads(files[2].read_text('utf8'));positions=np.array([p['position'] for p in poses]);offsets=[Vector((x,y,z)) for x in [-.55,0,.55] for y in [-.55,0,.55] for z in [-.35,0,.35]];flighthits=[]
for i,(a,b) in enumerate(zip(positions,positions[1:])):
 a=Vector(a);d=Vector(b)-a
 if d.length<1e-7:continue
 for off in offsets:
  h=bvh.ray_cast(a+off,d.normalized(),d.length)
  if h[0] is not None:flighthits.append({'frame':i+1,'time':i/24,'object':names[h[2]],'point':list(h[0])});break
print('FLIGHT',len(flighthits),'NEW_OLD_INTERSECTIONS',len(newold),flush=True)
P=json.loads((R/'视频制作/第一集山水总图白模-20261024-v0.1/layout-plan.json').read_text('utf8'));HD=json.loads((OLD/'landscape-data.json').read_text('utf8'))
def roadname(n):
 if n.startswith('bank-'):return 'Continuous bank lane '+n[5:]
 if n.endswith('-entry') and n!='middle-entry':return n[:-6]+' entry connection'
 if n.startswith('hill-'):return 'Upper slope street '+n[5:]
 if n.startswith('slope-link-'):
  side,cs=n[11:].rsplit('-',1);return 'Bank to slope connector '+side+' '+cs
 if n=='middle-entry':return 'Second-level through passage and gallery'
 return None
oldhits=[];oldgroundchanges=[]
for path in P['paths']+HD['stairs']:
 id=path['id']
 if path in HD['stairs']:
  deck,_=combine([get(o) for o in obs.values() if o.type=='MESH' and o.name.startswith(id+' ') and ('stone step' in o.name or 'landing' in o.name)])
 else:
  name=roadname(id)
  if name not in obs:continue
  deck=get(obs[name])['bvh']
 pts=np.array(path['points']);hits={};maxdelta=0.;gaps=0
 for a,b in zip(pts,pts[1:]):
  dd=b-a;n=np.array([-dd[1],dd[0],0]);n/=max(np.linalg.norm(n),1e-9)
  for lat in [-.9,0,.9]:
   aa=a+n*lat;bb=b+n*lat;za=height(deck,aa,aa[2]+.4,1);zb=height(deck,bb,bb[2]+.4,1)
   if za is None or zb is None:continue
   gn=height(ground['bvh'],aa);go=height(oldgb,aa)
   if gn is None:gaps+=1
   elif go is not None:maxdelta=max(maxdelta,abs(gn-go))
   start=Vector((aa[0],aa[1],za));end=Vector((bb[0],bb[1],zb));dd=end-start
   if dd.length<1e-7:continue
   for h in [.15,.9,1.8]:
    hit=newbvh.ray_cast(start+Vector((0,0,h)),dd.normalized(),dd.length)
    if hit[0] is not None:hits.setdefault(newnames[hit[2]],{'point':list(hit[0]),'height':h,'lateral':lat})
 if hits:oldhits.append({'path':id,'hits':hits})
 if maxdelta>.001 or gaps:oldgroundchanges.append({'path':id,'max_ground_delta_m':maxdelta,'ground_missing_samples':gaps})
links=[]
for path in D['walk_links']:
 name=path['name'];deck=get(obs[name])['bvh'];pts=np.array(path['points']);missing=[];terrainhits=[];headhits={};pathlinehits={};sample_count=0
 for a,b in zip(pts,pts[1:]):
  d=b-a;length=np.linalg.norm(d[:2]);n=np.array([-d[1],d[0],0])/max(length,1e-9)
  for lat in [-.8,0,.8]:
   for f in np.linspace(0,1,max(2,int(math.ceil(length/.25))+1)):
    p=a+d*f+n*lat;z=height(deck,p,p[2]+.3,.8);sample_count+=1
    if z is None:
     if len(missing)<12:missing.append(p.tolist())
     continue
    gg=height(ground['bvh'],p)
    if gg is not None and gg-z>.04 and len(terrainhits)<20:terrainhits.append({'point':[p[0],p[1],z],'ground_above_m':gg-z})
    h=bvh.ray_cast(Vector((p[0],p[1],z+.08)),Vector((0,0,1)),1.72)
    if h[0] is not None:headhits.setdefault(names[h[2]],{'point':list(h[0]),'height':h[0].z-z,'lateral':lat})
   for h in [.15,.9,1.8]:
    aa=Vector(a+n*lat+[0,0,h]);dd=Vector(b-a);hit=bvh.ray_cast(aa,dd.normalized(),dd.length)
    if hit[0] is not None:pathlinehits.setdefault(names[hit[2]],{'point':list(hit[0]),'height':h,'lateral':lat})
 links.append({'name':name,'samples':sample_count,'missing_floor':missing,'terrain_intrusions':terrainhits,'headroom_hits':headhits,'longitudinal_hits':pathlinehits})
print('OLD_WALK',len(oldhits),'LINKS_WITH_ISSUES',sum(bool(r['headroom_hits'] or r['terrain_intrusions'] or r['missing_floor']) for r in links),flush=True)
supports=[]
supportprefixes={r['name'] for r in D['support_roots']}
for o in obs.values():
 if o.type!='MESH' or not any(o.name==n or o.name.startswith(n+'.') for n in supportprefixes):continue
 g=get(o);z=float(g['lo'][2]);vs=[v for v in g['v'] if v.z<z+1e-4];off=[v.z-height(ground['bvh'],v) if height(ground['bvh'],v) is not None else None for v in vs];supports.append({'name':o.name,'bottom_offsets_m':off})
lift_connections=[]
for feature in D['features']:
 if feature['kind'].startswith('two stop'):
  id=feature['id'].split()[0];center=np.array(feature['center']);a=np.array(next(p for p in D['walk_links'] if p['name']==id+' lower access')['points'][-1]);b=np.r_[center,feature['lower']];hits={}
  for z in [.15,.9,1.8]:
   aa=Vector(a+[0,0,z]);dd=Vector(b-a);h=bvh.ray_cast(aa,dd.normalized(),dd.length)
   if h[0] is not None:hits[names[h[2]]]={'point':list(h[0]),'height':z}
  cabin=get(obs[id+' lift cabin at lower stop'])['bvh'];gap=[]
  for f in np.linspace(0,1,20):
   p=a+(b-a)*f;zz=height(cabin,p,feature['lower']+.4,1)
   if zz is None:gap.append(p.tolist())
  floorb,_=combine([get(obs[id+' lift cabin at lower stop']),get(obs[id+' lower access'])]);uniongaps=[]
  for t in np.linspace(0,1,191):
   p=a+(b-a)*t
   if height(floorb,p,feature['lower']+.4,1) is None:uniongaps.append(p.tolist())
  lift_connections.append({'id':id,'lower_entry_to_cabin_hits':hits,'cabin_only_missing_samples':gap,'combined_gallery_cabin_missing_samples':uniongaps,'combined_gap_span_m':float(np.linalg.norm(np.array(uniongaps[-1])-uniongaps[0])) if len(uniongaps)>1 else 0,'note':'Combined deck+cabin checked at 1 cm spacing; static upper cabin absence alone not a blocker.'})
cam=bpy.context.scene.camera;curves=[]
for layer in cam.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:curves.extend(bag.fcurves)
ch={(f.data_path,f.array_index):f for f in curves};ps=np.array([[ch['location',j].evaluate(i) for j in range(3)] for i in range(1,1393)]);qs=np.array([[ch['rotation_quaternion',j].evaluate(i) for j in range(4)] for i in range(1,1393)]);oldposes=json.loads((OLD/'route-poses.json').read_text('utf8'));op=np.array([p['position'] for p in oldposes]);oq=np.array([p['quaternion'] for p in oldposes]);changedpos=np.flatnonzero(np.max(abs(ps-op),axis=1)>1e-4)+1;changedrot=np.flatnonzero(np.max(abs(qs-oq),axis=1)>1e-5)+1;qn=qs/np.linalg.norm(qs,axis=1)[:,None];turn=np.degrees(2*np.arccos(np.clip(abs(np.sum(qn[:-1]*qn[1:],axis=1)),0,1)))
report={'hashes':hashes,'stable':all(sha(Path(p))==h for p,h in hashes.items()),'unallowed_original_changes':changed,'material_bindings':bindings,'original_material_changes':matdiff,'original_material_datablocks_absent':matmissing,'ground':terrain,'new_old_building_surface_intersections':newold,'full_flight_27_hits':flighthits,'old_walk_hits':oldhits,'old_walk_ground_changes':oldgroundchanges,'new_walk_links':links,'new_support_bottoms':supports,'lift_entries':lift_connections,'camera_pose_json_max_error_m':float(np.max(abs(ps-positions))),'actual_position_changed_frames':changedpos.tolist(),'actual_rotation_changed_frames':changedrot.tolist(),'camera_max_rotation_deg_frame':float(turn.max()),'camera_max_rotation_at_frame':int(turn.argmax()+1),'scope':['CPU read-only geometry; no GPU/render/save/Git.','Material original summaries, meshes, matrices checked; approved regional-copy material bindings and ground deformation excluded from ordinary unchanged rule.','Surface overlap candidates require intended join interpretation; no complete containment proof.','27 world-offset sweep not exact solid swept volume; old walking and new links sampled.','Lift cabin is static lower-stop proposal, upper absence alone not a missing-floor blocker; actual entry obstacles are reported.']}
report['authorized_rock_height_follow']=rockcheck
finalconnections=[]
for path_name,extra in [('Dorm door approach',[o for o in obs.values() if o.name.startswith('Dorm threshold stone step')]),('Ferry lower bank entry',[obs['Public lift lower cabin']])]:
 path=next(p for p in D['walk_links'] if p['name']==path_name);pts=np.array(path['points']);floorb,_=combine([get(obs[path_name])]+[get(o) for o in extra]);worst={'rise_m':0};missing=0
 for a,b in zip(pts,pts[1:]):
  d=b-a;length=float(np.linalg.norm(d[:2]));normal=np.array([-d[1],d[0],0])/length
  for lat in [-1,0,1]:
   prev=None
   for f in np.linspace(.001,.999,int(length/.01)+1):
    p=a+d*f+normal*lat;z=height(floorb,p,max(a[2],b[2])+1,4)
    if z is None:missing+=1;prev=None;continue
    if prev is not None and z-prev[2]>worst['rise_m']:worst={'rise_m':z-prev[2],'from':prev,'to':[float(p[0]),float(p[1]),z],'lateral':lat}
    prev=[float(p[0]),float(p[1]),z]
 finalconnections.append({'name':path_name,'combined_floor_missing':missing,'max_sampled_rise':worst,'sampling':'1 cm longitudinal and laterals -1,0,1; floor union includes actual steps/cabin, excludes endpoints'})
report['final_connection_floor_profiles']=finalconnections
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('V12_AUDIT_DONE',flush=True)
