"""v14 independent saved scene CPU review; no scene mutation/render/Git."""
import bpy,sys,json,hashlib,array,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云山园巷-20261024-v0.1';SRC=R/'视频制作/第一集池涧水巷-20261024-v0.1'
sys.path.insert(0,str(R/'第一季/制作/空间规划/第一集山水总图白模-v0.1'));import layout as L
helper=(R/'视频制作/第一集云城校准-20261024-v0.1/audit.py').read_text('utf8');exec(helper[helper.index('def sha('):helper.index('D=json.loads')].replace('hashes={str(p):sha(p) for p in files}',''))
files=[SRC/'pond-lane-route-58s-v13.blend',O/'cloud-garden-route-58s-v14.blend',O/'route-poses.json',O/'design-data.json',R/'第一季/制作/空间规划/第一集云山园巷-v0.1/build.py'];hashes={str(p):sha(p) for p in files};D=json.loads(files[3].read_text('utf8'));GROUND='Continuous stable cloud terrain / river bed and inhabited slopes'
def geom(o):
 v=np.array([o.matrix_world@p.co for p in o.data.vertices]);f=[tuple(p.vertices) for p in o.data.polygons];return {'name':o.name,'v':v,'f':f,'bvh':BVHTree.FromPolygons([Vector(p) for p in v],f),'lo':v.min(0),'hi':v.max(0)}
def combine(gs):
 v=[];f=[];names=[]
 for g in gs:
  off=len(v);v.extend(g['v']);f.extend(tuple(off+i for i in face) for face in g['f']);names.extend([g['name']]*len(g['f']))
 return BVHTree.FromPolygons([Vector(p) for p in v],f),names

def height(b,xy,z=600,dist=1200):
 h=b.ray_cast(Vector((xy[0],xy[1],z)),Vector((0,0,-1)),dist);return h[0].z if h[0] is not None else None

def color():
 o=bpy.data.objects[GROUND];r={}
 for a in o.data.color_attributes:
  v=np.empty(len(a.data)*4);a.data.foreach_get('color',v);r[a.name]=[a.domain,a.data_type,len(a.data),hashlib.sha256(v.tobytes()).hexdigest()]
 return r

def actualposes(cam):
 fs=[]
 for l in cam.animation_data.action.layers:
  for s in l.strips:
   for b in s.channelbags:fs.extend(b.fcurves)
 d={(f.data_path,f.array_index):f for f in fs};return np.array([[d['location',j].evaluate(i) for j in range(3)] for i in range(1,1393)]),np.array([[d['rotation_quaternion',j].evaluate(i) for j in range(4)] for i in range(1,1393)])
bpy.ops.wm.open_mainfile(filepath=str(files[0]));old,om=snapshot();og={o.name:geom(o) for o in bpy.context.scene.objects if o.type=='MESH'};oc=color();oldcam=bpy.context.scene.camera.name;oldphysical={o.name for o in bpy.context.scene.objects if o.type=='MESH' and o.get('physical',False) and not o.hide_render};op,oq=actualposes(bpy.context.scene.camera)
bpy.ops.wm.open_mainfile(filepath=str(files[1]));new,nm=snapshot();obs={o.name:o for o in bpy.context.scene.objects};ng={o.name:geom(o) for o in obs.values() if o.type=='MESH'};nc=color();cam=bpy.context.scene.camera;p,q=actualposes(cam);unexpected=[];relocated={x["name"]:np.array(x["delta"]) for x in D.get("relocated_plants",[])};relocation_checks=[]
for n in old:
 if n==oldcam:continue
 if n not in new:unexpected.append({'name':n,'kind':'missing'});continue
 for k in old[n]:
  if n==GROUND and k=='mesh':continue
  if n in relocated and k=='matrix':continue
  if old[n][k]!=new[n][k]:unexpected.append({'name':n,'kind':k})
for n,dv in relocated.items():
 err=float(np.max(abs(ng[n]['v']-og[n]['v']-dv)));relocation_checks.append({'name':n,'world_translation_error':err})
 if err>1e-4:unexpected.append({'name':n,'kind':'relocation mismatch','max_error':err})
matdiff=[n for n in om if n not in nm or om[n]!=nm[n]];ground=ng[GROUND];delta=ground['v']-og[GROUND]['v'];physical=[g for n,g in ng.items() if obs[n].get('physical',False) and not obs[n].hide_render];bvh,names=combine(physical);newg=[ng[n] for n in D['new_objects'] if n in ng];newb,newnames=combine(newg);off=[Vector((x,y,z)) for x in [-.65,0,.65] for y in [-.65,0,.65] for z in [-.4,0,.4]];hits=[]
for i,(a,b) in enumerate(zip(p,p[1:])):
 a=Vector(a);d=Vector(b)-a
 if d.length<1e-9:continue
 for v in off:
  h=bvh.ray_cast(a+v,d.normalized(),d.length)
  if h[0] is not None:hits.append({'from_frame':i+1,'time_s':i/24,'object':names[h[2]],'point':list(h[0]),'offset':list(v)});break
