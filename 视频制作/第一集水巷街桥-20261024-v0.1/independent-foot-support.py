import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集水巷街桥-20261024-v0.1';src=O/'waterlane-masterplan-v09.blend';digest=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));obs={o.name:o for o in bpy.context.scene.objects}
def bv(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
ground=bv(obs['Continuous stable cloud terrain / river bed and inhabited slopes']);quays=[(n,bv(o)) for n,o in obs.items() if n.endswith('continuous inhabited quay')];rows=[]
for n,o in obs.items():
 if 'stone column foot' not in n:continue
 verts=[o.matrix_world@v.co for v in o.data.vertices];center=sum(verts,Vector())/len(verts);bottom=min(v.z for v in verts);h=ground.ray_cast(Vector((center.x,center.y,400)),Vector((0,0,-1)),800);supports=[{'name':'terrain','z':h[0].z}] if h[0] is not None else []
 for qn,q in quays:
  hh=q.ray_cast(Vector((center.x,center.y,400)),Vector((0,0,-1)),800)
  if hh[0] is not None:supports.append({'name':qn,'z':hh[0].z})
 highest=max(supports,key=lambda x:x['z']) if supports else None
 if highest and bottom-highest['z']>.15:rows.append({'object':n,'xy':[center.x,center.y],'foot_bottom_z':bottom,'highest_support':highest,'gap_m':bottom-highest['z']})
report={'source_hash':digest,'stable':digest==hashlib.sha256(src.read_bytes()).hexdigest(),'unsupported_foot_candidates':rows,'scope':'Stone column feet center compared with actual terrain AND continuous quay top. Whole column support is separate; no GPU/render/save.'};(O/'independent-foot-support.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('FOOT_SUPPORT',len(rows),flush=True)
