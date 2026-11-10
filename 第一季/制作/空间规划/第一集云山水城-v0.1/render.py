import bpy,sys,time,argparse,json
from pathlib import Path
from mathutils import Quaternion
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--frames',default='275,331,375,408,600,697,1177');p.add_argument('--full',action='store_true');p.add_argument('--file',default='cloud-stone-water-city-58s-v07.blend');p.add_argument('--output',default='preview-v07');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);R=Path(a.root);O=R/'视频制作/第一集云山水城-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/a.file));s=bpy.data.scenes.get('RENDER ONLY batched static architecture') if a.file.startswith('render-only') else bpy.context.scene
bpy.context.window.scene=s
def curves(owner):return [fc for la in owner.animation_data.action.layers for st in la.strips for b in st.channelbags for fc in b.fcurves]
rigcache={};obs={o.name:o for o in s.objects}
for ob in [s.camera,obs['Same carrier ROOT placeholder']]:
 c=curves(ob);rigcache[ob.name]={p:[[fc.evaluate(f) for fc in sorted([q for q in c if q.data_path==p],key=lambda q:q.array_index)] for f in range(1,1393)] for p in ['location','rotation_quaternion']};ob.animation_data_clear()
tree=s.compositing_node_group;cc=curves(tree);sat=[cc[0].evaluate(f) for f in range(1,1393)];tree.animation_data_clear();hue=next(n for n in tree.nodes if n.bl_idname=='CompositorNodeHueSat')
for n in tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=s.view_layers[0].name
folder=O/a.output;folder.mkdir(exist_ok=True)
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.eevee.taa_render_samples=16;s.eevee.volumetric_tile_size='4';s.eevee.volumetric_samples=80;s.render.use_motion_blur=False
tokens=range(1,1393) if a.full else [int(x) for x in a.frames.split(',')]
for f in tokens:
 target=folder/f'{f:04}.png'
 if a.full and target.exists():continue
 start=time.time()
 for name,cache in rigcache.items():obs[name].location=cache['location'][f-1];obs[name].rotation_quaternion=Quaternion(cache['rotation_quaternion'][f-1])
 hue.inputs['Saturation'].default_value=sat[f-1];s.render.image_settings.file_format='PNG';s.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=s.name);print('FRAME_DONE',f,round(time.time()-start,3),flush=True)
print('RENDER_COMPLETE',flush=True)
