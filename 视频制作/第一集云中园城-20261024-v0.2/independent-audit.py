"""CPU-only read audit. No scene saving or rendering.
blender --background --factory-startup --threads 2 --python THIS -- --root PROJECT
"""
import bpy, ast, json, hashlib, math, sys, argparse
import numpy as np
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True)
ROOT=Path(p.parse_args(sys.argv[sys.argv.index('--')+1:]).root)
OUT=ROOT/'视频制作/第一集云中园城-20261024-v0.2'
BASE=ROOT/'视频制作/第一集云中园城-20261024-v0.1/city-within-cloud-reference-v03.blend'
NEW=OUT/'cloud-city-water-reveal-58s-v04.blend'
HELPER=ROOT/'视频制作/第一集云海城市-20261023-v0.1/independent-preservation-audit.py'
tree=ast.parse(HELPER.read_text('utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name!='snapshot'],type_ignores=[]),str(HELPER),'exec'))
curve_geometry=geometry
def geometry(d):
 if not isinstance(d,bpy.types.Mesh):return curve_geometry(d)
 return {'counts':[len(d.vertices),len(d.edges),len(d.polygons),len(d.loops)],
  'co':array_hash(d.vertices,'co',3),'edges':array_hash(d.edges,'vertices',2,np.int32),
  'loops':array_hash(d.loops,'vertex_index',1,np.int32),'start':array_hash(d.polygons,'loop_start',1,np.int32),
  'total':array_hash(d.polygons,'loop_total',1,np.int32),'material':array_hash(d.polygons,'material_index',1,np.int32),
  'smooth':array_hash(d.polygons,'use_smooth',1,np.bool_)}
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8388608),b''):h.update(block)
 return h.hexdigest()
def fcurves(o):
 return [fc for la in o.animation_data.action.layers for st in la.strips for bag in st.channelbags for fc in bag.fcurves]
def sampled(o,path,frames):
 fs=sorted([fc for fc in fcurves(o) if fc.data_path==path],key=lambda fc:fc.array_index)
 return np.array([[fc.evaluate(f) for fc in fs] for f in frames])
def snapshot(path):
 h=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(1)
 lookup={o.name:o for o in s.objects};geo={};objects={};actions={}
 for i,(name,o) in enumerate(lookup.items()):
  data=o.data;key=(o.type,data.name) if data else None
  if o.type in {'MESH','CURVE','SURFACE','FONT'} and key not in geo:geo[key]=digest(geometry(data))
  objects[name]={'type':o.type,'data':data.name if data else None,'geometry':geo.get(key),
   'materials':[(sl.link,sl.material.name if sl.material else None) for sl in o.material_slots],
   'matrix_frame1':[v for row in o.matrix_world for v in row],'parent':o.parent.name if o.parent else None,
   'hide_render':o.hide_render,'modifiers':[rna_simple(m) for m in o.modifiers],
   'constraints':[rna_simple(c) for c in o.constraints],
   'animation':animation(o,actions),'data_animation':animation(data,actions) if data else None}
  if i%15000==0:print('AUDIT',path.name,i,flush=True)
 materials={m.name:material_signature(m) for m in bpy.data.materials}
 cam=s.camera;carrier=lookup['Same carrier ROOT placeholder'];frames=np.arange(1,1393)
 edge_frames=[1+t*24 for t in [10.7166666667,10.7583333333,10.8,10.8416666667,10.8833333333,19.7166666667,19.7583333333,19.8,19.8416666667,19.8833333333]]
 return {'hash_before':h,'hash_after':sha(path),'objects':objects,'materials':materials,'geometry_blocks':len(geo),
  'camera_name':cam.name,'camera_location':sampled(cam,'location',frames),'camera_quaternions':sampled(cam,'rotation_quaternion',frames),
  'camera_nonrotation_fcurves':digest([curve_record(fc) for fc in fcurves(cam) if fc.data_path!='rotation_quaternion']),
  'camera_edge_quaternions':sampled(cam,'rotation_quaternion',edge_frames),'edge_frames':edge_frames,
  'camera_settings':{k:basic(getattr(cam.data,k)) for k in ['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']},
  'carrier_location':sampled(carrier,'location',frames),
  'timing':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base]}
base=snapshot(BASE);new=snapshot(NEW)
missing=sorted(set(base['objects'])-set(new['objects']));added=sorted(set(new['objects'])-set(base['objects']))
changes=[];roundoff=[]
for name,old in base['objects'].items():
 if name not in new['objects']:continue
 for key,value in old.items():
  other=new['objects'][name][key]
  if value==other:continue
  if name==base['camera_name'] and key in {'animation','matrix_frame1'}:continue
  c={'object':name,'field':key,'before':value,'after':other}
  if key=='matrix_frame1' and max(abs(a-b) for a,b in zip(value,other))<=1e-4:roundoff.append(c)
  else:changes.append(c)
