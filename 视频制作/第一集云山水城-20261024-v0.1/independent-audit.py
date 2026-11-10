"""Read-only CPU v06 -> v07 audit. Never renders, saves scenes or initializes GPU.
blender -b --factory-startup --threads 2 --python THIS -- --root PROJECT
"""
import bpy,ast,json,hashlib,math,sys,argparse
import numpy as np
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True)
ROOT=Path(p.parse_args(sys.argv[sys.argv.index('--')+1:]).root)
OUT=ROOT/'视频制作/第一集云山水城-20261024-v0.1'
BASE=ROOT/'视频制作/第一集云中园城-20261024-v0.4/cloud-city-layered-58s-v06.blend'
NEW=OUT/'cloud-stone-water-city-58s-v07.blend'
HELPER=ROOT/'视频制作/第一集云海城市-20261023-v0.1/independent-preservation-audit.py'
PREVIOUS=ROOT/'视频制作/第一集云中园城-20261024-v0.2/independent-audit.py'
def loaddefs(path,excluded=()):
 tree=ast.parse(path.read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name not in excluded],type_ignores=[]),str(path),'exec'),globals())
loaddefs(HELPER,('snapshot',));curve_geometry=geometry;loaddefs(PREVIOUS)
planpath=OUT/'construction-plan.json';plan=json.loads(planpath.read_text('utf8'));planhash=sha(planpath)
def node_tree_record(tree):
 if tree is None:return None
 return {'nodes':[{'name':n.name,'type':n.bl_idname,
  'settings':rna_simple(n,{'location','width','height','dimensions','select','show_options','show_preview','show_texture','color','use_custom_color','parent'}),
  'inputs':[(s.identifier,basic(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]} for n in tree.nodes],
  'links':sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links)}
def lighting():
 s=bpy.context.scene
 return {'light_data':{o.name:rna_simple(o.data) for o in s.objects if o.type=='LIGHT'},
  'world_name':s.world.name if s.world else None,
  'world_rna':rna_simple(s.world) if s.world else None,
  'world_nodes':node_tree_record(s.world.node_tree) if s.world else None,
  'view_settings':rna_simple(s.view_settings),
  'compositor_nodes':node_tree_record(s.compositing_node_group)}
base=snapshot(BASE);base_light=lighting();new=snapshot(NEW);new_light=lighting()
missing=sorted(set(base['objects'])-set(new['objects']));added=sorted(set(new['objects'])-set(base['objects']))
changes=[]
for name,old in base['objects'].items():
 if name not in new['objects']:continue
 for key,value in old.items():
  other=new['objects'][name][key]
  if value!=other:changes.append({'object':name,'field':key,'before':value,'after':other})
material_changes=sorted(n for n,h in base['materials'].items() if new['materials'].get(n)!=h)
allowed=[];added_materials=sorted(set(new['materials'])-set(base['materials']))
light_changes=[k for k in base_light if base_light[k]!=new_light[k]]
position_delta=float(np.max(np.abs(base['camera_location']-new['camera_location'])))
rotation_delta=float(np.max(np.abs(base['camera_quaternions']-new['camera_quaternions'])))
carrier_delta=float(np.max(np.abs(base['carrier_location']-new['carrier_location'])))
stable=all(x['hash_before']==x['hash_after'] for x in [base,new]) and planhash==sha(planpath)
report={'baseline':str(BASE),'candidate':str(NEW),'baseline_sha256':[base['hash_before'],base['hash_after']],
 'candidate_sha256':[new['hash_before'],new['hash_after']],'source_files_stable':stable,
 'revision_sha256':planhash,'revision_source_hash_matches':plan['source_sha256']==base['hash_before'],
 'original_objects':len(base['objects']),'original_geometry_blocks':base['geometry_blocks'],
 'original_material_count':len(base['materials']),'missing_objects':missing,'added_objects':added,
 'unexpected_object_changes':changes,'changed_original_materials':material_changes,'authorized_materials':allowed,
 'added_materials':added_materials,'lighting_world_display_compositor_changes':light_changes,
 'camera_positions_max_difference_m':position_delta,'camera_quaternion_components_max_difference':rotation_delta,
 'carrier_positions_max_difference_m':carrier_delta,
 'camera_action_identical':base['objects'][base['camera_name']]['animation']==new['objects'][new['camera_name']]['animation'],
 'carrier_action_identical':base['objects']['Same carrier ROOT placeholder']['animation']==new['objects']['Same carrier ROOT placeholder']['animation'],
 'camera_settings_identical':base['camera_settings']==new['camera_settings'],'timing_identical':base['timing']==new['timing'],
 'timing':new['timing'],
 'serializer_dependencies':{str(HELPER):sha(HELPER),str(PREVIOUS):sha(PREVIOUS)},
 'scope':'Editable source to editable source. Exact original geometry signatures, bindings, frame1 matrices, parents, modifiers, constraints, visibility, active actions and their keyframe data compared. All direct material parameters protected; new LANDSCAPE07 objects and new materials permitted. Light datablock settings, world nodes/settings, display settings and compositor direct nodes also compared.',
 'limits':['Read-only CPU. No GPU, render, scene save or Git. Render-only batching proxy not audited here.',
 'Mesh coordinates/topology/material indices/smoothing compared; UV/custom attributes/custom normals/shape keys and external texture bytes excluded.',
 'Direct shader nodes/inputs/settings/links compared, not recursively evaluated nested groups or all unused Blender datablocks.',
 'Motion sampled from saved F-curves at 1392 integer frames, with action keyframe records also compared; no per-frame scene evaluation or new collision check.',
 'Asset preservation is independent of static visual review and does not certify continuous cloud appearance or final video acceptance.']}
report['passed']=bool(stable and report['revision_source_hash_matches'] and not missing and all(n.startswith('LANDSCAPE07 ') for n in added) and not changes and material_changes==allowed and not light_changes and position_delta==0 and rotation_delta==0 and carrier_delta==0 and report['camera_action_identical'] and report['carrier_action_identical'] and report['camera_settings_identical'] and report['timing_identical'])
(OUT/'independent-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('V07_AUDIT_DONE',report['passed'],len(changes),material_changes,light_changes,flush=True)
