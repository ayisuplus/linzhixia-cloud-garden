import bpy,json,hashlib,sys
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集山谷植物-20261024-v0.1';src=O/'valley-masterplan-v10.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src))
obs={o.name:o for o in bpy.context.scene.objects};ground=obs['Continuous stable cloud terrain / river bed and inhabited slopes'];gb=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[tuple(p.vertices) for p in ground.data.polygons])
paths=json.loads((R/'视频制作/第一集山水总图白模-20261024-v0.1/layout-plan.json').read_text('utf8'))['paths'];rows=[]
for o in obs.values():
 if not o.name.startswith('Irregular moss and low ground cover'):continue
 vs=np.array([o.matrix_world@v.co for v in o.data.vertices]);ps=np.vstack([vs,np.array([vs[list(p.vertices)].mean(0) for p in o.data.polygons])]);gaps=[]
 for v in vs:
  h=gb.ray_cast(Vector(v+[0,0,20]),Vector((0,0,-1)),40)
  if h[0] is not None:gaps.append(float(v[2]-h[0].z))
 overlaps=[];closest=None
 for path in paths:
  pp=np.array(path['points'])[:,:2];a=pp[:-1];dd=np.diff(pp,axis=0);den=np.sum(dd*dd,axis=1);delta=ps[:,None,:2]-a[None,:,:];t=np.clip(np.sum(delta*dd[None,:,:],axis=2)/np.maximum(den[None,:],1e-12),0,1);dist=np.sqrt(np.sum((delta-t[:,:,None]*dd[None,:,:])**2,axis=2));mind=dist.min(axis=1);margin=float(mind.min()-path['width']/2)
  if closest is None or margin<closest['margin_m']:closest={'path':path['id'],'margin_m':margin}
  if margin<0:overlaps.append({'path':path['id'],'sample_count':int(np.sum(mind<path['width']/2)),'minimum_edge_margin_m':margin})
 rows.append({'name':o.name,'physical':bool(o.get('physical',True)),'sample_count':len(ps),'vertex_ground_gap_min_max_m':[min(gaps),max(gaps)],'closest_old_path_edge':closest,'path_footprint_sample_overlaps':overlaps})
rocks=[]
for o in obs.values():
 if not o.name.startswith('Valley limestone folded outcrop'):continue
 values=[]
 for vertex in list(o.data.vertices)[:11]:
  v=o.matrix_world@vertex.co;hit=gb.ray_cast(Vector((v.x,v.y,500)),Vector((0,0,-1)),1000);values.append(float(v.z-hit[0].z) if hit[0] is not None else None)
 rocks.append({'name':o.name,'bottom_ring_vertex_ground_offsets_m':values})
report={'rock_bottom_rings':rocks,'source_sha256':sha,'stable':hashlib.sha256(src.read_bytes()).hexdigest()==sha,'patch_count':len(rows),'patches':rows,'method':'Vertices and face centers against exact plan path segments plus half width; actual terrain rays at each vertex. Footprint sampling, not exact polygon intersection. Nonphysical decorative layers, no movement collision claim.'};(O/'moss-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('MOSS_AUDIT',len(rows),sum(bool(r['path_footprint_sample_overlaps']) for r in rows))
