"""Apply the reviewed courtyard planting offsets to the saved candidate."""
import bpy,sys,json
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]);out=root/'视频制作/第一集园城航线重排-20261023-v0.1'
p=out/'garden-city-space-v01.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
if not s.get('replan_court_planting_refined'):
    data=json.loads((out/'space-plan.json').read_text(encoding='utf8'))
    for c in data['new_compounds']:
        n=c['name'];w,d=c['size']
        for o in s.objects:
            if o.name.startswith(n+' court pine'):o.location.x-=w*.26
            elif o.name.startswith(n+' court rock'):o.location.x-=w*.18;o.location.y+=3-d*.32
    s['replan_court_planting_refined']=True
    bpy.ops.wm.save_as_mainfile(filepath=str(p))
print('COURT_PLANTING_REFINED')
