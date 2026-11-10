import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云中园城-20261024-v0.4'
bpy.ops.wm.open_mainfile(filepath=str(R/'视频制作/第一集云中园城-20261024-v0.3/render-only-batched-v05.blend'))
s=bpy.context.scene
rows=[]
for o in s.objects:
 if o.type=='MESH' and any(m and m.use_nodes and any(n.type=='PRINCIPLED_VOLUME' for n in m.node_tree.nodes) for m in o.data.materials):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];rows.append({'name':o.name,'materials':[m.name for m in o.data.materials],'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)],'hidden':o.hide_render})
(O/'cloud-inventory.json').write_text(json.dumps(rows,indent=2))
for o in s.objects:
 if o.name=='One connected giant cloud / stable support':o.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'diagnostic-no-support.blend'))
