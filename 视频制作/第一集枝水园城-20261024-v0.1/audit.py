"""v14 independent saved scene CPU review; no scene mutation/render/Git."""
import bpy,sys,json,hashlib,array,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集枝水园城-20261024-v0.1';SRC=R/'视频制作/第一集云山园巷-20261024-v0.1'
sys.path.insert(0,str(R/'第一季/制作/空间规划/第一集山水总图白模-v0.1'));import layout as L
helper=(R/'视频制作/第一集云城校准-20261024-v0.1/audit.py').read_text('utf8');exec(helper[helper.index('def sha('):helper.index('D=json.loads')].replace('hashes={str(p):sha(p) for p in files}',''))
files=[SRC/'cloud-garden-route-58s-v14.blend',O/'branch-garden-route-58s-v15.blend',O/'route-poses.json',O/'design-data.json',R/'第一季/制作/空间规划/第一集枝水园城-v0.1/build.py'];hashes={str(p):sha(p) for p in files};D=json.loads(files[3].read_text('utf8'));GROUND='Continuous stable cloud terrain / river bed and inhabited slopes'
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

# Actual water strips: cross-channel and longitudinal interior terrain coverage.
waters=[]
for branch in D['branches']:
 g=ng[branch['id']+' connected water'];strip=g['v'].reshape(-1,2,3);covered=[];maxcover=-1e9;minbed=1e9;count=0
 for aa,bb in zip(strip,strip[1:]):
  for f in [.05,.25,.5,.75,.95]:
   cross=aa*(1-f)+bb*f
   for t in [.02,.25,.5,.75,.98]:
    v=cross[0]*(1-t)+cross[1]*t;gz=height(ground['bvh'],v);count+=1
    if gz is None:continue
    diff=float(gz-v[2]);maxcover=max(maxcover,diff);minbed=min(minbed,-diff)
    if diff>.04 and len(covered)<8:covered.append({'point':v.tolist(),'ground_above_water_m':diff})
 waters.append({'id':branch['id'],'samples':count,'maximum_ground_above_water_m':maxcover,'minimum_depth_m':minbed,'covered_examples':covered})
# Compare genuine previously grounded support, not high roofs/crowns/rails.
lost=[x for x in supportchanges if any(v['old_bottom_gap_m']<=.10 for v in x['examples'])]
# Crossings: deck-side actual gap from soffit TOP to intended original road.
crosschecks=[]
for cross in D['crossings']:
 g=ng[cross['id']+' supporting soffit'];road=ng[cross['road']];v=g['v'];top=v[4:8];gap=[]
 for p0 in [top.mean(0),*top]:
  rh=height(road['bvh'],p0)
  if rh is not None:gap.append(float(rh-p0[2]))
 crosschecks.append({'id':cross['id'],'road':cross['road'],'soffit_top_to_road_gaps_m':gap,'specified_under_clearance_m':cross['clearance_under_soffit_m']})
# Newly constructed abutment ALL bottom corners after conforming.
abut=[]
for name,g in ng.items():
 if name in D['new_objects'] and 'bank abutment' in name:
  gaps=[float(v[2]-height(ground['bvh'],v)) for v in g['v'][:4]]
  if max(gaps)>.04:abut.append({'name':name,'gaps':gaps})
