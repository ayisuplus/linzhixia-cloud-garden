import bpy, json, sys
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]); out=root/'视频制作/第一集园城航线重排-20261023-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(root/'视频制作/第一集园城设计-20261023-v0.1/garden-city-flight-58s-v03.blend'))
bpy.context.scene.frame_set(1)
data=[]
for o in bpy.context.scene.objects:
    if o.hide_render or o.type not in {'MESH','CURVE'}:continue
    v=[o.matrix_world@Vector(q) for q in o.bound_box]
    data.append({'name':o.name,'min':[min(q[i] for q in v) for i in range(3)],'max':[max(q[i] for q in v) for i in range(3)],'collections':[c.name for c in o.users_collection],'physical':bool(o.get('physical',True))})
(out/'review/scene-bounds.local.json').write_text(json.dumps(data),encoding='utf8')
for d in data:
    if any(s in d['name'] for s in ['Reveal','Moon window','screen coping']):print(d)
print('INSPECT_DONE',len(data))
