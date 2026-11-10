import bpy,sys,json
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集池涧水巷-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'pond-lane-route-58s-v13.blend'));r=[]
for name in ['West-neighbourhood-+1-00 court floor','Two-level-water-court court floor','Lower-lane--1-02 court floor']:
 o=bpy.data.objects[name];v=[o.matrix_world@p.co for p in o.data.vertices];o.data.calc_loop_triangles();cross=[(v[t.vertices[1]]-v[t.vertices[0]]).cross(v[t.vertices[2]]-v[t.vertices[0]]).z for t in o.data.loop_triangles];r.append({'name':name,'triangles':len(cross),'positive':sum(c>1e-8 for c in cross),'negative':sum(c< -1e-8 for c in cross),'min_z':min(p.z for p in v),'max_z':max(p.z for p in v)})
(O/'audit-pad-winding.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8');print(json.dumps(r,ensure_ascii=False),flush=True)