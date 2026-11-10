import bpy,sys,json
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云中园城-20261024-v0.3';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'视频制作/第一集云中园城-20261024-v0.2/cloud-city-water-reveal-58s-v04.blend'));s=bpy.context.scene
materials={}
for m in bpy.data.materials:
 nodes=[]
 if m.use_nodes:
  for n in m.node_tree.nodes:
   row={'name':n.name,'type':n.type,'inputs':{}}
   for x in n.inputs:
    if x.is_linked:row['inputs'][x.name]={'linked_from':x.links[0].from_node.name,'socket':x.links[0].from_socket.name}
    elif hasattr(x,'default_value'):
     v=x.default_value
     try:row['inputs'][x.name]=list(v)
     except TypeError:row['inputs'][x.name]=v
   nodes.append(row)
 materials[m.name]={'diffuse':list(m.diffuse_color),'nodes':nodes,'sample_objects':[ob.name for ob in s.objects if ob.type=='MESH' and any(mm==m for mm in ob.data.materials)][:18]}
lights=[{'name':ob.name,'type':ob.data.type,'energy':ob.data.energy,'color':list(ob.data.color),'rotation':list(ob.rotation_euler),'position':list(ob.location)} for ob in s.objects if ob.type=='LIGHT']
world=[{'name':n.name,'type':n.type,'inputs':{x.name:list(x.default_value) if x.type=='RGBA' else x.default_value for x in n.inputs if hasattr(x,'default_value') and x.type in {'RGBA','VALUE'}}} for n in s.world.node_tree.nodes]
(O/'source-inspection.json').write_text(json.dumps({'materials':materials,'lights':lights,'world':world,'view':{'transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure}},ensure_ascii=False,indent=2),encoding='utf8');print('INSPECTED',flush=True)
