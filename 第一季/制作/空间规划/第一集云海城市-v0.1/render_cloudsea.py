"""Render optical review in Cycles, keeping cloud revision and saved camera fixed."""
import bpy,sys,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--frames',default='697');p.add_argument('--width',type=int,default=960);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
R=Path(a.root);O=R/'视频制作/第一集云海城市-20261023-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'cloudsea-city-v02.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.max_bounces=4;s.cycles.volume_bounces=1;s.cycles.volume_step_rate=1.5;s.cycles.volume_max_steps=512
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.render.resolution_x=a.width;s.render.resolution_y=int(a.width*9/16);s.render.resolution_percentage=100
# Cloud fronts wrap the bank in selected sectors, instead of hanging uniformly below it.
for o in s.objects:
 if o.name.startswith('Shore rises from rolling cloud'):o.location.z+=8
# Preserve the existing world lighting.
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'cloudsea-city-v03.blend'))
(O/'preview-v03').mkdir(exist_ok=True)
for f in map(int,a.frames.split(',')):
 s.frame_set(f);s.render.filepath=str(O/'preview-v03'/f'{f:04}.png');s.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True);print('CYCLES_FRAME',f,flush=True)
