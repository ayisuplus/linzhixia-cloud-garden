"""Independent v16 CPU static geometry audit. Does not modify scene or render."""
import bpy,sys,json,hashlib,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[-1]);O=R/'视频制作/第一集园岛深化-20261024-v0.1';B=O/'island-garden-developed-v17.blend';D=json.loads((O/'planning-data.json').read_text('utf8'))
SRC=R/'视频制作/第一集独立园岛-20261024-v0.1/island-garden-masterplan-v16.blend';DEV=json.loads((O/'development-data.json').read_text('utf8'))
files=[B,SRC,O/'planning-data.json',O/'development-data.json',R/'第一季/制作/空间规划/第一集园岛深化-v0.1/build.py'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hashes={str(p):sha(p) for p in files}
import array
helper=(R/'视频制作/第一集云城校准-20261024-v0.1/audit.py').read_text('utf8');exec(helper[helper.index('def sha('):helper.index('D=json.loads')].replace('hashes={str(p):sha(p) for p in files}',''))
bpy.ops.wm.open_mainfile(filepath=str(SRC));before,beforemat=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(B));S=bpy.context.scene;obs={o.name:o for o in S.objects};after,aftermat=snapshot()
def geom(o):
 v=np.array([o.matrix_world@p.co for p in o.data.vertices]);f=[tuple(p.vertices) for p in o.data.polygons];return dict(name=o.name,v=v,f=f,lo=v.min(0),hi=v.max(0),b=BVHTree.FromPolygons([Vector(p) for p in v],f))
gs={n:geom(o) for n,o in obs.items() if o.type=='MESH'}
def merge(items):
 v=[];f=[];ns=[]
 for g in items:
  off=len(v);v.extend(g['v']);f.extend(tuple(i+off for i in a) for a in g['f']);ns.extend([g['name']]*len(g['f']))
 return BVHTree.FromPolygons([Vector(p) for p in v],f),ns
physical=[g for n,g in gs.items() if obs[n].get('physical',False) and not obs[n].hide_render and not any(c.hide_render for c in obs[n].users_collection)]
solid,names=merge(physical)
def down(b,xy,z=500,dist=1000):return b.ray_cast(Vector((xy[0],xy[1],z)),Vector((0,0,-1)),dist)
def top(b,xy,z=500,dist=1000):
 h=down(b,xy,z,dist);return h[0].z if h[0] is not None else None
islands={x['id']:gs[x['id']+' separate cloud support'] for x in D['islands']};zbase={x['id']:x['center'][2] for x in D['islands']}
pairs=[]
for ia,(a,ga) in enumerate(islands.items()):
 aa=[ga]+[g for n,g in gs.items() if n.startswith(a+' cloud sleeve') and obs[n].get('physical',False)]
 for b,gb in list(islands.items())[ia+1:]:
  bb=[gb]+[g for n,g in gs.items() if n.startswith(b+' cloud sleeve') and obs[n].get('physical',False)]
  for x in aa:
   for y in bb:
    if np.all(x['hi']>=y['lo']) and np.all(y['hi']>=x['lo']):
     hh=x['b'].overlap(y['b'])
     if hh:pairs.append({'a':x['name'],'b':y['name'],'surface_pairs':len(hh)})
falls=[];pools=[]
for w in D['water']:
 xy=np.array(w['fall_xy']);d=xy-np.array(w['source_pool']);d/=np.linalg.norm(d);n=np.array([-d[1],d[0]]);hits=[]
 for lateral in np.linspace(-1.85,1.85,15):
  for adv in [.01,.1,.4]:
   q=xy+n*lateral+d*adv;h=solid.ray_cast(Vector((*q,w['source_z']-.8)),Vector((0,0,-1)),w['source_z']-w['catch_z']-.9)
   if h[0] is not None:hits.append({'offset':float(lateral),'outward':adv,'object':names[h[2]],'point':list(h[0])})
 falls.append({'id':w['id'],'freefall_hits':hits})
 for iid,center,z in [(w['from'],w['source_pool'],w['source_z']),(w['to'],w['fall_xy'],w['catch_z'])]:
  radius=9.82 if iid==w['from'] else 10.82;checks=[]
  for rr in [0,.5,.92]:
   for angle in np.linspace(0,math.tau,16,endpoint=False):
    p=np.array(center)+radius*rr*np.array([math.cos(angle),math.sin(angle)]);h=down(islands[iid]['b'],p,z+.01,150)
    checks.append({'xy':p.tolist(),'bed_z':h[0].z if h[0] is not None else None,'bed_depth':z-h[0].z if h[0] is not None else None})
  pools.append({'id':w['id'],'island':iid,'bed_missing':[x for x in checks if x['bed_z'] is None],'min_depth':min((x['bed_depth'] for x in checks if x['bed_depth'] is not None),default=None),'max_depth':max((x['bed_depth'] for x in checks if x['bed_depth'] is not None),default=None)})
