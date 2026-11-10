"""Independent v13 saved-scene CPU audit; never saves/renders scene."""
import bpy,sys,json,hashlib,array,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集池涧水巷-20261024-v0.1';OLD=R/'视频制作/第一集云城校准-20261024-v0.1'
sys.path.insert(0,str(R/'第一季/制作/空间规划/第一集池涧水巷-v0.1'));import water_layout as W
L=W.L;D=json.loads((O/'water-design-data.json').read_text('utf8'));zones=D['zones'];group_for={n:g for g,r in D['rigid_groups'].items() for n in r['members']}
helper=(OLD/'audit.py').read_text('utf8');exec(helper[helper.index('def sha('):helper.index('D=json.loads')].replace('hashes={str(p):sha(p) for p in files}',''))
files=[OLD/'cloud-city-route-58s-v12.blend',O/'pond-lane-route-58s-v13.blend',O/'route-poses.json',O/'water-design-data.json',R/'第一季/制作/空间规划/第一集池涧水巷-v0.1/build.py',R/'第一季/制作/空间规划/第一集池涧水巷-v0.1/water_layout.py'];hashes={str(p):sha(p) for p in files}
def geom(o):
 v=np.array([o.matrix_world@p.co for p in o.data.vertices]);f=[tuple(p.vertices) for p in o.data.polygons];return {'name':o.name,'v':v,'f':f,'bvh':BVHTree.FromPolygons([Vector(p) for p in v],f),'lo':v.min(0),'hi':v.max(0)}
def combine(gs):
 v=[];f=[];names=[]
 for g in gs:
  off=len(v);v.extend(g['v']);f.extend(tuple(off+i for i in face) for face in g['f']);names.extend([g['name']]*len(g['f']))
 return BVHTree.FromPolygons([Vector(p) for p in v],f),names
def height(b,xy,z=600,distance=1200):
 h=b.ray_cast(Vector((xy[0],xy[1],z)),Vector((0,0,-1)),distance);return h[0].z if h[0] is not None else None
bpy.ops.wm.open_mainfile(filepath=str(files[0]));bs,bm=snapshot();bg={o.name:geom(o) for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(files[1]));ns,nm=snapshot();obs={o.name:o for o in bpy.context.scene.objects};ng={o.name:geom(o) for o in obs.values() if o.type=='MESH'}
rigid=[];zchanges=[];topochanges=[];cloudchanges=[]
for name,old in bg.items():
 if name not in ng:topochanges.append({'name':name,'kind':'missing'});continue
 new=ng[name]
 if old['f']!=new['f'] or old['v'].shape!=new['v'].shape:topochanges.append({'name':name,'kind':'topology'});continue
 zd=float(np.max(abs(old['v'][:,2]-new['v'][:,2])))
 if zd>1e-4:zchanges.append({'name':name,'z_max_abs':zd})
 if name in group_for:
  delta=np.r_[D['rigid_groups'][group_for[name]]['delta'],0];err=float(np.max(abs(new['v']-old['v']-delta)));materr=float(np.max(abs(np.array(bs[name]['matrix']).reshape(4,4)[:3,:3]-np.array(ns[name]['matrix']).reshape(4,4)[:3,:3])))
  if err>1e-4 or materr>1e-6:rigid.append({'name':name,'group':group_for[name],'translation_error':err,'matrix_rotation_scale_error':materr})
 if name in D['retained_clouds'] and (bs[name]!=ns[name]):cloudchanges.append(name)
matdiff=[n for n in bm if nm.get(n)!=bm[n]];bindingdiff=[n for n in bs if n in ns and bs[n]['materials']!=ns[n]['materials']]
phys=[g for name,g in ng.items() if obs[name].get('physical',False) and not obs[name].hide_render];bvh,names=combine(phys)
poses=json.loads(files[2].read_text('utf8'));pos=np.array([p['position'] for p in poses]);off=[Vector((x,y,z)) for x in [-.55,0,.55] for y in [-.55,0,.55] for z in [-.35,0,.35]];flight=[]
jsonpos=pos.copy();cam=bpy.context.scene.camera;curves=[]
for layer in cam.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:curves.extend(bag.fcurves)
channels={(f.data_path,f.array_index):f for f in curves};pos=np.array([[channels['location',j].evaluate(i) for j in range(3)] for i in range(1,1393)])
for i,(a,b) in enumerate(zip(pos,pos[1:])):
 a=Vector(a);d=Vector(b)-a
 if d.length<1e-8:continue
 for offset in off:
  h=bvh.ray_cast(a+offset,d.normalized(),d.length)
  if h[0] is not None:flight.append({'from_frame':i+1,'to_frame':i+2,'time':i/24,'object':names[h[2]],'point':list(h[0]),'offset':list(offset)});break
