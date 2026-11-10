"""Apply the last reviewed visibility-only correction without rebuilding valid animation."""
import bpy,json,sys,argparse,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.root)/'视频制作/第一集园城设计-20261023-v0.1'
retired=[]
for filename in ['garden-city-design-v01.blend','garden-city-flight-58s-v03.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(out/filename));names=[]
    for o in bpy.context.scene.objects:
        if o.name.startswith('Ink distant terrain PROXY'):
            o.hide_render=True;o.hide_set(True);o['design_v01_replaced']=True;names.append(o.name)
    assert len(names)==10,names
    bpy.ops.wm.save_as_mainfile(filepath=str(out/filename));retired=names
d=json.loads((out/'design-audit.json').read_text(encoding='utf8'));d['hidden_old_objects']=sorted(set(d['hidden_old_objects']+retired));d['retired_legacy_terrain_proxies']=retired
(out/'design-audit.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
f=json.loads((out/'flight-checks.json').read_text(encoding='utf8'));f['source_sha256']=hashlib.sha256((out/'garden-city-design-v01.blend').read_bytes()).hexdigest();f['retired_nonphysical_terrain_proxies']=retired
(out/'flight-checks.json').write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf8');print('FINAL_SCENE_READY',flush=True)
