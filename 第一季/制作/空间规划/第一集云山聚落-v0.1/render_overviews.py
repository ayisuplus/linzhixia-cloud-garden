import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;O=R/'视频制作/第一集云山聚落-20261024-v0.1'
sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-hamlet-masterplan-v11.blend'));S=bpy.context.scene
data=json.loads((O/'landscape-data.json').read_text('utf8'));ca=bpy.data.cameras.new('Hamlet inspection');cam=bpy.data.objects.new('Hamlet inspection',ca);S.collection.objects.link(cam);S.camera=cam;ca.lens=35;ca.clip_end=5000
S.render.resolution_x=1280;S.render.resolution_y=800;S.render.resolution_percentage=100;S.eevee.taa_render_samples=32
for i,h in enumerate(data['houses'][::2]):
 t,n=L.basis(h['s']);out=n*h['side'];target=Vector((*h['center'],h['floor']+6));cam.location=target+Vector((*(-out*66+t*40),35));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(O/f'hamlet-{i+1}.png');bpy.ops.render.render(write_still=True)
print('OVERVIEWS_READY',flush=True)