material_changes=[n for n,h in base['materials'].items() if new['materials'].get(n)!=h]
allowed_cloud_prefixes=('ENCLOSING CLOUD','MOTHER CLOUD','Ordinary mist /')
unexpected_materials=[n for n in material_changes if not n.startswith(allowed_cloud_prefixes)]
def norm(q):return q/np.linalg.norm(q,axis=-1,keepdims=True)
def angle(a,b):
 a=norm(a);b=norm(b);b=b*np.where(np.sum(a*b,axis=-1,keepdims=True)<0,-1,1)
 return np.degrees(4*np.arctan2(np.linalg.norm(a-b,axis=-1),np.linalg.norm(a+b,axis=-1)))
q0=norm(base['camera_quaternions']);q1=norm(new['camera_quaternions'])
turn0=angle(q0[:-1],q0[1:]);turn1=angle(q1[:-1],q1[1:]);relative=angle(q0,q1)
times=np.arange(1392)/24;outside=(times<=10.8)|(times>=19.8)
edge_relative=angle(base['camera_edge_quaternions'],new['camera_edge_quaternions'])
edge_rows=[{'time_s':(f-1)/24,'additional_rotation_deg':float(v)} for f,v in zip(base['edge_frames'],edge_relative)]
windows=[]
for edge in [10.8,19.8]:
 ids=np.where(np.abs(times[:-1]-edge)<.2)[0]
 windows.append({'boundary_s':edge,'turn_samples':[{'from_frame':int(i+1),'from_time_s':float(times[i]),'baseline_deg':float(turn0[i]),'candidate_deg':float(turn1[i]),'difference_deg':float(turn1[i]-turn0[i])} for i in ids]})
position_delta=float(np.max(np.abs(new['camera_location']-base['camera_location'])))
carrier_delta=float(np.max(np.abs(new['carrier_location']-base['carrier_location'])))
stable=all(x['hash_before']==x['hash_after'] for x in [base,new])
report={'baseline':str(BASE),'candidate':str(NEW),'baseline_sha256':[base['hash_before'],base['hash_after']],
 'candidate_sha256':[new['hash_before'],new['hash_after']],'files_stable':stable,
 'original_object_count':len(base['objects']),'original_geometry_blocks':base['geometry_blocks'],
 'original_material_count':len(base['materials']),'missing_objects':missing,'added_objects':added,
 'asset_changes':changes,'matrix_roundoff_within_1e_4':roundoff,'changed_cloud_materials':material_changes,
 'unexpected_material_changes':unexpected_materials,'camera_position_max_absolute_difference_m':position_delta,
 'carrier_position_max_absolute_difference_m':carrier_delta,
 'carrier_action_identical':base['objects']['Same carrier ROOT placeholder']['animation']==new['objects']['Same carrier ROOT placeholder']['animation'],
 'camera_nonrotation_curves_identical':base['camera_nonrotation_fcurves']==new['camera_nonrotation_fcurves'],
 'camera_settings_identical':base['camera_settings']==new['camera_settings'],'camera_settings':new['camera_settings'],
 'timing_identical':base['timing']==new['timing'],'timing':new['timing'],
 'motion':{'baseline_max_turn_deg_per_frame':float(turn0.max()),'new_max_turn_deg_per_frame':float(turn1.max()),
 'maximum_turn_from_frame':int(np.argmax(turn1)+1),'maximum_turn_from_time_s':float(np.argmax(turn1)/24),
 'max_additional_rotation_deg':float(relative.max()),'outside_glance_max_rotation_difference_deg':float(relative[outside].max()),
 'outside_glance_frames_above_1e_4_degrees':(np.where(outside&(relative>1e-4))[0]+1).tolist(),
 'additional_rotation_boundary_samples':edge_rows,'boundary_turn_windows':windows,
 'method':'Normalized quaternion shortest angles in float64 from saved F-curves. Integer frames and boundary subframes; no scene evaluated per frame. sin^4 authored profile has zero first/second derivatives at endpoints; saved LINEAR channels remain piecewise, not analytic C2.'},
 'serializer_dependency':str(HELPER),'serializer_sha256':sha(HELPER),
 'limits':['Read-only CPU asset and saved F-curve audit; no rendering, GPU initialization or saving.',
 'Mesh coordinates/topology/material indices/smoothing checked. UV/custom attributes/custom normals/shape keys and external texture bytes excluded.',
 'Direct material node values/settings/links compared; not recursive node-group evaluation.',
 'No new collision/optical or continuous-video success claim. Camera angular audit does not prove pleasing movement.']}
report['passed']=bool(stable and not missing and added==['Cloud clearing world coordinate origin'] and not changes and not unexpected_materials and position_delta==0 and carrier_delta==0 and report['carrier_action_identical'] and report['camera_nonrotation_curves_identical'] and report['camera_settings_identical'] and report['timing_identical'] and relative[outside].max()<1e-4)
(OUT/'independent-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('INDEPENDENT_AUDIT_DONE',report['passed'],len(changes),unexpected_materials,report['motion']['new_max_turn_deg_per_frame'],flush=True)
