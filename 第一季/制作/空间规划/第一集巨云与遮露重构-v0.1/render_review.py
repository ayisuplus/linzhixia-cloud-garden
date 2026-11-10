import bpy,sys,argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--source',default='mother-cloud-flight-58s-v01.blend');p.add_argument('--frames',default='overview');p.add_argument('--width',type=int,default=960);p.add_argument('--samples',type=int,default=24);p.add_argument('--engine',default='CYCLES');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
R=Path(a.root);O=R/'视频制作/第一集巨云重构-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/a.source));s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.render.use_persistent_data=True;s.render.resolution_x=a.width;s.render.resolution_y=int(a.width*9/16);s.render.resolution_percentage=100
s.render.engine=a.engine
if a.engine=='BLENDER_EEVEE':
 s.eevee.taa_render_samples=a.samples;s.eevee.volumetric_tile_size='4';s.eevee.volumetric_samples=96;s.eevee.use_volume_custom_range=True;s.eevee.volumetric_start=.3;s.eevee.volumetric_end=5000;s.eevee.use_volumetric_shadows=True
(O/'preview').mkdir(exist_ok=True);original=s.camera
for token in a.frames.split(','):
 if token=='overview':
  s.frame_set(600);d=bpy.data.cameras.new('Giant cloud side review');ob=bpy.data.objects.new('Giant cloud side review',d);s.collection.objects.link(ob);ob.location=(-2300,-1400,920);ob.rotation_euler=(Vector((-650,430,-120))-ob.location).to_track_quat('-Z','Y').to_euler();d.lens=38;d.clip_end=9000;s.camera=ob
 else:s.camera=original;s.frame_set(int(token))
 s.render.image_settings.file_format='PNG';s.render.filepath=str(O/'preview'/f'{token}{"-eevee" if a.engine=="BLENDER_EEVEE" else ""}.png');bpy.ops.render.render(write_still=True);print('REVIEW_FRAME',token,flush=True)
