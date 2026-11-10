"""Read-only CPU saved whitebox geometry audit, no render or save."""
import bpy,json,math,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(sys.argv[sys.argv.index('--')+1]);OUT=ROOT/'视频制作/第一集山水总图白模-20261024-v0.1'
source=OUT/'landscape-masterplan-v08.blend';planpath=OUT/'layout-plan.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
hashes={str(p):sha(p) for p in [source,planpath]};P=json.loads(planpath.read_text('utf8'))
bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene;S.frame_set(1);lookup={o.name:o for o in S.objects}
def geo(o):
 v=[o.matrix_world@x.co for x in o.data.vertices];f=[tuple(x.vertices) for x in o.data.polygons];a=np.array(v)
 return {'name':o.name,'bvh':BVHTree.FromPolygons(v,f),'lo':a.min(0),'hi':a.max(0)}
buildings=[geo(o) for o in S.objects if o.type=='MESH' and any(o.name.endswith(' / '+n) for n in ['back hall','left wing','right wing'])]
ground=geo(lookup['Continuous stable cloud terrain / river bed and inhabited slopes'])
def inside(g,p):
 if np.any(p<g['lo']) or np.any(p>g['hi']):return False
 h=g['bvh'].find_nearest(Vector(p));return h[0] is not None and (Vector(p)-h[0]).dot(h[1])<-.005
def polygon(court):
 o=lookup[court['id']+' court floor'];return [np.array((o.matrix_world@o.data.vertices[i].co)[:2]) for i in range(4)]
def area(poly):return abs(sum(np.cross(poly[(i+1)%len(poly)],p) for i,p in enumerate(poly)))/2 if len(poly)>2 else 0
def clip(poly,other):
 # Box bottom corners are counterclockwise in XY.
 for a,b in zip(other,other[1:]+other[:1]):
  if not poly:break
  result=[]
  for q,r in zip(poly,poly[1:]+poly[:1]):
   fq=np.cross(b-a,q-a);fr=np.cross(b-a,r-a);iq=fq>=-1e-8;ir=fr>=-1e-8
   if iq:result.append(q)
   if iq!=ir:result.append(q+(r-q)*fq/(fq-fr))
  poly=result
 return poly
overlaps=[];courts=P['courts'];polys={c['id']:polygon(c) for c in courts}
for i,a in enumerate(courts):
 for b in courts[i+1:]:
  ar=area(clip(polys[a['id']],polys[b['id']]))
  if ar>.01:overlaps.append({'a':a['id'],'b':b['id'],'plan_overlap_m2':float(ar),'floor_delta_m':abs(a['floor']-b['floor'])})
building_pairs=[]
for i,a in enumerate(buildings):
 for b in buildings[i+1:]:
  if a['name'].split(' / ')[0]==b['name'].split(' / ')[0]:continue
  if np.any(a['hi']<b['lo']) or np.any(b['hi']<a['lo']):continue
  hit=a['bvh'].overlap(b['bvh'])
  if hit:building_pairs.append({'a':a['name'],'b':b['name'],'surface_triangle_pairs':len(hit)})
support=[]
for c in courts:
 xy=np.array(c['center']);t=np.array(c['tangent']);n=np.array(c['outward']);delta=[];samples=[];missing=0
 for u in np.linspace(-18,18,7):
  for v in np.linspace(-18,18,7):
   pt=np.r_[xy+t*u+n*v,c['floor']+200];h=ground['bvh'].ray_cast(Vector(pt),Vector((0,0,-1)),500)
   if h[0] is None:missing+=1
   else:delta.append(float(c['floor']-h[0].z));samples.append({'xy':pt[:2].tolist(),'floor':c['floor'],'terrain_z':h[0].z})
 if missing or min(delta,default=0)<-.15 or max(delta,default=0)>.15:support.append({'court':c['id'],'missing':missing,'max_floor_above_ground_m':max(delta,default=None),'max_ground_above_floor_m':-min(delta,default=0),'most_buried_sample':samples[int(np.argmin(delta))] if delta else None,'most_floating_sample':samples[int(np.argmax(delta))] if delta else None})
roads=[]
for path in P['paths']:
 pts=np.array(path['points']);d=np.diff(pts,axis=0);h=np.linalg.norm(d[:,:2],axis=1);slope=np.abs(d[:,2])/np.maximum(h,1e-9);hits={};floating=[];buried=[]
 for a,b in zip(pts,pts[1:]):
  length=np.linalg.norm(b[:2]-a[:2]);side=np.array([-(b-a)[1],(b-a)[0],0]);side/=max(np.linalg.norm(side),1e-9)
  for fraction in np.linspace(0,1,max(2,math.ceil(length)+1)):
   foot=a+(b-a)*fraction
   for lateral in [-min(1,path['width']*.3),0,min(1,path['width']*.3)]:
    p=foot+side*lateral+np.array([0,0,.9])
    for g in buildings:
     if inside(g,p):hits.setdefault(g['name'],{'point':p.tolist(),'lateral':float(lateral)})
   h0=ground['bvh'].ray_cast(Vector(foot+np.array([0,0,200])),Vector((0,0,-1)),500)
   if h0[0] is not None:
    gap=float(foot[2]-h0[0].z)
    if gap>1:floating.append(gap)
    if gap<-.2:buried.append(gap)
 roads.append({'id':path['id'],'type':path['type'],'maximum_slope_percent':float(slope.max()*100),'steepest_segment':int(slope.argmax()),'building_body_intersections':hits,'max_above_terrain_m':max(floating,default=0),'max_below_terrain_m':-min(buried,default=0)})
 print('ROAD_AUDIT',path['id'],len(hits),flush=True)
water=P['water_samples'];z=np.array([x['center'][2] for x in water]);xyz=np.array([x['center'] for x in water]);dz=np.diff(z);length=np.linalg.norm(np.diff(xyz[:,:2],axis=0),axis=1)
bay=[x for x in water if .575<=x['s']<=.715]
report={'input_hashes':hashes,'inputs_stable':all(sha(Path(p))==h for p,h in hashes.items()),'court_count':len(courts),'court_footprint_overlaps':overlaps,'court_support_exceptions':support,'paths':roads,'water':{'uphill_segments':int(np.count_nonzero(dz>1e-6)),'max_grade_percent':float(np.max(-dz/length)*100),'total_drop_m':float(z[0]-z[-1]),'water_bay_0575_0715_drop_m':bay[0]['center'][2]-bay[-1]['center'][2],'bay_length_m':(.715-.575)*P['river_length_m']},'limits':['Saved mesh geometry; no render or scene save.','Road body points at 1m longitudinal spacing, three lateral positions and 0.9m height; not continuous body sweep. Building boxes only, not roof/rails/terrain headroom.','Plan footprint overlap does not alone prove volume collision; floor height difference supplied.','Court support uses 7x7 samples against actual 6m terrain triangles. Road terrain gap is diagnostic: bridge/upper-street gap can be intentional but requires explicit structural/connection design.','New flight does not yet exist here; no flight acceptance.']}
report['different_court_building_surface_intersections']=building_pairs
(OUT/'independent-blockout-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('BLOCKOUT_AUDIT_DONE',len(overlaps),len(support),len(building_pairs),flush=True)