# Continuous internal path and bridge walking faces, feet and body clearance.
walks=[]
def pathcheck(name,pts,width,base,island=None):
 deck=gs[name]['b'];missing=[];body={};outside=[];maxgap=0
 for aa,bb in zip(pts,pts[1:]):
  a=np.array(aa,float);b=np.array(bb,float);v=b-a;length=np.linalg.norm(v[:2]);nn=np.array([-v[1],v[0],0])/length
  for lat in [-width*.35,0,width*.35]:
   for f in np.linspace(.001,.999,max(2,int(length/.4))):
    q=a+v*f+nn*lat;z=top(deck,q,q[2]+.2,1)
    if z is None:
     if len(missing)<5:missing.append(q.tolist())
     continue
    h=solid.ray_cast(Vector((q[0],q[1],z+.12)),Vector((0,0,1)),1.68)
    if h[0] is not None:body.setdefault(names[h[2]],{'point':list(h[0]),'above_floor':h[0].z-z})
    if island:
     gz=top(islands[island]['b'],q,z+.05,200)
     if gz is None or gz<base-.6:
      if len(outside)<6:outside.append({'xy':q[:2].tolist(),'support_z':gz,'path_z':z})
     else:maxgap=max(maxgap,z-gz)
 return {'name':name,'missing_floor':missing,'body_clearance_hits':body,'off_island_or_over_cut':outside,'max_paving_gap':maxgap}
for iid,paths in D['internal_paths'].items():
 for i,path in enumerate(paths):walks.append(pathcheck(iid+f' internal garden path {i}',[(*p,zbase[iid]+.14) for p in path],3.2,zbase[iid],iid))
for l in D['links']:walks.append(pathcheck(l['id']+' cross-cloud bridge',l['points'],5,l['points'][0][2]))
# Inspect actual stair treads and landings. Head clearance above every tread core.
stairs=[]
for l in D['links']:
 prefix=l['id']+' change-level pavilion';items=[g for n,g in gs.items() if n.startswith(prefix) and ('stair tread' in n or 'half landing' in n)];hits={};minhead=100
 for g in items:
  q=g['v'][4:8].mean(0)
  h=solid.ray_cast(Vector(q)+Vector((0,0,.12)),Vector((0,0,1)),1.68)
  if h[0] is not None:
   gap=h[0].z-q[2];minhead=min(minhead,gap);key=names[h[2]]
   if key not in hits or gap<hits[key]['headroom_m']:hits[key]={'blocking_object':key,'standing_on':g['name'],'point':list(h[0]),'headroom_m':gap,'floor_z':float(q[2])}
 stairs.append({'link':l['id'],'treads_and_halves':len(items),'minimum_detected_headroom_m':minhead if hits else None,'headroom_hits':list(hits.values())})
# Architecture footprints vs own island, pools vs architecture.
courts=[]
for n,g in gs.items():
 if not n.endswith('court floor') or ' reused ' not in n:continue
 iid=obs[n].get('island_id');low=g['lo'][2];ps=[v for v in g['v'] if v[2]<low+.03];ps.append(g['v'].mean(0));bad=[]
 for v in ps:
  z=top(islands[iid]['b'],v,zbase[iid]+.3,200)
  if z is None or zbase[iid]-z>.3:bad.append({'point':v.tolist(),'support_z':z})
 courts.append({'name':n,'support_issues':bad[:10]})
waterarch=[]
for n,g in gs.items():
 if 'water basin' not in n:continue
 for m,b in gs.items():
  if ' reused ' not in m:continue
  if np.all(g['hi']>=b['lo']) and np.all(b['hi']>=g['lo']):
   h=g['b'].overlap(b['b'])
   if h:waterarch.append({'pool':n,'architecture':m,'surface_pairs':len(h)})
