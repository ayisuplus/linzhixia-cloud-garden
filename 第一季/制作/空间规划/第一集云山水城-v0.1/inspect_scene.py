import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云山水城-20261024-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(R/'视频制作/第一集云中园城-20261024-v0.4/cloud-city-layered-58s-v06.blend'));s=bpy.context.scene
rows=[]
for ob in s.objects:
 if ob.type!='MESH' or ob.hide_render:continue
 if any(w in ob.name.lower() for w in ['cascade','spill','waterfall','pond','pool','receiving','foam']):
  pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];rows.append({'name':ob.name,'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)],'materials':[m.material.name if m.material else '' for m in ob.material_slots]})
(O/'existing-water-inventory.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
cam=s.camera;fc=[q for la in cam.animation_data.action.layers for st in la.strips for b in st.channelbags for q in b.fcurves];rig=bpy.data.objects['Same carrier ROOT placeholder'];rf=[q for la in rig.animation_data.action.layers for st in la.strips for b in st.channelbags for q in b.fcurves]
rows=[]
for f in range(1,1393):
 def val(curves,p):return [q.evaluate(f) for q in sorted([q for q in curves if q.data_path==p],key=lambda q:q.array_index)]
 rows.append({'frame':f,'camera':val(fc,'location'),'quaternion':val(fc,'rotation_quaternion'),'carrier':val(rf,'location')})
(O/'source-flight.json').write_text(json.dumps(rows),encoding='utf8')
print('INVENTORY_READY',len(rows),flush=True)
