"""Resume a verified saved rehearsal; no scene changes or external services."""
import bpy,sys,argparse,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.root)/'视频制作/第一集无人机试飞-20261022-v0.1';bpy.ops.wm.open_mainfile(filepath=str(out/'episode1-drone-rehearsal-v01.blend'));s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
frames=out/'frames';frames.mkdir(exist_ok=True)
for f in range(s.frame_start,s.frame_end+1):
    dest=frames/f'{f:04d}.png'
    if dest.exists():continue
    s.frame_set(f);s.render.filepath=str(dest);t=time.time();bpy.ops.render.render(write_still=True)
    if f%24==0:print('FLIGHT_PROGRESS',f,s.frame_end,round(time.time()-t,2),flush=True)
print('FLIGHT_RENDER_COMPLETE',flush=True)
