import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
O=R/'视频制作/第一集云山园巷-20261024-v0.1';data=json.loads((O/'design-data.json').read_text('utf8'));bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-garden-route-58s-v14.blend'));S=bpy.context.scene;cam=S.camera;cam.animation_data_clear();cam.data.lens=32
S.render.resolution_x=1280;S.render.resolution_y=800;S.render.resolution_percentage=100;S.eevee.taa_render_samples=24;S.eevee.volumetric_samples=32
g=data['gardens'][0];xy=np.array(g['center']);t,n=L.basis(g['s']);f=g['floor'];g2=data['gardens'][1];xy2=np.array(g2['center']);t2,n2=L.basis(g2['s'])
views=[('01-garden-threshold',np.r_[xy-t*24+n*22,f+17],np.r_[xy,f+2]),('02-cloud-shoulder',L.point(.208,-27,108),L.point(.230,-58,97)),('03-courtyard-roofs',L.point(.455,28,77),L.point(.48,45,56)),('04-hidden-water-garden',np.r_[xy2-t2*25+n2*24,g2['floor']+20],np.r_[xy2,g2['floor']+2])]
for name,pos,target in views:
 if len(sys.argv)>sys.argv.index('--')+2 and name!=sys.argv[sys.argv.index('--')+2]:continue
 cam.location=pos;cam.rotation_quaternion=(Vector(target)-cam.location).to_track_quat('-Z','Y');bpy.context.view_layer.update();S.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
print('OVERVIEWS_READY')
