"""Read-only CPU static v09 review; no route/render/save."""
import bpy,sys,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集水巷街桥-20261024-v0.1';OLD=R/'视频制作/第一集山水总图白模-20261024-v0.1';src=O/'waterlane-masterplan-v09.blend';dp=O/'design-data.json';pp=OLD/'layout-plan.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
hashes={str(p):sha(p) for p in [src,dp,pp]};D=json.loads(dp.read_text('utf8'));P=json.loads(pp.read_text('utf8'));bpy.ops.wm.open_mainfile(filepath=str(src));S=bpy.context.scene;obs={o.name:o for o in S.objects}
def geo(o):
 v=[o.matrix_world@p.co for p in o.data.vertices];f=[tuple(p.vertices) for p in o.data.polygons];a=np.array(v);return {'name':o.name,'v':v,'f':f,'lo':a.min(0),'hi':a.max(0),'bvh':BVHTree.FromPolygons(v,f)}
def combine(gs):
 v=[];f=[];names=[]
 for g in gs:
  offset=len(v);v.extend(g['v']);f.extend(tuple(i+offset for i in p) for p in g['f']);names.extend([g['name']]*len(g['f']))
 return BVHTree.FromPolygons(v,f),names
cache={}
def get(o):
 if o.name not in cache:cache[o.name]=geo(o)
 return cache[o.name]
def overlapping(a,b):return np.all(a['hi']>=b['lo']) and np.all(b['hi']>=a['lo'])
front_ids=[x['id'] for x in D['frontages']]
def front_owner(n):return next((f for f in front_ids if n.startswith(f+' ')),None)
newobjs=[o for c in ['09 Waterfront streets and inhabited bridgeheads','10 Connected bridges and quays','11 Garden canopy rhythm'] for o in bpy.data.collections[c].objects if o.type=='MESH' and o.get('physical',True)]
new=[get(o) for o in newobjs];primary=[g for g in new if front_owner(g['name']) and any(g['name'].endswith(t) for t in ['upper floor','upper rooms','tiled roof','ground shop','ground shop.001'])]
oldarch=[get(o) for o in bpy.data.collections['04 Contour courtyard clusters'].objects if o.type=='MESH']
bridge=[g for g in new if not front_owner(g['name']) and any(k in g['name'] for k in ['bridge deck','bridge continuous roof','bridge roof column'])]
pairs=[]
for i,a in enumerate(primary):
 for b in primary[i+1:]+oldarch+bridge:
  if front_owner(a['name'])==front_owner(b['name']):continue
  if not overlapping(a,b):continue
  overlap=a['bvh'].overlap(b['bvh'])
  if overlap:pairs.append({'a':a['name'],'b':b['name'],'surface_intersection_pairs':len(overlap)})
ground=get(obs['Continuous stable cloud terrain / river bed and inhabited slopes'])
def gz(xy):
 h=ground['bvh'].ray_cast(Vector((xy[0],xy[1],400)),Vector((0,0,-1)),800);return h[0].z if h[0] is not None else None
supports=[]
for o in newobjs:
 if 'arcade column' not in o.name and 'stone column foot' not in o.name and 'abutment' not in o.name:continue
 g=get(o);center=(g['lo']+g['hi'])/2;z=gz(center[:2]);supports.append({'name':o.name,'base_z':float(g['lo'][2]),'terrain_center_z':z,'base_gap_m':float(g['lo'][2]-z) if z is not None else None})
def roadname(n):
 if n.startswith('bank-'):return 'Continuous bank lane '+n[5:]
 if n.endswith('-entry') and n!='middle-entry':return n[:-6]+' entry connection'
 if n.startswith('bridge-'):return 'Cross-water bridge '+n[7:]
 if n.startswith('hill-'):return 'Upper slope street '+n[5:]
 if n.startswith('slope-link-'):
  side,cs=n[11:].rsplit('-',1);return 'Bank to slope connector '+side+' '+cs
 if n=='middle-entry':return 'Second-level through passage and gallery'
 if n=='framing-bridge':return 'Framing bridge supported bank to bank'
 raise ValueError(n)
