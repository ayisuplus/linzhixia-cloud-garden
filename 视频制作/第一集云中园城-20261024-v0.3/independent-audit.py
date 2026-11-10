"""Read-only CPU v04 -> v05 audit. No GPU, render, save or Git.
blender -b --factory-startup --threads 2 --python THIS -- --root PROJECT
"""
import bpy,ast,json,hashlib,math,sys,argparse
import numpy as np
from pathlib import Path
from collections import Counter
p=argparse.ArgumentParser();p.add_argument('--root',required=True)
ROOT=Path(p.parse_args(sys.argv[sys.argv.index('--')+1:]).root)
OUT=ROOT/'视频制作/第一集云中园城-20261024-v0.3'
BASE=ROOT/'视频制作/第一集云中园城-20261024-v0.2/cloud-city-water-reveal-58s-v04.blend'
NEW=OUT/'cloud-city-color-58s-v05.blend'
HELPER=ROOT/'视频制作/第一集云海城市-20261023-v0.1/independent-preservation-audit.py'
PREVIOUS=ROOT/'视频制作/第一集云中园城-20261024-v0.2/independent-audit.py'
def loaddefs(path,excluded=()):
 tree=ast.parse(path.read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name not in excluded],type_ignores=[]),str(path),'exec'),globals())
loaddefs(HELPER,('snapshot',));curve_geometry=geometry
loaddefs(PREVIOUS)
planpath=OUT/'color-cloud-plan.json';plan_hash=sha(planpath);plan=json.loads(planpath.read_text('utf8'))
planned={x['object']:Counter((a['source'],a['material']) for a in x['assignments']) for x in plan['changed_object_bindings']}
protected_names={'01_Architecture','02_Bed','03_Cabinet','04_Desk','05_Curtains','06_Corridor','08_Props','E01_HOME_EXTENSION','E01_WORKSHOP','E01_SCHOOL_GROUND','E01_DORM','E01_DANCE_HALL'}
def protected():
 return {c.name:sorted(o.name for o in c.all_objects) for c in bpy.data.collections if c.name in protected_names or c.name.removeprefix('HOME_') in protected_names}
base=snapshot(BASE);protected_groups=protected();new=snapshot(NEW)
missing=sorted(set(base['objects'])-set(new['objects']));added=sorted(set(new['objects'])-set(base['objects']))
changes=[];actual_bindings={};binding_errors=[];sun_changes=[]
for name,old in base['objects'].items():
 if name not in new['objects']:continue
 for key,value in old.items():
  other=new['objects'][name][key]
  if value==other:continue
  if key=='materials':
   if len(value)!=len(other):binding_errors.append({'object':name,'reason':'slot count changed'})
   assignments=Counter()
   for before,after in zip(value,other):
    if before==after:continue
    if after[0]!='OBJECT':binding_errors.append({'object':name,'reason':'changed binding not OBJECT','before':before,'after':after})
    assignments[(before[1],after[1])]+=1
   actual_bindings[name]=assignments
   if assignments!=planned.get(name):binding_errors.append({'object':name,'reason':'exact source/destination binding multiset differs from plan','actual':list(assignments.elements()),'planned':list(planned.get(name,Counter()).elements())})
  elif name=='Neutral morning sun' and key=='matrix_frame1':sun_changes.append({'object':name,'field':key,'before':value,'after':other})
  else:changes.append({'object':name,'field':key,'before':value,'after':other})
for name in set(planned)-set(actual_bindings):binding_errors.append({'object':name,'reason':'planned binding change absent'})
material_changes=[n for n,h in base['materials'].items() if new['materials'].get(n)!=h]
allowed_cloud=set(plan['changed_cloud_materials'])
unexpected_materials=sorted(set(material_changes)-allowed_cloud)
missing_cloud_changes=sorted(allowed_cloud-set(material_changes))
added_materials=sorted(set(new['materials'])-set(base['materials']))
unexpected_new_materials=[n for n in added_materials if not n.startswith('CITY05 ')]
protected_binding_changes={g:sorted(set(names)&set(actual_bindings)) for g,names in protected_groups.items()}
protected_binding_changes={g:names for g,names in protected_binding_changes.items() if names}
positions=float(np.max(np.abs(base['camera_location']-new['camera_location'])))
quat=float(np.max(np.abs(base['camera_quaternions']-new['camera_quaternions'])))
carrier=float(np.max(np.abs(base['carrier_location']-new['carrier_location'])))
stable=all(x['hash_before']==x['hash_after'] for x in [base,new]) and plan_hash==sha(planpath)
report={'baseline':str(BASE),'candidate':str(NEW),'baseline_sha256':[base['hash_before'],base['hash_after']],
 'candidate_sha256':[new['hash_before'],new['hash_after']],'source_files_stable':stable,
 'plan_sha256':plan_hash,'plan_source_hash_matches':plan['source_sha256']==base['hash_before'],
 'original_objects':len(base['objects']),'original_geometry_blocks':base['geometry_blocks'],
 'missing_objects':missing,'added_objects':added,'unexpected_asset_changes':changes,
 'authorized_sun_transform_changes':sun_changes,'planned_binding_objects':len(planned),'actual_binding_objects':len(actual_bindings),
 'binding_plan_errors':binding_errors,'changed_original_cloud_materials':material_changes,
 'unexpected_original_material_changes':unexpected_materials,'declared_cloud_changes_missing':missing_cloud_changes,
 'original_material_count':len(base['materials']),'new_city_materials':added_materials,'unexpected_new_materials':unexpected_new_materials,
 'protected_collections_object_counts':{g:len(names) for g,names in protected_groups.items()},
 'protected_collection_binding_changes':protected_binding_changes,
 'camera_positions_max_difference_m':positions,'camera_quaternion_components_max_difference':quat,
 'carrier_positions_max_difference_m':carrier,
 'camera_action_identical':base['objects'][base['camera_name']]['animation']==new['objects'][new['camera_name']]['animation'],
 'carrier_action_identical':base['objects']['Same carrier ROOT placeholder']['animation']==new['objects']['Same carrier ROOT placeholder']['animation'],
 'camera_settings_identical':base['camera_settings']==new['camera_settings'],'timing_identical':base['timing']==new['timing'],
 'serializer_dependencies':{str(HELPER):sha(HELPER),str(PREVIOUS):sha(PREVIOUS)},
 'scope':'All original mesh coordinates/topology/material polygon indices/smoothing, object matrices (authorized sun rotation excepted), bindings against exact listed per-object source/destination assignments; every original object animation and direct material shader signature. Named original home/interior/school collections separately checked for unchanged bindings. Added CITY05 material datablocks allowed.',
 'limits':['No render, GPU or scene save. No new collision or continuous viewing claim.',
 'UV/custom attributes/custom normals/shape keys, external image bytes and recursively evaluated node groups excluded.',
 'World, sunlight and AgX appearance changes authorized; unchanged interior material does not imply unchanged lit screen appearance.',
 'Object-level bindings are intentionally allowed; original data-level materials must remain unchanged.']}
report['passed']=bool(stable and report['plan_source_hash_matches'] and not missing and not added and not changes and not binding_errors and not unexpected_materials and not unexpected_new_materials and not protected_binding_changes and positions==0 and quat==0 and carrier==0 and report['camera_action_identical'] and report['carrier_action_identical'] and report['camera_settings_identical'] and report['timing_identical'])
(OUT/'independent-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('V05_AUDIT_DONE',report['passed'],len(changes),len(binding_errors),unexpected_materials,protected_binding_changes,flush=True)
