import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(R/'视频制作/第一集云中园城-20261024-v0.4/cloud-city-layered-58s-v06.blend'))
rows=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or 'roof' not in ob.name.lower() or 'seam' in ob.name.lower() or 'tile' in ob.name.lower():continue
 p=[ob.matrix_world@Vector(v) for v in ob.bound_box];lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 if hi[0]>-730 and lo[0]<-620 and hi[1]>610 and lo[1]<695:rows.append({'name':ob.name,'lo':lo,'hi':hi})
print(json.dumps(rows),flush=True)