print('CORE',len(rigid),'rigid errors;',len(flight),'flight segments hit',flush=True)
folds=[]
for name in ['Continuous stable cloud terrain / river bed and inhabited slopes','Main water spine / upstream to downstream collection']:
 old=bg[name];new=ng[name];hits=[];zero=[]
 if old['f']!=new['f'] or old['v'].shape!=new['v'].shape:
  for fi,face in enumerate(new['f']):
   for j in range(1,len(face)-1):
    ids=[face[0],face[j],face[j+1]];a=new['v'][ids,:2];area=float(np.linalg.det(np.stack([a[1]-a[0],a[2]-a[0]])))
    if area<0:hits.append({'face':fi,'new_twice_area':area,'center':new['v'][ids].mean(0).tolist()})
    elif area<1e-8:zero.append(fi)
  folds.append({'name':name,'method':'new rebuilt ground upward XY triangulation; no same-index comparison','negative_triangles':len(hits),'new_zero_triangles':len(zero),'examples':hits[:40]});continue
 for fi,face in enumerate(old['f']):
  for j in range(1,len(face)-1):
   ids=[face[0],face[j],face[j+1]];a=old['v'][ids,:2];b=new['v'][ids,:2];aa=np.linalg.det(np.stack([a[1]-a[0],a[2]-a[0]]));bb=np.linalg.det(np.stack([b[1]-b[0],b[2]-b[0]]))
   if abs(aa)<1e-6:continue
   if aa*bb<0:hits.append({'face':fi,'triangle':ids,'old_twice_area':float(aa),'new_twice_area':float(bb),'center':new['v'][ids].mean(0).tolist()})
   elif abs(bb)<1e-8:zero.append(fi)
 folds.append({'name':name,'flipped_triangles':len(hits),'new_zero_triangles':len(zero),'examples':hits[:40]})
q=np.array([p['quaternion'] for p in poses]);q/=np.linalg.norm(q,axis=1)[:,None];turn=np.degrees(2*np.arccos(np.clip(abs(np.sum(q[1:]*q[:-1],axis=1)),0,1)))
report={'hashes':hashes,'stable':all(sha(Path(p))==h for p,h in hashes.items()),'rigid_group_count':len(D['rigid_groups']),'rigid_members':len(group_for),'rigid_errors_gt_0_1mm':rigid,'z_changes_gt_0_1mm':zchanges,'topology_changes':topochanges,'retained_cloud_changes':cloudchanges,'original_material_changes':matdiff,'original_binding_changes':bindingdiff,'full_flight_27_hits':flight,'terrain_water_folds':folds,'max_camera_turn_deg_frame':float(turn.max()),'max_camera_turn_from_frame':int(turn.argmax()+1),'scope':['CPU saved mesh check, no GPU/render/save/Git','27 world-offset segment sweep, not continuous solid volume proof','Triangle XY orientation compared to original; folds require actual topology inspection.']}
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),'utf8');print('V13_CORE_DONE',json.dumps(folds,ensure_ascii=False)[:900],flush=True)
# Targeted orientation/width extension, prioritised after first ground-fold finding.
roadfold=[]
roadnames={o.name for c in bpy.data.collections if c.name.startswith(('03 ','10 ','17 ','18 ')) for o in c.objects if o.type=='MESH' and ('deck' in o.name.lower() or 'landing' in o.name.lower() or 'lane' in o.name.lower() or 'street' in o.name.lower() or 'connection' in o.name.lower() or 'gallery' in o.name.lower() or 'access' in o.name.lower() or 'entry' in o.name.lower() or 'bridge' in o.name.lower()) and not any(t in o.name for t in ['rail','support','frame','roof'])}
for name in sorted(roadnames):
 if name not in bg or name not in ng:continue
 old=bg[name];new=ng[name]
 if old['f']!=new['f']:continue
 flips=[];oldtop=0
 for fi,face in enumerate(old['f']):
  for j in range(1,len(face)-1):
   ids=[face[0],face[j],face[j+1]];a=old['v'][ids,:2];b=new['v'][ids,:2];aa=np.linalg.det(np.stack([a[1]-a[0],a[2]-a[0]]));bb=np.linalg.det(np.stack([b[1]-b[0],b[2]-b[0]]))
   if aa<=1e-6:continue
   oldtop+=1
   if bb<0:flips.append({'face':fi,'twice_area':float(bb),'center':new['v'][ids].mean(0).tolist()})
 if flips:roadfold.append({'name':name,'old_positive_triangles':oldtop,'flipped_top_triangles':len(flips),'examples':sorted(flips,key=lambda x:x['twice_area'])[:12]})