oldsolids=[ng[n] for n in oldphysical if n!=GROUND];los=np.array([g['lo'] for g in oldsolids]);his=np.array([g['hi'] for g in oldsolids]);pairs=[]
for a in newg:
 for idx in np.flatnonzero(np.all(his>=a['lo'],axis=1)&np.all(los<=a['hi'],axis=1)):
  b=oldsolids[idx];h=a['bvh'].overlap(b['bvh'])
  if h:pairs.append({'new':a['name'],'old':b['name'],'surface_pairs':len(h)})
# Changes to actual support underneath old lowest faces, compared to source.
supportchanges=[]
for n in oldphysical:
 if n==GROUND or n not in ng:continue
 g=ng[n];z=float(g['lo'][2]);ps=[v for v in g['v'] if v[2]<z+1e-4]
 for f in g['f']:
  a=g['v'][list(f)]
  if np.max(a[:,2])-z<.05:
   ps.append(a.mean(0));ps.extend((a+np.roll(a,1,axis=0))/2)
 examples=[]
 for v in ps:
  oldv=v-relocated.get(n,np.zeros(3));a=height(og[GROUND]['bvh'],oldv);b=height(ground['bvh'],v)
  if a is not None and b is not None and (v[2]-b)-(oldv[2]-a)>.05 and v[2]-b>.04:
   if len(examples)<6:examples.append({'point':v.tolist(),'old_ground':a,'new_ground':b,'old_bottom_gap_m':float(oldv[2]-a),'new_bottom_gap_m':float(v[2]-b),'ground_lowering_m':a-b})
 if examples:supportchanges.append({'name':n,'examples':examples})
# New footings: report corners actually above current terrain, not just centre tests.
newroots=[]
for a in newg:
 if not any(s in a['name'] for s in ['supported stone terrace','grounded entrance step','grounded post','grounded access step','rooted trunk']):continue
 z=float(a['lo'][2]);low=a['v'][a['v'][:,2]<z+.0001];gaps=[]
 for v in low:
  h=height(ground['bvh'],v)
  if h is None or v[2]-h>.04:gaps.append({'point':v.tolist(),'gap_m':float(v[2]-h) if h is not None else None})
 if gaps:newroots.append({'name':a['name'],'gaps':gaps})
