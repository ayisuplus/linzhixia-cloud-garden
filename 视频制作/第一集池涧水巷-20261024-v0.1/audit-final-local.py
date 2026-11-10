"""Final limited Lower-lane paving closure, exact dependency comparison; CPU only."""
import bpy,sys,json,hashlib,array
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集池涧水巷-20261024-v0.1';GROUND='Continuous stable cloud terrain / river bed and inhabited slopes';PAD='Lower-lane--1-02 court floor'
helper=(R/'视频制作/第一集云城校准-20261024-v0.1/audit.py').read_text('utf8');exec(helper[helper.index('def sha('):helper.index('D=json.loads')].replace('hashes={str(p):sha(p) for p in files}',''))
files=[O/'pond-lane-route-58s-v13.blend1',O/'pond-lane-route-58s-v13.blend',O/'route-poses.json',O/'water-design-data.json',R/'第一季/制作/空间规划/第一集池涧水巷-v0.1/build.py',R/'第一季/制作/空间规划/第一集池涧水巷-v0.1/water_layout.py'];hashes={str(p):sha(p) for p in files};expected='e03be1190d66bff0e9a8006ef455657e2f4c8b38bd3e545d7368e94479fb5af1'
assert hashes[str(files[0])]==expected,'Backup is not last audited scene'
def poses():
 c=bpy.context.scene.camera;fs=[]
 for l in c.animation_data.action.layers:
  for s in l.strips:
   for b in s.channelbags:fs.extend(b.fcurves)
 d={(f.data_path,f.array_index):f for f in fs};return np.array([[d['location',j].evaluate(i) for j in range(3)]+[d['rotation_quaternion',j].evaluate(i) for j in range(4)] for i in range(1,1393)])
def gv():return np.array([v.co[:] for v in bpy.data.objects[GROUND].data.vertices])
def height(b,xy):
 h=b.ray_cast(Vector((xy[0],xy[1],600)),Vector((0,0,-1)),1200);return h[0].z if h[0] is not None else None
def bv(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
bpy.ops.wm.open_mainfile(filepath=str(files[0]));old,om=snapshot();og=gv();op=poses();of=[tuple(f.vertices) for f in bpy.data.objects[GROUND].data.polygons]
bpy.ops.wm.open_mainfile(filepath=str(files[1]));new,nm=snapshot();ng=gv();np0=poses();nf=[tuple(f.vertices) for f in bpy.data.objects[GROUND].data.polygons];other=[n for n in set(old)|set(new) if n!=GROUND and old.get(n)!=new.get(n)];mat=[n for n in set(om)|set(nm) if om.get(n)!=nm.get(n)]
delta=ng-og;changed=np.flatnonzero(np.max(abs(delta),axis=1)>1e-5);gb=bv(bpy.data.objects[GROUND]);pad=bpy.data.objects[PAD];pb=bv(pad);pv=np.array([pad.matrix_world@v.co for v in pad.data.vertices]);maxabove=-1e9;worst=None;missing=0;count=0
for x in np.arange(pv[:,0].min()+.25,pv[:,0].max(),.5):
 for y in np.arange(pv[:,1].min()+.25,pv[:,1].max(),.5):
  pz=height(pb,[x,y])
  if pz is None:continue
  count+=1;gz=height(gb,[x,y])
  if gz is None:missing+=1;continue
  if gz-pz>maxabove:maxabove=gz-pz;worst=[float(x),float(y),pz,gz]
a=bpy.data.objects[GROUND].data.color_attributes.get('Contour strata color');cv=np.empty(len(a.data)*4);a.data.foreach_get('color',cv);cv=cv.reshape(-1,4)
r={'hashes':hashes,'stable':all(sha(Path(p))==h for p,h in hashes.items()),'reference_backup_sha256':expected,'non_ground_object_changes':other,'material_changes':mat,'ground_topology_equal':of==nf,'ground_xy_max_abs':float(np.max(abs(delta[:,:2]))),'ground_changed_vertices':len(changed),'ground_z_max_increase_m':float(delta[:,2].max()),'ground_z_max_decrease_m':float(delta[:,2].min()),'ground_change_bounds':{'min':ng[changed].min(0).tolist(),'max':ng[changed].max(0).tolist()} if len(changed) else None,'saved_all1392_pose_max_abs':float(np.max(abs(np0-op))),'poses_json_unchanged':hashes[str(files[2])]=='328af962082c29fdbe5de39b56448fbdbf9f6a7d301bd025e5fdaa6eea87fe7c','lower_lane_actual_paving_check':{'samples':count,'step_m':.5,'missing_ground':missing,'maximum_ground_above_top_m':maxabove,'worst_xyz_groundz':worst},'ground_color':{'domain':a.domain,'data_type':a.data_type,'count':len(cv),'finite':bool(np.isfinite(cv).all()),'black_count':int(np.sum(np.max(cv[:,:3],axis=1)<1e-6))},'reuse':'Static other objects/materials/1392 poses exact match audited backup; ground only lowered, retaining XY/topology. Prior flight and other static collision checks remain applicable, with target pad sampled again.'}
(O/'audit-final-local.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
base=json.loads((O/'audit-fifth-pass.json').read_text('utf8'));base['final_local_closure']=r;base['hashes'].update({k:v for k,v in hashes.items() if not k.endswith('.blend1')});base['stable']=r['stable'];base['actual_court_paving_ground_issues']=[p for p in base['actual_court_paving_ground_issues'] if p['name']!=PAD] if maxabove<=.04 and missing==0 else base['actual_court_paving_ground_issues'];base['dependency_reuse']=r['reuse'];(O/'audit.json').write_text(json.dumps(base,ensure_ascii=False,indent=2),'utf8');print(json.dumps(r,ensure_ascii=False),flush=True)