landfold=[];old=bg['Continuous stable cloud terrain / river bed and inhabited slopes'];new=ng[old['name']]
for fi,face in enumerate(old['f'] if old['f']==new['f'] else []):
 for j in range(1,len(face)-1):
  ids=[face[0],face[j],face[j+1]];a=old['v'][ids,:2];b=new['v'][ids,:2];aa=np.linalg.det(np.stack([a[1]-a[0],a[2]-a[0]]));bb=np.linalg.det(np.stack([b[1]-b[0],b[2]-b[0]]))
  if aa*bb<0:
   p=old['v'][ids].mean(0);s,d,_=L.nearest(p[:2]);q=abs(float(d[0]))-float(L.width(s[0],1 if d[0]>=0 else -1));zc=[z['id'] for z in zones if np.all(p[:2]>=z['lo']) and np.all(p[:2]<=z['hi'])]
   landfold.append({'face':fi,'new_twice_area':float(bb),'s':float(s[0]),'old_q':q,'old_center':p.tolist(),'new_center':new['v'][ids].mean(0).tolist(),'overlapping_zone_cores':zc})
water=ng['Main water spine / upstream to downstream collection']['v'];ws=np.linspace(0,1,len(water)//2);actual=np.linalg.norm(water[1::2,:2]-water[0::2,:2],axis=1);target=W.full_width(ws);wi=np.argsort(abs(actual-target))[-15:][::-1]
report['road_top_orientation_flips']=roadfold;report['ground_folds_above_old_water_bank_count']=sum(x['old_q']>=0 for x in landfold);report['ground_worst_land_folds']=sorted([x for x in landfold if x['old_q']>=0],key=lambda x:x['new_twice_area'])[:30];report['water_actual_width_worst_errors']=[{'s':float(ws[i]),'actual_m':float(actual[i]),'target_m':float(target[i]),'difference_m':float(actual[i]-target[i])} for i in wi];report['original_material_changes']=[n for n in bm if n in nm and nm[n]!=bm[n]];report['original_material_datablocks_absent']=[n for n in bm if n not in nm]
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),'utf8');print('ROAD_FOLDS',json.dumps(roadfold,ensure_ascii=False)[:2500],flush=True)

# Walk sampling on actual floors; mapped old routes, with rigid group exceptions.
oldaudit=(OLD/'audit.py').read_text('utf8');exec(oldaudit[oldaudit.index('def roadname('):oldaudit.index('oldhits=[]')])
P=json.loads((R/'视频制作/第一集山水总图白模-20261024-v0.1/layout-plan.json').read_text('utf8'));HD=json.loads((R/'视频制作/第一集云山聚落-20261024-v0.1/landscape-data.json').read_text('utf8'));VD=json.loads((OLD/'world-repair-data.json').read_text('utf8'))
walkdata=[]
for path in P['paths']:
 name=roadname(path['id'])
 if name in bg:walkdata.append((path['id'],path['points'],[name]))
for path in HD['stairs']:
 ns0=[n for n in bg if n.startswith(path['id']+' ') and ('stone step' in n or 'landing' in n)]
 if ns0:walkdata.append((path['id'],path['points'],ns0))
