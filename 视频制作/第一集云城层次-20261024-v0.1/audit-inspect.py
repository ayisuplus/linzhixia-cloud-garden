import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path(r'E:/projects/内容创作/未来女孩林知夏/视频制作/第一集云城层次-20261024-v0.1')
bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-neighbourhood-flight-58s-v19.blend'))
r=[]
for o in bpy.context.scene.objects:
 if not o.name.startswith('G ') or o.type!='MESH':continue
 if o.name.startswith('G linked') or o.name.startswith('G lane') or o.name.startswith('G rooted') or o.name.startswith('G street'):continue
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 r.append({'name':o.name,'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)],'matrix':[list(row) for row in o.matrix_world],'local_min':[min(v.co[i] for v in o.data.vertices) for i in range(3)],'local_max':[max(v.co[i] for v in o.data.vertices) for i in range(3)]})
(O/'audit-gate-bounds.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
print(json.dumps([x for x in r if 'back hall opening.001' in x['name']],ensure_ascii=False));print('SLOTS',[(s.material.name if s.material else None,s.link) for s in bpy.data.objects['G reused Repair-workshop / back hall'].material_slots]);print('USED',sorted(set(p.material_index for p in bpy.data.objects['G reused Repair-workshop / back hall'].data.polygons)))
