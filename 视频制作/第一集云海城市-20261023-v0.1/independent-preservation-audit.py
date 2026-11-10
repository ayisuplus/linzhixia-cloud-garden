"""Read-only CPU comparison. Never saves scenes, evaluates animation frames, or renders."""
import bpy, json, hashlib, math
import numpy as np
from pathlib import Path

ROOT = Path(r'E:/projects/内容创作/未来女孩林知夏')
OUT = ROOT / '视频制作/第一集云海城市-20261023-v0.1'
BASE = ROOT / '视频制作/第一集园城航线重排-20261023-v0.1/garden-city-flight-58s-v04.blend'
CANDIDATE = OUT / 'cloudsea-city-v04.blend'

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def basic(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, bpy.types.ID):
        return {'id_type': value.bl_rna.identifier, 'name': value.name}
    try:
        return [basic(x) for x in value]
    except TypeError:
        return str(value)

def rna_simple(item, excluded=()):
    result = {}
    for prop in item.bl_rna.properties:
        key = prop.identifier
        if key == 'rna_type' or key in excluded or prop.type == 'COLLECTION':
            continue
        if prop.is_readonly and prop.type != 'POINTER':
            continue
        try:
            value = getattr(item, key)
            if prop.type == 'POINTER' and value is not None and not isinstance(value, bpy.types.ID):
                continue
            result[key] = basic(value)
        except (AttributeError, TypeError, ValueError):
            pass
    return result

def array_hash(collection, property_name, size, dtype=np.float32):
    a = np.empty(len(collection) * size, dtype=dtype)
    if len(a):
        collection.foreach_get(property_name, a)
    return hashlib.sha256(a.tobytes()).hexdigest()

def geometry(data):
    if isinstance(data, bpy.types.Mesh):
        result = {
            'vertex_count': len(data.vertices), 'edge_count': len(data.edges),
            'polygon_count': len(data.polygons), 'loop_count': len(data.loops),
            'positions': array_hash(data.vertices, 'co', 3),
            'edges': array_hash(data.edges, 'vertices', 2, np.int32),
            'loops': array_hash(data.loops, 'vertex_index', 1, np.int32),
            'polygon_start': array_hash(data.polygons, 'loop_start', 1, np.int32),
            'polygon_size': array_hash(data.polygons, 'loop_total', 1, np.int32),
            'polygon_material': array_hash(data.polygons, 'material_index', 1, np.int32),
            'polygon_smoothing': array_hash(data.polygons, 'use_smooth', 1, np.bool_),
            'attributes': {},
        }
        kinds = {'FLOAT': ('value', 1, np.float32), 'INT': ('value', 1, np.int32),
                 'INT8': ('value', 1, np.int32), 'BOOLEAN': ('value', 1, np.bool_),
                 'FLOAT_VECTOR': ('vector', 3, np.float32), 'FLOAT2': ('vector', 2, np.float32),
                 'FLOAT_COLOR': ('color', 4, np.float32), 'BYTE_COLOR': ('color', 4, np.float32)}
        for attr in data.attributes:
            if attr.data_type in kinds:
                prop, size, dt = kinds[attr.data_type]
                try:
                    h = array_hash(attr.data, prop, size, dt)
                except (TypeError, ValueError, RuntimeError):
                    h = digest([basic(getattr(v, prop)) for v in attr.data])
                result['attributes'][attr.name] = [attr.domain, attr.data_type, h]
            else:
                result['attributes'][attr.name] = [attr.domain, attr.data_type, len(attr.data), 'not_hashed']
        if data.shape_keys:
            result['shape_keys'] = {k.name: array_hash(k.data, 'co', 3) for k in data.shape_keys.key_blocks}
        return result
    if isinstance(data, bpy.types.Curve):
        return {'settings': rna_simple(data, {'materials', 'animation_data'}),
                'splines': [{'settings': rna_simple(s),
                             'points': [list(p.co) + [p.radius, p.tilt] for p in s.points],
                             'bezier': [{'co': list(p.co), 'left': list(p.handle_left), 'right': list(p.handle_right),
                                         'types': [p.handle_left_type, p.handle_right_type], 'radius': p.radius, 'tilt': p.tilt}
                                        for p in s.bezier_points]} for s in data.splines]}
    return None