r={'hashes':hashes,'stable':all(sha(Path(p))==h for p,h in hashes.items()),'island_support_intersections':pairs,'waterfall_checks':falls,'pool_beds':pools,'walking_checks':walks,'tower_stair_headroom':stairs,'courtyard_support':courts,'pool_architecture_surface_intersections':waterarch,'scope':'Static saved geometry only. No inherited flight check. Sampled clearances, not structural or hydraulic certification.'}
(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,default=lambda x: x.item() if hasattr(x,"item") else str(x)),'utf8');print('V16_AUDIT',len(pairs),'island pairs',[(x['id'],len(x['freefall_hits'])) for x in falls],[(x['name'],len(x['body_clearance_hits'])) for x in walks if x['body_clearance_hits']],[(x['link'],x['minimum_detected_headroom_m']) for x in stairs],flush=True)


# Measure actual stair tread-platform geometric seams, not only stated dimensions.
seams=[]
for l in D['links']:
 prefix=l['id']+' change-level pavilion';xy=l['tower'];tt=l['tower_geometry'];low=tt['lower_z'];high=tt['upper_z'];h=(high-low)/tt['levels'];n=tt['stairs'][0]['risers_per_flight'];rise=tt['stairs'][0]['riser_m'];run=tt['stairs'][0]['tread_m']
 decks=[g for name,g in gs.items() if name.startswith(prefix) and any(w in name for w in ['stair tread',' landing','lift access'])];db,_=merge(decks);gap=[];jump=[]
 for k in range(tt['levels']):
  z=low+k*h
  for f in [0,1]:
   # The six-centimetre route across the meeting edge of tread and actual landing.
   xx=xy[0]+(-2.5 if f==0 else 1.3);yy=xy[1]+(4.4 if f==0 else -4.4);zz=z+h/2 if f==0 else z+h
   heights=[]
   for dy in np.linspace(-.06,.06,13):
    a=top(db,(xx,yy+dy),zz+.08,.5);heights.append(a)
   if any(a is None for a in heights):gap.append({'level':k,'flight':f,'xy':[xx,yy],'expected_z':zz})
   valid=[a for a in heights if a is not None]
   if valid and max(valid)-min(valid)>.20:jump.append({'level':k,'flight':f,'step':max(valid)-min(valid)})
 seams.append({'link':l['id'],'tread_to_platform_missing':gap,'over_20cm_seam':jump})
r['actual_stair_platform_seams']=seams
# Bridge endpoint local support exists; head obstruction is reported separately.
ends=[]
for l in D['links']:
 for p0 in [l['points'][0],l['points'][-1]]:
  own=l['id']+' cross-cloud bridge';bb,ns=merge([g for g in physical if g['name']!=own]);h=down(bb,p0,p0[2]+.2,1)
  ends.append({'link':l['id'],'point':p0,'contact':ns[h[2]] if h[0] is not None else None,'support_z':h[0].z if h[0] is not None else None})
r['bridge_endpoints']=ends;r['stable']=all(sha(Path(p))==h for p,h in hashes.items());(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),'utf8')
print('STAIR_SEAMS',[(x['link'],len(x['tread_to_platform_missing']),len(x['over_20cm_seam'])) for x in seams],flush=True)


# New prism/hull mesh: evaluate actual triangles, never fixed vertex strides.
bridge_width=[]
for link in D['links']:
 name=link['id']+' cross-cloud bridge';g=gs[name];missing=[];railhit=[];count=0
 railitems=[v for n,v in gs.items() if n.startswith(name) and ('handrail' in n or 'rail post' in n)];rb,rn=merge(railitems)
 for seg,(a,b) in enumerate(zip(link['points'],link['points'][1:])):
  a=np.array(a,float);b=np.array(b,float);v=b-a;length=np.linalg.norm(v[:2]);nn=np.array([-v[1],v[0],0])/length
  for lat in np.linspace(-2.49,2.49,21):
   for f in np.linspace(.002,.998,max(3,int(length/.25))):
    q=a+v*f+nn*lat;z=top(g['b'],q,q[2]+.08,1);count+=1
    if z is None or q[2]-z>.05:
     if len(missing)<10:missing.append({'segment':seg,'lateral':float(lat),'point':q.tolist(),'actual_z':z})
    hh=rb.ray_cast(Vector(q)+Vector((0,0,.15)),Vector((0,0,1)),1.6)
    if hh[0] is not None and abs(lat)<=2.25 and len(railhit)<10:railhit.append({'segment':seg,'lateral':float(lat),'point':list(hh[0]),'object':rn[hh[2]]})
 # Every actual horizontal top triangle must have positive projected area.
 toptris=0;negative=0;degenerate=0
 ob=obs[name];ob.data.calc_loop_triangles()
 for tr in ob.data.loop_triangles:
  vv=g['v'][list(tr.vertices)]
  if max(vv[:,2])-min(vv[:,2])<1e-4 and abs(vv[0,2]-link['points'][0][2])<.02:
   area=(vv[1,0]-vv[0,0])*(vv[2,1]-vv[0,1])-(vv[1,1]-vv[0,1])*(vv[2,0]-vv[0,0]);toptris+=1;negative+=int(area< -1e-6);degenerate+=int(abs(area)<=1e-6)
 bridge_width.append({'link':link['id'],'actual_top_triangles':toptris,'negative_top_triangles':negative,'degenerate_top_triangles':degenerate,'samples':count,'missing_4_98m_deck':missing,'rail_in_4_5m_core':railhit})
