"""Final saved-camera collision and linked courtyard bounds audit."""
import bpy,sys,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集巨云重构-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'mother-cloud-flight-58s-v01.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
f=json.loads((O/'flight-checks.json').read_text('utf8'));cam=s.camera
fc=[fc for layer in cam.animation_data.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves if fc.data_path=='location'];fc.sort(key=lambda c:c.array_index)
points=np.array([[c.evaluate(i+1) for c in fc] for i in range(1392)]);carrier=np.array([r['position'] for r in f['records']]);records=np.array([r['camera'] for r in f['records']]);assert np.max(np.abs(records-points))<.001
positions=np.vstack((points,carrier));stepmax=max(np.linalg.norm(np.diff(points,axis=0),axis=1).max(),np.linalg.norm(np.diff(carrier,axis=0),axis=1).max());instance_clear=[];fits=[]
for o in s.objects:
 if not o.name.startswith('Cloud city linked courtyard'):continue
 vv=np.array([list(o.matrix_world@src.matrix_world@Vector(q)) for src in o.instance_collection.objects for q in src.bound_box]);lo=vv.min(0);hi=vv.max(0)
 distance=np.linalg.norm(np.maximum(np.maximum(lo-positions,positions-hi),0),axis=1).min()-stepmax/2-1.2
 instance_clear.append(float(distance));fits.append(bool(np.all(hi[:2]-lo[:2]<=32)))
assert all(fits) and min(instance_clear)>0
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];names=[];excluded={'E01_FLIGHT_PROXY','V05_TEMPORARY_QUADROTOR','V06_CLOUD_EDGE_REFINEMENT','V03_ROUTE_GUIDES'}
for o in s.objects:
 if o.type not in {'MESH','CURVE'} or not o.get('physical',True) or o.hide_render or any(c.name in excluded for c in o.users_collection):continue
 bounds=np.array([list(o.matrix_world@Vector(q)) for q in o.bound_box]);lo=bounds.min(0);hi=bounds.max(0)
 if np.linalg.norm(np.maximum(np.maximum(lo-points,points-hi),0),axis=1).min()>stepmax+1:continue
 ev=o.evaluated_get(dg);mesh=ev.to_mesh()
 if mesh is None:continue
 base=len(verts);verts.extend(ev.matrix_world@v.co for v in mesh.vertices);faces.extend(tuple(base+i for i in f.vertices) for f in mesh.polygons);names.extend([o.name]*len(mesh.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces);hits=[]
for i,(a,b) in enumerate(zip(points,points[1:])):
 a,b=Vector(a),Vector(b);d=b-a
 if d.length<1e-6:continue
 h=bvh.ray_cast(a,d.normalized(),d.length+.0001)
 if h[2] is not None:hits.append({'frame':i+1,'object':names[h[2]]})
result={'saved_camera_frames':1392,'saved_curve_vs_report_max_error_m':float(np.max(np.abs(records-points))),'final_camera_hits':hits,'linked_courtyard_count':len(fits),'all_courtyard_bounds_fit_32m_foundations':all(fits),'minimum_continuous_envelope_to_instance_AABB_lower_bound_m':min(instance_clear),'method':'Conservative AABB lower bound for distant instances, subtract half max frame travel and 1.2m envelope; final saved camera swept against nearby actual geometry including arrival patch.'}
(O/'final-audit.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('FINAL_AUDIT',json.dumps(result));assert not hits