def curve_record(fc):
    return {'path': fc.data_path, 'index': fc.array_index, 'extrapolation': fc.extrapolation,
            'keys': [{'co': list(k.co), 'left': list(k.handle_left), 'right': list(k.handle_right),
                      'interpolation': k.interpolation, 'easing': k.easing,
                      'handles': [k.handle_left_type, k.handle_right_type],
                      'amplitude': k.amplitude, 'back': k.back, 'period': k.period} for k in fc.keyframe_points],
            'samples': [list(k.co) for k in fc.sampled_points],
            'modifiers': [rna_simple(m) for m in fc.modifiers]}

def action_record(action):
    return {'slots': [rna_simple(s) for s in action.slots],
            'layers': [{'name': l.name, 'settings': rna_simple(l),
                        'strips': [{'type': s.type, 'channelbags': [
                            {'slot_handle': b.slot_handle, 'fcurves': [curve_record(fc) for fc in b.fcurves]}
                            for b in s.channelbags]} for s in l.strips]} for l in action.layers]}

def animation(id_block, action_cache):
    ad = getattr(id_block, 'animation_data', None)
    if not ad:
        return None
    if ad.action and ad.action.name not in action_cache:
        action_cache[ad.action.name] = digest(action_record(ad.action))
    return {'action': ad.action.name if ad.action else None, 'slot': ad.action_slot_handle,
            'action_hash': action_cache.get(ad.action.name) if ad.action else None,
            'blend': ad.action_blend_type, 'extrapolation': ad.action_extrapolation,
            'influence': ad.action_influence, 'use_nla': ad.use_nla,
            'nla': [{'name': t.name, 'mute': t.mute, 'strips': [rna_simple(s) for s in t.strips]} for t in ad.nla_tracks],
            'drivers': [{'curve': curve_record(fc), 'type': fc.driver.type, 'expression': fc.driver.expression,
                         'variables': [{'name': v.name, 'type': v.type, 'targets': [rna_simple(t) for t in v.targets]}
                                       for v in fc.driver.variables]} for fc in ad.drivers]}

def material_signature(m):
    result = {'diffuse_color': list(m.diffuse_color), 'roughness': m.roughness,
              'metallic': m.metallic, 'use_nodes': m.use_nodes}
    if m.use_nodes:
        result['nodes'] = [{'name': n.name, 'type': n.bl_idname,
                            'settings': rna_simple(n, {'location', 'width', 'height', 'dimensions', 'select', 'show_options', 'show_preview', 'show_texture', 'color', 'use_custom_color', 'parent'}),
                            'inputs': [(s.identifier, basic(s.default_value)) for s in n.inputs if hasattr(s, 'default_value')]}
                           for n in m.node_tree.nodes]
        result['links'] = sorted((l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier) for l in m.node_tree.links)
    return digest(result)

def snapshot(path):
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(path))
    s = bpy.context.scene
    s.frame_set(1)
    objects, geo_cache, actions, materials = {}, {}, {}, {}
    for i, o in enumerate(s.objects):
        data = o.data
        key = (o.type, data.name) if data else None
        if data and o.type in {'MESH', 'CURVE', 'FONT', 'SURFACE'} and key not in geo_cache:
            geo_cache[key] = digest(geometry(data))
        bindings = [(slot.link, slot.material.name if slot.material else None) for slot in o.material_slots]
        for _, name in bindings:
            if name and name not in materials:
                materials[name] = material_signature(bpy.data.materials[name])
        record = {'type': o.type, 'data_name': data.name if data else None,
                  'geometry': geo_cache.get(key), 'materials': bindings,
                  'matrix_world_frame1': [v for row in o.matrix_world for v in row],
                  'location': list(o.location), 'rotation_mode': o.rotation_mode,
                  'rotation_euler': list(o.rotation_euler), 'rotation_quaternion': list(o.rotation_quaternion),
                  'scale': list(o.scale), 'parent': o.parent.name if o.parent else None,
                  'hide_render': o.hide_render, 'constraints': [rna_simple(c) for c in o.constraints],
                  'modifiers': [rna_simple(m) for m in o.modifiers],
                  'animation': animation(o, actions),
                  'data_animation': animation(data, actions) if data else None}
        if o.type == 'CAMERA':
            record['camera_data'] = {k: basic(getattr(data, k)) for k in ['type', 'lens', 'sensor_width', 'sensor_height', 'sensor_fit', 'shift_x', 'shift_y', 'clip_start', 'clip_end', 'ortho_scale']}
        objects[o.name] = record
        if i % 15000 == 0:
            print('SNAPSHOT', path.name, i, flush=True)
    return {'sha256_at_open': sha, 'sha256_at_end': hashlib.sha256(path.read_bytes()).hexdigest(),
            'objects': objects, 'materials': materials, 'actions': actions,
            'scene': {'fps': s.render.fps, 'fps_base': s.render.fps_base, 'frame_start': s.frame_start,
                      'frame_end': s.frame_end, 'camera': s.camera.name if s.camera else None},
            'unique_geometry_blocks': len(geo_cache)}

