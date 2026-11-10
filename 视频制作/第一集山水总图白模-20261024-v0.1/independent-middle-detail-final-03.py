import bpy,json,sys,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集山水总图白模-20261024-v0.1';source=O/'landscape-masterplan-v08.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest();plan=json.loads((O/'layout-plan.json').read_text('utf8'));bpy.ops.wm.open_mainfile(filepath=str(source));lookup={o.name:o for o in bpy.context.scene.objects}
def bvh(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
road=bvh(lookup['Second-level through passage and gallery']);roofs=[(n,bvh(o)) for n,o in lookup.items() if n.startswith('Two-level-water-court / ') and n.endswith(' roof')]
pts=np.array(next(p for p in plan['paths'] if p['id']=='middle-entry')['points']);hits=[];miss=[]
for si,(a,b) in enumerate(zip(pts,pts[1:])):
 side=np.array([-(b-a)[1],(b-a)[0],0]);side/=max(np.linalg.norm(side),1e-9)
 for t in np.linspace(0,1,math.ceil(np.linalg.norm(b-a)/.2)+1):
  center=a+(b-a)*t
  for offset in [-.9,0,.9]:
   foot=center+side*offset;h=road.ray_cast(Vector(foot+np.array([0,0,50])),Vector((0,0,-1)),100)
   if h[0] is None:
    if 0<t<1:miss.append({'segment':si,'t':float(t),'point':foot.tolist(),'lateral':offset})
    continue
   for name,roof in roofs:
    hit=roof.ray_cast(h[0]+Vector((0,0,.03)),Vector((0,0,1)),1.77)
    if hit[0] is not None:hits.append({'segment':si,'roof':name,'floor':list(h[0]),'roof_point':list(hit[0]),'headroom_m':hit[3]+.03,'lateral':offset})
report={'source_hash':digest,'stable':digest==hashlib.sha256(source.read_bytes()).hexdigest(),'roof_headroom_surface_hits':hits,'walk_core_floor_misses':miss,'method':'Actual saved middle-entry mesh, 0.2m path sampling, lateral +/-0.9m and center. Vertical headroom rays 0.03..1.8m from projected actual deck; no roof solid-containment assumption.'}
(O/'independent-middle-detail-final-03.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('MIDDLE_DETAIL',len(hits),len(miss),flush=True)
