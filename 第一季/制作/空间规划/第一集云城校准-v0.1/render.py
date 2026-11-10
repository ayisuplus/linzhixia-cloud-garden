import bpy,sys,json,time,math
from pathlib import Path
from mathutils import Quaternion,Vector
R=Path(sys.argv[sys.argv.index('--')+1]);mode=sys.argv[sys.argv.index('--')+2];O=R/'视频制作/第一集云城校准-20261024-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-city-route-58s-v12.blend'));s=bpy.context.scene;cam=s.camera;cam.animation_data_clear();poses=json.loads((O/'route-poses.json').read_text('utf8'))
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.eevee.taa_render_samples=16;s.eevee.volumetric_samples=32
if mode in ['compact-probe','compact-full','compact-tail']:
 # Render-only batching. Editable scene, actions and audit geometry are untouched.
 bpy.ops.object.select_all(action='DESELECT')
 for c in list(s.collection.children):
  if c.name.startswith(('01 ','05 ')):continue
  obs=[o for o in c.objects if o.type=='MESH' and not o.hide_render and not o.modifiers]
  if len(obs)<2:continue
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();bpy.context.view_layer.objects.active.name='Render batch '+c.name;bpy.ops.object.select_all(action='DESELECT')
folder=O/('frames' if mode in ['full','compact-full','compact-tail'] else ('compact-probe' if mode=='compact-probe' else 'flight-preview'));folder.mkdir(exist_ok=True)
indices=range(1392) if mode in ['full','compact-full'] else ([0,384,768] if mode=='compact-probe' else sorted(set(list(range(0,1392,96))+[24,48,120,144,168,264,456,744,780,804,840,864,888,912,960,1008,1296,1320,1344,1368,1391])))
if mode=='compact-tail':indices=range(1301,1392)
start=time.time()
for i in indices:
 p=poses[i];cam.location=p['position'];cam.rotation_quaternion=Quaternion(p['quaternion']);bpy.context.view_layer.update();s.render.filepath=str(folder/f'{i+1:04d}.png');bpy.ops.render.render(write_still=True)
 if i%120==0:print('RENDER_PROGRESS',i+1,round(time.time()-start,1),flush=True)
print('RENDER_READY',mode,round(time.time()-start,1),flush=True)