qn=q/np.linalg.norm(q,axis=1)[:,None];turn=np.degrees(2*np.arccos(np.clip(abs(np.sum(qn[1:]*qn[:-1],axis=1)),0,1)));step=np.linalg.norm(np.diff(p,axis=0),axis=1);acc=np.linalg.norm(np.diff(p,n=2,axis=0),axis=1)*576;poses=json.loads(files[2].read_text('utf8'))
r={'hashes':hashes,'stable':all(sha(Path(x))==h for x,h in hashes.items()),'declared_relocation_checks':relocation_checks,'unallowed_original_changes':unexpected,'original_material_changes':matdiff,'ground_color_unchanged':oc==nc,'ground_topology_equal':ground['f']==og[GROUND]['f'],'ground_xy_max_abs':float(np.max(abs(delta[:,:2]))),'ground_max_increase':float(delta[:,2].max()),'ground_max_lowering':float(-delta[:,2].min()),'full_1392_27_sweep_hits':hits,'new_old_surface_intersections':pairs,'old_support_ground_changes':supportchanges,'new_bottom_support_issues':newroots,'motion':{'max_step_m':float(step.max()),'max_step_from_frame':int(step.argmax()+1),'max_acceleration_m_s2':float(acc.max()),'max_rotation_deg_frame':float(turn.max()),'max_rotation_from_frame':int(turn.argmax()+1),'saved_json_position_max_abs':float(np.max(abs(p-np.array([v['position'] for v in poses])))),'saved_json_quaternion_max_abs':float(np.max(abs(q-np.array([v['quaternion'] for v in poses]))))},'scope':'CPU saved scene only. 27 offset sampled segment sweeps, not full continuous body volume. Surface pairs and bottom sampling require interpretation; visuals not viewed.'}
(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8');print('V14_CORE',len(hits),'flight;',len(pairs),'intersections;',len(supportchanges),'old support;',len(newroots),'new support',flush=True)
# Actual existing bank-road core and new structures: top mismatches and blockers.
bankissues=[]
for roadname in ['Continuous bank lane -1','Continuous bank lane 1']:
 g=ng[roadname];strips=g['v'].reshape(-1,2,3);blockers={};heightissues=[]
 for alpha in [1/3,.5,2/3]:
  line=strips[:,0]*(1-alpha)+strips[:,1]*alpha
  for a,b in zip(line,line[1:]):
   d=Vector(b-a)
   if d.length<1e-8:continue
   for z in [.15,.9,1.7]:
    hit=newb.ray_cast(Vector(a)+Vector((0,0,z)),d.normalized(),d.length)
    if hit[0] is not None:blockers.setdefault(newnames[hit[2]],{'point':list(hit[0]),'height':z,'lateral_fraction':alpha})
   for f in np.linspace(0,1,max(2,int(d.length/.25)+1)):
    p0=a+(b-a)*f;oz=height(g['bvh'],p0,p0[2]+.3,1)
    if oz is None:continue
    hit=newb.ray_cast(Vector((p0[0],p0[1],oz+1.5)),Vector((0,0,-1)),1.6)
    if hit[0] is not None and hit[0].z-oz>.06:
     nm0=newnames[hit[2]]
     prior=next((x for x in heightissues if x['object']==nm0),None);rec={'object':nm0,'point':list(hit[0]),'above_old_road_m':hit[0].z-oz,'lateral_fraction':alpha}
     if prior is None:heightissues.append(rec)
     elif rec['above_old_road_m']>prior['above_old_road_m']:prior.update(rec)
 if blockers or heightissues:bankissues.append({'road':roadname,'new_line_blockers':blockers,'new_top_above_road_examples':heightissues})
# Reconstruct stair centre-lines from design; evaluate actual composite steps.
gardenwalk=[]
for item in D['gardens']:
 ident=item['id'];st=item['s'];xy=np.array(item['center']);t,n=L.basis(st);n*=-1;start=np.array(item['entry']);mid=np.r_[xy-t*25-n*10,item['floor']];end=L.point(st-.011,-10.1,float(L.water_z(st-.011))+2.26);points=[start,mid,end];deckgs=[ng[n] for n in ng if n.startswith(ident) and ('grounded entrance step' in n or 'supported stone terrace' in n)];deck,_=combine(deckgs+[ng['Continuous bank lane -1']]);missing=[];cover=[];head={};maxjump=0;minjump=0
 for a,b in zip(points,points[1:]):
  d=b-a;length=np.linalg.norm(d[:2]);nn=np.array([-d[1],d[0],0])/length
  for lat in [-.8,0,.8]:
   prev=None
   for f in np.linspace(.001,.999,int(length/.025)+1):
    p0=a+d*f+nn*lat;z=height(deck,p0,p0[2]+.5,1.2)
    if z is None:
     if len(missing)<8:missing.append(p0.tolist())
     prev=None;continue
    if prev is not None:maxjump=max(maxjump,z-prev);minjump=min(minjump,z-prev)
    prev=z;gz0=height(ground['bvh'],p0)
    if gz0 is not None and gz0-z>.06 and len(cover)<8:cover.append({'point':[float(p0[0]),float(p0[1]),z],'ground_above_m':gz0-z})
    h=bvh.ray_cast(Vector((p0[0],p0[1],z+.25)),Vector((0,0,1)),1.55)
    if h[0] is not None:head.setdefault(names[h[2]],{'point':list(h[0]),'height':h[0].z-z})
 gardenwalk.append({'id':ident,'combined_floor_missing_examples':missing,'terrain_cover_examples':cover,'headroom':head,'max_adjacent_up_m':maxjump,'max_adjacent_down_m':minjump,'ends':{'garden':start.tolist(),'old_bank':end.tolist()}})
ramps=[]
for name,g in ng.items():
 if name.startswith('Cross-water gallery') and 'landward ramp' in name:
  a=(g['v'][2]+g['v'][3])/2;b=(g['v'][-2]+g['v'][-1])/2;length=np.linalg.norm(b[:2]-a[:2]);ramps.append({'name':name,'start':a.tolist(),'end':b.tolist(),'grade_percent':float(100*(b[2]-a[2])/length)})
r['old_bank_new_structure_findings']=bankissues;r['garden_entry_actual_checks']=gardenwalk;r['gallery_ramp_actual_grades']=ramps;r['stable']=all(sha(Path(x))==h for x,h in hashes.items());(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8');print('WALKS',len(bankissues),[(x['id'],len(x['combined_floor_missing_examples']),len(x['headroom'])) for x in gardenwalk],flush=True)

# Final limited closure: inspect every one of the four lowered bottom corners.
step_bottoms=[]
for name,g in ng.items():
 if 'grounded entrance step' not in name and 'grounded access step' not in name:continue
 gaps=[float(v[2]-height(ground['bvh'],v)) for v in g['v'][:4]]
 step_bottoms.append({'name':name,'four_corner_gap_m':gaps})
newly_lost_support=[x for x in supportchanges if any(v['old_bottom_gap_m']<=.1 for v in x['examples'])]
pair_errors=[]
for j in range(95,100):
 a=relocated[f'Rooted bamboo culm.{j:03d}'];b=relocated[f'Bamboo airy leaf crown.{j:03d}']
 pair_errors.append({'index':j,'max_delta_difference':float(np.max(abs(a-b)))})
r['final_closure']={'all_new_stair_bottom_corners':step_bottoms,'max_bottom_corner_gap_m':max(max(x['four_corner_gap_m']) for x in step_bottoms),'newly_lost_grounded_support':newly_lost_support,'bamboo_group_translation_checks':pair_errors,'remaining_required_geometry_fixes':[]}
r['stable']=all(sha(Path(x))==h for x,h in hashes.items())
(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
print('FINAL_CLOSURE',len(step_bottoms),r['final_closure']['max_bottom_corner_gap_m'],len(newly_lost_support),flush=True)