allnew,names=combine(new);lows=np.array([g['lo'] for g in new]);highs=np.array([g['hi'] for g in new]);path_hits=[]
for path in P['paths']:

 name=roadname(path['id'])
 if name not in obs:continue # Old bridge decks replaced; actual new bridge/bank surfaces checked below.
 deck=get(obs[name])['bvh'];pts=np.array(path['points']);hits={}
 for a,b in zip(pts,pts[1:]):
  lo=np.minimum(a,b)-[2,2,.2];hi=np.maximum(a,b)+[2,2,2]
  nearby=np.flatnonzero(np.all(highs>=lo,axis=1)&np.all(lows<=hi,axis=1))
  if not len(nearby):continue
  delta=b-a;length=np.linalg.norm(delta);side=np.array([-delta[1],delta[0],0]);side/=max(np.linalg.norm(side),1e-9)
  for lateral in [-.9,0,.9]:
   qa=a+side*lateral;qb=b+side*lateral
   ha=deck.ray_cast(Vector(qa+[0,0,20]),Vector((0,0,-1)),40);hb=deck.ray_cast(Vector(qb+[0,0,20]),Vector((0,0,-1)),40)
   if ha[0] is None or hb[0] is None:continue
   for height in [.15,.9,1.8]:
    start=ha[0]+Vector((0,0,height));end=hb[0]+Vector((0,0,height));d=end-start
    if d.length<1e-6:continue
    h=allnew.ray_cast(start,d.normalized(),d.length)
    if h[0] is not None:hits.setdefault(names[h[2]],{'point':list(h[0]),'height':height,'lateral':lateral})
 if hits:path_hits.append({'path':path['id'],'hits':hits})
 # Print even zero to show scope; only static old walk routes, no new flight.
print('STATIC_PAIRS',len(pairs),'WALK_HITS',len(path_hits),flush=True)
bankbvh={side:get(obs['Continuous bank lane '+str(side)])['bvh'] for side in [-1,1]};connections=[]
for bridgeinfo in D['bridges']:
 station=bridgeinfo['s'];kind=bridgeinfo['kind'];deckname=kind+' deck';deck=get(obs[deckname])['bvh'];pts=np.array(bridgeinfo['points']);row={'bridge':kind,'ends':[]}
 for side,p,opposite in [(-1,pts[0],pts[-1]),(1,pts[-1],pts[0])]:
  forward=(opposite-p);forward/=np.linalg.norm(forward);perp=np.array([-forward[1],forward[0],0]);perp/=np.linalg.norm(perp);samples=[]
  for inward in np.linspace(0,4,9):
   for across in [-1,0,1]:
    q=p+forward*inward+perp*across;h1=deck.ray_cast(Vector(q+[0,0,30]),Vector((0,0,-1)),60);h2=bankbvh[side].ray_cast(Vector(q+[0,0,30]),Vector((0,0,-1)),60)
    if h1[0] is not None and h2[0] is not None:samples.append({'point':q.tolist(),'deck_minus_bank_m':h1[0].z-h2[0].z})
  row['ends'].append({'side':side,'overlap_sample_count':len(samples),'maximum_height_mismatch_m':max((abs(x['deck_minus_bank_m']) for x in samples),default=None),'sample':max(samples,key=lambda x:abs(x['deck_minus_bank_m'])) if samples else None})
 connections.append(row)
report={'input_hashes':hashes,'inputs_stable':all(sha(Path(p))==h for p,h in hashes.items()),'frontage_count':len(front_ids),'bridges':len(D['bridges']),'intersections':pairs,'walk_route_new_obstacle_hits':path_hits,'support_center_checks':supports,'bridge_bank_actual_surface_overlaps':connections,'removed_ring_objects_remaining':[n for n in obs if n.startswith(('School valley framing aperture','Framing gate pier'))],'limits':['Read-only saved geometry; no GPU/render/save/Git. Current changing flight excluded.','Surface intersections are candidates, not automatically unacceptable designed joins. Containment-only pairs not certified.','Walk core swept lines at three lateral positions and three heights, against new physical meshes. Does not prove exact swept human volume.','Support checks compare centers; decorative column feet can be embedded with columns, distinguish from actual column bottom. Bridge abutment foundations may embed river bed.','Bridge joins sample actual old/new saved surfaces; endpoint declarations alone not used.']}
(O/'independent-static-audit-final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('STATIC_DONE',flush=True)
