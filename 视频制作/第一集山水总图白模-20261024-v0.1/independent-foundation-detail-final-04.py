import bpy,sys,json,hashlib
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集山水总图白模-20261024-v0.1';src=O/'landscape-masterplan-v08.blend';digest=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));obs={o.name:o for o in bpy.context.scene.objects};g=obs['Continuous stable cloud terrain / river bed and inhabited slopes'];ground=BVHTree.FromPolygons([g.matrix_world@v.co for v in g.data.vertices],[tuple(f.vertices) for f in g.data.polygons]);hits=[]
for name,o in obs.items():
 if o.type!='MESH' or not o.data.materials or o.data.materials[0].name!='Retained CITY05 palette / wall' or len(o.data.vertices)!=8:continue
 vs=np.array([o.matrix_world@v.co for v in o.data.vertices]);base=vs[:4];peak=None
 for u in np.linspace(.05,.95,7):
  for v in np.linspace(.05,.95,7):
   pt=base[0]+u*(base[1]-base[0])+v*(base[3]-base[0]);h=ground.ray_cast(Vector(pt+np.array([0,0,200])),Vector((0,0,-1)),400)
   if h[0] is not None and h[0].z-pt[2]>.2:
    delta=float(h[0].z-pt[2])
    if peak is None or delta>peak['intrusion_above_box_bottom_m']:peak={'object':name,'point':pt.tolist(),'terrain_z':h[0].z,'intrusion_above_box_bottom_m':delta,'box_top_z':float(vs[:,2].max())}
 if peak:hits.append(peak)
report={'source_hash':digest,'stable':digest==hashlib.sha256(src.read_bytes()).hexdigest(),'building_ground_intrusions':hits,'method':'7x7 points strictly inside actual wall-box XY footprints, 5%-95% extent; terrain ray versus box base/top. Includes split two-level hall wall parts; no roof solid assumption.'};(O/'independent-foundation-detail-final-04.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('FOUNDATION_DETAIL',len(hits),flush=True)