for path in VD['walk_links']:
 name=path['name'];decknames=[name]
 if name=='Dorm door approach':decknames += [n for n in bg if n.startswith('Dorm threshold stone step')]
 # Rebuilt bridges are checked separately using their actual new centerline.
 if name not in ['Upper boarding bridge','Practice hall shore access','Dorm shipping jetty']:walkdata.append((name,path['points'],decknames))
oldphys,_=combine([bg[n] for n in bg if n in ng and obs[n].get('physical',False) and not obs[n].hide_render]);walkresults=[]
for id,points,decks in walkdata:
 ob,_=combine([bg[n] for n in decks]);nb,_=combine([ng[n] for n in decks]);points=np.array(points);sample=[]
 for a,b in zip(points,points[1:]):
  d=b-a;length=np.linalg.norm(d[:2])
  if length<1e-8:continue
  norm=np.array([-d[1],d[0],0])/length
  for lateral in [-.8,0,.8]:
   for f in np.linspace(.005,.995,max(2,int(length/.5)+1)):
    p=a+d*f+norm*lateral;z=height(ob,p,p[2]+.6,1.3)
    if z is not None:sample.append([p[0],p[1],z])
 if not sample:continue
 a=np.array(sample);gs={group_for.get(n) for n in decks}
 if len(gs)==1 and None not in gs:
  b=a.copy();b[:,:2]+=D['rigid_groups'][next(iter(gs))]['delta']
 else:b=W.mapped(a,zones)
 gaps=[];head={};terrain=[]
 for op,np0 in zip(a,b):
  z=height(nb,np0,np0[2]+.6,1.3)
  if z is None:
   if len(gaps)<12:gaps.append(np0.tolist())
   continue
  h=bvh.ray_cast(Vector((np0[0],np0[1],z+.22)),Vector((0,0,1)),1.58)
  if h[0] is not None:
   oldh=oldphys.ray_cast(Vector((op[0],op[1],op[2]+.22)),Vector((0,0,1)),1.58)
   if oldh[0] is None:head.setdefault(names[h[2]],{'point':list(h[0]),'height_above_floor':float(h[0].z-z)})
 if gaps or head:walkresults.append({'path':id,'mapped_samples':len(b),'floor_missing_examples':gaps,'new_headroom_hits':head})
plantintersections=[]
newplants=[ng[o.name] for o in bpy.data.collections['21 Garden water edge clusters'].objects if o.type=='MESH'];roadgs=[ng[n] for n in roadnames if n in ng]
for a in newplants:
 for b in roadgs:
  if np.all(a['hi']>=b['lo']) and np.all(b['hi']>=a['lo']):
   pairs=a['bvh'].overlap(b['bvh'])
   if pairs:plantintersections.append({'plant':a['name'],'road':b['name'],'surface_pairs':len(pairs),'plant_bounds':[a['lo'].tolist(),a['hi'].tolist()]})
report['walk_mapped_route_findings']=walkresults;report['new_plant_road_surface_intersections']=plantintersections
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),'utf8');print('WALK',len(walkresults),'PLANT_ROAD',len(plantintersections),flush=True)

# Separate numerical route sampling departures from substantial missing floors.
walkdict={id:decks for id,pts,decks in walkdata};gapdetails=[]
for row in walkresults:
 deck,_=combine([ng[n] for n in walkdict[row['path']]])
 for p in row['floor_missing_examples']:
  h=deck.find_nearest(Vector(p));gapdetails.append({'path':row['path'],'point':p,'nearest_mesh_distance_m':float(h[3]) if h[0] is not None else None,'nearest_point':list(h[0]) if h[0] is not None else None})
ground=ng['Continuous stable cloud terrain / river bed and inhabited slopes'];padissues=[]
for name,g in ng.items():
 if not name.endswith('court floor'):continue
 missing=[];above=[];maxabove=-1000
 for x in np.arange(g['lo'][0]+.25,g['hi'][0],1):
  for y in np.arange(g['lo'][1]+.25,g['hi'][1],1):
   z=height(g['bvh'],[x,y]);
   if z is None:continue
   gz=height(ground['bvh'],[x,y])
   if gz is None:
    if len(missing)<6:missing.append([float(x),float(y),z])
   else:
    maxabove=max(maxabove,gz-z)
    if gz-z>.04 and len(above)<12:
     delta=np.array(D['rigid_groups'][group_for[name]]['delta']);oldgz=height(bg[ground['name']]['bvh'],np.array([x,y])-delta);above.append({'point':[float(x),float(y),z],'ground_above_m':gz-z,'old_ground_above_m':oldgz-z if oldgz is not None else None})
 if missing or above:padissues.append({'name':name,'missing_support_examples':missing,'terrain_cover_examples':above,'maximum_ground_above_m':maxabove})
