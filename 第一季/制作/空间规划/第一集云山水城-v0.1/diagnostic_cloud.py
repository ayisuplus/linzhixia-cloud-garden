import bpy,json
from pathlib import Path
O=Path('E:/projects/内容创作/未来女孩林知夏/视频制作/第一集云山水城-20261024-v0.1')
bpy.ops.wm.open_mainfile(filepath=str(O/'render-only-batched-v07.blend'))
for o in bpy.data.objects:
 if o.name.startswith('LANDSCAPE07 Main mountain'):
  print('OBJ',o.name,o.hide_render,list(o.location),list(o.scale),[c.name for c in o.users_collection])
for m in bpy.data.materials:
 if m.name.startswith('LANDSCAPE07 cloud '):
  v=next(n for n in m.node_tree.nodes if n.type=='PRINCIPLED_VOLUME');print('VOL',m.name,[(l.from_node.type,l.to_node.type,l.to_socket.name) for l in m.node_tree.links])
  for l in list(v.inputs['Density'].links):m.node_tree.links.remove(l)
  v.inputs['Density'].default_value=.15
for s in bpy.data.scenes:print('SCENE',s.name,len(s.objects),s.eevee.volumetric_start,s.eevee.volumetric_end)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'render-only-diagnostic.blend'))
