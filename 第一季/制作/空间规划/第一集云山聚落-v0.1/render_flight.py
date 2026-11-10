import bpy,sys,json,time
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(sys.argv[sys.argv.index('--')+1]);mode=sys.argv[sys.argv.index('--')+2];O=R/'视频制作/第一集云山聚落-20261024-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-hamlet-route-58s-v11.blend'));s=bpy.context.scene;cam=s.camera
poses=json.loads((O/'route-poses.json').read_text('utf8'));cam.animation_data_clear()
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.eevee.taa_render_samples=16;s.eevee.volumetric_samples=32
bpy.data.collections['05 Atmospheric envelope optional'].hide_render=False
folder=O/('flight-preview' if mode=='preview' else 'frames');folder.mkdir(exist_ok=True)
indices=sorted(set(list(range(0,1392,96))+list(range(1152,1273,12))+[1391])) if mode=='preview' else range(1392)
start=time.time()
for i in indices:
 p=poses[i];cam.location=p['position'];cam.rotation_quaternion=Quaternion(p['quaternion']);s.render.filepath=str(folder/f'{i+1:04d}.png');bpy.ops.render.render(write_still=True)
 if i%120==0:print('RENDER_PROGRESS',i+1,round(time.time()-start,1),flush=True)
print('FLIGHT_RENDER_READY',mode,round(time.time()-start,1),flush=True)