r['water_surface_terrain']=waters;r['previously_grounded_support_changes']=lost;r['crossing_soffit_interfaces']=crosschecks;r['abutment_bottom_issues']=abut
r['camera_source_position_max_abs']=float(np.max(abs(p-op)));r['camera_source_quaternion_max_abs']=float(np.max(abs(q-oq)))
r['stable']=all(sha(Path(x))==h for x,h in hashes.items());(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
print('V15_EXTRA',[(x['id'],round(x['maximum_ground_above_water_m'],3)) for x in waters], 'lost',len(lost),'abutment',len(abut),flush=True)

# Channel continuity beneath local water: structural banks/abutments must not form plugs.
channel=[];joining=[];winding=[]
main=ng['Main water spine / upstream to downstream collection']['bvh']
for branch in D['branches']:
 g=ng[branch['id']+' connected water'];strip=g['v'].reshape(-1,2,3);count=0;hh=[]
 for alpha in [.1,.3,.5,.7,.9]:
  line=strip[:,0]*(1-alpha)+strip[:,1]*alpha
  for i,(a,bb) in enumerate(zip(line,line[1:])):
   for depth in [.1,.5]:
    aa=Vector(a)-Vector((0,0,depth));d=Vector(bb-a);hit=newb.ray_cast(aa,d.normalized(),d.length);count+=1
    # The water surface itself is not a solid obstruction.
    if hit[0] is not None and 'connected water' not in newnames[hit[2]] and len(hh)<10:hh.append({'segment':i,'object':newnames[hit[2]],'point':list(hit[0]),'depth':depth})
 channel.append({'branch':branch['id'],'ray_count':count,'hits':hh})
 for i in [0,len(strip)-1]:
  p0=strip[i].mean(0);z=height(main,p0);joining.append({'branch':branch['id'],'end':i,'overlaps_main_surface':z is not None,'branch_minus_main_z':float(p0[2]-z) if z is not None else None})
 areas=[]
 for a in g['f']:
  vv=g['v'][list(a)];areas.extend(float(np.cross(vv[j,:2]-vv[0,:2],vv[j+1,:2]-vv[0,:2])) for j in [1,2])
 winding.append({'branch':branch['id'],'positive':sum(x>1e-6 for x in areas),'negative':sum(x< -1e-6 for x in areas),'degenerate':sum(abs(x)<=1e-6 for x in areas)})
for x in lost:
 for e in x['examples']:
  v=e['point'];h=height(newb,v,v[2]+.01,10);e['new_structure_support_below_m']=float(v[2]-h) if h is not None else None
r['channel_subsurface_checks']=channel;r['main_water_joins']=joining;r['branch_projected_triangle_winding']=winding;r['previously_grounded_support_changes']=lost
r['stable']=all(sha(Path(x))==h for x,h in hashes.items());(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
print('CHANNEL',[(x['branch'],len(x['hits'])) for x in channel],flush=True)

# Second-pass closure: a foundation top may intentionally overlap the old bottom.
foundation_checks=[]
for spec in D.get('foundations',[]):
 g=ng[spec['name']];supported=ng[spec['supports']];topz=spec['top'];nt=len(g['v'])//2;bottom=g['v'][nt:];gap=[];bearing=[]
 for v in bottom:
  z=height(ground['bvh'],v);gap.append(float(v[2]-z))
 # Actual target low-face sample points, nudged 1mm inward to avoid ray-edge precision.
 center=supported['v'][:,:2].mean(0);low=supported['lo'][2]
 for v in supported['v'][supported['v'][:,2]<low+.04]:
  xy=v[:2]+(center-v[:2])*1e-4;h=height(g['bvh'],xy,float(low)+.12,20)
  bearing.append(None if h is None else float(h-low))
 mids=[]
 for face in g['f']:
  if all(j>=nt for j in face):
   a=g['v'][list(face)]
   for v in [a.mean(0),*((a+np.roll(a,1,axis=0))/2)]:
    z=height(ground['bvh'],v)
    if z is not None and v[2]-z>.06:mids.append({'point':v.tolist(),'bottom_above_ground_m':float(v[2]-z)})
 foundation_checks.append({'name':spec['name'],'supports':spec['supports'],'top_minus_old_bottom_samples':bearing,'bottom_vertex_gap_max':max(gap),'bottom_interior_gap_examples':mids[:10]})
bridge_profiles=[]
for spec in D['crossings']:
 g=ng[spec['id']+' supporting soffit'];road=ng[spec['road']];vs=g['v'][4:8];examples=[];delta=[]
 for f in np.linspace(.005,.995,25):
  for u in np.linspace(.005,.995,13):
   p0=(vs[0]*(1-f)+vs[1]*f)*(1-u)+(vs[3]*(1-f)+vs[2]*f)*u
   rh=height(road['bvh'],p0);sh=height(g['bvh'],p0)
   if rh is None or sh is None:continue
   dz=sh-rh;delta.append(dz)
   if abs(dz)>.15 and len(examples)<4:examples.append({'point':p0.tolist(),'soffit_top_minus_road_m':dz})
 bridge_profiles.append({'id':spec['id'],'samples':len(delta),'min_top_minus_road_m':min(delta) if delta else None,'max_top_minus_road_m':max(delta) if delta else None,'large_gap_or_lip':examples})
r['foundation_closure']=foundation_checks;r['dense_bridge_surface_profiles']=bridge_profiles
r['stable']=all(sha(Path(x))==h for x,h in hashes.items());(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
print('FOUNDATION',[(x['supports'],len(x['bottom_interior_gap_examples'])) for x in foundation_checks],'BRIDGE',[(x['id'],len(x['large_gap_or_lip'])) for x in bridge_profiles if x['large_gap_or_lip']],flush=True)

# Foundations may overlap by design; test union before flagging a local underside gap.
uniongaps=[];fg=[ng[x['name']] for x in D.get('foundations',[])]
for item in foundation_checks:
 for ex in item['bottom_interior_gap_examples']:
  pt=ex['point'];gz=height(ground['bvh'],pt);ints=[]
  for gg in fg:
   if np.any(np.array(pt[:2])<gg['lo'][:2]-.001) or np.any(np.array(pt[:2])>gg['hi'][:2]+.001):continue
   top=height(gg['bvh'],pt);hit=gg['bvh'].ray_cast(Vector((pt[0],pt[1],-100)),Vector((0,0,1)),700)
   if top is not None and hit[0] is not None:ints.append([float(hit[0].z),float(top),gg['name']])
  connected=sorted(ints,key=lambda x:x[0]);reach=gz+.06
  for a,b,n in connected:
   if a<=reach:reach=max(reach,b)
  if reach<pt[2]-.04:uniongaps.append({'foundation':item['name'],'point':pt,'ground':gz,'solid_intervals':ints,'local_lowest_foundation_bottom_to_ground_m':min(v[0] for v in ints)-gz if ints else None,'severity':'minor underside terrain gap; other footprint corners embedded, not unsupported whole foundation'})
r['foundation_union_unbridged_gaps']=uniongaps
for item in r['foundation_closure']:
 vals=item.pop('top_minus_old_bottom_samples');valid=[x for x in vals if x is not None];item['bearing_samples_summary']={'count':len(vals),'missing':len(vals)-len(valid),'min_top_minus_old_bottom':min(valid) if valid else None,'max_top_minus_old_bottom':max(valid) if valid else None}
r['stable']=all(sha(Path(x))==h for x,h in hashes.items());(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
print('UNION_GAPS',uniongaps,flush=True)

points=[];g=ng['Water-side continuous foundation Water-bay-+1-00 court floor']
for xy in [(-18.024911880493164,-52.847900390625),(-19.336149215698242,-51.278648376464844)]:
 h=g['bvh'].ray_cast(Vector((*xy,-100)),Vector((0,0,1)),700)[0];gz=height(ground['bvh'],xy)
 points.append({'xy':list(xy),'ground_z':gz,'foundation_bottom_z':h.z if h else None,'bottom_minus_ground':float(h.z-gz) if h else None})
r['final_targeted_underside_points']=points;r['remaining_required_geometry_fixes']=[];r['stable']=all(sha(Path(x))==h for x,h in hashes.items())
(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8');print('FINAL_POINTS',points,flush=True)
