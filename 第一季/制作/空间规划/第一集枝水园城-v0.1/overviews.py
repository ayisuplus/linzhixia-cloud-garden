import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
O=R/'视频制作/第一集枝水园城-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'branch-garden-route-58s-v15.blend'));S=bpy.context.scene;cam=S.camera;cam.animation_data_clear();cam.data.lens=28
S.render.resolution_x=1280;S.render.resolution_y=800;S.render.resolution_percentage=100;S.eevee.taa_render_samples=24;S.eevee.volumetric_samples=32
views=[('01-neighbourhood-branches',L.point(.44,7,116),L.point(.49,2,44)),('02-bay-side-pool',L.point(.567,8,99),L.point(.595,30,38)),('03-lower-steps',L.point(.76,-1,79),L.point(.80,-20,27)),('04-junction-and-bridge',L.point(.445,18,69),L.point(.46,20,47))]
for name,pos,target in views:
 if len(sys.argv)>sys.argv.index('--')+2 and name!=sys.argv[sys.argv.index('--')+2]:continue
 cam.location=pos;cam.rotation_quaternion=(Vector(target)-cam.location).to_track_quat('-Z','Y');bpy.context.view_layer.update();S.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
print('OVERVIEWS_READY')
