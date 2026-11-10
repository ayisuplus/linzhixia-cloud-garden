import bpy,sys,json
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集巨云重构-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'mother-cloud-space-v01.blend'));s=bpy.context.scene
rows=[]
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and any(m and m.use_nodes and any(n.type in ['PRINCIPLED_VOLUME','VOLUME_SCATTER'] for n in m.node_tree.nodes) for m in o.data.materials):rows.append({'name':o.name,'dimensions':list(o.dimensions),'location':list(o.location),'materials':[m.name for m in o.data.materials]})
print('VISIBLE_VOLUMES',json.dumps(rows));print('LIGHTS',[(o.name,o.data.energy,list(o.rotation_euler),o.hide_render) for o in s.objects if o.type=='LIGHT' and o.data.type=='SUN']);print('WORLD',[(n.type,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in s.world.node_tree.nodes]);print('TEMPLATE_BOUNDS',[(min(v[i] for o in bpy.data.collections['Mother cloud existing courtyard template'].objects for v in [o.matrix_world@__import__('mathutils').Vector(q) for q in o.bound_box]),max(v[i] for o in bpy.data.collections['Mother cloud existing courtyard template'].objects for v in [o.matrix_world@__import__('mathutils').Vector(q) for q in o.bound_box])) for i in range(3)])