roots=[];prefixes={r['name'] for r in VD['support_roots']}
for n,g in ng.items():
 if not (any(n==p or n.startswith(p+'.') for p in prefixes) or 'grounded stilt' in n):continue
 z=g['v'][:,2].min();low=g['v'][g['v'][:,2]<z+.0001];off=[]
 for p in low:
  gz=height(ground['bvh'],p);off.append(float(p[2]-gz) if gz is not None else None)
 if None in off or max(off)>.04:roots.append({'name':n,'bottom_offsets_m':off,'bottom_center':low.mean(0).tolist()})
gardenissues=[];arch=[ng[o.name] for c in bpy.data.collections if c.name.startswith(('04 ','09 ','13 ')) for o in c.objects if o.type=='MESH' and not o.hide_render and not any(t in o.name for t in ['floor','deck','footing','baluster','handrail'])]
for ob in bpy.data.collections['22 Pocket water gardens'].objects:
 if ob.type!='MESH':continue
 a=ng[ob.name]
 for b in arch:
  if np.all(a['hi']>=b['lo']) and np.all(b['hi']>=a['lo']):
   pairs=a['bvh'].overlap(b['bvh'])
   if pairs:gardenissues.append({'new':a['name'],'old':b['name'],'surface_pairs':len(pairs)})
watercovers=[];wv=ng['Main water spine / upstream to downstream collection']['v'].reshape(-1,2,3)
for i in range(0,len(wv),5):
 for t in [.1,.3,.5,.7,.9]:
  p=wv[i,0]*(1-t)+wv[i,1]*t;gz=height(ground['bvh'],p)
  if gz is not None and gz>p[2]+.1:watercovers.append({'s':i/(len(wv)-1),'across_fraction':t,'point':p.tolist(),'terrain_above_water_m':gz-p[2]})
report.update({'walk_missing_floor_nearest_geometry':gapdetails,'actual_court_paving_ground_issues':padissues,'original_post_bottom_support_issues':roots,'new_garden_old_arch_intersections':gardenissues,'water_terrain_cover_samples':watercovers,'stable':all(sha(Path(p))==h for p,h in hashes.items())})
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),'utf8');print('DETAILS','pad',len(padissues),'roots',len(roots),'garden',len(gardenissues),'watercovers',len(watercovers),flush=True)

# Saved animation verification and final added-cascade/road intersections.
cam=bpy.context.scene.camera;curves=[]
for layer in cam.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:curves.extend(bag.fcurves)
channels={(f.data_path,f.array_index):f for f in curves};actualp=np.array([[channels['location',j].evaluate(i) for j in range(3)] for i in range(1,1393)]);actualq=np.array([[channels['rotation_quaternion',j].evaluate(i) for j in range(4)] for i in range(1,1393)])
report['saved_camera_pose_json_error']={'position_max_abs_m':float(np.max(abs(actualp-jsonpos))),'quaternion_max_abs':float(np.max(abs(actualq-np.array([p['quaternion'] for p in poses])))),'parent':cam.parent.name if cam.parent else None}
# Coordinates lie on unique regular XY grid; each four-corner cell appears once.
xy=ground['v'][:,:2];cellkeys=[];nongrid=0
for face in ground['f']:
 p=xy[list(face)];lo=p.min(0);hi=p.max(0);cellkeys.append(tuple(lo));nongrid+=int(len(face)!=4 or np.max(abs((hi-lo)-2.5))>1e-5)
