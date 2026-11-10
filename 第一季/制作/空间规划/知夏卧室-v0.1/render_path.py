"""Render the saved spatial camera path only, no model edits or AI generation."""
import bpy, sys, argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.root).resolve()/'视频制作/知夏卧室三维空间-20261022-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(out/'zhixia-bedroom-v01.blend'))
s=bpy.context.scene;s.camera=bpy.data.objects['PATH_A010W_spatial_only']
cp=bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
for d in cp.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.cycles.samples=12;s.render.resolution_x=640;s.render.resolution_y=360
frames=out/'path-frames';frames.mkdir(exist_ok=True)
for index,frame in enumerate(range(1,146,2)):
    s.frame_set(frame);s.render.filepath=str(frames/f'{index:04d}.png');bpy.ops.render.render(write_still=True)
print('PATH_PREVIEW_OK',flush=True)