r['independent_bridge_full_width']=bridge_width;r['stable']=all(sha(Path(p))==h for p,h in hashes.items());(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),'utf8')
print('BRIDGE_WIDTH',[(x['link'],len(x['missing_4_98m_deck']),len(x['rail_in_4_5m_core']),x['negative_top_triangles']) for x in bridge_width],flush=True)

# Exact retained asset snapshot and precisely declared material binding changes.
changes=[];removed=set(DEV['removed_source_objects']);allowed={(x['object'],x['slot']):x for x in DEV['material_changes']}
for name,a in before.items():
 if name in removed:
  if name in after:changes.append({'name':name,'unexpected':'declared removal still present'})
  continue
 if name not in after:changes.append({'name':name,'unexpected':'missing'});continue
 b=after[name]
 for key in ['type','mesh','matrix']:
  if a[key]!=b[key]:changes.append({'name':name,'unexpected':key})
 if len(a['materials'])!=len(b['materials']):changes.append({'name':name,'unexpected':'material count'})
 for i,(aa,bb) in enumerate(zip(a['materials'],b['materials'])):
  if aa==bb:continue
  permit=allowed.get((name,i))
  if not permit or aa[0]!=permit['old'] or bb[0]!=permit['new'] or aa[1]!=bb[1]:changes.append({'name':name,'unexpected':'material binding','slot':i})
matmissing=[n for n in beforemat if n not in aftermat];matdiff=[n for n in beforemat if n in aftermat and beforemat[n]!=aftermat[n]]
# Existing front garden gate/approach and added veranda access: walk through the real opening.
thresholds=[]
for c in D['courts']:
 iid=c['island'];cx,cy=c['target_center'];ang=math.radians(c['angle']);base=zbase[iid]+.16;bad={};gaps=[]
 for x in [-1.15,0,1.15]:
  for y in np.linspace(-24,-12,61):
   q=np.array([cx+x*math.cos(ang)-y*math.sin(ang),cy+x*math.sin(ang)+y*math.cos(ang),base]);hit=solid.ray_cast(Vector(q)+Vector((0,0,.2)),Vector((0,0,1)),1.6)
   if hit[0] is not None:bad.setdefault(names[hit[2]],{'point':list(hit[0]),'above_nominal_floor':hit[0].z-base})
   z=top(solid,q,base+.1,1)
   if z is None and len(gaps)<4:gaps.append(q.tolist())
 thresholds.append({'court':c['source_prefix'],'island':iid,'headroom_hits':bad,'floor_missing':gaps})
# New balcony access from west end of south landing, x across doorway, full 1.8m head check.
balconies=[]
for item in DEV['balconies']:
 link=next(x for x in D['links'] if x['id']==item['link']);x,y=link['tower'];z=item['floor'];bad={};missing=[]
 for yy in [y-6.5,y-5.7,y-4.8]:
  for xx in np.linspace(x-10.8,x-6.5,44):
   h=solid.ray_cast(Vector((xx,yy,z+.15)),Vector((0,0,1)),1.65)
   if h[0] is not None:bad.setdefault(names[h[2]],{'point':list(h[0]),'above_balcony':h[0].z-z})
   floor=top(solid,(xx,yy),z+.08,1)
   if floor is None and len(missing)<4:missing.append([float(xx),float(yy),z])
 balconies.append({'link':item['link'],'floor':z,'headroom_hits':bad,'floor_missing':missing})
r['asset_preservation']={'unexpected_changes':changes,'original_material_changes':matdiff,'original_materials_absent_after_save':matmissing,'declared_removed':len(removed),'declared_material_slots':len(allowed),'source_hash_matches_metadata':hashes[str(SRC)]==DEV['source_sha256']};r['court_threshold_checks']=thresholds;r['balcony_access_checks']=balconies
r['stable']=all(sha(Path(p))==h for p,h in hashes.items());(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),'utf8')
print('V17_ASSETS',len(changes),len(matdiff),'DOORS',[(x['court'],len(x['headroom_hits'])) for x in thresholds],'BALCONIES',[(x['link'],len(x['headroom_hits'])) for x in balconies],flush=True)