report['terrain_single_value_grid']={'duplicate_xy_vertices':len(xy)-len(np.unique(xy,axis=0)),'duplicate_cells':len(cellkeys)-len(set(cellkeys)),'non_2_5m_cells':nongrid,'method':'unique XY vertices and nonoverlapping axis-aligned 2.5m cells with positive triangulation'}
extra_road=[]
for ob in bpy.data.collections['22 Pocket water gardens'].objects:
 if ob.type!='MESH':continue
 a=ng[ob.name]
 for b in roadgs:
  if np.all(a['hi']>=b['lo']) and np.all(b['hi']>=a['lo']):
   pairs=a['bvh'].overlap(b['bvh'])
   if pairs:extra_road.append({'new':a['name'],'road':b['name'],'surface_pairs':len(pairs)})
report['new_gardens_cascades_road_intersections']=extra_road;report['stable']=all(sha(Path(p))==h for p,h in hashes.items())
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),'utf8');print('FINAL_EXTENSION',report['terrain_single_value_grid'],'CASCADE_ROAD',len(extra_road),flush=True)

step=np.linalg.norm(np.diff(actualp,axis=0),axis=1);acc=np.linalg.norm(np.diff(actualp,n=2,axis=0),axis=1)*24**2;qn=actualq/np.linalg.norm(actualq,axis=1)[:,None];turn=np.degrees(2*np.arccos(np.clip(abs(np.sum(qn[1:]*qn[:-1],axis=1)),0,1)))
sourceposes=json.loads((OLD/'route-poses.json').read_text('utf8'));mappedends=W.mapped(np.array([sourceposes[0]['position'],sourceposes[-1]['position']]),zones)
report['actual_motion']={'maximum_step_m':float(step.max()),'max_step_from_frame':int(step.argmax()+1),'maximum_speed_m_s':float(step.max()*24),'maximum_vector_acceleration_m_s2':float(acc.max()),'max_acceleration_center_frame':int(acc.argmax()+2),'maximum_adjacent_step_length_change_m':float(abs(np.diff(step)).max()),'max_step_length_change_center_frame':int(abs(np.diff(step)).argmax()+2),'max_rotation_deg_frame':float(turn.max()),'max_rotation_from_frame':int(turn.argmax()+1),'endpoint_difference_from_unsmoothed_map_m':np.linalg.norm(actualp[[0,-1]]-mappedends,axis=1).tolist(),'first_10_steps_m':step[:10].tolist(),'last_10_steps_m':step[-10:].tolist(),'around_48_7s_steps_m':step[1164:1174].tolist(),'top_step_events':[{'from_frame':int(i+1),'time_s':float(i/24),'step_m':float(step[i]),'from':actualp[i].tolist(),'to':actualp[i+1].tolist()} for i in np.argsort(step)[-8:][::-1]],'scope':'Actual saved location/quaternion keys at integer frames; no physical dynamics simulation or continuous subframe eval.'}
report['stable']=all(sha(Path(p))==h for p,h in hashes.items())
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),'utf8');print('MOTION',json.dumps(report['actual_motion'])[:1000],flush=True)

# Ground colour attribute restoration is geometry data, not merely material state.
ob=obs['Continuous stable cloud terrain / river bed and inhabited slopes'];attr=ob.data.color_attributes.get('Contour strata color');colour={'exists':attr is not None,'name':'Contour strata color'}
if attr:
 values=np.empty(len(attr.data)*4);attr.data.foreach_get('color',values);values=values.reshape(-1,4);colour.update({'domain':attr.domain,'data_type':attr.data_type,'count':len(values),'vertex_count':len(ob.data.vertices),'finite':bool(np.isfinite(values).all()),'rgba_min':values.min(0).tolist(),'rgba_max':values.max(0).tolist(),'rgb_mean':values[:,:3].mean(0).tolist(),'rgb_std':values[:,:3].std(0).tolist(),'black_rgb_count':int(np.sum(np.max(values[:,:3],axis=1)<=1e-6))})
refs=[]
for slot in ob.material_slots:
 if slot.material and slot.material.use_nodes:
  for node in slot.material.node_tree.nodes:
   ref=getattr(node,'attribute_name',getattr(node,'layer_name',None))
   if ref:refs.append({'material':slot.material.name,'node':node.name,'reference':ref})
colour['material_attribute_references']=refs;report['ground_contour_color']=colour;report['stable']=all(sha(Path(p))==h for p,h in hashes.items())
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),'utf8');print('GROUND_COLOR',json.dumps(colour,ensure_ascii=False),flush=True)
