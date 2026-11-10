"""Render the saved 58-second timeline without changing its camera or timing."""
import argparse, bpy, sys, time, json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--root',required=True)
p.add_argument('--artifact',default='视频制作/第一集全程快飞-20261023-v0.1')
p.add_argument('--blend',default='episode1-full-route-58s-v01.blend')
p.add_argument('--engine',default='BLENDER_EEVEE')
p.add_argument('--frames',default='1,481,721,1081,1369')
p.add_argument('--all',action='store_true')
p.add_argument('--animation',action='store_true')
p.add_argument('--end',type=int,default=1392)
p.add_argument('--offset',type=int,default=0)
p.add_argument('--stride',type=int,default=1)
p.add_argument('--folder',default='render-review/eevee-test')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.root)/a.artifact
bpy.ops.wm.open_mainfile(filepath=str(out/a.blend))
s=bpy.context.scene
s.render.engine=a.engine
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.use_file_extension=True
if a.engine=='BLENDER_EEVEE':
    s.eevee.taa_render_samples=16
    s.eevee.volumetric_tile_size='8'
    s.eevee.volumetric_samples=64
elif a.engine=='CYCLES':
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    s.cycles.device='GPU'
dest=out/a.folder;dest.mkdir(parents=True,exist_ok=True)
if a.animation:
    s.frame_start=1+a.offset;s.frame_end=a.end;s.frame_step=a.stride
    s.render.filepath=str(dest/'')+'/';s.render.use_overwrite=False
    bpy.ops.render.render(animation=True)
    print('RENDER_COMPLETE',a.engine,flush=True)
    sys.exit(0)
frames=range(1+a.offset,1393,a.stride) if a.all else [int(f) for f in a.frames.split(',')]
for f in frames:
    target=dest/f'{f:04d}.png'
    if target.exists():continue
    s.frame_set(f);s.render.filepath=str(target)
    t=time.monotonic();bpy.ops.render.render(write_still=True)
    print('FRAME_COMPLETE',f,round(time.monotonic()-t,2),flush=True)
print('RENDER_COMPLETE',a.engine,flush=True)