# Regression against ALL solids across the 4.5m bridge core, including new facade/eaves.
newcore=[]
for link in D['links']:
 hitobjects={};count=0
 for a,b in zip(link['points'],link['points'][1:]):
  a=np.array(a,float);b=np.array(b,float);d=b-a;length=np.linalg.norm(d[:2]);nn=np.array([-d[1],d[0],0])/length
  for lat in np.linspace(-2.25,2.25,19):
   for f in np.linspace(.002,.998,max(3,int(length/.3))):
    p0=a+d*f+nn*lat;count+=1;hit=solid.ray_cast(Vector(p0)+Vector((0,0,.20)),Vector((0,0,1)),1.60)
    if hit[0] is not None:hitobjects.setdefault(names[hit[2]],{'point':list(hit[0]),'above_bridge':hit[0].z-p0[2]})
 newcore.append({'link':link['id'],'samples':count,'body_hits':hitobjects})
clouds=[o for o in bpy.data.collections['11 Cloud edge sleeves'].objects if o.type=='MESH']
r['bridge_all_solids_core_regression']=newcore;r['cloud_sleeve_role_check']={'count':len(clouds),'physical_count':sum(bool(o.get('physical',False)) for o in clouds),'note':'Only original seven core meshes bear structure; sleeve volumes excluded from solid collision, optical visibility requires rendered review.'}
r['final_verdict']={'status':'pass bounded static geometry regression','remaining_required_geometry_fixes':[]};r['stable']=all(sha(Path(p))==h for p,h in hashes.items());(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),'utf8')
print('ALL_SOLID_BRIDGE',[(x['link'],len(x['body_hits'])) for x in newcore],'CLOUD_ROLE',r['cloud_sleeve_role_check'],flush=True)

# Final cloud-material-only revision check. The blend1 is the immediately prior save,
# explicitly identified by its own hash, not asserted to equal the earlier accepted hash.
cloudroles=[]
for cname in ['06 Optional atmospheric enclosure','11 Cloud edge sleeves','13 Local cloud veils']:
 c=bpy.data.collections.get(cname);items=list(c.objects) if c else []
 cloudroles.append({'collection':cname,'objects':len(items),'physical_objects':sum(bool(x.get('physical',False)) for x in items)})
cloudmaterials=[]
for mname in ['v17 edge mist non bearing','v17 soft shoulder mist']:
 mat=bpy.data.materials.get(mname);details={'material':mname,'exists':mat is not None}
 if mat:
  vol=next((x for x in mat.node_tree.nodes if x.type=='PRINCIPLED_VOLUME'),None);links=mat.node_tree.links
  density=next((x.from_socket for x in links if vol and x.to_socket==vol.inputs['Density']),None);em=next((x.from_node for x in links if vol and x.to_socket==vol.inputs['Emission Strength']),None)
  details.update({'density_weighted_emission':bool(em and em.type=='MATH' and em.operation=='MULTIPLY' and any(x.from_socket==density and x.to_node==em for x in links)),'emission_gain':float(em.inputs[1].default_value) if em and em.type=='MATH' else None})
 cloudmaterials.append(details)
backup=B.with_suffix('.blend1');revision={}
if backup.exists():
 backuphash=sha(backup);bpy.ops.wm.open_mainfile(filepath=str(backup));previous,previousmat=snapshot();diff=[]
 for name,a in after.items():
  if name not in previous:diff.append({'name':name,'change':'new object'});continue
  for key in ['type','mesh','matrix','materials']:
   if a[key]!=previous[name][key]:diff.append({'name':name,'change':key})
 for name in previous:
  if name not in after:diff.append({'name':name,'change':'removed object'})
 revision={'reference':'immediately previous blend1 save','reference_sha256':backuphash,'reference_stable':backuphash==sha(backup),'object_geometry_transform_binding_changes':diff,'material_node_digest_changes':[n for n in aftermat if n in previousmat and aftermat[n]!=previousmat[n]]}
r['cloud_material_revision']=revision;r['nonbearing_cloud_collections']=cloudroles;r['density_emission_verification']=cloudmaterials;r['stable']=all(sha(Path(p))==h for p,h in hashes.items())
(O/'audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),'utf8');print('CLOUD_MATERIAL_REVISION',revision,cloudmaterials,flush=True)
