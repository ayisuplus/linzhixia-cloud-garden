import bpy,sys,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D));import routing
O=R/'视频制作/第一集云城层次-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-neighbourhood-v19.blend'));S=bpy.context.scene
raw,arc,dist,positions=routing.timed_route();length=arc[-1]
data=bpy.data.cameras.new('v19 school to workshop FPV');cam=bpy.data.objects.new(data.name,data);S.collection.objects.link(cam);data.lens=22;data.clip_start=.1;data.clip_end=3500;cam.rotation_mode='QUATERNION';quats=[]
for i,(d,p) in enumerate(zip(dist,positions)):
 ahead=min(d+13,length);behind=max(d-6,0);aa=np.array([np.interp(ahead,arc,raw[:,j]) for j in range(3)]);bb=np.array([np.interp(behind,arc,raw[:,j]) for j in range(3)]);direction=aa-bb
 arrival=np.array([350.5,-80.5,50.2])-p;mix=routing.smooth((d-(length-40))/40);direction=direction/max(np.linalg.norm(direction),1e-8)*(1-mix)+arrival/max(np.linalg.norm(arrival),1e-8)*mix
 direction[2]-=.055*np.linalg.norm(direction[:2]);q=Vector(direction).to_track_quat('-Z','Y')
 if quats and q.dot(Quaternion(quats[-1]))<0:q.negate()
 cam.location=p;cam.rotation_quaternion=q;cam.keyframe_insert('location',frame=i+1);cam.keyframe_insert('rotation_quaternion',frame=i+1);quats.append(list(q))
S.camera=cam;S.frame_start=1;S.frame_end=1392;S.render.fps=24;S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'cloud-neighbourhood-flight-58s-v19.blend'))
vs=[];faces=[];owners=[]
for ob in S.objects:
 if ob.type!='MESH' or not ob.get('physical',False) or ob.hide_render or any(c.hide_render for c in ob.users_collection):continue
 owners.extend([ob.name]*len(ob.data.polygons));start=len(vs);vs.extend(ob.matrix_world@v.co for v in ob.data.vertices);faces.extend(tuple(start+j for j in f.vertices) for f in ob.data.polygons)
bvh=BVHTree.FromPolygons(vs,faces);hits=[];offsets=[Vector((x,y,z)) for x in [-.6,0,.6] for y in [-.6,0,.6] for z in [-.4,0,.4]]
for i in range(1391):
 a=Vector(positions[i]);b=Vector(positions[i+1]);delta=b-a
 if delta.length<1e-6:continue
 for shift in offsets:
  h=bvh.ray_cast(a+shift,delta.normalized(),delta.length)
  if h[0] is not None:hits.append({'frame':i+1,'time':i/24,'point':list(h[0]),'object':owners[h[2]]});break
v=np.diff(positions,axis=0)*24;acc=np.diff(v,axis=0)*24;turns=[math.degrees(Quaternion(a).rotation_difference(Quaternion(b)).angle) for a,b in zip(quats,quats[1:])]
poses=[{'frame':i+1,'time':i/24,'position':p.tolist(),'quaternion':q} for i,(p,q) in enumerate(zip(positions,quats))]
report={'duration_seconds':58,'frames':1392,'fps':24,'length_m':float(length),'max_speed_m_s':float(np.linalg.norm(v,axis=1).max()),'max_acceleration_m_s2':float(np.linalg.norm(acc,axis=1).max()),'max_rotation_deg_per_frame':max(turns),'swept_sample_collisions':hits,'envelope_m':[1.2,1.2,.8],'scope':'FPV geometric reference. 27 swept samples, not exact swept-solid or dynamics proof; no loading/unloading character action.'}
(O/'route-poses.json').write_text(json.dumps(poses),encoding='utf8');(O/'route-check.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('ROUTE_READY',json.dumps(report),flush=True)