base = snapshot(BASE)
candidate = snapshot(CANDIDATE)
missing, changed, allowed = [], [], []
for name, old in base['objects'].items():
    new = candidate['objects'].get(name)
    if new is None:
        missing.append(name)
        continue
    for key in old:
        if old[key] == new[key]:
            continue
        if key == 'materials' and old[key] and all(m is None or m.startswith('V06 ') for _, m in old[key]):
            allowed.append({'object': name, 'field': key, 'before': old[key], 'after': new[key]})
        elif key == 'camera_data':
            differences = {k: [old[key][k], new[key][k]] for k in old[key] if old[key][k] != new[key][k]}
            if set(differences) == {'clip_end'} and new[key]['clip_end'] >= old[key]['clip_end']:
                allowed.append({'object': name, 'field': key, 'differences': differences})
            else:
                changed.append({'object': name, 'field': key, 'differences': differences})
        else:
            changed.append({'object': name, 'field': key, 'before': old[key], 'after': new[key]})
material_changes = [{'material': n, 'before': h, 'after': candidate['materials'].get(n)}
                    for n, h in base['materials'].items()
                    if n in candidate['materials'] and h != candidate['materials'][n]]
scene_changed = base['scene'] != candidate['scene']
report = {'baseline': str(BASE), 'candidate': str(CANDIDATE),
          'baseline_hashes': [base['sha256_at_open'], base['sha256_at_end']],
          'candidate_hashes': [candidate['sha256_at_open'], candidate['sha256_at_end']],
          'original_object_count': len(base['objects']), 'candidate_object_count': len(candidate['objects']),
          'added_scene_objects': sorted(set(candidate['objects']) - set(base['objects'])),
          'unique_original_geometry_blocks': base['unique_geometry_blocks'],
          'missing_original_objects': missing, 'unexpected_object_changes': changed,
          'allowed_changes': allowed, 'original_used_material_parameter_changes': material_changes,
          'original_animation_actions': base['actions'],
          'scene_timing_and_camera': {'baseline': base['scene'], 'candidate': candidate['scene'], 'changed': scene_changed},
          'passed': not missing and not changed and not material_changes and not scene_changed,
          'scope': 'All original scene objects, mesh coordinates/topology/material indices/smoothing/available attributes, curves, material bindings and selected shader parameters, frame1 transforms and parent/modifier/constraint records, active action association and all its keyframe/handle/modifier records. New scenery objects excluded from preservation requirement.',
          'limits': ['No rendering and no per-frame evaluation; frame1 plus animation data comparison.',
                     'Not a complete byte comparison of external textures, simulations, nested node groups or every Blender datablock setting.',
                     'Collection memberships can expand for distant collection instances; original object transforms/data are compared.',
                     'Render engine/sampling/volume settings are intentionally outside architecture preservation.']}
(OUT / 'independent-preservation-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print('AUDIT_DONE', report['passed'], 'missing', len(missing), 'unexpected', len(changed), 'materials', len(material_changes), 'allowed', len(allowed), flush=True)
if changed:
    print('CHANGES', json.dumps(changed[:5], ensure_ascii=False), flush=True)
