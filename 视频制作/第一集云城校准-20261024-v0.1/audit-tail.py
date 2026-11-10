"""Read-only v12 arrival revision audit. No render/save/GPU."""
import bpy,sys,json,hashlib,array,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云城校准-20261024-v0.1';B=O/'rejected-arrival'
helper=(O/'audit.py').read_text('utf8');exec(helper[helper.index('def sha('):helper.index('D=json.loads')].replace('hashes={str(p):sha(p) for p in files}',''))
files=[B/'cloud-city-route-58s-v12.blend',O/'cloud-city-route-58s-v12.blend',B/'route-poses.json',O/'route-poses.json',R/'第一季/制作/空间规划/第一集云城校准-v0.1/build.py',O/'world-repair-data.json'];hashes={str(p):sha(p) for p in files}
def actualposes(cam):
 curves=[]
 for layer in cam.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:curves.extend(bag.fcurves)
 ch={(f.data_path,f.array_index):f for f in curves}
 return np.array([[ch['location',j].evaluate(i) for j in range(3)] for i in range(1,1393)]),np.array([[ch['rotation_quaternion',j].evaluate(i) for j in range(4)] for i in range(1,1393)])
def extra():
 return {o.name:[o.hide_render,o.hide_viewport,o.get('physical',None)] for o in bpy.context.scene.objects}
bpy.ops.wm.open_mainfile(filepath=str(files[0]));before,bmat=snapshot();be=extra();oldcam=bpy.context.scene.camera.name;bp,bq=actualposes(bpy.context.scene.camera)
bpy.ops.wm.open_mainfile(filepath=str(files[1]));after,amat=snapshot();ae=extra();cam=bpy.context.scene.camera;ap,aq=actualposes(cam)
staticdiff=[]
for name in sorted(set(before)|set(after)):
 if name in [oldcam,cam.name]:continue
 if before.get(name)!=after.get(name) or be.get(name)!=ae.get(name):staticdiff.append(name)
matdiff=[n for n in set(bmat)|set(amat) if bmat.get(n)!=amat.get(n)]
vs=[];fs=[];names=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or not ob.get('physical',False) or ob.hide_render:continue
 off=len(vs);vs.extend(ob.matrix_world@v.co for v in ob.data.vertices)
 for f in ob.data.polygons:fs.append(tuple(off+int(i) for i in f.vertices));names.append(ob.name)
bvh=BVHTree.FromPolygons(vs,fs);hits=[]
for i in range(1300,1391):
 a=Vector(ap[i]);d=Vector(ap[i+1])-a
 if d.length<1e-8:continue
 for x in [-.55,0,.55]:
  for y in [-.55,0,.55]:
   for z in [-.35,0,.35]:
    h=bvh.ray_cast(a+Vector((x,y,z)),d.normalized(),d.length)
    if h[0] is not None:hits.append({'from_frame':i+1,'to_frame':i+2,'object':names[h[2]],'point':list(h[0]),'offset':[x,y,z]})
qn=aq/np.linalg.norm(aq,axis=1)[:,None];turn=np.degrees(2*np.arccos(np.clip(abs(np.sum(qn[:-1]*qn[1:],axis=1)),0,1)))
oldj=json.loads(files[2].read_text('utf8'));newj=json.loads(files[3].read_text('utf8'));jpos=np.array([p['position'] for p in newj]);jquat=np.array([p['quaternion'] for p in newj])
r={'hashes':hashes,'stable':all(sha(Path(p))==h for p,h in hashes.items()),'static_object_changes':staticdiff,'material_changes':matdiff,'pre1301_actual_position_max_abs':float(np.max(abs(ap[:1301]-bp[:1301]))),'pre1301_actual_quaternion_max_abs':float(np.max(abs(aq[:1301]-bq[:1301]))),'pre1301_json_identical':oldj[:1301]==newj[:1301],'changed_actual_position_frames':(np.flatnonzero(np.max(abs(ap-bp),axis=1)>0)+1).tolist(),'changed_actual_quaternion_frames':(np.flatnonzero(np.max(abs(aq-bq),axis=1)>0)+1).tolist(),'tail_27_swept_hits':hits,'tail_swept_segment_count':91,'actual_json_position_max_abs':float(np.max(abs(ap-jpos))),'actual_json_quaternion_max_abs':float(np.max(abs(aq-jquat))),'max_turn_deg_frame':float(turn.max()),'max_turn_from_frame':int(turn.argmax()+1),'tail_max_turn_deg_frame':float(turn[1300:].max()),'tail_max_turn_from_frame':int(turn[1300:].argmax()+1301),'boundary_turn_1300_to_1301':float(turn[1299]),'boundary_turn_1301_to_1302':float(turn[1300]),'boundary_turn_1302_to_1303':float(turn[1301]),'reusable_frames':'1-1301 inclusive','rerender_frames':'1302-1392 inclusive (91 frames)','scope':'Saved actual camera keyframes; static mesh/matrix/material bindings/visibility/physical flags; 27 world-offset rays only on revised 91 segments, no full-body continuous collision proof; no continuous video viewing.'}
(O/'audit-tail.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8');print(json.dumps({k:v for k,v in r.items() if k not in ['hashes','changed_actual_position_frames','changed_actual_quaternion_frames']},ensure_ascii=False),flush=True)
base=json.loads((B/'audit.json').read_text('utf8'))
base['dependency_reuse']={'from_scene_sha256':hashes[str(files[0])],'static_geometry_walk_support_material_checks':'Reused after exact static snapshot equality; not rerun walk checks.','full_flight':'Frames 1-1301 identical; revised segments 1301-1392 rescanned with same 27 offsets.','evidence':'audit-tail.json'}
base['hashes'].update({k:v for k,v in hashes.items() if 'rejected-arrival' not in k})
base['stable']=r['stable'];base['tail_revision']=r
base['full_flight_27_hits']=hits
base['camera_pose_json_max_error_m']=r['actual_json_position_max_abs'];base['camera_max_rotation_deg_frame']=r['max_turn_deg_frame'];base['camera_max_rotation_at_frame']=r['max_turn_from_frame']
v11=json.loads((R/'视频制作/第一集云山聚落-20261024-v0.1/route-poses.json').read_text('utf8'));op=np.array([p['position'] for p in v11]);oq=np.array([p['quaternion'] for p in v11])
base['actual_position_changed_frames']=(np.flatnonzero(np.max(abs(ap-op),axis=1)>1e-4)+1).tolist();base['actual_rotation_changed_frames']=(np.flatnonzero(np.max(abs(aq-oq),axis=1)>1e-5)+1).tolist()
(O/'audit.json').write_text(json.dumps(base,ensure_ascii=False,indent=2),'utf8')
