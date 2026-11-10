import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云山水城-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'render-only-batched-v07.blend'));s=bpy.context.scene;s.frame_set(331)
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.eevee.volumetric_samples=96
for n in s.compositing_node_group.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=s.view_layers[0].name
folder=O/'details';folder.mkdir(exist_ok=True)
views=[('mountain-water-overview',(-1190,930,140),(-1020,805,55),33),('grotto-and-spillway',(-1050,902,73),(-991,826,49),34)]
for name,loc,target,lens in views:
 d=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,d);s.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=9000;s.camera=cam;s.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
(O/'detail-views.json').write_text(json.dumps({'role':'Additional inspection cameras; original flight unchanged','views':views},indent=2),encoding='utf8')
