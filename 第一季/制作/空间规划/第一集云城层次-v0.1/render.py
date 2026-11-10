import bpy,sys,json,time,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(sys.argv[sys.argv.index('--')+1]);mode=sys.argv[sys.argv.index('--')+2];O=R/'视频制作/第一集云城层次-20261024-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-neighbourhood-flight-58s-v19.blend'));S=bpy.context.scene;cam=S.camera;cam.animation_data_clear()
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100;S.eevee.taa_render_samples=16;S.eevee.volumetric_samples=48
if mode=='overview':
 S.render.resolution_x=1440;S.render.resolution_y=900;S.eevee.taa_render_samples=32
 for name,p,target,lens in [('01-overview',(690,-850,610),(5,65,70),48),('02-city-depth',(-310,-85,170),(80,25,80),30),('03-home-neighbours',(315,-230,125),(235,-93,67),40)]:
  cam.location=p;cam.rotation_quaternion=(Vector(target)-cam.location).to_track_quat('-Z','Y');cam.data.lens=lens;S.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
else:
 poses=json.loads((O/'route-poses.json').read_text('utf8'));folder=O/('preview' if mode in ['preview','frame'] else 'frames');folder.mkdir(exist_ok=True);start=time.time()
 args=sys.argv[sys.argv.index('--')+3:]
 ids=sorted(set(list(range(0,1392,72))+[1391])) if mode=='preview' else ([int(args[0])] if mode=='frame' else range(int(args[0]) if args else 0,int(args[1]) if len(args)>1 else 1392))
 if mode=='full':
  context={'scene_sha256':hashlib.sha256((O/'cloud-neighbourhood-flight-58s-v19.blend').read_bytes()).hexdigest(),'poses_sha256':hashlib.sha256((O/'route-poses.json').read_bytes()).hexdigest(),'dimensions':[960,540],'samples':16,'volume_samples':48,'fps':24,'frames':1392,'clouds':'static, camera movement only'}
  ctx=O/'render-context.json'
  if ctx.exists():assert json.loads(ctx.read_text('utf8'))==context,'Frozen render context changed'
  else:ctx.write_text(json.dumps(context,indent=2),encoding='utf8')
 for i in ids:
  if mode=='full' and (folder/f'{i+1:04d}.png').exists():continue
  p=poses[i];cam.location=p['position'];cam.rotation_quaternion=Quaternion(p['quaternion']);S.render.filepath=str(folder/f'{i+1:04d}.png');bpy.ops.render.render(write_still=True)
  if i%120==0:print('RENDER_PROGRESS',i+1,round(time.time()-start,1),flush=True)
print('V19_RENDER_READY',mode,flush=True)
