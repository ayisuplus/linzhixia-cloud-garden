import bpy,sys
from pathlib import Path
from mathutils import Vector
import json
from bpy_extras.object_utils import world_to_camera_view
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集山水总图白模-20261024-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(O/'landscape-masterplan-v08.blend'));s=bpy.context.scene
(O/'whitebox').mkdir(exist_ok=True)
P=json.loads((O/'layout-plan.json').read_text('utf8'));p=next(x for x in P['courts'] if x['id']=='Two-level-water-court');n=Vector((*p['outward'],0));c=Vector((*p['center'],0));upper=P['upper_entry']['middle_floor'];target=c-n*70;target.z=40
for name,pos in [('08-upper-entry-view',c+n*23+Vector((0,0,upper+1.7))),('09-lower-water-view',c-n*34+Vector((0,0,41.8)))]:
 d=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();d.lens=24;d.clip_end=5000
for name in ['01-masterplan','02-valley-overview','03-school-to-valley','04-water-bay','05-two-level-court','06-home-workshop','08-upper-entry-view','09-lower-water-view']:
 s.camera=bpy.data.objects[name]
 if name=='01-masterplan':s.render.resolution_x=1200;s.render.resolution_y=1400;s.camera.data.ortho_scale=1850
 else:s.render.resolution_x=1280;s.render.resolution_y=720
 s.render.filepath=str(O/'whitebox'/f'{name}.png');bpy.ops.render.render(write_still=True)
 if name=='01-masterplan':
  labels=[]
  for station,title in [(.065,'① 上游学园'),(.30,'② 夹谷溪路'),(.615,'③ 水湾邻里'),(.94,'④ 半园与作坊')]:
   w=min(P['water_samples'],key=lambda x:abs(x['s']-station));uv=world_to_camera_view(s,s.camera,Vector(w['center']));labels.append({'title':title,'x':uv.x*100,'y':(1-uv.y)*100})
  (O/'map-labels.json').write_text(json.dumps(labels,ensure_ascii=False),encoding='utf8')
print('WHITEBOX_VIEWS_READY',flush=True)
