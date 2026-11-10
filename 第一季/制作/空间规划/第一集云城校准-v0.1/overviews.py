import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;O=R/'视频制作/第一集云城校准-20261024-v0.1'
sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-city-route-58s-v12.blend'));S=bpy.context.scene;cam=S.camera;cam.animation_data_clear();cam.data.lens=32
S.render.resolution_x=1280;S.render.resolution_y=800;S.render.resolution_percentage=100;S.eevee.taa_render_samples=24;S.eevee.volumetric_samples=32
views=[('01-school',L.point(.006,-22,109),L.point(.025,25,101)),('02-cloud-hamlet',L.point(.18,-16,115),L.point(.205,65,99)),('03-ferry',L.point(.60,-10,72),L.point(.635,45,48)),('04-banyuan',L.point(.943,0,37),L.point(.965,-18,24)),('05-cloud-garden',L.point(.285,10,112),L.point(.245,-100,90))]
for name,pos,target in views:
 cam.location=pos;cam.rotation_quaternion=(Vector(target)-cam.location).to_track_quat('-Z','Y');bpy.context.view_layer.update();S.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
print('OVERVIEWS_READY',flush=True)
