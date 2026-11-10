"""Resume the cloud-refined rehearsal; retain native frames for inspection."""
import bpy,sys,argparse,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--offset',type=int,default=0);p.add_argument('--stride',type=int,default=1);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.root)/'视频制作/第一集无人机试飞-20261022-v0.2';bpy.ops.wm.open_mainfile(filepath=str(out/'episode1-drone-rehearsal-v02.blend'));s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
frames=out/'frames';frames.mkdir(exist_ok=True)
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
for f in range(s.frame_start+a.offset,s.frame_end+1,a.stride):
    dest=frames/f'{f:04d}.png'
    if dest.exists():continue
    s.frame_set(f);s.render.filepath=str(dest);t=time.time();bpy.ops.render.render(write_still=True)
    if f%24==0:print('FLIGHT_PROGRESS',f,s.frame_end,round(time.time()-t,2),flush=True)
print('FLIGHT_RENDER_COMPLETE',flush=True)
