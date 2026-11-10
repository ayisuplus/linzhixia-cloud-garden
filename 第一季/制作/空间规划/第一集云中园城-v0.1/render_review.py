import bpy,sys,time,argparse
from mathutils import Quaternion
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--frames',default='outside,inside,shoulder,230,275,331,495,697,1177');p.add_argument('--motion',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);R=Path(a.root);O=R/'视频制作/第一集云中园城-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'city-within-cloud-reference-v03.blend'));s=bpy.context.scene;original=s.camera
folder=O/('reveal-frames-v03' if a.motion else 'preview-v03');folder.mkdir(exist_ok=True)
# Evaluate only the active animated rig instead of repeatedly updating every inactive historical camera.
def curves(owner):return [fc for l in owner.animation_data.action.layers for st in l.strips for b in st.channelbags for fc in b.fcurves]
rigcache={}
for ob in [original,s.objects['Same carrier ROOT placeholder']]:
 c=curves(ob);rigcache[ob.name]={p:[[fc.evaluate(f) for fc in sorted([q for q in c if q.data_path==p],key=lambda q:q.array_index)] for f in range(1,1393)] for p in ['location','rotation_quaternion']};ob.animation_data_clear()
tree=s.compositing_node_group;cc=curves(tree);sat=[cc[0].evaluate(f) for f in range(1,1393)];tree.animation_data_clear();hue=next(n for n in tree.nodes if n.bl_idname=='CompositorNodeHueSat')
def pose(f):
 for name,cache in rigcache.items():
  ob=s.objects[name];ob.location=cache['location'][f-1];ob.rotation_quaternion=Quaternion(cache['rotation_quaternion'][f-1])
 hue.inputs['Saturation'].default_value=sat[f-1]
if a.motion:s.render.resolution_x=640;s.render.resolution_y=360;s.eevee.taa_render_samples=8;s.eevee.volumetric_tile_size='8';s.eevee.volumetric_samples=48
tokens=list(range(217,409,2)) if a.motion else a.frames.split(',')
for token in tokens:
 start=time.time()
 if str(token) in ['outside','inside','shoulder']:
  name={'outside':'Cloud exterior / partial city glimpses','inside':'Cloud garden interior','shoulder':'Cloud shoulder cut through inhabited volume'}[token];pose(600);s.camera=s.objects[name]
 else:s.camera=original;pose(int(token))
 s.render.image_settings.file_format='PNG';s.render.filepath=str(folder/(f'{int(token):04}.png' if a.motion else f'{token}.png'));bpy.ops.render.render(write_still=True);print('CLOUD_REVIEW',token,round(time.time()-start,2),flush=True)
