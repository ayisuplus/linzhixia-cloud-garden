"""Read-only CPU audit: blender --background --python this.py -- --root PROJECT.
Never saves a blend file, renders, initializes GPU devices, or edits source assets.
Uses the versioned project's prior serializer functions via AST definitions only.
"""
import bpy, sys, json, hashlib, ast, argparse
import numpy as np
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--root', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
ROOT = Path(a.root)
OUT = ROOT / '视频制作/第一集云中园城-20261024-v0.1'
BASE = ROOT / '视频制作/第一集园城航线重排-20261023-v0.1/garden-city-flight-58s-v04.blend'
CANDIDATE = OUT / 'city-within-cloud-reference-v03.blend'
HELPER = ROOT / '视频制作/第一集云海城市-20261023-v0.1/independent-preservation-audit.py'
functions = {'digest', 'basic', 'rna_simple', 'array_hash', 'geometry', 'material_signature'}
tree = ast.parse(HELPER.read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in functions], type_ignores=[]), str(HELPER), 'exec'))
curve_geometry = geometry

def geometry(data):
    if not isinstance(data, bpy.types.Mesh):
        return curve_geometry(data)
    return {
        'counts': [len(data.vertices), len(data.edges), len(data.polygons), len(data.loops)],
        'positions': array_hash(data.vertices, 'co', 3),
        'edges': array_hash(data.edges, 'vertices', 2, np.int32),
        'loops': array_hash(data.loops, 'vertex_index', 1, np.int32),
        'polygon_start': array_hash(data.polygons, 'loop_start', 1, np.int32),
        'polygon_size': array_hash(data.polygons, 'loop_total', 1, np.int32),
        'polygon_material': array_hash(data.polygons, 'material_index', 1, np.int32),
        'polygon_smoothing': array_hash(data.polygons, 'use_smooth', 1, np.bool_),
    }

def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def excluded(o):
    if o.type not in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
        return 'not original mesh/curve asset'
    if 'cloud' in o.name.lower():
        return 'original cloud object'
    if any(c.name in {'E01_FLIGHT_PROXY', 'V05_TEMPORARY_QUADROTOR', 'V03_ROUTE_GUIDES'} for c in o.users_collection):
        return 'flight carrier/drone/route guide'
    return None

def bsdf_colors(m):
    if not m.use_nodes:
        return {'viewport_diffuse': list(m.diffuse_color)}
    return {n.name: {s.identifier: list(s.default_value) for s in n.inputs
                     if s.type == 'RGBA' and hasattr(s, 'default_value')}
            for n in m.node_tree.nodes if 'BSDF' in n.type}

def snapshot(path, names=None, material_names=None):
    start_hash = file_hash(path)
    bpy.ops.wm.open_mainfile(filepath=str(path))
    objects, geom, mats, exemptions = {}, {}, {}, {}
    s = bpy.context.scene
    # Original building transforms are static; animation/camera differences excluded.
    s.frame_set(1)
    lookup = {o.name: o for o in s.objects}
    targets = list(lookup.values()) if names is None else [lookup.get(n) for n in names]
    for i, o in enumerate(targets):
        if o is None:
            continue
        if names is None:
            reason = excluded(o)
            if reason:
                exemptions[o.name] = reason
                continue
        key = (o.type, o.data.name) if o.data else None
        if key not in geom:
            geom[key] = geometry(o.data)
        objects[o.name] = {
            'type': o.type, 'data_name': o.data.name,
            'geometry_hash': digest(geom[key]),
            'material_slots': [(slot.link, slot.material.name if slot.material else None) for slot in o.material_slots],
            'matrix_world_frame1': [v for row in o.matrix_world for v in row],
            'modifiers': [rna_simple(m) for m in o.modifiers],
        }
        if i % 15000 == 0:
            print('AUDIT_ASSETS', path.name, i, flush=True)
    used = sorted({name for o in objects.values() for _, name in o['material_slots'] if name}) if material_names is None else material_names
    for name in used:
        m = bpy.data.materials.get(name)
        if m:
            mats[name] = {'shader_signature': material_signature(m), 'bsdf_colors': bsdf_colors(m)}
    unhashed = {str(k): [n for n, v in g.get('attributes', {}).items() if 'not_hashed' in v]
                for k, g in geom.items() if isinstance(g, dict)}
    return {'hash_before': start_hash, 'hash_after': file_hash(path), 'objects': objects,
            'materials': mats, 'exempt_objects': exemptions, 'geometry_blocks': len(geom),
            'unhashed_attributes': {k: v for k, v in unhashed.items() if v}}

