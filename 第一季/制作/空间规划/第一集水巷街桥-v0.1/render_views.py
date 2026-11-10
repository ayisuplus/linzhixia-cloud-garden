import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
O=R/'视频制作/第一集水巷街桥-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'waterlane-route-58s-v09.blend'));S=bpy.context.scene
folder=O/'views';folder.mkdir(exist_ok=True);S.eevee.taa_render_samples=24
bpy.data.collections['05 Atmospheric envelope optional'].hide_render=True
S.camera=bpy.data.objects['01-masterplan'];S.render.resolution_x=1200;S.render.resolution_y=1400;S.camera.data.ortho_scale=1850;S.render.filepath=str(folder/'01-masterplan.png');bpy.ops.render.render(write_still=True)
S.render.resolution_x=1280;S.render.resolution_y=720
def point(s,d,h):return Vector(L.point(s,d,float(L.water_z(s)+h)))
for name,pos,target in [('02-school-waterfront',point(.075,-18,13),point(.06,31,7)),('03-bay-bridgeheads',point(.55,5,45),point(.605,-15,4)),('04-workshop-lane',point(.928,3,12),point(.885,-18,5))]:
 data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);S.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();data.lens=24;data.clip_end=5000;S.camera=cam;S.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
print('VIEWS_READY',flush=True)
