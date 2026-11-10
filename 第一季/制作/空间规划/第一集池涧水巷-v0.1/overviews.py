import bpy,sys,json
from pathlib import Path
import numpy as np
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D));import water_layout as W
L=W.L;O=R/'视频制作/第一集池涧水巷-20261024-v0.1';data=json.loads((O/'water-design-data.json').read_text('utf8'));Z=data['zones']
bpy.ops.wm.open_mainfile(filepath=str(O/'pond-lane-route-58s-v13.blend'));S=bpy.context.scene;cam=S.camera;cam.animation_data_clear();cam.data.lens=32
S.render.resolution_x=1280;S.render.resolution_y=800;S.render.resolution_percentage=100;S.eevee.taa_render_samples=24;S.eevee.volumetric_samples=32
def p(s,d,z):return W.mapped(L.point(s,d,z),Z)[0]
c=next(c for c in L.COURTS if c['id']=='West-neighbourhood-+1-01');xy=np.array(c['center'])+data['rigid_groups'][c['id']]['delta'];t=np.array(c['tangent']);n=np.array(c['outward'])
views=[('01-school-ponds',p(.035,-60,140),p(.065,0,98)),('02-valley-runnel',p(.228,-32,114),p(.245,0,79)),('03-courtyard-pool',np.r_[xy+t*20-n*27,c['floor']+30],np.r_[xy,c['floor']+1]),('04-public-bay',p(.605,-80,90),p(.635,7,43)),('05-waterlane',p(.885,0,60),p(.908,0,24))]
drop=next(g for g in data['added_gardens'] if g['id'].startswith('Rock-side cascade'));t,n=L.basis(drop['station']);n*=drop['side'];xy=np.array(drop['center']);views.append(('06-rock-cascade',np.r_[xy+t*9-n*8,drop['floor']+7],np.r_[xy,drop['floor']-1]))
for name,pos,target in views:
 if len(sys.argv)>sys.argv.index('--')+2 and name!=sys.argv[sys.argv.index('--')+2]:continue
 cam.location=pos;cam.rotation_quaternion=(Vector(target)-cam.location).to_track_quat('-Z','Y');bpy.context.view_layer.update();S.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
print('OVERVIEWS_READY',flush=True)