base = snapshot(BASE)
new = snapshot(CANDIDATE, list(base['objects']), list(base['materials']))
missing = sorted(set(base['objects']) - set(new['objects']))
changes = []
for name, old in base['objects'].items():
    if name not in new['objects']:
        continue
    for key, value in old.items():
        if value != new['objects'][name][key]:
            changes.append({'object': name, 'field': key, 'before': value, 'after': new['objects'][name][key]})
material_changes = [{'material': name, 'before': value, 'after': new['materials'].get(name)}
                    for name, value in base['materials'].items() if value != new['materials'].get(name)]
exact_matrix_differences = [dict(c, maximum_absolute_component_delta=float(np.max(np.abs(np.array(c['before'])-c['after']))))
                            for c in changes if c['field'] == 'matrix_world_frame1']
matrix_absolute_tolerance = 1e-4
changes = [c for c in changes if not (c['field'] == 'matrix_world_frame1' and
           np.max(np.abs(np.array(c['before'])-c['after'])) <= matrix_absolute_tolerance)]
stable_files = all(q['hash_before'] == q['hash_after'] for q in (base, new))
result = {
    'baseline': str(BASE), 'candidate': str(CANDIDATE), 'serializer_dependency': str(HELPER),
    'serializer_sha256': file_hash(HELPER),
    'baseline_hashes': [base['hash_before'], base['hash_after']],
    'candidate_hashes': [new['hash_before'], new['hash_after']],
    'source_files_stable_during_audit': stable_files,
    'protected_original_mesh_curve_objects': len(base['objects']),
    'protected_unique_geometry_blocks': base['geometry_blocks'],
    'protected_bound_materials': len(base['materials']),
    'protected_materials_with_bsdf_color_sockets': sum(bool(m['bsdf_colors']) for m in base['materials'].values()),
    'missing_original_assets': missing, 'asset_changes': changes,
    'matrix_absolute_tolerance': matrix_absolute_tolerance,
    'exact_matrix_differences': exact_matrix_differences,
    'exact_world_transforms_preserved': not exact_matrix_differences,
    'bound_material_parameter_or_bsdf_color_changes': material_changes,
    'explicit_exempt_objects': base['exempt_objects'],
    'unhashed_attributes': base['unhashed_attributes'],
    'passed': stable_files and not missing and not changes and not material_changes and not base['unhashed_attributes'],
    'scope': 'All original non-cloud mesh/curve assets including architecture, interior props, plants and ground. Compare local coordinates/topology/material polygon indices/smoothing, material slots, frame1 transforms, modifiers, bound shader parameters and BSDF color socket values. New objects/collection instances, cloud objects, cameras and flight proxy/rotor/route-guide collections excluded; all visibility and animation excluded.',
    'limits': ['No rendering or GPU initialization, no save operation.',
               'Shader signature includes direct node inputs/settings/links; not recursive nested-group evaluation or external texture-byte comparison. UV maps/custom attributes/custom normals/shape keys are not included.',
               'This audit proves asset preservation only, not collision, light appearance or final visual acceptance.',
               'Frame 275 lower water-court optical reveal still requires dynamic viewing; geometry repair does not imply all visual criteria passed.'],
}
(OUT / 'independent-preservation-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
print('PRESERVATION_AUDIT_DONE', result['passed'], len(missing), len(changes), len(material_changes), flush=True)
if not result['passed']:
    print(json.dumps({'changes': changes[:5], 'materials': material_changes[:5]}, ensure_ascii=False), flush=True)
