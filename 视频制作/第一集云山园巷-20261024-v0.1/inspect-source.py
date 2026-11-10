import bpy,sys,json,numpy as np
from pathlib import Path
R=Path(sys.argv[-1]);O=R/'视频制作/第一集云山园巷-20261024-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(R/'视频制作/第一集池涧水巷-20261024-v0.1/pond-lane-route-58s-v13.blend'))
res=[]
for c in bpy.context.scene.collection.children:
 obs=[]
 for o in c.objects:
  if o.type!='MESH':continue
  v=np.array([o.matrix_world@v.co for v in o.data.vertices]);obs.append({'name':o.name,'lo':v.min(0).tolist(),'hi':v.max(0).tolist(),'physical':bool(o.get('physical',False))})
 res.append({'collection':c.name,'count':len(obs),'objects':obs})
(O/'source-inventory.json').write_text(json.dumps(res,ensure_ascii=False),encoding='utf8')
for c in res:
 print(c['collection'],c['count']);print([x['name'] for x in c['objects'][:8]])
