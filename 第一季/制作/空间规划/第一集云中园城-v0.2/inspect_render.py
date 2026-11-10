import bpy,sys,json,collections
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云中园城-20261024-v0.2';bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-city-water-reveal-58s-v04.blend'));s=bpy.context.scene
stats={'camera':{'lens':s.camera.data.lens,'sensor_width':s.camera.data.sensor_width,'sensor_fit':s.camera.data.sensor_fit},'objects':len(s.objects),'visible_meshes':0,'materials':{}}
for ob in s.objects:
 if ob.type=='MESH' and not ob.hide_render:stats['visible_meshes']+=1
for m in bpy.data.materials:
 if m.use_nodes:
  stats['materials'][m.name]={'nodes':[n.type for n in m.node_tree.nodes],'coord_links':[[l.from_node.type,l.from_socket.name,l.to_node.type] for l in m.node_tree.links if l.from_node.type in ['TEX_COORD','NEW_GEOMETRY','ATTRIBUTE']]}
(O/'render-inspection.json').write_text(json.dumps(stats,indent=2),encoding='utf8');print('INSPECTED',flush=True)
