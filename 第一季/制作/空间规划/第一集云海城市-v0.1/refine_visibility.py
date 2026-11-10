import bpy,sys,argparse,math
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
R=Path(a.root);O=R/'视频制作/第一集云海城市-20261023-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'cloudsea-city-v03.blend'));s=bpy.context.scene
banks=sorted([o for o in s.objects if o.name.startswith('Shore rises from rolling cloud')],key=lambda o:o.name)
for i,o in enumerate(banks):
 o.location.z-=8
 if i%3!=0:o.hide_render=True
for o in s.objects:
 if o.name.startswith('Cloud sea rolling crest'):o.location.z-=26
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU'
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'cloudsea-city-v04.blend'))
(O/'preview-v04').mkdir(exist_ok=True)
for f in [697,505,817,241,481,1010,1177]:
 s.frame_set(f);s.render.filepath=str(O/'preview-v04'/f'{f:04}.png');bpy.ops.render.render(write_still=True);print('FINAL_CLOUD_FRAME',f,flush=True)
# Separate establishing view; never inserted into the 58-second flight.
cam=s.camera;data=bpy.data.cameras.new('Cloudsea establishing review');ob=bpy.data.objects.new('Cloudsea establishing review',data);s.collection.objects.link(ob);ob.location=(-1850,-400,700);ob.rotation_euler=(Vector((-700,500,0))-ob.location).to_track_quat('-Z','Y').to_euler();data.lens=36;data.clip_end=7000;s.camera=ob;s.render.filepath=str(O/'preview-v04/overview.png');bpy.ops.render.render(write_still=True);s.camera=cam
