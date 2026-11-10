"""Targeted read-only saved-mesh checks, final-05. No render/save."""
import bpy,sys,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集山水总图白模-20261024-v0.1';src=O/'landscape-masterplan-v08.blend';pp=O/'layout-plan.json';fp=O/'local-geometry-fixes.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
hashes={str(p):sha(p) for p in [src,pp,fp]};P=json.loads(pp.read_text('utf8'));F=json.loads(fp.read_text('utf8'));bpy.ops.wm.open_mainfile(filepath=str(src));obs={o.name:o for o in bpy.context.scene.objects}
def bv(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
ground=bv(obs['Continuous stable cloud terrain / river bed and inhabited slopes'])
def ground_z(xy):
 h=ground.ray_cast(Vector((xy[0],xy[1],1000)),Vector((0,0,-1)),2000);return h[0].z if h[0] is not None else None
courts=[]
for fix in F['trimmed_corners']:
 c=next(x for x in P['courts'] if x['id']==fix['court']);ob=obs[c['id']+' court floor'];vv=[ob.matrix_world@v.co for v in ob.data.vertices];topz=max(v.z for v in vv);ff=[tuple(p.vertices) for p in ob.data.polygons if all(abs(vv[i].z-topz)<.0001 for i in p.vertices)];floor=BVHTree.FromPolygons(vv,ff);hx,hy=c['half_size'];corner=np.array([hx if c['id']=='Lower-lane--1-02' else -hx,hy]);count=0;bad=[];bad_uv=[];maxdelta=-1e9;worst=None;required=0
 for u in np.linspace(-hx,hx,math.ceil(2*hx/.25)+1):
  for v in np.linspace(-hy,hy,math.ceil(2*hy/.25)+1):
   xy=np.array(c['center'])+np.array(c['tangent'])*u+np.array(c['outward'])*v
   hit=floor.ray_cast(Vector((xy[0],xy[1],c['floor']+100)),Vector((0,0,-1)),200)
   if hit[0] is None:continue
   gz=ground_z(xy)
   if gz is None:continue
   count+=1;delta=gz-hit[0].z
   row={'xy':xy.tolist(),'local_uv':[float(u),float(v)],'floor_top':hit[0].z,'terrain_z':gz,'intrusion_m':delta}
   if delta>maxdelta:maxdelta=delta;worst=row
   if delta>.15:
    bad_uv.append([float(u),float(v)])
    required=max(required,float(np.abs(np.array([u,v])-corner).sum()))
    if len(bad)<12:bad.append(row)
 courts.append({'id':c['id'],'actual_floor_vertices':len(ob.data.vertices),'sample_count':count,'maximum_intrusion_m':maxdelta,'worst':worst,'examples_over_015m':bad,'intruding_local_bounds':[np.min(bad_uv,axis=0).tolist(),np.max(bad_uv,axis=0).tolist()] if bad_uv else None,'suggested_corner_chamfer_leg_to_exclude_sampled_intrusions_m':math.ceil((required+.5)*4)/4 if required else fix['corner_trim_leg_m'],'recommendation_limit':'Chamfer estimate only; must separately protect building footprints before trimming. A long edge intrusion should use a narrow edge trim rather than this large diagonal chamfer.'})
fills=[]
for name in F['filled_connections']:
 ob=obs[name+' supported fill'];verts=np.array([ob.matrix_world@v.co for v in ob.data.vertices]);ob.data.calc_loop_triangles();bottom_triangles=[tuple(t.vertices) for t in ob.data.loop_triangles if t.polygon_index%6==0];actual_bottom=BVHTree.FromPolygons(verts.tolist(),bottom_triangles,all_triangles=True);worst=None;maxgap=-1e9;count=0;actualmax=-1e9;actualworst=None
 for start in range(0,len(verts),8):
  bottom=verts[start:start+4]
  for u in [.125,.375,.625,.875]:
   for v in [.125,.375,.625,.875]:
    # Blender's bottom quad tessellation may choose either diagonal; take both
    # interpolated triangle surfaces conservatively, recording the larger gap.
    pts=[]
    if u+v<=1:pts.append(bottom[0]+u*(bottom[1]-bottom[0])+v*(bottom[3]-bottom[0]))
    else:pts.append(bottom[2]+(1-u)*(bottom[3]-bottom[2])+(1-v)*(bottom[1]-bottom[2]))
    if u>=v:pts.append(bottom[0]+(u-v)*(bottom[1]-bottom[0])+v*(bottom[2]-bottom[0]))
    else:pts.append(bottom[0]+(v-u)*(bottom[3]-bottom[0])+u*(bottom[2]-bottom[0]))
    for pt in pts:
     gz=ground_z(pt[:2]);count+=1
     if gz is None:continue
     ah=actual_bottom.ray_cast(Vector((pt[0],pt[1],1000)),Vector((0,0,-1)),2000)
     if ah[0] is not None and ah[0].z-gz>actualmax:actualmax=ah[0].z-gz;actualworst={'point':list(ah[0]),'terrain_z':gz,'gap_m':actualmax}
     gap=float(pt[2]-gz)
     if gap>maxgap:maxgap=gap;worst={'point':pt.tolist(),'terrain_z':gz,'gap_m':gap,'fill_segment':start//8}
 fills.append({'name':ob.name,'sample_count':count,'maximum_bottom_above_terrain_m':maxgap,'worst':worst,'actual_saved_triangle_maximum_bottom_gap_m':actualmax,'actual_saved_triangle_worst':actualworst})
report={'input_hashes':hashes,'inputs_stable':all(sha(Path(p))==h for p,h in hashes.items()),'trimmed_court_actual_top':courts,'fill_bottom_checks':fills,'scope':'Only three trimmed actual terrace tops and five added connector fills. Court rays 0.25m grid, original removed corners excluded. Fill bottom interior samples 4x4 per segment with two diagonal alternatives; positive gap requires actual saved triangulation confirmation before calling unsupported.','limits':['No source modification, render/GPU or Git. Not a repeat of complete route/building checks.','0.15m terrace threshold is a review tolerance, not building standard. Suggested extra corner trim is geometric and must not remove building supports.']}
(O/'independent-local-check-final-05.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('LOCAL05',[(x['id'],x['maximum_intrusion_m']) for x in courts],[(x['name'],x['maximum_bottom_above_terrain_m']) for x in fills],flush=True)
